"""
Modul main.py představuje zakladní řídící jednotku pro naši hru.
"""

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

