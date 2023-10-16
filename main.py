"""
Modul main.py představuje zakladní řídící jednotku pro naši hru.
"""

import random


class Karta:
    """ class Karta: objekt predstavujici hraci kartu,
    které postupně hráči vykládají na hrací plochu """
    def __init__(self, nazev, popis, hodnota):
        self.hodnota = hodnota
        self.nazev = nazev
        self.popis = popis


class CilovaKarta:
    """ O cilove karty se soutezi"""
    def __init__(self,nazev, hodnota):
        self.nazev = nazev
        self.hodnota = hodnota

class Hrac:
    """
    class Hrac je reprezentujici objekt hrajiciho hrace
    """
    def __init__(self, jmeno, vek):
        self.jmeno = jmeno
        self.vek = vek
        self.balicek = self.vytvoreni_balicku()
        self.body = 0
        self.cilove_karty = []
        self.princ = 0
        self.panos = 0

    def vytvoreni_balicku(self):
        """
        vytvari balicek a rovnou ho zamicha
        :return: zamichany balicek
        """
        balicek = []
        # vytvareni karet 1 - bez specialni schopnosti 2 - vyssi hodnota podle toho, kde je
        # 3 - karty s ihned akci 4 - karty s akci az pri vyhodnocovani
        self.pridej_kartu(balicek, "Král", "", 20)
        self.pridej_kartu(balicek, "Královna", "", 16)
        self.pridej_kartu(balicek, "Julie", "", 14)
        self.pridej_kartu(balicek, "Alchymista", "", 8)
        self.pridej_kartu(balicek, "Šermíř", "", 8)
        self.pridej_kartu(balicek, "Statkář", "", 8)
        self.pridej_kartu(balicek, "Kupec", "", 8)
        self.pridej_kartu(balicek, "Kardinál", "", 8)
        self.pridej_kartu(balicek, "Trubadúr", "", 8)
        self.pridej_kartu(balicek, "Objevitel", "", 13)
        self.pridej_kartu(balicek, "Mordýř", "", 9.5)
        self.pridej_kartu(balicek, "Bouře", "", 9)
        self.pridej_kartu(balicek, "Převlek", "", 0)
        self.pridej_kartu(balicek, "Zrádce", "", 10)
        self.pridej_kartu(balicek, "Mušketýři", "", 11)
        self.pridej_kartu(balicek, "Mág", "", 7)
        self.pridej_kartu(balicek, "Čarodějnice", "", 1)
        self.pridej_kartu(balicek, "Princ", "", 14)
        self.pridej_kartu(balicek, "Panoš", "", 2)
        self.pridej_kartu(balicek, "Poustevník", "", 12)
        self.pridej_kartu(balicek, "Paleček", "", 2)
        self.pridej_kartu(balicek, "Dvojník", "", None)
        self.pridej_kartu(balicek, "Drak", "", 11)
        self.pridej_kartu(balicek,  "Romeo", "", 5)
        self.pridej_kartu(balicek, "Žebrák", "", 4)
        random.shuffle(balicek)

        return balicek

    @staticmethod
    def pridej_kartu(balicek, nazev, popis, hodnota):
        """pridava kartu do daneho balicku"""
        karta = Karta(nazev, popis, hodnota)
        balicek.append(karta)

    def karty_v_ruce(self):
        """
        vypise sve karty v ruce,
        pokud nema dostatecny pocet tj. 3, napoji na svuj balicek nove karty
        """
        if len(self.balicek) < 3:
            print("dosel balicek")
            balicek_zalozni = self.vytvoreni_balicku()
            balicek_zalozni.remove(self.balicek[0])
            balicek_zalozni.remove(self.balicek[1])

            self.balicek = self.balicek + balicek_zalozni

        return f"{self.balicek[0].nazev} + {self.balicek[1].nazev} + {self.balicek[2].nazev}"

    # vrati nazev a hodnotu karty
    def vyloz(self, poradi_karty):
        """
        :param poradi_karty: cele cislo odpovidajici karte-1,
            ktera byla vypsana jako ty, co ma hrac v ruce
        :return: nazev a hodnota vylozene karty
        """
        nazev = self.balicek[poradi_karty - 1].nazev
        hodnota = self.balicek[poradi_karty - 1].hodnota
        self.balicek.pop(poradi_karty - 1)
        return {"nazev": nazev, "hodnota": hodnota}

    def get_panos_princ(self):
        """pokud ma hrac panose a prince, automaticky vyhral cely sloupec,
            pokud tomu tak neni, tak se hodnoty pro jistotu vynuluji pro dalsi sloupec"""
        if self.panos == 1 and self.panos == 1:
            return True
        self.panos = 0
        self.princ = 0
        return False

    def set_body_kolo(self, plus_body):
        """hracovi body za kolo"""
        if isinstance(plus_body, int):
            self.body = self.body + plus_body

    def pridej_cilovou_kartu(self, nova_cilova_karta):
        """pridava hraci vyhranou cilovou kartu"""
        self.cilove_karty.append(nova_cilova_karta)


