"""
Modul main.py představuje zakladní řídící jednotku pro naši hru.
"""

import random
import threading
from queue import Queue
from hraci_plocha_gui import HraciPlochaGui


class Hrac:
    """
    class Hrac je reprezentujici objekt hrajiciho hrace
    """
    def __init__(self, jmeno):
        self.jmeno = jmeno
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
        karta = {"nazev": nazev, "popis": popis, "hodnota": hodnota}
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

        return " + ".join(karta["nazev"] for karta in self.balicek[:3])

    # vrati nazev a hodnotu karty
    def vyloz(self, poradi_karty):
        """
        :param poradi_karty: cele cislo odpovidajici karte-1,
            ktera byla vypsana jako ty, co ma hrac v ruce
        :return: nazev a hodnota vylozene karty
        """
        nazev = self.balicek[poradi_karty - 1]["nazev"]
        hodnota = self.balicek[poradi_karty - 1]["hodnota"]
        self.balicek.pop(poradi_karty - 1)
        return {"nazev": nazev, "hodnota": hodnota}

    def get_panos_princ(self):
        """pokud ma hrac panose a prince, automaticky vyhral cely sloupec,
            pokud tomu tak neni, tak se hodnoty pro jistotu vynuluji pro dalsi sloupec"""
        if self.panos == 1 and self.panos == 1:
            self.panos = 0
            self.princ = 0
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

