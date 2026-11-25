"""
Testy pravidel, ktera originalni pravidla nerikaji jednoznacne
(README, oddil "Co originalni pravidla nerikaji jednoznacne").
Testy fixuji rozhodnuti, jak je dnes implementuje rosady/engine.py.
"""

import pytest

from rosady.engine import TAH
from rosady.karty import KATEGORIE

from .test_engine import (dej_do_ruky, karta, nastav_cile, nastav_sloupec,
                          nova_hra, vyhodnot)


# ------------- Mag a Carodejnice posuzuji hodnoty se zapocitanymi bonusy

def test_mag_posuzuje_palecka_s_bonusem():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Paleček", 0), ("Mág", 1),
                            ("Kupec", 2), ("Kupec", 2)])
    # Palecek 2 + 3 * 3 = 11 -> Mag ho odstrani (zakladni 2 by zustala)
    assert vyhodnot(hra, 0)["soucty"] == {1: 7, 2: 16}


def test_mag_posuzuje_romea_s_julii():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Romeo", 0), ("Julie", 0), ("Mág", 1),
                            ("Kupec", 2)])
    # Romeo s Julii ma 15 -> Mag ho odstrani i s Julii (zakladni 5 by zustala)
    assert vyhodnot(hra, 0)["soucty"] == {1: 7, 2: 8}


def test_mag_posuzuje_dvojnika_s_prevzatou_hodnotou():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Dvojník", 0), ("Královna", 1), ("Mág", 2)])
    # Dvojnik prevzal 16 -> Mag ho odstrani spolu s Kralovnou
    assert vyhodnot(hra, 0)["soucty"] == {2: 7}


def test_carodejnice_posuzuje_specialistu_s_bonusem():
    hra = nova_hra(2)
    nastav_sloupec(hra, 0, [("Kupec", 0), ("Čarodějnice", 1)],
                   kategorie="Obchod")
    # Kupec ve sloupci Obchod ma 12 -> Carodejnice ho nechá
    assert vyhodnot(hra, 0)["soucty"] == {0: 12, 1: 1}

    nastav_sloupec(hra, 0, [("Kupec", 0), ("Čarodějnice", 1)],
                   kategorie="Hudba")
    # mimo svou kategorii ma 8 -> odstranen
    assert vyhodnot(hra, 0)["soucty"] == {1: 1}


def test_carodejnice_posuzuje_dvojnika_s_prevzatou_hodnotou():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Dvojník", 0), ("Král", 1),
                            ("Čarodějnice", 2)])
    # Dvojnik ma 20 (zakladni 0), Carodejnice ho nechá
    assert vyhodnot(hra, 0)["soucty"] == {0: 20, 1: 20, 2: 1}


# ---- po zasahu Maga/Carodejnice se hodnoty prepocitaji ze zbylych karet

def test_poustevnik_se_po_magovi_prepocita():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Poustevník", 0), ("Mág", 1),
                            ("Král", 2), ("Královna", 2)])
    # pri posouzeni ma Poustevnik 12 - 3 = 9 a prezije; po odstraneni
    # Krale a Kralovny ma 12 - 1 = 11 (Mag uz znovu nepusobi)
    assert vyhodnot(hra, 0)["soucty"] == {0: 11, 1: 7}


def test_palecek_se_po_carodejnici_prepocita():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Paleček", 0), ("Čarodějnice", 1),
                            ("Bouře", 2), ("Bouře", 2)])
    # pri posouzeni ma Palecek 2 + 9 = 11 a prezije; po odstraneni
    # obou Bouri ma 2 + 3 = 5
    assert vyhodnot(hra, 0)["soucty"] == {0: 5, 1: 1}


def test_dvojnik_prevezme_prepocitanou_hodnotu():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Dvojník", 0), ("Paleček", 1), ("Král", 2),
                            ("Čarodějnice", 2), ("Bouře", 2)])
    # posouzeni: Palecek 2 + 12 = 14, Dvojnik 14; Carodejnice odstrani Bouri;
    # prepocet: Palecek 2 + 9 = 11 a Dvojnik ho kopiruje
    assert vyhodnot(hra, 0)["soucty"] == {0: 11, 1: 11, 2: 21}


