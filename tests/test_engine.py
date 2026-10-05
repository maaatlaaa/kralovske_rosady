import json
import random

import pytest

from rosady.engine import KONEC, TAH, VOLBA, VYHODNOCENI, ChybaHry, Hra
from rosady.karty import KARTY


def nova_hra(pocet=3, seed=1):
    return Hra([f"hrac{i}" for i in range(pocet)], rng=random.Random(seed))


def dej_do_ruky(hra, hrac, *karty):
    hra.hraci[hrac]["ruka"] = list(karty)


def poloz(hra, radek, sloupec, karta, hrac, odkryta=True, prevlek=None):
    hra.plocha[radek][sloupec] = {"karta": karta, "hrac": hrac,
                                  "odkryta": odkryta, "pod_prevlekem": prevlek}


def nastav_sloupec(hra, sloupec, kategorie, karty):
    """karty = seznam (nazev, hrac) shora dolu"""
    hra.hlavicka[sloupec] = {"kategorie": kategorie, "hodnota": 3}
    for radek, (nazev, hrac) in enumerate(karty):
        poloz(hra, radek, sloupec, nazev, hrac)


# ------------------------------------------------------------ zaklad hry

def test_nova_hra():
    hra = nova_hra(4)
    assert hra.faze == TAH
    assert len(hra.hlavicka) == 4
    assert all(len(h["ruka"]) == 3 for h in hra.hraci)
    assert all(len(h["balicek"]) == 22 for h in hra.hraci)
    assert len(hra.cilove_balicek) == 36 - 4


def test_pocet_hracu():
    with pytest.raises(ChybaHry):
        Hra(["sam"])
    with pytest.raises(ChybaHry):
        Hra([str(i) for i in range(7)])


def test_vylozeni_a_otoceni():
    hra = nova_hra(3)
    dej_do_ruky(hra, 0, "Král", "Žebrák", "Mág")
    hra.vyloz(0, 0, 1)
    assert hra.plocha[0][1]["karta"] == "Král"
    assert hra.plocha[0][1]["odkryta"] is False
    assert len(hra.hraci[0]["ruka"]) == 3
    assert hra.na_tahu == 1

    dej_do_ruky(hra, 1, "Královna", "Žebrák", "Mág")
    hra.vyloz(1, 0, 1)
    assert hra.plocha[0][1]["odkryta"] is True
    assert hra.plocha[1][1]["odkryta"] is False
    assert hra.na_tahu == 2


def test_tah_mimo_poradi_a_plny_sloupec():
    hra = nova_hra(2)
    with pytest.raises(ChybaHry):
        hra.vyloz(1, 0, 0)
    poloz(hra, 0, 0, "Král", 1)
    poloz(hra, 1, 0, "Král", 1)
    with pytest.raises(ChybaHry):
        hra.vyloz(0, 0, 0)
    with pytest.raises(ChybaHry):
        hra.vyloz(0, 5, 1)


def test_dobirani_po_dojiti_balicku():
    hra = nova_hra(2)
    hrac = hra.hraci[0]
    hrac["balicek"] = []
    hrac["ruka"] = ["Král", "Mág"]
    hra._dober(hrac)
    assert len(hrac["ruka"]) == 3
    assert len(set(hrac["ruka"])) == 3
    assert len(hrac["balicek"]) == 25 - 3


def test_cela_hra_dobehne():
    """nahodne hrani az do konce - hra nesmi spadnout"""
    for seed in range(40):
        rng = random.Random(seed)
        pocet = 2 + seed % 5
        hra = nova_hra(pocet, seed)
        kroky = 0
        while hra.faze != KONEC:
            kroky += 1
            assert kroky < 5000
            if hra.faze == TAH:
                volne = [s for s in range(pocet)
                         if hra._volny_radek(s) is not None]
                hra.vyloz(hra.na_tahu, rng.randrange(3), rng.choice(volne))
            elif hra.faze == VOLBA:
                hrac = hra.volba["hrac"]
                if hra.volba["typ"] == "prevlek":
                    hra.prevlek(hrac, rng.choice([None, 0, 1, 2]))
                else:
                    a, b = rng.sample(range(pocet), 2)
                    hra.zradce(hrac, a, b)
            elif hra.faze == VYHODNOCENI:
                for hrac in range(pocet):
                    hra.pokracovat(hrac)
            # stav musi jit ulozit a nacist
            hra = Hra.ze_slovniku(json.loads(json.dumps(hra.do_slovniku())),
                                  rng=rng)
            for hrac in range(pocet):
                json.dumps(hra.pohled(hrac))
        assert len(hra.poradi) == pocet
        vyhrane = sum(len(h["cilove_karty"]) for h in hra.hraci)
        assert vyhrane <= 6 * pocet


