"""
Herní engine Královských rošád.

Engine nic nečte ani nevypisuje - dostává akce hráčů (vylož kartu, rozhodni
o Převleku, ...) a mění stav hry. Server pak každému hráči posílá jen to,
co smí vidět (metoda pohled).

Hrací plocha má N řádků a N sloupců (N = počet hráčů). Pole je:
    None                         volné místo
    {"blokovano": True}          místo zablokované Bouří
    {"karta", "hrac", "odkryta", "pod_prevlekem"}   vyložená karta
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
                    "ruka": [], "cilove_karty": []}
            self.hraci.append(hrac)
            self._dober(hrac)
        self.pocet = len(jmena)
        self.cilove_balicek = nove_cilove_karty(self.rng)
        self.kolo = 0
        self.hlavicka = []
        self.plocha = []
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
        """hrac vylozi kartu z ruky do sloupce (na prvni volne misto)"""
        self._kontrola_faze(TAH)
        if hrac != self.na_tahu:
            raise ChybaHry("Nejsi na tahu.")
        ruka = self.hraci[hrac]["ruka"]
        if not 0 <= index_karty < len(ruka):
            raise ChybaHry("Taková karta v ruce není.")
        if not 0 <= sloupec < self.pocet:
            raise ChybaHry("Takový sloupec neexistuje.")
        radek = self._volny_radek(sloupec)
        if radek is None:
            raise ChybaHry("Tento sloupec je už plný.")

        nazev = ruka.pop(index_karty)
        self._dober(self.hraci[hrac])
        self.plocha[radek][sloupec] = {"karta": nazev, "hrac": hrac,
                                       "odkryta": False, "pod_prevlekem": None}
        self._zaznam(f"{self._jmeno(hrac)} vyložil(a) kartu "
                     f"do sloupce {sloupec + 1}.")
        self._otoc_nad(radek, sloupec)
        if self.volba is None:
            self._dalsi_tah()

    def prevlek(self, hrac, index_karty):
        """vlastnik otoceneho Prevleku pod nej vlozi kartu (None = nic)"""
        self._kontrola_volby(hrac, "prevlek")
        pole = self.plocha[self.volba["radek"]][self.volba["sloupec"]]
        if index_karty is None:
            self._zaznam(f"{self._jmeno(hrac)} pod Převlek nic nevložil(a).")
        else:
            ruka = self.hraci[hrac]["ruka"]
            if not 0 <= index_karty < len(ruka):
                raise ChybaHry("Taková karta v ruce není.")
            pole["pod_prevlekem"] = ruka.pop(index_karty)
            self._dober(self.hraci[hrac])
            self._zaznam(f"{self._jmeno(hrac)} skryl(a) kartu pod Převlek.")
        self._dokonci_volbu()

    def zradce(self, hrac, sloupec_a, sloupec_b):
        """vlastnik otoceneho Zradce prohodi dve cilove karty (None = nic)"""
        self._kontrola_volby(hrac, "zradce")
        if sloupec_a is None or sloupec_b is None:
            self._zaznam(f"{self._jmeno(hrac)} se rozhodl(a) nic neprohazovat.")
        else:
            if not (0 <= sloupec_a < self.pocet and 0 <= sloupec_b < self.pocet):
                raise ChybaHry("Takový sloupec neexistuje.")
            if sloupec_a == sloupec_b:
                raise ChybaHry("Vyber dva různé sloupce.")
            hlavicka = self.hlavicka
            hlavicka[sloupec_a], hlavicka[sloupec_b] = (hlavicka[sloupec_b],
                                                        hlavicka[sloupec_a])
            self._zaznam(f"Zrádce! {self._jmeno(hrac)} prohodil(a) cílové "
                         f"karty ve sloupcích {sloupec_a + 1} a {sloupec_b + 1}.")
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
        self.hlavicka = [self.cilove_balicek.pop() for _ in range(self.pocet)]
        self.plocha = [[None] * self.pocet for _ in range(self.pocet)]
        # zacinajici hrac se kazde kolo posouva
        self.na_tahu = self.kolo % self.pocet
        self.faze = TAH
        self.volba = None
        self.vysledky_kola = []
        self.potvrdili = []
        self._zaznam(f"Začíná {self.kolo + 1}. kolo, "
                     f"první hraje {self._jmeno(self.na_tahu)}.")

    def _dalsi_tah(self):
        if self._plna():
            self._vyhodnot_kolo()
        else:
            self.na_tahu = (self.na_tahu + 1) % self.pocet
            self.faze = TAH

    def _dokonci_volbu(self):
        self.volba = None
        self._dalsi_tah()

    def _plna(self):
        return all(pole is not None for radek in self.plocha for pole in radek)

    def _volny_radek(self, sloupec):
        for radek in range(self.pocet):
            if self.plocha[radek][sloupec] is None:
                return radek
        return None

    def _dober(self, hrac):
        """doplni ruku; dojde-li balicek, zamicha se novy bez karet v ruce"""
        while len(hrac["ruka"]) < VELIKOST_RUKY:
            if not hrac["balicek"]:
                hrac["balicek"] = [karta for karta in novy_balicek(self.rng)
                                   if karta not in hrac["ruka"]]
            hrac["ruka"].append(hrac["balicek"].pop())

    # ------------------------------------------------------- otaceni karet

    def _otoc_nad(self, radek, sloupec):
        """karta polozena na (radek, sloupec) otoci zakrytou kartu nad sebou"""
        if radek == 0:
            return
        nad = self.plocha[radek - 1][sloupec]
        if nad and not nad.get("blokovano") and not nad["odkryta"]:
            self._otoc(radek - 1, sloupec)

    def _otoc(self, radek, sloupec):
        pole = self.plocha[radek][sloupec]
        pole["odkryta"] = True
        nazev = pole["karta"]
        kdo = self._jmeno(pole["hrac"])
        self._zaznam(f"Otočena karta {nazev} ({kdo}) ve sloupci {sloupec + 1}.")

        if nazev == "Objevitel":
            self._objevitel(radek, sloupec)
        elif nazev == "Mordýř":
            pod = self.plocha[radek + 1][sloupec]
            self.plocha[radek + 1][sloupec] = None
            self._zaznam(f"Mordýř zabil kartu hráče {self._jmeno(pod['hrac'])}.")
        elif nazev == "Bouře":
            if radek + 2 < self.pocet:
                for radek_pod in range(radek + 2, self.pocet):
                    self.plocha[radek_pod][sloupec] = {"blokovano": True}
                self._zaznam(f"Bouře uzavřela sloupec {sloupec + 1}.")
        elif nazev == "Převlek":
            self.volba = {"typ": "prevlek", "hrac": pole["hrac"],
                          "radek": radek, "sloupec": sloupec}
            self.faze = VOLBA
        elif nazev == "Zrádce":
            self.volba = {"typ": "zradce", "hrac": pole["hrac"],
                          "radek": radek, "sloupec": sloupec}
            self.faze = VOLBA

    def _objevitel(self, radek, sloupec):
        """Objevitel odcestuje na prvni volne misto v dalsich sloupcich"""
        for posun in range(1, self.pocet):
            cil_sloupec = (sloupec + posun) % self.pocet
            cil_radek = self._volny_radek(cil_sloupec)
            if cil_radek is not None:
                break
        else:
            self._zaznam("Objevitel nemá kam odcestovat, zůstává na místě.")
            return

        self.plocha[cil_radek][cil_sloupec] = self.plocha[radek][sloupec]
        self.plocha[radek][sloupec] = self.plocha[radek + 1][sloupec]
        self.plocha[radek + 1][sloupec] = None
        self._zaznam(f"Objevitel odcestoval do sloupce {cil_sloupec + 1}.")
        # v novem sloupci je jako nove vylozeny
        self._otoc_nad(cil_radek, cil_sloupec)

    # ----------------------------------------------------------- vyhodnoceni

    def _vyhodnot_kolo(self):
        for radek in self.plocha:
            for pole in radek:
                if pole and not pole.get("blokovano"):
                    pole["odkryta"] = True

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

    def _vyhodnot_sloupec(self, sloupec):
        """spocita sloupec a vrati podrobny vysledek pro zobrazeni"""
        kategorie = self.hlavicka[sloupec]["kategorie"]
        karty = []
        for radek in range(self.pocet):
            pole = self.plocha[radek][sloupec]
            if pole is None or pole.get("blokovano"):
                continue
            nazev = pole["pod_prevlekem"] or pole["karta"]
            hodnota = KARTY[nazev]["hodnota"]
            if SPECIALISTE.get(nazev) == kategorie:
                hodnota = BONUS_SPECIALISTY
            karty.append({"radek": radek, "hrac": pole["hrac"], "nazev": nazev,
                          "prevlek": pole["pod_prevlekem"] is not None,
                          "hodnota": hodnota, "odstranena": False})
        poznamky = []
        vysledek = {"sloupec": sloupec, "karty": karty, "poznamky": poznamky,
                    "soucty": {}, "vitez": None, "nejnizsi_vyhrava": False}

        def je(nazev):
            return any(k["nazev"] == nazev and not k["odstranena"]
                       for k in karty)

        if je("Mušketýři"):
            poznamky.append("Mušketýři: zvláštní schopnosti neplatí.")
        else:
            for i, karta in enumerate(karty):
                if karta["nazev"] == "Dvojník":
                    vzor = next((k for k in karty[i + 1:]
                                 if k["nazev"] != "Dvojník"), None)
                    karta["hodnota"] = vzor["hodnota"] if vzor else 0

            if je("Mág"):
                poznamky.append("Mág odstranil karty s hodnotou 10 a více.")
                for karta in karty:
                    karta["odstranena"] = karta["hodnota"] >= 10
            elif je("Čarodějnice"):
                poznamky.append("Čarodějnice odstranila karty s hodnotou "
                                "9 a méně.")
                for karta in karty:
                    karta["odstranena"] = (karta["hodnota"] <= 9 and
                                           karta["nazev"] != "Čarodějnice")

            aktivni = [k for k in karty if not k["odstranena"]]
            vitez = self._princ_panos(aktivni)
            if vitez is not None:
                poznamky.append(f"{self._jmeno(vitez)} má Prince i Panoše "
                                f"a vyhrává sloupec.")
                vysledek["vitez"] = vitez
                return vysledek

            for i, karta in enumerate(karty):
                pocet_pod = len(karty) - i - 1
                if karta["odstranena"]:
                    continue
                if karta["nazev"] == "Poustevník":
                    karta["hodnota"] -= pocet_pod
                elif karta["nazev"] == "Paleček":
                    karta["hodnota"] += 3 * pocet_pod
                elif karta["nazev"] == "Romeo" and any(
                        k["nazev"] == "Julie" and k["hrac"] == karta["hrac"]
                        for k in aktivni):
                    karta["hodnota"] = 15
            for drak in [k for k in aktivni if k["nazev"] == "Drak"]:
                poznamky.append(f"Drak ({self._jmeno(drak['hrac'])}) ubral "
                                f"soupeřům 2 body z každé karty.")
                for karta in aktivni:
                    if karta["hrac"] != drak["hrac"]:
                        karta["hodnota"] -= 2
            if je("Žebrák"):
                poznamky.append("Žebrák: vyhrává nejnižší součet.")
                vysledek["nejnizsi_vyhrava"] = True

        aktivni = [k for k in karty if not k["odstranena"]]
        soucty = {}
        for karta in aktivni:
            soucty[karta["hrac"]] = soucty.get(karta["hrac"], 0) + karta["hodnota"]
        vysledek["soucty"] = soucty
        if not soucty:
            poznamky.append("Ve sloupci nezůstala žádná karta.")
            return vysledek

        nejnizsi = vysledek["nejnizsi_vyhrava"]
        cil = min(soucty.values()) if nejnizsi else max(soucty.values())
        remiza = [hrac for hrac, soucet in soucty.items() if soucet == cil]
        if len(remiza) > 1:
            # pri remize vyhrava ten, cija karta je nejvys
            # (se Zebrakem ten, cija karta je nejniz)
            poradi = reversed(aktivni) if nejnizsi else aktivni
            vysledek["vitez"] = next(k["hrac"] for k in poradi
                                     if k["hrac"] in remiza)
            poznamky.append("Remíza - rozhodla pozice karet ve sloupci.")
        else:
            vysledek["vitez"] = remiza[0]
        return vysledek

    @staticmethod
    def _princ_panos(aktivni):
        """hrac s Princem i Panosem ve sloupci; pri vice takovych vyhrava
        ten, jehoz karta z dvojice lezi nejvys"""
        nejlepsi = None
        for hrac in {k["hrac"] for k in aktivni}:
            radky = [k["radek"] for k in aktivni
                     if k["hrac"] == hrac and k["nazev"] in ("Princ", "Panoš")]
            nazvy = {k["nazev"] for k in aktivni if k["hrac"] == hrac}
            if "Princ" in nazvy and "Panoš" in nazvy:
                if nejlepsi is None or min(radky) < nejlepsi[0]:
                    nejlepsi = (min(radky), hrac)
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
        plocha = []
        for radek in self.plocha:
            radek_pohled = []
            for pole in radek:
                if pole is None or pole.get("blokovano"):
                    radek_pohled.append(pole)
                    continue
                moje = pole["hrac"] == ja
                videt = pole["odkryta"] or moje
                prevlek = pole["pod_prevlekem"]
                radek_pohled.append({
                    "hrac": pole["hrac"],
                    "odkryta": pole["odkryta"],
                    "karta": pole["karta"] if videt else None,
                    "ma_prevlek": prevlek is not None,
                    "pod_prevlekem": prevlek if (moje or konec_kola) else None,
                })
            plocha.append(radek_pohled)

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
            "plocha": plocha,
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
                 "plocha", "na_tahu", "faze", "volba", "vysledky_kola",
                 "potvrdili", "zaznamy", "poradi"]

    def do_slovniku(self):
        """kompletni stav pro ulozeni na disk"""
        return {klic: getattr(self, klic) for klic in self._UKLADANE}

    @classmethod
    def ze_slovniku(cls, data, rng=None):
        hra = cls.__new__(cls)
        hra.rng = rng or random.Random()
        for klic in cls._UKLADANE:
            setattr(hra, klic, data[klic])
        # JSON nezna celociselne klice slovniku
        for vysledek in hra.vysledky_kola:
            vysledek["soucty"] = {int(k): v
                                  for k, v in vysledek["soucty"].items()}
        return hra
