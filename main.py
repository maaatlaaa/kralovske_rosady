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
            self.balicek = []
            self.body = 0
            self.body_kolo = 0
            self.cilove_karty = []  
            self.princ = 0
            self.panos = 0

            # vytvareni karet
            """
            typ:
            1 - bez specialni schopnosti
            2 - vyssi hodnota podle toho, kde je
            3 - karty s ihned akci
            4 - karty s akci az pri vyhodnocovani
            """
            karta = Karta(1, "Král", "", 20)
            self.balicek.append(karta)
            karta = Karta(1, "Královna", "", 16)
            self.balicek.append(karta)
            karta = Karta(1, "Julie", "", 14)
            self.balicek.append(karta)
            karta = Karta(2, "Alchymista", "", 8)
            self.balicek.append(karta)
            karta = Karta(2, "Šermíř", "", 8)
            self.balicek.append(karta)
            karta = Karta(2, "Statkář", "", 8)
            self.balicek.append(karta)
            karta = Karta(2, "Kupec", "", 8)
            self.balicek.append(karta)
            karta = Karta(2, "Kardinál", "", 8)
            self.balicek.append(karta)
            karta = Karta(2, "Trubadúr", "", 8)
            self.balicek.append(karta)
            karta = Karta(3, "Objevitel", "", 13)
            self.balicek.append(karta)
            karta = Karta(3, "Mordýř", "", 9.5)
            self.balicek.append(karta)
            karta = Karta(3, "Bouře", "", 9)
            self.balicek.append(karta)
            karta = Karta(3, "Převlek", "", 0)
            self.balicek.append(karta)
            karta = Karta(3, "Zrádce", "", 10)
            self.balicek.append(karta)
            karta = Karta(4, "Mušketýři", "", 11)
            self.balicek.append(karta)
            karta = Karta(4, "Mág", "", 7)
            self.balicek.append(karta)
            karta = Karta(4, "Čarodějnice", "", 1)
            self.balicek.append(karta)
            karta = Karta(4, "Princ", "", 14)
            self.balicek.append(karta)
            karta = Karta(4, "Panoš", "", 2)
            self.balicek.append(karta)
            karta = Karta(4, "Poustevník", "", 12)
            self.balicek.append(karta)
            karta = Karta(4, "Paleček", "", 2)
            self.balicek.append(karta)
            karta = Karta(4, "Dvojník", "", None)
            self.balicek.append(karta)
            karta = Karta(4, "Drak", "", 11)
            self.balicek.append(karta)
            karta = Karta(4, "Romeo", "", 5)
            self.balicek.append(karta)
            karta = Karta(4, "Žebrák", "", 4)
            self.balicek.append(karta)
            self.balicek_zalozni = self.balicek
            self.zamichat()

        def get_jmeno(self):
            """
            vraci sve jmeno
            """
            return self.jmeno

        def zamichat(self):
            """
            zamichava svuj balicek
            """
            random.shuffle(self.balicek)

        def karty_v_ruce(self):
            """
            vypise sve karty v ruce, pokud nema dostatecny pocet - 3, napoji na svuj balicek nove karty
            """
            if len(self.balicek) < 3:
                print("dosel balicek")
                self.balicek_zalozni.remove(self.balicek[0])
                self.balicek_zalozni.remove(self.balicek[1])
                self.balicek = self.balicek + self.balicek_zalozni

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
            self.body_kolo = self.body_kolo + plus_body

        def reset_body_kolo(self):
            """resetovani bodu za kolo"""
            self.body_kolo = 0

        def get_body_kolo(self):
            """vraci pocet bodu, ktere hrac ziskal v kole"""
            return self.body_kolo

        def pridej_cilovou_kartu(self, nova_cilova_karta):
            """pridava hraci vyhranou cilovou kartu"""
            self.cilove_karty.append(nova_cilova_karta)