def test_zacinajici_hrac_se_strida():
    hra = nova_hra(3)
    assert hra.na_tahu == 0
    for radek in range(3):
        for sloupec in range(3):
            poloz(hra, radek, sloupec, "Král", 0)
    hra.plocha[2][2] = None
    hra.na_tahu = 2
    dej_do_ruky(hra, 2, "Panoš", "Panoš", "Panoš")
    hra.vyloz(2, 0, 2)
    assert hra.faze == VYHODNOCENI
    for hrac in range(3):
        hra.pokracovat(hrac)
    assert hra.kolo == 1
    assert hra.na_tahu == 1


# -------------------------------------------------- karty pri otoceni

def test_mordyr_zabije_kartu_pod_sebou():
    hra = nova_hra(3)
    poloz(hra, 0, 0, "Mordýř", 1, odkryta=False)
    dej_do_ruky(hra, 0, "Král", "Mág", "Mág")
    hra.vyloz(0, 0, 0)
    assert hra.plocha[0][0]["odkryta"]
    assert hra.plocha[1][0] is None


def test_boure_uzavre_sloupec():
    hra = nova_hra(4)
    poloz(hra, 0, 0, "Bouře", 1, odkryta=False)
    dej_do_ruky(hra, 0, "Král", "Mág", "Mág")
    hra.vyloz(0, 0, 0)
    assert hra.plocha[1][0]["karta"] == "Král"
    assert hra.plocha[2][0] == {"blokovano": True}
    assert hra.plocha[3][0] == {"blokovano": True}
    with pytest.raises(ChybaHry):
        hra.vyloz(1, 0, 0)


def test_objevitel_odcestuje():
    hra = nova_hra(3)
    poloz(hra, 0, 0, "Objevitel", 1, odkryta=False)
    poloz(hra, 0, 1, "Král", 2)
    poloz(hra, 1, 1, "Král", 2)
    poloz(hra, 2, 1, "Král", 2)
    poloz(hra, 0, 2, "Královna", 2, odkryta=False)
    dej_do_ruky(hra, 0, "Žebrák", "Mág", "Mág")
    hra.vyloz(0, 0, 0)
    # sloupec 1 je plny, Objevitel jde do sloupce 2 a otoci Kralovnu
    assert hra.plocha[0][0]["karta"] == "Žebrák"
    assert hra.plocha[1][0] is None
    assert hra.plocha[1][2]["karta"] == "Objevitel"
    assert hra.plocha[0][2]["odkryta"]


def test_objevitel_nema_kam():
    hra = nova_hra(2)
    poloz(hra, 0, 0, "Objevitel", 1, odkryta=False)
    poloz(hra, 0, 1, "Král", 1)
    poloz(hra, 1, 1, "Král", 1)
    dej_do_ruky(hra, 0, "Žebrák", "Mág", "Mág")
    hra.vyloz(0, 0, 0)
    assert hra.plocha[0][0]["karta"] == "Objevitel"
    assert hra.faze == VYHODNOCENI