class HraciPlocha:
    """ HraciPlocha reprezentuje hraci plochu,
    ktera interaguje s hrou a s hraci dle stavu hry a vykladanych karet"""
    def __init__(self, hraci):
        self.hraci = hraci
        self.pocet_hracu = len(hraci)

        # Vytvoříme balíček cílových karet
        self.cilove_karty = []
        self.vytvor_cilove_karty("Alchymie")
        self.vytvor_cilove_karty("Šerm")
        self.vytvor_cilove_karty("Rolnictví")
        self.vytvor_cilove_karty("Obchod")
        self.vytvor_cilove_karty("Náboženství")
        self.vytvor_cilove_karty("Hudba")
        random.shuffle(self.cilove_karty)

        vychozi_hraci_pole = {
            "sloupec": 0,
            "radek": 0,
            "karta": "volne",
            "stav": 0,
            "hrac": "jmeno",
            "hodnota": 0}
        # definice hlavicku hraci plochy a samotnou hraci plochu
        self.hlavicka_hraci_plochy = None

        self.hraci_plocha = []
        for _ in range(self.pocet_hracu):
            row = [vychozi_hraci_pole for _ in range(self.pocet_hracu)]
            self.hraci_plocha.append(row)

    def vytvor_cilove_karty(self, nazev):
        """ vytvari cilove karty """
        for i in range(5):
            cilova_karta = {"nazev": nazev, "hodnota": i+1}
            self.cilove_karty.append(cilova_karta)
        cilova_karta = {"nazev": nazev, "hodnota": 3}
        self.cilove_karty.append(cilova_karta)

    def start_hraci_plochy(self):
        """start_kola zajistuje, ze je vse pripraveno na nove kolo"""
        self.hlavicka_hraci_plochy = []
        for sloupec in range(self.pocet_hracu):
            self.hlavicka_hraci_plochy.append(self.cilove_karty[sloupec])

        for cilova_karta in self.hlavicka_hraci_plochy:
            self.cilove_karty.remove(cilova_karta)

        for sloupec in range(self.pocet_hracu):
            for radek in range(self.pocet_hracu):
                self.reset_pole(radek, sloupec)

    def reset_pole(self, radek, sloupec):
        """resetovani pole daneho v argumentech"""
        self.hraci_plocha[radek][sloupec] = {
            "sloupec": 0,
            "radek": 0,
            "karta": "volne",
            "stav": 0,
            "hrac": "jmeno",
            "hodnota": 0}

    def plna(self):
        """ funkce kontroluje, zda je hraci plocha plna"""
        return all(all(policko["karta"] != "volne" for policko in radek)
                   for radek in self.hraci_plocha)

    def vylozena_karta(self, sloupec, karta, hrac_jmeno):
        """vylozena_karta ma za funkci zkontrolovat,
        zda lze opravdu vlozit kartu na urcene misto a provest spojene akce"""
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
        aktualni_hraci_pole = self.hraci_plocha[radek][sloupec]
        aktualni_hraci_pole["stav"] = 2
        nazev_cilove_karty = self.hlavicka_hraci_plochy[sloupec]["nazev"]

        # je karta ve sloupci s bonus body?
        if aktualni_hraci_pole["karta"] == "Alchymista" and nazev_cilove_karty == "Alchymie":
            aktualni_hraci_pole["hodnota"] = 12
        elif aktualni_hraci_pole["karta"] == "Šermíř" and nazev_cilove_karty == "Šerm":
            aktualni_hraci_pole["hodnota"] = 12
        elif aktualni_hraci_pole["karta"] == "Statkář" and nazev_cilove_karty == "Rolnictví":
            aktualni_hraci_pole["hodnota"] = 12
        elif aktualni_hraci_pole["karta"] == "Kupec" and nazev_cilove_karty == "Obchod":
            aktualni_hraci_pole["hodnota"] = 12
        elif aktualni_hraci_pole["karta"] == "Kardinál" and nazev_cilove_karty == "Náboženství":
            aktualni_hraci_pole["hodnota"] = 12
        elif aktualni_hraci_pole["karta"] == "Trubadúr" and nazev_cilove_karty == "Hudba":
            aktualni_hraci_pole["hodnota"] = 12

        # karty typu - po otoceni akce
        elif aktualni_hraci_pole["karta"] == "Objevitel":
            # cestuje napravo, pokud je uplne vpravo,
            # do prvniho sloupce vlevo. Tam je jakoby 'nove vlozen'
            self.objevitel_akce(radek, sloupec)

        elif aktualni_hraci_pole["karta"] == "Mordýř":
            print("mordyr zamordoval vlozenou kartu")
            self.reset_pole(radek + 1, sloupec)
        elif aktualni_hraci_pole["karta"] == "Bouře":
            print("boure bouri")
            radek += 2
            while radek < self.pocet_hracu - 1:
                self.hraci_plocha[radek][sloupec]["stav"] = 2
                self.hraci_plocha[radek][sloupec]["karta"] = "zabrane"
                radek += 1

        elif aktualni_hraci_pole["karta"] == "Převlek":
            print("odkryta karta prevlek")
            self.prevlek_akce(radek, sloupec)

        elif aktualni_hraci_pole["karta"] == "Zrádce":
            print("zradce se pripravuje k uderu")
            self.zradce_akce(radek, sloupec)

    def vyskyt_ridicich_karet(self, sloupec):
        """ kontrola vyskytu karet. Hledane karty se lisi typem hledanych karet"""
        vyskyt_karet = {"musketyr": 0, "mag": 0, "carodejnice": 0}
        for radek in range(self.pocet_hracu):
            if self.hraci_plocha[radek][sloupec]["karta"] == "Mušketýři":
                vyskyt_karet["musketyr"] += 1
            elif self.hraci_plocha[radek][sloupec]["karta"] == "Mág":
                vyskyt_karet["mag"] += 1
            elif self.hraci_plocha[radek][sloupec]["karta"] == "Čarodějnice":
                vyskyt_karet["carodejnice"] += 1
            elif (self.hraci_plocha[radek][sloupec]["karta"] == "Převlek" and
                  not isinstance(self.hraci_plocha[radek][sloupec]["radek"], int)):
                # do "karta" se ulozi nazev karty pod prevlekem
                self.hraci_plocha[radek][sloupec]["karta"] = str(
                    self.hraci_plocha[radek][sloupec]["radek"]
                )
                # do "hodnota" se ulozi hodnota karty pod prevlekem
                self.hraci_plocha[radek][sloupec]["hodnota"] = (
                    self.hraci_plocha)[radek][sloupec]["sloupec"]

            print(self.hraci_plocha[radek][sloupec]["karta"] + ": " + str(
                self.hraci_plocha[radek][sloupec]["hodnota"]) + ": " +
                  self.hraci_plocha[radek][sloupec]["hrac"])

            return vyskyt_karet

    def princ_panos(self, sloupec):
        """ logika resici princ a panos situaci"""
        vyskyt = []
        for hrac in self.hraci:
            princ_panos = {"princ": 0, "panos": 0, "radek": 100, "hrac": hrac.jmeno}
            for radek in range(self.pocet_hracu):
                if self.hraci_plocha[radek][sloupec]["karta"] == "Princ" and hrac.jmeno == \
                        self.hraci_plocha[radek][sloupec]["hrac"]:
                    princ_panos["princ"] = 1
                    if radek < princ_panos["radek"]:
                        princ_panos["radek"] = radek
                elif self.hraci_plocha[radek][sloupec]["karta"] == "Panoš" and hrac.jmeno == \
                        self.hraci_plocha[radek][sloupec]["hrac"]:
                    princ_panos["panos"] = 1
                    if radek < princ_panos["radek"]:
                        princ_panos["radek"] = radek
            if princ_panos["princ"] == 1 and princ_panos["panos"] == 1:
                vyskyt.append(princ_panos)

        vitez = 100
        nejmensi_radek = 100
        for vysledek in vyskyt:
            if vysledek["radek"] < nejmensi_radek:
                nejmensi_radek = vysledek["radek"]
                vitez = vysledek["hrac"]
        return vitez

    def vyskyt_karet(self, sloupec):
        """ kontrola vyskytu karet. Hledane karty se lisi typem hledanych karet"""
        vyskyt_karet = {"zebrak": 0}
        vyskyt_draka = []
        for radek in range(self.pocet_hracu):
            if self.hraci_plocha[radek][sloupec]["karta"] == "Drak":
                vyskyt_draka.append(self.hraci_plocha[radek][sloupec]["hrac"])
            elif self.hraci_plocha[radek][sloupec]["karta"] == "Žebrák":
                vyskyt_karet["zebrak"] += 1
            elif self.hraci_plocha[radek][sloupec]["karta"] == "Poustevník":
                self.hraci_plocha[radek][sloupec]["hodnota"] = (
                        self.hraci_plocha[radek][sloupec]["hodnota"] - self.pocet_hracu - radek - 1)
            elif self.hraci_plocha[radek][sloupec]["karta"] == "Paleček":
                self.hraci_plocha[radek][sloupec]["hodnota"]\
                    = (self.hraci_plocha[radek][sloupec]["hodnota"]
                       + (self.pocet_hracu - radek - 1) * 3)
            elif self.hraci_plocha[radek][sloupec]["karta"] == "Dvojník":
                self.dvojnik_akce(radek, sloupec)
            elif self.hraci_plocha[radek][sloupec]["karta"] == "Romeo":
                self.romeo_akce(radek, sloupec)

        # pokud se nasel nejaky drak, tak rovnou aplikuje efekt
        if len(vyskyt_draka) != 0:
            self.drak_akce(sloupec, vyskyt_draka)

        return vyskyt_karet

    def drak_akce(self, sloupec, vyskyt_draka):
        """
        aplikuje akci draka v danem sloupci
        """
        for hrac_jmeno in vyskyt_draka:
            for radek in range(self.pocet_hracu):
                if hrac_jmeno != self.hraci_plocha[radek][sloupec]["hrac"]:
                    self.hraci_plocha[radek][sloupec]["hodnota"] = (
                            self.hraci_plocha[radek][sloupec]["hodnota"] - 2)

    def mag_akce(self, sloupec):
        """
        aplikuje akci maga
        """
        for radek in range(self.pocet_hracu):
            if self.hraci_plocha[radek][sloupec]["hodnota"] >= 10:
                self.reset_pole(radek, sloupec)

    def carodejnice_akce(self, sloupec):
        """
        aplikuje akci carodejnice
        """
        for radek in range(self.pocet_hracu):
            if (self.hraci_plocha[radek][sloupec]["hodnota"] <= 9
                    and self.hraci_plocha[radek][sloupec][
                        "karta"] != "Čarodějnice"):
                self.reset_pole(radek, sloupec)

    def dvojnik_akce(self, radek, sloupec):
        """ akce pro kartu dvojnik """
        for radek_x in range(radek + 1, self.pocet_hracu):
            if self.hraci_plocha[radek_x][sloupec]["karta"] != "Dvojník" and \
                    self.hraci_plocha[radek_x][sloupec]["karta"] != "volne":
                self.hraci_plocha[radek][sloupec]["hodnota"]\
                    = self.hraci_plocha[radek_x][sloupec]["hodnota"]
                break

    def romeo_akce(self, radek, sloupec):
        """ akce pro kartu romeo """
        for radek_x in range(self.pocet_hracu):
            if (self.hraci_plocha[radek_x][sloupec]["karta"] == "Julie"
                    and self.hraci_plocha[radek_x][sloupec]["hrac"] ==
                    self.hraci_plocha[radek][sloupec]["hrac"]):
                self.hraci_plocha[radek][sloupec]["hodnota"] = 15
                break

    def zradce_akce(self, radek, sloupec):
        """ akce zradce """
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

    def prevlek_akce(self, radek, sloupec):
        """ prevlek akce """
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

    def objevitel_akce(self, radek, sloupec):
        """ objevitel akce"""
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
            self.hraci_plocha[volne_misto][prohledavany_sloupec] = (
                self.hraci_plocha)[radek][sloupec]
            self.hraci_plocha[radek][sloupec] = self.hraci_plocha[radek + 1][sloupec]
            self.reset_pole(radek + 1, sloupec)
            if volne_misto != 0:
                self.otoceni_karty(volne_misto - 1, prohledavany_sloupec)

    def scitani_hodnot(self, sloupec):
        """
        scita a prirazuje body jednotlivym hracum
        """
        for radek in range(self.pocet_hracu):
            for hrac in self.hraci:
                if hrac.jmeno == self.hraci_plocha[radek][sloupec]["hrac"]:
                    hrac.set_body_kolo(self.hraci_plocha[radek][sloupec]["hodnota"])

    def kdo_driv(self, sloupec, serazeni_hraci, prepinac):
        """ zjistuje, ktery hrac je driv
        ci pozdeji ve sloupecku """
        if prepinac == 1:
            for radek in range(self.pocet_hracu - 1, -1, -1):
                if self.hraci_plocha[radek][sloupec]["hrac"] == serazeni_hraci[1].jmeno:
                    print(f"vyherce sloupce {sloupec} je {serazeni_hraci[1].jmeno}")
                    return serazeni_hraci[1]
                if self.hraci_plocha[radek][sloupec]["hrac"] == serazeni_hraci[0].jmeno:
                    print(f"vyherce sloupce {sloupec} je {serazeni_hraci[0].jmeno}")
                    return serazeni_hraci[0]
        for radek in range(self.pocet_hracu):
            if self.hraci_plocha[radek][sloupec]["hrac"] == serazeni_hraci[0].jmeno:
                print(f"vyherce sloupce {sloupec} je {serazeni_hraci[0].jmeno}")
                return serazeni_hraci[0]
            if self.hraci_plocha[radek][sloupec]["hrac"] == serazeni_hraci[1].jmeno:
                print(f"vyherce sloupce {sloupec} je {serazeni_hraci[1].jmeno}")
                return serazeni_hraci[1]
        return serazeni_hraci[0]

    def vypis(self):
        """vypis slouzi k prubeznemu nahlidnuti na hraci plochu pomoci terminalu"""
        print("")
        for cilova_karta in self.hlavicka_hraci_plochy:
            nazev = cilova_karta["nazev"]
            hodnota = cilova_karta["hodnota"]
            print(f"{nazev} : {hodnota}", end="\t")
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
                        karta_info = f'[{karta}:{hodnota}:{hrac}:{stav}]'
                        print(karta_info, end="\t")
            print("\n" + "-" * 8 * self.pocet_hracu)

        print("\n\n")
        return self.hraci_plocha


