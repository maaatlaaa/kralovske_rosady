"""
Modul main.py představuje zakladní řídící jednotku pro naši hru.
"""

import random


class Karta:
    """ class Karta: obejkt predstavujici hraci kartu,
    které postupně hráči vykládají na hrací plochu """
    def __init__(self, nazev, popis, hodnota):
        self.hodnota = hodnota
        self.nazev = nazev
        self.popis = popis

    def get_nazev(self):
        """ Vraci nazev sama sebe """
        return self.nazev

    def get_hodnota(self):
        """ Vraci svou hodnotu """
        return self.hodnota


class CilovaKarta:
    """ O cilove karty se soutezi"""
    def __init__(self,nazev, hodnota):
        # id = 1-6 pro jednotlivé názvy
        self.nazev = nazev
        self.hodnota = hodnota

    def get_jmeno(self):
        """ Vraci sve jmeno """
        return self.nazev
    def get_hodnotu(self):
        """ Vraci svou hodnotu """
        return self.hodnota

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

        def get_jmeno(self):
            """
            vraci sve jmeno
            """
            return self.jmeno

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
            nazev = self.balicek[poradi_karty - 1].get_nazev()
            hodnota = self.balicek[poradi_karty - 1].get_hodnota()
            self.balicek.pop(poradi_karty - 1)
            return {"nazev": nazev, "hodnota": hodnota}

        def set_princ(self, princ):
            """nastavuje hodnotu pro princ pro dalsi kontrolu"""
            self.princ = princ

        def set_panos(self, panos):
            """nastavuje hodnotu pro panos pro dalsi kontrolu"""
            self.panos = panos

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
            self.body = self.body + plus_body

        def reset_body_kolo(self):
            """resetovani bodu za kolo"""
            self.body= 0

        def get_body_kolo(self):
            """vraci pocet bodu, ktere hrac ziskal v kole"""
            return self.body

        def pridej_cilovou_kartu(self, nova_cilova_karta):
            """pridava hraci vyhranou cilovou kartu"""
            self.cilove_karty.append(nova_cilova_karta)