def test_prevlek_ceka_na_vlastnika():
    hra = nova_hra(3)
    poloz(hra, 0, 0, "Převlek", 2, odkryta=False)
    dej_do_ruky(hra, 0, "Žebrák", "Mág", "Mág")
    dej_do_ruky(hra, 2, "Král", "Panoš", "Mág")
    hra.vyloz(0, 0, 0)
    assert hra.faze == VOLBA
    assert hra.volba["hrac"] == 2
    with pytest.raises(ChybaHry):
        hra.vyloz(1, 0, 1)
    with pytest.raises(ChybaHry):
        hra.prevlek(0, 0)
    hra.prevlek(2, 0)
    assert hra.plocha[0][0]["pod_prevlekem"] == "Král"
    assert "Král" not in hra.hraci[2]["ruka"]
    assert len(hra.hraci[2]["ruka"]) == 3
    assert hra.faze == TAH and hra.na_tahu == 1
    # ostatni nevidi, co je pod prevlekem, vlastnik ano
    assert hra.pohled(1)["plocha"][0][0]["pod_prevlekem"] is None
    assert hra.pohled(1)["plocha"][0][0]["ma_prevlek"] is True
    assert hra.pohled(2)["plocha"][0][0]["pod_prevlekem"] == "Král"


def test_zradce_prohodi_cilove_karty():
    hra = nova_hra(3)
    poloz(hra, 0, 0, "Zrádce", 1, odkryta=False)
    dej_do_ruky(hra, 0, "Žebrák", "Mág", "Mág")
    puvodni = list(hra.hlavicka)
    hra.vyloz(0, 0, 0)
    assert hra.faze == VOLBA
    with pytest.raises(ChybaHry):
        hra.zradce(1, 1, 1)
    hra.zradce(1, 0, 2)
    assert hra.hlavicka == [puvodni[2], puvodni[1], puvodni[0]]
    assert hra.na_tahu == 1


def test_pohled_skryva_cizi_karty():
    hra = nova_hra(2)
    dej_do_ruky(hra, 0, "Král", "Mág", "Mág")
    hra.vyloz(0, 0, 0)
    assert hra.pohled(1)["plocha"][0][0]["karta"] is None
    assert hra.pohled(0)["plocha"][0][0]["karta"] == "Král"
    assert hra.pohled(1)["ruka"] == hra.hraci[1]["ruka"]
    assert "balicek" not in json.dumps(hra.pohled(1))


# ------------------------------------------------------- vyhodnoceni

def vyhodnot(hra, sloupec):
    return hra._vyhodnot_sloupec(sloupec)


def test_soucet_a_mordyr_pul_bodu():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, "Hudba", [("Mordýř", 0), ("Bouře", 1), ("Panoš", 2)])
    vysledek = vyhodnot(hra, 0)
    assert vysledek["soucty"] == {0: 9.5, 1: 9, 2: 2}
    assert vysledek["vitez"] == 0


def test_specialista_bonus():
    hra = nova_hra(2)
    nastav_sloupec(hra, 0, "Hudba", [("Trubadúr", 0), ("Kupec", 1)])
    vysledek = vyhodnot(hra, 0)
    assert vysledek["soucty"] == {0: 12, 1: 8}


def test_mag_odstrani_silne_karty():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, "Hudba", [("Král", 0), ("Mág", 1), ("Mordýř", 2)])
    vysledek = vyhodnot(hra, 0)
    assert vysledek["soucty"] == {1: 7, 2: 9.5}
    assert vysledek["vitez"] == 2


def test_carodejnice_odstrani_slabe_karty():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, "Hudba",
                   [("Čarodějnice", 0), ("Bouře", 1), ("Mordýř", 2)])
    vysledek = vyhodnot(hra, 0)
    assert vysledek["soucty"] == {0: 1, 2: 9.5}


def test_musketyri_ruseji_schopnosti():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, "Hudba", [("Král", 0), ("Mág", 1), ("Mušketýři", 2)])
    vysledek = vyhodnot(hra, 0)
    assert vysledek["soucty"] == {0: 20, 1: 7, 2: 11}
    assert vysledek["vitez"] == 0


def test_princ_a_panos():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, "Hudba", [("Král", 0), ("Princ", 1), ("Panoš", 1)])
    assert vyhodnot(hra, 0)["vitez"] == 1


