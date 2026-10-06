"""
Herní engine Královských rošád (originál: Ruse & Bruise / Gambit Royale).

Engine nic nečte ani nevypisuje - dostává akce hráčů (vylož kartu, rozhodni
o Převleku, ...) a mění stav hry. Server pak každému hráči posílá jen to,
co smí vidět (metoda pohled).

V každém kole leží na stole tolik cílových karet, kolik je hráčů. Pod každou
cílovou kartou vzniká sloupec karet vlivu (seznam shora dolů). Sloupec je
"splněný", když má aspoň tolik karet, kolik je hodnota cílové karty, nebo
ho uzavřela Bouře. Kolo končí okamžitě, jakmile jsou splněné všechny sloupce.

Karta ve sloupci je slovník {"karta", "hrac", "odkryta", "pod_prevlekem"}.
"""

import random

from .karty import (BONUS_SPECIALISTY, KARTY, KATEGORIE, MAX_HRACU, MIN_HRACU,
                    POCET_KOL, SPECIALISTE, nove_cilove_karty, novy_balicek)

VELIKOST_RUKY = 3
MAX_ZAZNAMU = 200

# faze hry
TAH = "tah"                    # hrac na tahu vyklada kartu
VOLBA = "volba"                # ceka se na rozhodnuti o Prevleku/Zradci
VYHODNOCENI = "vyhodnoceni"    # kolo je vyhodnocene, ceka se na potvrzeni
KONEC = "konec"


class ChybaHry(Exception):
    """neplatna akce hrace - zprava je urcena primo hraci"""