def test_romeo_bez_julie_po_prepoctu():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Romeo", 0), ("Julie", 1), ("Čarodějnice", 2)])
    # Julie jineho hrace Romea neposili: 5 -> Carodejnice ho odstrani
    assert vyhodnot(hra, 0)["soucty"] == {1: 14, 2: 1}


def test_drak_plati_az_po_prepoctu():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Drak", 0), ("Paleček", 1), ("Čarodějnice", 2),
                            ("Bouře", 2)])
    # posouzeni bez Draka: Palecek 2 + 9 = 11 prezije (s Drakem by mel 9
    # a Carodejnice by ho odstranila); Boure odstranena; prepocet
    # Palecek 2 + 6 = 8; teprve pak Drak: 8 - 2 = 6, Carodejnice 1 -> 0
    assert vyhodnot(hra, 0)["soucty"] == {0: 11, 1: 6, 2: 0}


# ------------------------------------- Musketyri rusi i bonus specialistu

@pytest.mark.parametrize("kategorie", list(KATEGORIE))
def test_musketyri_rusi_bonus_specialisty(kategorie):
    specialista = KATEGORIE[kategorie]["specialista"]
    hra = nova_hra(2)
    nastav_sloupec(hra, 0, [(specialista, 0), ("Mušketýři", 1)],
                   kategorie=kategorie)
    vysledek = vyhodnot(hra, 0)
    assert vysledek["soucty"] == {0: 8, 1: 11}
    assert vysledek["vitez"] == 1


def test_musketyri_rusi_bonus_i_pred_magem():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Statkář", 0), ("Mušketýři", 1), ("Mág", 2)],
                   kategorie="Rolnictví")
    # bez Musketyru by mel Statkar 12 a Mag by ho odstranil
    assert vyhodnot(hra, 0)["soucty"] == {0: 8, 1: 11, 2: 7}


# ------------------------------ Objevitel preskakuje sloupce uzavrene Bouri

def test_objevitel_preskoci_vic_uzavrenych_sloupcu():
    hra = nova_hra(4)
    nastav_cile(hra, 5, 5, 5, 5)
    hra.uzavrene[1] = hra.uzavrene[2] = True
    hra.sloupce[0] = [karta("Objevitel", 1, odkryta=False)]
    dej_do_ruky(hra, 0, "Žebrák", "Mág", "Mág")
    hra.vyloz(0, 0, 0)
    assert hra.sloupce[1] == [] and hra.sloupce[2] == []
    assert hra.sloupce[3] == [karta("Objevitel", 1, odkryta=False)]
    assert hra.sloupce[0] == [karta("Žebrák", 0, odkryta=False)]


def test_objevitel_zustane_kdyz_jsou_ostatni_sloupce_uzavrene():
    hra = nova_hra(3)
    nastav_cile(hra, 5, 5, 5)
    hra.uzavrene[1] = hra.uzavrene[2] = True
    hra.sloupce[0] = [karta("Objevitel", 1, odkryta=False)]
    dej_do_ruky(hra, 0, "Žebrák", "Mág", "Mág")
    hra.vyloz(0, 0, 0)
    assert hra.sloupce[0] == [karta("Objevitel", 1),
                              karta("Žebrák", 0, odkryta=False)]


def test_objevitel_preskoci_sloupec_uzavreny_v_temze_kole():
    hra = nova_hra(3)
    nastav_cile(hra, 5, 5, 5)
    # prvni Objevitel prijde pod zakrytou Bouri ve sloupci 1 a ta ho uzavre
    hra.sloupce[0] = [karta("Objevitel", 1, odkryta=False)]
    hra.sloupce[1] = [karta("Bouře", 2, odkryta=False)]
    dej_do_ruky(hra, 0, "Žebrák", "Mág", "Mág")
    hra.vyloz(0, 0, 0)
    assert hra.uzavrene[1]
    assert hra.sloupce[1] == [karta("Bouře", 2),
                              karta("Objevitel", 1, odkryta=False)]
    # druhy Objevitel ze sloupce 0 uz sloupec 1 preskoci
    dej_do_ruky(hra, 1, "Objevitel", "Mág", "Mág")
    hra.vyloz(1, 0, 0)
    dej_do_ruky(hra, 2, "Žebrák", "Mág", "Mág")
    hra.vyloz(2, 0, 0)
    assert hra.sloupce[0] == [karta("Žebrák", 0),
                              karta("Žebrák", 2, odkryta=False)]
    assert hra.sloupce[1] == [karta("Bouře", 2),
                              karta("Objevitel", 1, odkryta=False)]
    assert hra.sloupce[2] == [karta("Objevitel", 1, odkryta=False)]