def test_princ_a_panos_nejvyse_vyhrava():
    hra = nova_hra(4)
    nastav_sloupec(hra, 0, "Hudba", [("Panoš", 1), ("Princ", 0),
                                     ("Panoš", 0), ("Princ", 1)])
    assert vyhodnot(hra, 0)["vitez"] == 1


def test_zebrak_nejnizsi_vyhrava():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, "Hudba", [("Žebrák", 0), ("Král", 1), ("Panoš", 2)])
    vysledek = vyhodnot(hra, 0)
    assert vysledek["nejnizsi_vyhrava"]
    assert vysledek["vitez"] == 2


def test_drak_ubira_soupearum():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, "Hudba", [("Drak", 0), ("Král", 1), ("Bouře", 1)])
    vysledek = vyhodnot(hra, 0)
    assert vysledek["soucty"] == {0: 11, 1: 25}


def test_palecek_a_poustevnik():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, "Hudba",
                   [("Paleček", 0), ("Poustevník", 1), ("Panoš", 2)])
    vysledek = vyhodnot(hra, 0)
    assert vysledek["soucty"] == {0: 2 + 6, 1: 12 - 1, 2: 2}


def test_romeo_a_julie():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, "Hudba", [("Romeo", 0), ("Julie", 0), ("Romeo", 1)])
    vysledek = vyhodnot(hra, 0)
    assert vysledek["soucty"] == {0: 15 + 14, 1: 5}


def test_dvojnik_kopiruje_kartu_pod_sebou():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, "Hudba", [("Dvojník", 0), ("Dvojník", 1), ("Král", 2)])
    vysledek = vyhodnot(hra, 0)
    assert vysledek["soucty"] == {0: 20, 1: 20, 2: 20}
    # remiza - vyhrava karta nejvys
    assert vysledek["vitez"] == 0


def test_dvojnik_na_konci_ma_nulu():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, "Hudba", [("Drak", 0), ("Panoš", 1), ("Dvojník", 2)])
    vysledek = vyhodnot(hra, 0)
    assert vysledek["soucty"] == {0: 11, 1: 0, 2: -2}


def test_prevlek_se_promeni():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, "Hudba", [("Král", 0), ("Panoš", 1), ("Převlek", 2)])
    hra.plocha[2][0]["pod_prevlekem"] = "Mág"
    vysledek = vyhodnot(hra, 0)
    # skryty Mag odstranil Krale
    assert vysledek["soucty"] == {1: 2, 2: 7}


def test_remiza_zebrak_vyhrava_spodni():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, "Hudba", [("Žebrák", 0), ("Žebrák", 1), ("Král", 2)])
    assert vyhodnot(hra, 0)["vitez"] == 1


def test_prazdny_sloupec_nikdo_nevyhraje():
    hra = nova_hra(2)
    nastav_sloupec(hra, 0, "Hudba", [("Mág", 0), ("Mág", 1)])
    # Mag sam sebe neodstrani
    assert vyhodnot(hra, 0)["vitez"] is not None
    hra.plocha[0][0] = {"blokovano": True}
    hra.plocha[1][0] = {"blokovano": True}
    assert vyhodnot(hra, 0)["vitez"] is None


# ---------------------------------------------------------- konecne skore

def test_skore_zakladni():
    hra = nova_hra(2)
    hra.hraci[0]["cilove_karty"] = [{"kategorie": "Hudba", "hodnota": 5},
                                    {"kategorie": "Hudba", "hodnota": 3}]
    assert hra.skore(0) == 8


def test_skore_vsechny_kategorie():
    hra = nova_hra(2)
    karty = [{"kategorie": k, "hodnota": 5} for k in
             ["Alchymie", "Šerm", "Rolnictví", "Obchod", "Náboženství", "Hudba"]]
    karty.append({"kategorie": "Hudba", "hodnota": 1})
    hra.hraci[0]["cilove_karty"] = karty
    # zakladni 31, specialni 2 * 30 - 1 = 59
    assert hra.skore(0) == 59


def test_vsechny_karty_maji_obrazek_a_popis():
    for nazev, info in KARTY.items():
        assert info["soubor"] and info["popis"], nazev