class Hra:
    """stav jedne hry a pravidla"""

    def __init__(self, jmena, rng=None):
        if not MIN_HRACU <= len(jmena) <= MAX_HRACU:
            raise ChybaHry(f"Hrát může {MIN_HRACU} až {MAX_HRACU} hráčů.")
        self.rng = rng or random.Random()
        self.hraci = []
        for jmeno in jmena:
            hrac = {"jmeno": jmeno, "balicek": novy_balicek(self.rng),
                    "ruka": [], "odhozene": [], "cilove_karty": []}
            self.hraci.append(hrac)
            self._dober(hrac)
        self.pocet = len(jmena)
        self.cilove_balicek = nove_cilove_karty(self.rng)
        self.kolo = 0
        self.hlavicka = []
        self.sloupce = []
        self.uzavrene = []
        self.na_tahu = 0
        self.faze = TAH
        self.volba = None
        self.vysledky_kola = []
        self.potvrdili = []
        self.zaznamy = []
        self.poradi = []
        self._zacni_kolo()

    # ---------------------------------------------------------------- akce

    def vyloz(self, hrac, index_karty, sloupec):
        """hrac vylozi kartu z ruky lícem dolu na konec sloupce"""
        self._kontrola_faze(TAH)
        if hrac != self.na_tahu:
            raise ChybaHry("Nejsi na tahu.")
        ruka = self.hraci[hrac]["ruka"]
        if not 0 <= index_karty < len(ruka):
            raise ChybaHry("Taková karta v ruce není.")
        if not 0 <= sloupec < self.pocet:
            raise ChybaHry("Takový sloupec neexistuje.")
        if self.uzavrene[sloupec]:
            raise ChybaHry("Tento sloupec uzavřela Bouře.")

        nazev = ruka.pop(index_karty)
        self._dober(self.hraci[hrac])
        # Objevitele, kteri v tomto tahu uz cestovali (proti nekonecne smycce)
        self._cestovali = set()
        self._zaznam(f"{self._jmeno(hrac)} vyložil(a) kartu "
                     f"do sloupce {sloupec + 1}.")
        self._pridej(sloupec, {"karta": nazev, "hrac": hrac,
                               "odkryta": False, "pod_prevlekem": None})
        if self.volba is None:
            self._dalsi_tah()

    def prevlek(self, hrac, index_karty):
        """vlastnik otoceneho Prevleku pod nej vlozi kartu (None = nic)"""
        self._kontrola_volby(hrac, "prevlek")
        karta = self.sloupce[self.volba["sloupec"]][self.volba["index"]]
        if index_karty is None:
            self._zaznam(f"{self._jmeno(hrac)} pod Převlek nic nevložil(a).")
        else:
            ruka = self.hraci[hrac]["ruka"]
            if not 0 <= index_karty < len(ruka):
                raise ChybaHry("Taková karta v ruce není.")
            karta["pod_prevlekem"] = ruka.pop(index_karty)
            self._dober(self.hraci[hrac])
            self._zaznam(f"{self._jmeno(hrac)} skryl(a) kartu pod Převlek.")
        self._dokonci_volbu()

    def zradce(self, hrac, sloupec):
        """vlastnik otoceneho Zradce vymeni cilovou kartu sveho sloupce
        s cilovou kartou jineho sloupce (None = nic)"""
        self._kontrola_volby(hrac, "zradce")
        vlastni = self.volba["sloupec"]
        if sloupec is None:
            self._zaznam(f"{self._jmeno(hrac)} se rozhodl(a) nic neprohazovat.")
        else:
            if not 0 <= sloupec < self.pocet:
                raise ChybaHry("Takový sloupec neexistuje.")
            if sloupec == vlastni:
                raise ChybaHry("Vyber jiný sloupec, než ve kterém je Zrádce.")
            hlavicka = self.hlavicka
            hlavicka[vlastni], hlavicka[sloupec] = (hlavicka[sloupec],
                                                    hlavicka[vlastni])
            self._zaznam(f"Zrádce! {self._jmeno(hrac)} prohodil(a) cílové "
                         f"karty ve sloupcích {vlastni + 1} a {sloupec + 1}.")
        self._dokonci_volbu()

    def pokracovat(self, hrac, za_vsechny=False):
        """hrac potvrdi, ze videl vyhodnoceni kola"""
        self._kontrola_faze(VYHODNOCENI)
        if za_vsechny:
            self.potvrdili = list(range(self.pocet))
        elif hrac not in self.potvrdili:
            self.potvrdili.append(hrac)
        if len(self.potvrdili) == self.pocet:
            self.kolo += 1
            self._zacni_kolo()

    # --------------------------------------------------------- prubeh kola

    def _zacni_kolo(self):
        # karty vylozene v minulem kole jdou vlastnikum na odhazovaci balicek
        for sloupec in self.sloupce:
            for karta in sloupec:
                self._odhod(karta)
        self.hlavicka = [self.cilove_balicek.pop() for _ in range(self.pocet)]
        self.sloupce = [[] for _ in range(self.pocet)]
        self.uzavrene = [False] * self.pocet
        # poradi plynule pokracuje: nove kolo zacina hrac po tom,
        # kdo predchozi kolo ukoncil
        self.na_tahu = 0 if self.kolo == 0 else (self.na_tahu + 1) % self.pocet
        self.faze = TAH
        self.volba = None
        self.vysledky_kola = []
        self.potvrdili = []
        self._zaznam(f"Začíná {self.kolo + 1}. kolo, "
                     f"první hraje {self._jmeno(self.na_tahu)}.")

    def splneny(self, sloupec):
        """sloupec ma dost karet (nebo ho uzavrela Boure)"""
        return (self.uzavrene[sloupec] or
                len(self.sloupce[sloupec]) >= self.hlavicka[sloupec]["hodnota"])

    def _dalsi_tah(self):
        if all(self.splneny(s) for s in range(self.pocet)):
            self._vyhodnot_kolo()
            return
        # hrac bez karet (vzacne - dosly mu vsechny karty) se preskakuje
        for posun in range(1, self.pocet + 1):
            dalsi = (self.na_tahu + posun) % self.pocet
            if self.hraci[dalsi]["ruka"]:
                self.na_tahu = dalsi
                self.faze = TAH
                return
        self._zaznam("Nikdo už nemá karty, kolo končí.")
        self._vyhodnot_kolo()

    def _dokonci_volbu(self):
        self.volba = None
        self._dalsi_tah()

    def _dober(self, hrac):
        """doplni ruku; dojde-li balicek, zamicha se odhazovaci balicek"""
        while len(hrac["ruka"]) < VELIKOST_RUKY:
            if not hrac["balicek"]:
                if not hrac["odhozene"]:
                    return
                hrac["balicek"] = hrac["odhozene"]
                hrac["odhozene"] = []
                self.rng.shuffle(hrac["balicek"])
            hrac["ruka"].append(hrac["balicek"].pop())

    def _odhod(self, karta):
        """karta ze stolu jde vlastnikovi na odhazovaci balicek"""
        odhozene = self.hraci[karta["hrac"]]["odhozene"]
        odhozene.append(karta["karta"])
        if karta["pod_prevlekem"]:
            odhozene.append(karta["pod_prevlekem"])

    # ------------------------------------------------------- otaceni karet

    def _pridej(self, sloupec, karta):
        """polozi kartu na konec sloupce; zakryta karta nad ni se otoci"""
        sloupec_karet = self.sloupce[sloupec]
        sloupec_karet.append(karta)
        if len(sloupec_karet) >= 2 and not sloupec_karet[-2]["odkryta"]:
            self._otoc(sloupec, len(sloupec_karet) - 2)

    def _otoc(self, sloupec, index):
        karta = self.sloupce[sloupec][index]
        karta["odkryta"] = True
        nazev = karta["karta"]
        kdo = self._jmeno(karta["hrac"])
        self._zaznam(f"Otočena karta {nazev} ({kdo}) ve sloupci {sloupec + 1}.")

        if nazev == "Objevitel":
            if id(karta) in self._cestovali:
                self._zaznam("Objevitel už v tomto tahu cestoval, zůstává.")
            else:
                self._cestovali.add(id(karta))
                self._objevitel(sloupec, index)
        elif nazev == "Mordýř":
            obet = self.sloupce[sloupec].pop(index + 1)
            self._odhod(obet)
            self._zaznam(f"Mordýř zabil kartu hráče "
                         f"{self._jmeno(obet['hrac'])}.")
        elif nazev == "Bouře":
            self.uzavrene[sloupec] = True
            self._zaznam(f"Bouře uzavřela sloupec {sloupec + 1}.")
        elif nazev == "Převlek":
            self.volba = {"typ": "prevlek", "hrac": karta["hrac"],
                          "sloupec": sloupec, "index": index}
            self.faze = VOLBA
        elif nazev == "Zrádce":
            self.volba = {"typ": "zradce", "hrac": karta["hrac"],
                          "sloupec": sloupec, "index": index}
            self.faze = VOLBA

    def _objevitel(self, sloupec, index):
        """Objevitel se presune lícem dolu na konec dalsiho sloupce vpravo
        (za poslednim sloupcem pokracuje prvnim); uzavrene sloupce preskoci"""
        for posun in range(1, self.pocet):
            cil = (sloupec + posun) % self.pocet
            if not self.uzavrene[cil]:
                break
        else:
            self._zaznam("Objevitel nemá kam odcestovat, zůstává na místě.")
            return

        objevitel = self.sloupce[sloupec].pop(index)
        objevitel["odkryta"] = False
        self._zaznam(f"Objevitel odcestoval do sloupce {cil + 1}.")
        self._pridej(cil, objevitel)

    # ----------------------------------------------------------- vyhodnoceni

    def _vyhodnot_kolo(self):
        for sloupec in self.sloupce:
            for karta in sloupec:
                karta["odkryta"] = True

        self.vysledky_kola = [self._vyhodnot_sloupec(sloupec)
                              for sloupec in range(self.pocet)]
        for vysledek in self.vysledky_kola:
            cilova = self.hlavicka[vysledek["sloupec"]]
            if vysledek["vitez"] is None:
                self._zaznam(f"Sloupec {vysledek['sloupec'] + 1} nikdo "
                             f"nevyhrál.")
            else:
                self.hraci[vysledek["vitez"]]["cilove_karty"].append(cilova)
                self._zaznam(f"Sloupec {vysledek['sloupec'] + 1} "
                             f"({cilova['kategorie']} {cilova['hodnota']}) "
                             f"vyhrál(a) {self._jmeno(vysledek['vitez'])}.")

        if self.kolo + 1 >= POCET_KOL:
            self._konec_hry()
        else:
            self.faze = VYHODNOCENI

    def _spocitej_hodnoty(self, karty, kategorie):
        """hodnoty karet se schopnostmi, ktere meni jejich vlastni hodnotu
        (pocita se jen s kartami, ktere ve sloupci zustaly)"""
        aktivni = [k for k in karty if not k["odstranena"]]
        ostatnich = len(aktivni) - 1
        for karta in aktivni:
            nazev = karta["nazev"]
            hodnota = KARTY[nazev]["hodnota"]
            if SPECIALISTE.get(nazev) == kategorie:
                hodnota = BONUS_SPECIALISTY
            elif nazev == "Poustevník":
                hodnota -= ostatnich
            elif nazev == "Paleček":
                hodnota += 3 * ostatnich
            elif nazev == "Romeo" and any(
                    k["nazev"] == "Julie" and k["hrac"] == karta["hrac"]
                    for k in aktivni):
                hodnota += 10
            karta["hodnota"] = hodnota
        # Dvojnik prebira hodnotu karty tesne pod sebou (odspodu nahoru,
        # aby fungovalo i vic Dvojniku pod sebou); bez karty pod sebou
        # nema zadnou hodnotu (None)
        for i in range(len(aktivni) - 1, -1, -1):
            if aktivni[i]["nazev"] == "Dvojník":
                aktivni[i]["hodnota"] = (aktivni[i + 1]["hodnota"]
                                         if i + 1 < len(aktivni) else None)

    def _vyhodnot_sloupec(self, sloupec):
        """spocita sloupec a vrati podrobny vysledek pro zobrazeni"""
        kategorie = self.hlavicka[sloupec]["kategorie"]
        karty = []
        for index, karta in enumerate(self.sloupce[sloupec]):
            nazev = karta["pod_prevlekem"] or karta["karta"]
            karty.append({"index": index, "hrac": karta["hrac"], "nazev": nazev,
                          "prevlek": karta["pod_prevlekem"] is not None,
                          "hodnota": (None if nazev == "Dvojník"
                                      else KARTY[nazev]["hodnota"]),
                          "odstranena": False})
        poznamky = []
        vysledek = {"sloupec": sloupec, "karty": karty, "poznamky": poznamky,
                    "soucty": {}, "vitez": None, "nejnizsi_vyhrava": False}

        def je(nazev):
            return pocet(nazev) > 0

        def pocet(nazev):
            return sum(k["nazev"] == nazev and not k["odstranena"]
                       for k in karty)

        if je("Mušketýři"):
            poznamky.append("Mušketýři: žádné schopnosti neplatí, počítají "
                            "se jen základní hodnoty.")
        else:
            self._spocitej_hodnoty(karty, kategorie)
            # dva Magove (dve Carodejnice) se navzajem zrusi
            magu = pocet("Mág")
            if magu % 2:
                poznamky.append("Mág odstranil karty s hodnotou 10 a více.")
                for karta in karty:
                    if karta["hodnota"] is not None and karta["hodnota"] >= 10:
                        karta["odstranena"] = True
            elif magu:
                poznamky.append("Mágové se navzájem zrušili.")
            carodejnic = pocet("Čarodějnice")
            if carodejnic % 2:
                poznamky.append("Čarodějnice odstranila karty s hodnotou "
                                "9 a méně.")
                for karta in karty:
                    if (karta["hodnota"] is not None and karta["hodnota"] <= 9
                            and karta["nazev"] != "Čarodějnice"):
                        karta["odstranena"] = True
            elif carodejnic:
                poznamky.append("Čarodějnice se navzájem zrušily.")
            self._spocitej_hodnoty(karty, kategorie)

            aktivni = [k for k in karty if not k["odstranena"]]
            vitez = self._princ_panos(aktivni)
            if vitez is not None:
                poznamky.append(f"{self._jmeno(vitez)} má Prince i Panoše "
                                f"a vyhrává sloupec.")
                vysledek["vitez"] = vitez
                return vysledek

            for drak in [k for k in aktivni if k["nazev"] == "Drak"]:
                poznamky.append(f"Drak ({self._jmeno(drak['hrac'])}) ubral "
                                f"soupeřům 2 body z každé karty.")
                for karta in aktivni:
                    hodnota = karta["hodnota"]
                    if (karta["hrac"] != drak["hrac"] and hodnota is not None
                            and hodnota > 0):
                        # hodnota karty neklesne pod nulu
                        karta["hodnota"] = max(0, hodnota - 2)
            if je("Žebrák"):
                poznamky.append("Žebrák: vyhrává nejnižší součet.")
                vysledek["nejnizsi_vyhrava"] = True

        # Dvojnik bez hodnoty se nepocita - hrac jen s nim sloupec nevyhraje
        aktivni = [k for k in karty
                   if not k["odstranena"] and k["hodnota"] is not None]
        soucty = {}
        for karta in aktivni:
            soucty[karta["hrac"]] = soucty.get(karta["hrac"], 0) + karta["hodnota"]
        vysledek["soucty"] = soucty
        if not soucty:
            poznamky.append("Ve sloupci nezůstala žádná karta.")
            return vysledek

        cil = (min if vysledek["nejnizsi_vyhrava"] else max)(soucty.values())
        remiza = [hrac for hrac, soucet in soucty.items() if soucet == cil]
        if len(remiza) > 1:
            # pri remize vyhrava hrac s kartou nejbliz cilove karte,
            # se Zebrakem naopak hrac s kartou nejdal od ni
            if vysledek["nejnizsi_vyhrava"]:
                poradi = list(reversed(aktivni))
                poznamky.append("Remíza – vyhrává karta nejdál od cílové karty.")
            else:
                poradi = aktivni
                poznamky.append("Remíza – vyhrává karta nejblíž cílové kartě.")
            vysledek["vitez"] = next(k["hrac"] for k in poradi
                                     if k["hrac"] in remiza)
        else:
            vysledek["vitez"] = remiza[0]
        return vysledek

    @staticmethod
    def _princ_panos(aktivni):
        """hrac s Princem i Panosem ve sloupci; pri vice takovych vyhrava
        ten, jehoz karta z dvojice lezi nejvys"""
        nejlepsi = None
        for hrac in {k["hrac"] for k in aktivni}:
            dvojice = [k for k in aktivni
                       if k["hrac"] == hrac and k["nazev"] in ("Princ", "Panoš")]
            if {k["nazev"] for k in dvojice} == {"Princ", "Panoš"}:
                prvni = min(k["index"] for k in dvojice)
                if nejlepsi is None or prvni < nejlepsi[0]:
                    nejlepsi = (prvni, hrac)
        return None if nejlepsi is None else nejlepsi[1]

    def _konec_hry(self):
        self.faze = KONEC
        skore = [(self.skore(i), i) for i in range(self.pocet)]
        skore.sort(key=lambda x: -x[0])
        self.poradi = [{"hrac": i, "body": body} for body, i in skore]
        nejvic = skore[0][0]
        viteze = [self._jmeno(i) for body, i in skore if body == nejvic]
        self._zaznam(f"Konec hry! Vítězí {', '.join(viteze)} "
                     f"s {nejvic} body.")

    def skore(self, hrac):
        """body za cilove karty; ma-li hrac vsech 6 kategorii, muze
        se pocitat nejvyssi karta kazde kategorie dvojnasobne
        a za kazdou dalsi kartu se 1 bod odecte"""
        cilove = self.hraci[hrac]["cilove_karty"]
        zakladni = sum(karta["hodnota"] for karta in cilove)
        if {karta["kategorie"] for karta in cilove} != set(KATEGORIE):
            return zakladni
        nejvyssi = {}
        for karta in cilove:
            kat = karta["kategorie"]
            nejvyssi[kat] = max(nejvyssi.get(kat, 0), karta["hodnota"])
        specialni = 2 * sum(nejvyssi.values()) - (len(cilove) - len(nejvyssi))
        return max(zakladni, specialni)

    # ------------------------------------------------------------- pomocne

    def _kontrola_faze(self, faze):
        if self.faze != faze:
            raise ChybaHry("Tuto akci teď nelze provést.")

    def _kontrola_volby(self, hrac, typ):
        self._kontrola_faze(VOLBA)
        if self.volba["typ"] != typ or self.volba["hrac"] != hrac:
            raise ChybaHry("Teď nerozhoduješ ty.")

    def _jmeno(self, hrac):
        return self.hraci[hrac]["jmeno"]

    def _zaznam(self, text):
        self.zaznamy.append(text)
        del self.zaznamy[:-MAX_ZAZNAMU]

    # ------------------------------------------------- pohled a ukladani

    def pohled(self, ja):
        """stav hry tak, jak ho smi videt hrac ja (None = divak)"""
        konec_kola = self.faze in (VYHODNOCENI, KONEC)
        sloupce = []
        for sloupec in self.sloupce:
            sloupec_pohled = []
            for karta in sloupec:
                moje = karta["hrac"] == ja
                videt = karta["odkryta"] or moje
                prevlek = karta["pod_prevlekem"]
                sloupec_pohled.append({
                    "hrac": karta["hrac"],
                    "odkryta": karta["odkryta"],
                    "karta": karta["karta"] if videt else None,
                    "ma_prevlek": prevlek is not None,
                    "pod_prevlekem": prevlek if (moje or konec_kola) else None,
                })
            sloupce.append(sloupec_pohled)

        hraci = []
        for i, hrac in enumerate(self.hraci):
            hraci.append({"jmeno": hrac["jmeno"],
                          "cilove_karty": hrac["cilove_karty"],
                          "skore": self.skore(i)})

        return {
            "faze": self.faze,
            "kolo": self.kolo,
            "pocet_kol": POCET_KOL,
            "na_tahu": self.na_tahu,
            "ja": ja,
            "hraci": hraci,
            "hlavicka": self.hlavicka,
            "sloupce": sloupce,
            "uzavrene": self.uzavrene,
            "ruka": list(self.hraci[ja]["ruka"]) if ja is not None else [],
            "volba": ({"typ": self.volba["typ"], "hrac": self.volba["hrac"],
                       "sloupec": self.volba["sloupec"]}
                      if self.volba else None),
            "vysledky_kola": self.vysledky_kola if konec_kola else [],
            "potvrdili": self.potvrdili,
            "poradi": self.poradi,
            "zaznamy": self.zaznamy[-50:],
        }

    _UKLADANE = ["hraci", "pocet", "cilove_balicek", "kolo", "hlavicka",
                 "sloupce", "uzavrene", "na_tahu", "faze", "volba",
                 "vysledky_kola", "potvrdili", "zaznamy", "poradi"]

    def do_slovniku(self):
        """kompletni stav pro ulozeni na disk"""
        return {klic: getattr(self, klic) for klic in self._UKLADANE}

    @classmethod
    def ze_slovniku(cls, data, rng=None):
        hra = cls.__new__(cls)
        hra.rng = rng or random.Random()
        for klic in cls._UKLADANE:
            setattr(hra, klic, data[klic])
        for hrac in hra.hraci:
            hrac.setdefault("odhozene", [])
        # JSON nezna celociselne klice slovniku
        for vysledek in hra.vysledky_kola:
            vysledek["soucty"] = {int(k): v
                                  for k, v in vysledek["soucty"].items()}
        return hra