class Hra:
    """tato trida odkazuje na objekt ridici celou hru"""
    def __init__(self, hraci):
        self.hraci = []
        for hrac in hraci:
            self.hraci.append(Hrac(hrac))
        self.pocet_hracu = len(hraci)
        self.hraci_plocha = HraciPlocha(self.hraci)
        self.data_fronta = Queue()
        self.hraci_plocha_gui_thread = threading.Thread(target=HraciPlochaGui, args=(self.pocet_hracu, self.data_fronta))
        self.hraci_plocha_gui_thread.start()

        print("ahoj111")
        self.start_hry()

    def start_hry(self):
        """
        start hry je hlavni ridici smycka pro hru
        """
        for _ in range(6):
            self.kolo()
        self.zaverecne_vyhodnoceni()

    def zaverecne_vyhodnoceni(self):
        """
        konecne vyhodnoceni rozhodujici o vitezi hry
        """
        for hrac_x in self.hraci:
            cilove_karty_nazvy = set()
            skore = 0
            for cilova_karta in hrac_x.cilove_karty:
                skore += cilova_karta["hodnota"]
                cilove_karty_nazvy.add(cilova_karta["nazev"])
            if len(cilove_karty_nazvy) == 6:
                skore_specialni = 0
                skore_specialni_negativni = 0
                print("hrac ma vsechny nazvy karet")
                serazene_karty = sorted(hrac_x.cilove_karty,
                                        key=lambda karta_razeni: karta_razeni.hodnota, reverse=True)
                cilove_karty_nazvy.clear()
                for karta in serazene_karty:
                    if karta["nazev"] in cilove_karty_nazvy:
                        # uz tam je, pocitame ji k negativnimu skore
                        skore_specialni_negativni += 1
                    else:
                        # neni v mnozine, pricitame k specialnimu skore
                        cilove_karty_nazvy.add(karta["nazev"])
                        skore_specialni += karta.hodnota
                skore_specialni = skore_specialni * 2 - skore_specialni_negativni
                if skore_specialni > skore:
                    skore = skore_specialni
            hrac_x.body = skore

        serazeni_hraci = sorted(self.hraci, key=lambda hrac: hrac.body, reverse=True)
        print(f"vyherce je {serazeni_hraci[0].jmeno}")
        for hrac_x in serazeni_hraci:
            print(f"{hrac_x.jmeno} ma {hrac_x.body}")

    def kolo(self):
        """Kolo:
        vypise aktualni hraci pole
        vypise hracovi karty
        kam a kterou kartu chce dat
        vylozi se karta, otoci ta nad nove vylozenou a provede se akce
        pokud je hraci plocha plna, konec"""
        self.hraci_plocha.start_hraci_plochy()

        while not self.hraci_plocha.plna():
            for hrac_x in self.hraci:
                """tady budeme posilat to, co ma byt na hraci plose"""
                self.data_fronta.put({"aktualni_hrac": str(hrac_x.jmeno)})
                self.data_fronta.put({"hlavicka_hraci_plochy": self.hraci_plocha.hlavicka_hraci_plochy})
                self.data_fronta.put({"hraci_plocha": self.hraci_plocha.hraci_plocha})
                self.hraci_plocha.vypis()
                print("hraje " + str(hrac_x.jmeno))
                print(hrac_x.karty_v_ruce())
                volba_sloupce = int(input("Kam chcete kartu vyložit?"))
                volba_karty = int(input("Jakou kartu chcete vyložit?"))
                vylozena_karta = hrac_x.vyloz(volba_karty)
                self.hraci_plocha.vylozena_karta(volba_sloupce, vylozena_karta, hrac_x.jmeno)
                if self.hraci_plocha.plna():
                    break

        self.male_vyhodnoceni()

    def male_vyhodnoceni(self):
        """male vyhodnoceni se spousti po kazdem kole,
            kde se rozhodne, kteri hraci dostali ktere sloupce"""
        # odkyti zbyvajich karet v poslednich radcich
        for sloupec in range(self.pocet_hracu):
            self.hraci_plocha.hraci_plocha[self.pocet_hracu - 1][sloupec]["stav"] = 2

        self.hraci_plocha.vypis()
        for sloupec in range(self.pocet_hracu):
            # vyhodnocovani sloupce 0, ...
            print("sloupec" + str(sloupec))

            vyskyt_ridicich_karet = self.hraci_plocha.vyskyt_ridicich_karet(sloupec)

            self.hraci_plocha.vypis()
            # pokud musketyr neni ve hre
            if vyskyt_ridicich_karet["musketyr"] == 0:
                # odstraneni karet v dusledku akci Maga nebo Carodejnice

                if vyskyt_ridicich_karet["mag"] == 1:
                    self.hraci_plocha.mag_akce(sloupec)
                elif vyskyt_ridicich_karet["carodejnice"] == 1:
                    self.hraci_plocha.carodejnice_akce(sloupec)

                # vyskyt prince a panose
                vyherce = self.hraci_plocha.princ_panos(sloupec)
                if vyherce != 100:
                    for hrac in self.hraci:
                        if hrac.jmeno == vyherce:
                            hrac.cilove_karty.append(
                                self.hraci_plocha.hlavicka_hraci_plochy[sloupec])
                            break
                    break

                # vyskyt draka a zebraka a akce zbytku karet
                vyskyt_karet = self.hraci_plocha.vyskyt_karet(sloupec)

                # scitani hodnot
                self.hraci_plocha.scitani_hodnot(sloupec)
                vitez = self.urceni_viteze(sloupec, vyskyt_karet["zebrak"])

            else:
                self.hraci_plocha.scitani_hodnot(sloupec)
                vitez = self.urceni_viteze(sloupec, 0)

            print(f"vyherce sloupce {sloupec} je {vitez.jmeno}")
            self.hraci_plocha.vypis()
            vitez.pridej_cilovou_kartu(self.hraci_plocha.hlavicka_hraci_plochy[sloupec])

            for hrac in self.hraci:
                hrac.body = 0
            print("")

    def urceni_viteze(self, sloupec, zebrak):
        """
        urci poradi hracu dle sezbiranych bodu
        """
        if zebrak != 0:
            serazeni_hraci = sorted(self.hraci, key=lambda hrac_x: hrac_x.body, reverse=False)
            if serazeni_hraci[0].body == serazeni_hraci[1].body:
                return self.hraci_plocha.kdo_driv(sloupec, serazeni_hraci, 1)

            return serazeni_hraci[0]

        serazeni_hraci = sorted(self.hraci, key=lambda hrac_x: hrac_x.body, reverse=True)
        if serazeni_hraci[0].body == serazeni_hraci[1].body:
            return self.hraci_plocha.kdo_driv(sloupec, serazeni_hraci, 0)
        return serazeni_hraci[0]


hra = Hra(["Matous", "Sarinka", "Natka"])