# ------------------------- Objevitel cestuje v jednom tahu jen jednou

def test_objevitel_cestuje_v_tahu_jen_jednou():
    hra = nova_hra(2)
    nastav_cile(hra, 5, 5)
    hra.sloupce[0] = [karta("Objevitel", 0, odkryta=False)]   # A
    hra.sloupce[1] = [karta("Objevitel", 1, odkryta=False)]   # B
    dej_do_ruky(hra, 0, "Objevitel", "Mág", "Mág")            # C
    hra.vyloz(0, 0, 0)
    # A -> sloupec 1 (otoci B), B -> sloupec 0 (otoci C),
    # C -> sloupec 1 (otoci A); A uz cestoval, takze zustava odkryty
    assert hra.sloupce[0] == [karta("Objevitel", 1, odkryta=False)]
    assert hra.sloupce[1] == [karta("Objevitel", 0),
                              karta("Objevitel", 0, odkryta=False)]
    assert "Objevitel už v tomto tahu cestoval, zůstává." in hra.zaznamy
    assert hra.faze == TAH and hra.na_tahu == 1


def test_objevitel_muze_cestovat_znovu_v_dalsim_tahu():
    hra = nova_hra(2)
    nastav_cile(hra, 5, 5)
    hra.sloupce[0] = [karta("Objevitel", 1, odkryta=False)]
    dej_do_ruky(hra, 0, "Žebrák", "Mág", "Mág")
    hra.vyloz(0, 0, 0)
    assert hra.sloupce[1] == [karta("Objevitel", 1, odkryta=False)]
    # v dalsim tahu se stejny Objevitel po otoceni znovu presune
    dej_do_ruky(hra, 1, "Král", "Mág", "Mág")
    hra.vyloz(1, 0, 1)
    assert hra.sloupce[1] == [karta("Král", 1, odkryta=False)]
    assert hra.sloupce[0] == [karta("Žebrák", 0),
                              karta("Objevitel", 1, odkryta=False)]


# ------------------ tri Magove / Carodejnice: dva se zrusi, treti plati

def test_tri_magove_treti_plati():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Král", 0), ("Mág", 1), ("Mág", 2), ("Mág", 0)])
    vysledek = vyhodnot(hra, 0)
    assert vysledek["soucty"] == {0: 7, 1: 7, 2: 7}
    assert "Mág odstranil karty s hodnotou 10 a více." in vysledek["poznamky"]


def test_ctyri_magove_se_zrusi():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Král", 0), ("Mág", 1), ("Mág", 2),
                            ("Mág", 0), ("Mág", 1)])
    vysledek = vyhodnot(hra, 0)
    assert vysledek["soucty"] == {0: 27, 1: 14, 2: 7}
    assert "Mágové se navzájem zrušili." in vysledek["poznamky"]


def test_tri_carodejnice_treti_plati():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Bouře", 0), ("Čarodějnice", 1),
                            ("Čarodějnice", 2), ("Čarodějnice", 0),
                            ("Král", 1)])
    vysledek = vyhodnot(hra, 0)
    # Boure odstranena, Carodejnice samy sebe neodstrani
    assert vysledek["soucty"] == {0: 1, 1: 21, 2: 1}
    assert ("Čarodějnice odstranila karty s hodnotou 9 a méně."
            in vysledek["poznamky"])


def test_ctyri_carodejnice_se_zrusi():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Bouře", 0), ("Čarodějnice", 1),
                            ("Čarodějnice", 2), ("Čarodějnice", 0),
                            ("Čarodějnice", 1)])
    vysledek = vyhodnot(hra, 0)
    assert vysledek["soucty"] == {0: 10, 1: 2, 2: 1}
    assert "Čarodějnice se navzájem zrušily." in vysledek["poznamky"]