class Hra:
    """tato trida odkazuje na objekt ridici celou hru"""
    def __init__(self, hraci):
        self.hraci = hraci
        pocet_hracu = len(hraci)
        if pocet_hracu not in range(2, 7):
            raise ValueError("Neplatný počet hráčů. Povolený rozsah je 2 až 6 hráčů.")
        self.pocet_hracu = pocet_hracu

        # Vytvoříme balíček cílových karet
        self.cilove_karty = []
        for i in range(5):
            cilova_karta = CilovaKarta("Alchymie", i + 1)
            self.cilove_karty.append(cilova_karta)
        cilova_karta = CilovaKarta("Alchymie", 3)
        self.cilove_karty.append(cilova_karta)
        for i in range(5):
            cilova_karta = CilovaKarta("Šerm", i + 1)
            self.cilove_karty.append(cilova_karta)
        cilova_karta = CilovaKarta("Šerm", 3)
        self.cilove_karty.append(cilova_karta)
        for i in range(5):
            cilova_karta = CilovaKarta("Rolnictví", i + 1)
            self.cilove_karty.append(cilova_karta)
        cilova_karta = CilovaKarta("Rolnictví", 3)
        self.cilove_karty.append(cilova_karta)
        for i in range(5):
            cilova_karta = CilovaKarta("Obchod", i + 1)
            self.cilove_karty.append(cilova_karta)
        cilova_karta = CilovaKarta("Obchod", 3)
        self.cilove_karty.append(cilova_karta)
        for i in range(5):
            cilova_karta = CilovaKarta("Náboženství", i + 1)
            self.cilove_karty.append(cilova_karta)
        cilova_karta = CilovaKarta("Náboženství", 3)
        self.cilove_karty.append(cilova_karta)
        for i in range(5):
            cilova_karta = CilovaKarta("Hudba", i + 1)
            self.cilove_karty.append(cilova_karta)
        cilova_karta = CilovaKarta("Hudba", 3)
        self.cilove_karty.append(cilova_karta)

        random.shuffle(self.cilove_karty)

        vychozi_hraci_pole = {
            "sloupec": 0,
            "radek": 0,
            "karta": "volne",
            "stav": 0,
            "hrac": "jmeno",
            "hodnota": 0}
        # definice hlavicku hraci plochy a samotnou hraci plochu
        self.hlavicka_hraci_plochy = []

        self.hraci_plocha = []
        for _ in range(self.pocet_hracu):
            row = [vychozi_hraci_pole for _ in range(self.pocet_hracu)]
            self.hraci_plocha.append(row)

    def start_hry(self):
        """
        start hry je hlavni ridici smycka pro hru
        """
        for _ in range(6):
            hra.kolo()
        self.zaverecne_vyhodnoceni()

    def zaverecne_vyhodnoceni(self):
        """
        konecne vyhodnoceni rozhodujici o vitezi hry
        """
        for hrac_x in self.hraci:
            cilove_karty_nazvy = set()
            skore = 0
            for cilova_karta in hrac_x.cilove_karty:
                skore += cilova_karta.hodnota
                cilove_karty_nazvy.add(cilova_karta.nazev)
            if len(cilove_karty_nazvy) == 6:
                skore_specialni = 0
                skore_specialni_negativni = 0
                print("hrac ma vsechny nazvy karet")
                serazene_karty = sorted(hrac_x.cilove_karty, key=lambda karta_razeni: karta_razeni.hodnota, reverse=True)
                cilove_karty_nazvy.clear()
                for karta in serazene_karty:
                    if karta.nazev in cilove_karty_nazvy:
                        # uz tam je, pocitame ji k negativnimu skore
                        skore_specialni_negativni += 1
                    else:
                        # neni v mnozine, pricitame k specialnimu skore
                        cilove_karty_nazvy.add(karta.nazev)
                        skore_specialni += karta.hodnota
                skore_specialni = skore_specialni * 2 - skore_specialni_negativni
                if skore_specialni > skore:
                    skore = skore_specialni
            hrac_x.body = skore

        serazeni_hraci = sorted(self.hraci, key=lambda hrac: hrac.body, reverse=True)
        print(f"vyherce je {serazeni_hraci[0].jmeno}")
        for hrac_x in serazeni_hraci:
            print(f"{hrac_x.jmeno} ma {hrac_x.body}")

    def start_kola(self):
        """start_kola zajistuje, ze je vse pripraveno na nove kolo"""
        self.hlavicka_hraci_plochy = []
        for k in range(self.pocet_hracu):
            self.hlavicka_hraci_plochy.append(self.cilove_karty[k])

        for cilova_karta in self.hlavicka_hraci_plochy:
            self.cilove_karty.remove(cilova_karta)

        for sloupec in range(self.pocet_hracu):
            for radek in range(self.pocet_hracu):
                self.hraci_plocha[sloupec][radek] = {
            "sloupec": 0,
            "radek": 0,
            "karta": "volne",
            "stav": 0,
            "hrac": "jmeno",
            "hodnota": 0}

    def kolo(self):
        """Kolo:
        vypise aktualni hraci pole
        vypise hracovi karty
        kam a kterou kartu chce dat
        vylozi se karta, otoci ta nad nove vylozenou a provede se akce
        pokud je hraci plocha plna, konec"""
        self.start_kola()

        while not self.plna_hraci_plocha():
            for hrac_x in self.hraci:
                self.vypis()
                print("hraje " + hrac_x.jmeno)
                print(hrac_x.karty_v_ruce())
                volba_sloupce = int(input("Kam chcete kartu vyložit?"))
                volba_karty = int(input("Jakou kartu chcete vyložit?"))
                vylozena_karta = hrac_x.vyloz(volba_karty)
                self.vylozena_karta(volba_sloupce, vylozena_karta, hrac_x.jmeno)
                if self.plna_hraci_plocha():
                    break

        self.male_vyhodnoceni()

    def plna_hraci_plocha(self):
        """ funkce kontroluje, zda je hraci plocha plna"""
        return all(all(policko["karta"] != "volne" for policko in radek) for radek in self.hraci_plocha)

    def male_vyhodnoceni(self):
        """male vyhodnoceni se spousti po kazdem kole,
            kde se rozhodne, kteri hraci dostali ktere sloupce"""
        for sloupec in range(self.pocet_hracu):
            self.hraci_plocha[self.pocet_hracu - 1][sloupec]["stav"] = 2

        self.vypis()
        for sloupec in range(self.pocet_hracu):
            # vyhodnocovani sloupce 0, ...
            print("sloupec" + str(sloupec))
            vyskyt_musketyru = 0
            vyskyt_magu = 0
            vyskyt_carodejnice = 0

            for radek in range(self.pocet_hracu):

                if self.hraci_plocha[radek][sloupec]["karta"] == "Mušketýři":
                    vyskyt_musketyru += 1
                elif self.hraci_plocha[radek][sloupec]["karta"] == "Mág":
                    vyskyt_magu += 1
                elif self.hraci_plocha[radek][sloupec]["karta"] == "Čarodějnice":
                    vyskyt_carodejnice += 1
                elif (self.hraci_plocha[radek][sloupec]["karta"] == "Převlek" and
                      not isinstance(self.hraci_plocha[radek][sloupec]["radek"], int)):

                    self.hraci_plocha[radek][sloupec]["karta"] = str(
                        self.hraci_plocha[radek][sloupec]["radek"]
                    )
                    self.hraci_plocha[radek][sloupec]["hodnota"] = self.hraci_plocha[radek][sloupec]["sloupec"]

                print(self.hraci_plocha[radek][sloupec]["karta"] + ": " + str(
                    self.hraci_plocha[radek][sloupec]["hodnota"]) + ": " + self.hraci_plocha[radek][sloupec]["hrac"])

            self.vypis()
            if vyskyt_musketyru == 0:
                if vyskyt_magu == 1:
                    for radek in range(self.pocet_hracu):
                        if self.hraci_plocha[radek][sloupec]["hodnota"] >= 10:
                            self.hraci_plocha[radek][sloupec]= {
            "sloupec": 0,
            "radek": 0,
            "karta": "volne",
            "stav": 0,
            "hrac": "jmeno",
            "hodnota": 0}
                elif vyskyt_carodejnice == 1:
                    for radek in range(self.pocet_hracu):
                        if self.hraci_plocha[radek][sloupec]["hodnota"] <= 9 and self.hraci_plocha[radek][sloupec][
                            "karta"] != "Čarodějnice":
                            self.hraci_plocha[radek][sloupec] = {
            "sloupec": 0,
            "radek": 0,
            "karta": "volne",
            "stav": 0,
            "hrac": "jmeno",
            "hodnota": 0}
                for radek in range(self.pocet_hracu):
                    if self.hraci_plocha[radek][sloupec]["karta"] == "Princ":
                        for hrac in self.hraci:
                            if hrac.jmeno == self.hraci_plocha[radek][sloupec]["hrac"]:
                                hrac.princ = 1
                    elif self.hraci_plocha[radek][sloupec]["karta"] == "Panoš":
                        for hrac in self.hraci:
                            if hrac.jmeno == self.hraci_plocha[radek][sloupec]["hrac"]:
                                hrac.panos = 1

                for hrac in self.hraci:
                    if hrac.get_panos_princ():
                        hrac.cilove_karty.append(self.hlavicka_hraci_plochy[sloupec])
                        break

                vyskyt_julie = 0
                vyskyt_draka = []
                vyskyt_zebraka = 0
                for radek in range(self.pocet_hracu):
                    if self.hraci_plocha[radek][sloupec]["karta"] == "Julie":
                        vyskyt_julie = 1
                    elif self.hraci_plocha[radek][sloupec]["karta"] == "Drak":
                        vyskyt_draka.append(self.hraci_plocha[radek][sloupec]["hrac"])
                    elif self.hraci_plocha[radek][sloupec]["karta"] == "Žebrák":
                        vyskyt_zebraka = 1

                for radek in range(self.pocet_hracu):
                    if self.hraci_plocha[radek][sloupec]["karta"] == "Poustevník":
                        self.hraci_plocha[radek][sloupec]["hodnota"] = self.hraci_plocha[radek][sloupec]["hodnota"] - (
                                    self.pocet_hracu - radek - 1)
                    elif self.hraci_plocha[radek][sloupec]["karta"] == "Paleček":
                        self.hraci_plocha[radek][sloupec]["hodnota"] = self.hraci_plocha[radek][sloupec]["hodnota"] + (
                                    self.pocet_hracu - radek - 1) * 3
                    elif self.hraci_plocha[radek][sloupec]["karta"] == "Dvojník":
                        for r in range(radek + 1, self.pocet_hracu):
                            if (self.hraci_plocha[r][sloupec]["karta"] != "Dvojník"
                                    and self.hraci_plocha[r][sloupec]["karta"] != "volne"):
                                self.hraci_plocha[radek][sloupec]["hodnota"] = self.hraci_plocha[r][sloupec]["hodnota"]
                                break

                    elif self.hraci_plocha[radek][sloupec]["karta"] == "Romeo":
                        if vyskyt_julie == 1:
                            self.hraci_plocha[radek][sloupec]["hodnota"] = 15

                if len(vyskyt_draka) != 0:
                    for hrac_jmeno in vyskyt_draka:
                        for radek in range(self.pocet_hracu):
                            if hrac_jmeno != self.hraci_plocha[radek][sloupec]["hrac"]:
                                self.hraci_plocha[radek][sloupec]["hodnota"] = self.hraci_plocha[radek][sloupec]["hodnota"] - 2

                # scitani hodnot
                for radek in range(self.pocet_hracu):
                    for hrac in self.hraci:
                        if hrac.jmeno == self.hraci_plocha[radek][sloupec]["hrac"]:
                            hrac.set_body_kolo(self.hraci_plocha[radek][sloupec]["hodnota"])

                if vyskyt_zebraka != 1:
                    serazeni_hraci = sorted(self.hraci, key=lambda hrac_x: hrac_x.body, reverse=True)
                    if serazeni_hraci[0].body == serazeni_hraci[1].body:
                        for radek in range(self.pocet_hracu):
                            if self.hraci_plocha[radek][sloupec]["hrac"] == serazeni_hraci[0].jmeno:
                                print(f"vyherce sloupce {sloupec} je {serazeni_hraci[0].jmeno}")
                                break
                            if self.hraci_plocha[radek][sloupec]["hrac"] == serazeni_hraci[1].jmeno:
                                print(f"vyherce sloupce {sloupec} je {serazeni_hraci[1].jmeno}")
                                break
                else:
                    serazeni_hraci = sorted(self.hraci, key=lambda hrac_x: hrac_x.body, reverse=False)
                    if serazeni_hraci[0].body == serazeni_hraci[1].body:
                        for radek in range(self.pocet_hracu - 1, -1, -1):
                            if self.hraci_plocha[radek][sloupec]["hrac"] == serazeni_hraci[1].jmeno:
                                print(f"vyherce sloupce {sloupec} je {serazeni_hraci[1].jmeno}")
                                break
                            if self.hraci_plocha[radek][sloupec]["hrac"] == serazeni_hraci[0].jmeno:
                                print(f"vyherce sloupce {sloupec} je {serazeni_hraci[0].jmeno}")
                                break

            else:
                serazeni_hraci = sorted(self.hraci, key=lambda hrac_x: hrac_x.body, reverse=True)
                if serazeni_hraci[0].body == serazeni_hraci[1].body:
                    for radek in range(self.pocet_hracu):
                        if self.hraci_plocha[radek][sloupec]["hrac"] == serazeni_hraci[0].jmeno:
                            print(f"vyherce sloupce {sloupec} je {serazeni_hraci[0].jmeno}")
                            break
                        if self.hraci_plocha[radek][sloupec]["hrac"] == serazeni_hraci[1].jmeno:
                            print(f"vyherce sloupce {sloupec} je {serazeni_hraci[1].jmeno}")
                            break
            print(f"vyherce sloupce {sloupec} je {serazeni_hraci[0].jmeno}")
            self.vypis()
            serazeni_hraci[0].pridej_cilovou_kartu(self.hlavicka_hraci_plochy[sloupec])

            for hrac in self.hraci:
                hrac.body = 0
            print("")

    def vylozena_karta(self, sloupec, karta, hrac_jmeno):
        """vylozena_karta ma za funkci zkontrolovat, zda lze opravdu vlozit kartu na urcene misto a provest spojene akce"""
        sloupec = sloupec - 1
        status = 1  # status 1 nejde vlozit do sloupce, status 2 uspesne vlozen
        for radek in range(self.pocet_hracu):
            if self.hraci_plocha[radek][sloupec]["karta"] == "volne" and status == 1:
                self.hraci_plocha[radek][sloupec]["sloupec"] = sloupec
                self.hraci_plocha[radek][sloupec]["radek"] = radek
                self.hraci_plocha[radek][sloupec]["karta"] = karta["nazev"]
                self.hraci_plocha[radek][sloupec]["stav"] = 1
                self.hraci_plocha[radek][sloupec]["hrac"] = hrac_jmeno
                self.hraci_plocha[radek][sloupec]["hodnota"] = karta["hodnota"]
                status = 2
                # obraceni karty nad pridanou kartou
                if radek != 0 and self.hraci_plocha[radek - 1][sloupec]["stav"] == 1:
                    # predava souradnice radku a sloupce otocene karty
                    self.otoceni_karty(radek - 1, sloupec)
                    break
                if status == 2:
                    return 0
        return 1

    def otoceni_karty(self, radek, sloupec):
        """otoceni karty obdrzi souradnice karty
        a na zaklade jejiho jmena a schopnosti provede akci"""
        # dojde k otoceni
        self.hraci_plocha[radek][sloupec]["stav"] = 2
        # je karta ve sloupci s bonus body?
        if (self.hraci_plocha[radek][sloupec]["karta"] == "Alchymista"
                and self.hlavicka_hraci_plochy[sloupec].nazev == "Alchymie"):
            self.hraci_plocha[radek][sloupec]["hodnota"] = 12
        elif (self.hraci_plocha[radek][sloupec]["karta"] == "Šermíř"
              and self.hlavicka_hraci_plochy[sloupec].nazev == "Šerm"):
            self.hraci_plocha[radek][sloupec]["hodnota"] = 12
        elif (self.hraci_plocha[radek][sloupec]["karta"] == "Statkář"
              and self.hlavicka_hraci_plochy[sloupec].nazev == "Rolnictví"):
            self.hraci_plocha[radek][sloupec]["hodnota"] = 12
        elif (self.hraci_plocha[radek][sloupec]["karta"] == "Kupec"
              and self.hlavicka_hraci_plochy[sloupec].nazev == "Obchod"):
            self.hraci_plocha[radek][sloupec]["hodnota"] = 12
        elif (self.hraci_plocha[radek][sloupec]["karta"] == "Kardinál"
              and self.hlavicka_hraci_plochy[sloupec].nazev == "Náboženství"):
            self.hraci_plocha[radek][sloupec]["hodnota"] = 12
        elif (self.hraci_plocha[radek][sloupec]["karta"] == "Trubadúr"
              and self.hlavicka_hraci_plochy[sloupec].nazev == "Hudba"):
            self.hraci_plocha[radek][sloupec]["hodnota"] = 12

        # karty typu - po otoceni akce
        elif self.hraci_plocha[radek][sloupec]["karta"] == "Objevitel":
            # cestuje napravo, pokud je uplne vpravo,
            # do prvniho sloupce vlevo. Tam je jakoby 'nove vlozen'
            je_misto_jinde = False
            prohledavany_sloupec = sloupec
            volne_misto = int
            for _ in range(self.pocet_hracu - 1):
                prohledavany_sloupec += 1
                if prohledavany_sloupec == self.pocet_hracu:
                    prohledavany_sloupec = 0

                for volne_misto in range(self.pocet_hracu):
                    if self.hraci_plocha[volne_misto][prohledavany_sloupec]["karta"] == "volne":
                        je_misto_jinde = True
                        break
                if je_misto_jinde:
                    break

            if not je_misto_jinde:
                # karta nelze presunout
                print("nelze presunout Objevitele, zustava na miste")
            else:
                # karta lze presunout
                # na miste objevitele posunout novou kartu,
                # na miste nove karty dat volno,
                # kartu objevitele presunout, pokud tam bude jina karta, tak obratit
                print("objevitel se presunul")
                self.hraci_plocha[volne_misto][prohledavany_sloupec] =(
                    self.hraci_plocha)[radek][sloupec]
                self.hraci_plocha[radek][sloupec] = self.hraci_plocha[radek + 1][sloupec]
                self.hraci_plocha[radek + 1][sloupec] = {
            "sloupec": 0,
            "radek": 0,
            "karta": "volne",
            "stav": 0,
            "hrac": "jmeno",
            "hodnota": 0}
                if volne_misto != 0:
                    self.otoceni_karty(volne_misto - 1, prohledavany_sloupec)


        elif self.hraci_plocha[radek][sloupec]["karta"] == "Mordýř":
            # Karta, která odkryje Mordýře, je ihned odložena na
            # odkládací balíček svého majitele.
            # Nové kartě, položené pod již odkrytého Mordýře se nestane nic.
            print("mordyr zamordoval vlozenou kartu")
            self.hraci_plocha[radek + 1][sloupec] = {
            "sloupec": 0,
            "radek": 0,
            "karta": "volne",
            "stav": 0,
            "hrac": "jmeno",
            "hodnota": 0}

        elif self.hraci_plocha[radek][sloupec]["karta"] == "Bouře":
            # Je-li odkryta Bouře, tak již nemůže být do tohoto sloupce
            # položena žádná další karta. Cílová karta tohoto sloupce
            # je pokládána za naplněnou, i kdyby zde leželo méně karet
            # vlivu než je potřebné. Kdyby přicestoval do sloupce
            # s Bouří Objevitel, tak putuje do nejbližšího dalšího sloupce.
            print("boure bouri")
            radek += 2
            while radek < self.pocet_hracu - 1:
                self.hraci_plocha[radek][sloupec]["stav"] = 2
                self.hraci_plocha[radek][sloupec]["karta"] = "zabrane"
                radek += 1

        elif self.hraci_plocha[radek][sloupec]["karta"] == "Převlek":
            # Je-li odkryt Převlek, může jeho majitel vsunout zakrytě
            # kartu ze své ruky pod Převlek a ihned si kartu z balíčku dobrat.
            # Karta pod Převlekem je odkryta teprve na konci kola.
            # Má-li odkrytá karta Zvláštní schopnost,
            # která má vliv na braní dobytých cílových karet, tak je tato schopnost platná
            print("odkryta karta boure")
            for hrac in self.hraci:
                if hrac.jmeno == self.hraci_plocha[radek][sloupec]["hrac"]:
                    self.vypis()
                    print(hrac.karty_v_ruce())
                    if input("chces pod prevlek dat nejakou svou kartu? [y/n]") == "y":
                        volba_karty = int(input("Jakou kartu chcete vyložit?"))
                        vylozena_karta = hrac.vyloz(volba_karty)
                        self.hraci_plocha[radek][sloupec]["radek"] = vylozena_karta["nazev"]
                        self.hraci_plocha[radek][sloupec]["sloupec"] = vylozena_karta["hodnota"]
                    break

        elif self.hraci_plocha[radek][sloupec]["karta"] == "Zrádce":
            print("zradce se pripravuje k uderu")
            for hrac in self.hraci:
                if hrac.jmeno == self.hraci_plocha[radek][sloupec]["hrac"]:
                    self.vypis()
                    if input("chces prohodit nejake dve Cilove karty? [y/n]") == "y":
                        for i in self.hlavicka_hraci_plochy:
                            print(i, end=" ")
                        volba_karty1 = int(input("Jakou kartu chcete prohodit?"))
                        volba_karty2 = int(input("Se kterou ji chcete prohodit?"))
                        cilova_karta1 = self.hlavicka_hraci_plochy[volba_karty1 - 1]
                        self.hlavicka_hraci_plochy[volba_karty1 - 1] = (
                            self.hlavicka_hraci_plochy)[volba_karty2 - 1]
                        self.hlavicka_hraci_plochy[volba_karty2 - 1] = cilova_karta1
                    break

    def vypis(self):
        """vypis slouzi k prubeznemu nahlidnuti na hraci plochu pomoci terminalu"""
        print("")
        for i in self.hlavicka_hraci_plochy:
            print(f"{i.nazev} : {i.hodnota}", end="\t")
        print("\n" + "-" * 8 * self.pocet_hracu)

        for radek in range(self.pocet_hracu):
            for sloupec in range(self.pocet_hracu):
                karta = self.hraci_plocha[radek][sloupec]["karta"]
                hodnota = self.hraci_plocha[radek][sloupec]["hodnota"]
                hrac = self.hraci_plocha[radek][sloupec]["hrac"]
                stav = self.hraci_plocha[radek][sloupec]["stav"]

                if karta == "volne":
                    if stav == 1:
                        print("zabrane", end="\t")
                    else:
                        print(karta, end="\t")
                else:
                    if stav == 1:
                        print("zabrane", end="\t")
                    else:
                        karta_info = f'{karta}: {hodnota}: {hrac}'
                        print(karta_info, end="\t")
            print("\n" + "-" * 8 * self.pocet_hracu)

        print("\n\n")


hrac1 = Hrac("Matous", 21)
hrac2 = Hrac("Sarinka", 20)
hrac3 = Hrac("Natka", 11)
hrajici_hraci = [hrac1, hrac2, hrac3]

hra = Hra(hrajici_hraci)
hra.start_hry()
