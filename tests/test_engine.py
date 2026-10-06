import json
import random

import pytest

from rosady.engine import KONEC, TAH, VOLBA, VYHODNOCENI, ChybaHry, Hra
from rosady.karty import KARTY


def nova_hra(pocet=3, seed=1):
    return Hra([f"hrac{i}" for i in range(pocet)], rng=random.Random(seed))


def dej_do_ruky(hra, hrac, *karty):
    hra.hraci[hrac]["ruka"] = list(karty)


def karta(nazev, hrac, odkryta=True, prevlek=None):
    return {"karta": nazev, "hrac": hrac, "odkryta": odkryta,
            "pod_prevlekem": prevlek}


def nastav_cile(hra, *hodnoty, kategorie="Hudba"):
    hra.hlavicka = [{"kategorie": kategorie, "hodnota": h} for h in hodnoty]


def nastav_sloupec(hra, sloupec, karty, kategorie="Hudba"):
    """karty = seznam (nazev, hrac) shora dolu"""
    hra.hlavicka[sloupec] = {"kategorie": kategorie, "hodnota": 5}
    hra.sloupce[sloupec] = [karta(nazev, hrac) for nazev, hrac in karty]


def vyhodnot(hra, sloupec):
    return hra._vyhodnot_sloupec(sloupec)


# ------------------------------------------------------------ zaklad hry

def test_nova_hra():
    hra = nova_hra(4)
    assert hra.faze == TAH
    assert len(hra.hlavicka) == 4
    assert hra.sloupce == [[], [], [], []]
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
    nastav_cile(hra, 5, 5, 5)
    dej_do_ruky(hra, 0, "Král", "Žebrák", "Mág")
    hra.vyloz(0, 0, 1)
    assert hra.sloupce[1] == [karta("Král", 0, odkryta=False)]
    assert len(hra.hraci[0]["ruka"]) == 3
    assert hra.na_tahu == 1

    dej_do_ruky(hra, 1, "Královna", "Žebrák", "Mág")
    hra.vyloz(1, 0, 1)
    assert hra.sloupce[1][0]["odkryta"] is True
    assert hra.sloupce[1][1]["odkryta"] is False
    assert hra.na_tahu == 2


def test_tah_mimo_poradi():
    hra = nova_hra(2)
    with pytest.raises(ChybaHry):
        hra.vyloz(1, 0, 0)
    with pytest.raises(ChybaHry):
        hra.vyloz(0, 5, 1)
    with pytest.raises(ChybaHry):
        hra.vyloz(0, 0, 7)


def test_do_splneneho_sloupce_lze_vykladat_dal():
    hra = nova_hra(2)
    nastav_cile(hra, 1, 3)
    dej_do_ruky(hra, 0, "Žebrák", "Žebrák", "Žebrák")
    dej_do_ruky(hra, 1, "Žebrák", "Žebrák", "Žebrák")
    hra.vyloz(0, 0, 0)
    hra.vyloz(1, 0, 0)
    assert len(hra.sloupce[0]) == 2
    assert hra.faze == TAH


def test_kolo_konci_kdyz_jsou_splneny_vsechny_sloupce():
    hra = nova_hra(2)
    nastav_cile(hra, 1, 2)
    for hrac, sloupec in [(0, 0), (1, 1)]:
        dej_do_ruky(hra, hrac, "Žebrák", "Žebrák", "Žebrák")
        hra.vyloz(hrac, 0, sloupec)
    assert hra.faze == TAH
    dej_do_ruky(hra, 0, "Král", "Žebrák", "Žebrák")
    hra.vyloz(0, 0, 1)
    assert hra.faze == VYHODNOCENI
    assert all(k["odkryta"] for s in hra.sloupce for k in s)


def test_poradi_pokracuje_do_dalsiho_kola():
    hra = nova_hra(3)
    nastav_cile(hra, 1, 1, 1)
    for hrac in range(3):
        dej_do_ruky(hra, hrac, "Žebrák", "Žebrák", "Žebrák")
        hra.vyloz(hrac, 0, hrac)
    assert hra.faze == VYHODNOCENI
    for hrac in range(3):
        hra.pokracovat(hrac)
    assert hra.kolo == 1
    # kolo ukoncil hrac 2, dalsi zacina hrac 0
    assert hra.na_tahu == 0


def test_dobirani_z_odhazovaciho_balicku():
    hra = nova_hra(2)
    hrac = hra.hraci[0]
    hrac["balicek"] = []
    hrac["ruka"] = ["Král", "Mág"]
    hrac["odhozene"] = ["Drak", "Romeo"]
    hra._dober(hrac)
    assert len(hrac["ruka"]) == 3
    assert hrac["ruka"][-1] in ("Drak", "Romeo")
    assert len(hrac["balicek"]) == 1 and hrac["odhozene"] == []


def test_bez_karet_se_nedobira():
    hra = nova_hra(2)
    hrac = hra.hraci[0]
    hrac["balicek"], hrac["odhozene"], hrac["ruka"] = [], [], ["Král"]
    hra._dober(hrac)
    assert hrac["ruka"] == ["Král"]


def test_vylozene_karty_jdou_na_konci_kola_na_odhazovaci_balicek():
    hra = nova_hra(2)
    nastav_cile(hra, 1, 1)
    dej_do_ruky(hra, 0, "Převlek", "Žebrák", "Žebrák")
    hra.vyloz(0, 0, 0)
    hra.sloupce[0][0]["pod_prevlekem"] = "Král"
    dej_do_ruky(hra, 1, "Drak", "Žebrák", "Žebrák")
    hra.vyloz(1, 0, 1)
    assert hra.faze == VYHODNOCENI
    hra.pokracovat(0, za_vsechny=True)
    assert sorted(hra.hraci[0]["odhozene"]) == ["Král", "Převlek"]
    assert hra.hraci[1]["odhozene"] == ["Drak"]


def test_hrac_bez_karet_se_preskakuje():
    hra = nova_hra(3)
    nastav_cile(hra, 5, 5, 5)
    hra.hraci[1]["ruka"] = []
    dej_do_ruky(hra, 0, "Král", "Žebrák", "Žebrák")
    hra.vyloz(0, 0, 0)
    assert hra.na_tahu == 2


def test_cela_hra_dobehne():
    """nahodne hrani az do konce - hra nesmi spadnout"""
    for seed in range(60):
        rng = random.Random(seed)
        pocet = 2 + seed % 5
        hra = nova_hra(pocet, seed)
        kroky = 0
        while hra.faze != KONEC:
            kroky += 1
            assert kroky < 5000
            if hra.faze == TAH:
                otevrene = [s for s in range(pocet) if not hra.uzavrene[s]]
                hra.vyloz(hra.na_tahu, rng.randrange(3), rng.choice(otevrene))
            elif hra.faze == VOLBA:
                hrac = hra.volba["hrac"]
                if hra.volba["typ"] == "prevlek":
                    hra.prevlek(hrac, rng.choice([None, 0, 1, 2]))
                else:
                    jine = [s for s in range(pocet) if s != hra.volba["sloupec"]]
                    hra.zradce(hrac, rng.choice(jine + [None]))
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


# -------------------------------------------------- karty pri otoceni

def test_mordyr_zabije_kartu_pod_sebou():
    hra = nova_hra(3)
    nastav_cile(hra, 5, 5, 5)
    hra.sloupce[0] = [karta("Mordýř", 1, odkryta=False)]
    dej_do_ruky(hra, 0, "Král", "Mág", "Mág")
    hra.vyloz(0, 0, 0)
    assert hra.sloupce[0] == [karta("Mordýř", 1)]


def test_boure_uzavre_sloupec():
    hra = nova_hra(3)
    nastav_cile(hra, 5, 5, 5)
    hra.sloupce[0] = [karta("Bouře", 1, odkryta=False)]
    dej_do_ruky(hra, 0, "Král", "Mág", "Mág")
    hra.vyloz(0, 0, 0)
    assert hra.uzavrene[0]
    assert hra.splneny(0)
    with pytest.raises(ChybaHry):
        hra.vyloz(1, 0, 0)


def test_boure_muze_ukoncit_kolo():
    hra = nova_hra(2)
    nastav_cile(hra, 5, 1)
    hra.sloupce[0] = [karta("Bouře", 1, odkryta=False)]
    hra.sloupce[1] = [karta("Král", 1)]
    dej_do_ruky(hra, 0, "Žebrák", "Mág", "Mág")
    hra.vyloz(0, 0, 0)
    assert hra.faze == VYHODNOCENI


def test_objevitel_odcestuje_lícem_dolu_na_konec_dalsiho_sloupce():
    hra = nova_hra(3)
    nastav_cile(hra, 5, 5, 5)
    hra.sloupce[0] = [karta("Král", 2), karta("Objevitel", 1, odkryta=False)]
    hra.sloupce[1] = [karta("Královna", 2, odkryta=False)]
    dej_do_ruky(hra, 0, "Žebrák", "Mág", "Mág")
    hra.vyloz(0, 0, 0)
    assert [k["karta"] for k in hra.sloupce[0]] == ["Král", "Žebrák"]
    assert hra.sloupce[1] == [karta("Královna", 2),
                              karta("Objevitel", 1, odkryta=False)]


def test_objevitel_z_posledniho_sloupce_do_prvniho_a_preskoci_uzavreny():
    hra = nova_hra(3)
    nastav_cile(hra, 5, 5, 5)
    hra.uzavrene[0] = True
    hra.sloupce[2] = [karta("Objevitel", 1, odkryta=False)]
    dej_do_ruky(hra, 0, "Žebrák", "Mág", "Mág")
    hra.vyloz(0, 0, 2)
    assert hra.sloupce[0] == []
    assert hra.sloupce[1] == [karta("Objevitel", 1, odkryta=False)]
    assert [k["karta"] for k in hra.sloupce[2]] == ["Žebrák"]


def test_objevitel_otoci_kartu_v_novem_sloupci():
    hra = nova_hra(2)
    nastav_cile(hra, 5, 5)
    hra.sloupce[0] = [karta("Objevitel", 1, odkryta=False)]
    hra.sloupce[1] = [karta("Mordýř", 1, odkryta=False)]
    dej_do_ruky(hra, 0, "Žebrák", "Mág", "Mág")
    hra.vyloz(0, 0, 0)
    # Objevitel prisel pod Mordyre, ten se otocil a Objevitele zabil
    assert hra.sloupce[1] == [karta("Mordýř", 1)]


def test_objevitele_se_nezacykli():
    hra = nova_hra(2)
    nastav_cile(hra, 5, 5)
    hra.sloupce[0] = [karta("Objevitel", 0, odkryta=False)]
    hra.sloupce[1] = [karta("Objevitel", 1, odkryta=False)]
    dej_do_ruky(hra, 0, "Objevitel", "Mág", "Mág")
    hra.vyloz(0, 0, 0)
    assert hra.faze == TAH and hra.na_tahu == 1
    vsechny = hra.sloupce[0] + hra.sloupce[1]
    assert [k["karta"] for k in vsechny] == ["Objevitel"] * 3
    assert any(k["odkryta"] for k in vsechny)


def test_prevlek_ceka_na_vlastnika():
    hra = nova_hra(3)
    nastav_cile(hra, 5, 5, 5)
    hra.sloupce[0] = [karta("Převlek", 2, odkryta=False)]
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
    assert hra.sloupce[0][0]["pod_prevlekem"] == "Král"
    assert "Král" not in hra.hraci[2]["ruka"]
    assert len(hra.hraci[2]["ruka"]) == 3
    assert hra.faze == TAH and hra.na_tahu == 1
    # ostatni nevidi, co je pod prevlekem, vlastnik ano
    assert hra.pohled(1)["sloupce"][0][0]["pod_prevlekem"] is None
    assert hra.pohled(1)["sloupce"][0][0]["ma_prevlek"] is True
    assert hra.pohled(2)["sloupce"][0][0]["pod_prevlekem"] == "Král"


def test_zradce_vymeni_cilovou_kartu_sveho_sloupce():
    hra = nova_hra(3)
    hra.sloupce[0] = [karta("Zrádce", 1, odkryta=False)]
    dej_do_ruky(hra, 0, "Žebrák", "Mág", "Mág")
    hra.hlavicka = [{"kategorie": "Hudba", "hodnota": h} for h in (5, 4, 3)]
    puvodni = list(hra.hlavicka)
    hra.vyloz(0, 0, 0)
    assert hra.faze == VOLBA
    with pytest.raises(ChybaHry):
        hra.zradce(1, 0)
    hra.zradce(1, 2)
    assert hra.hlavicka == [puvodni[2], puvodni[1], puvodni[0]]
    assert hra.na_tahu == 1


def test_pohled_skryva_cizi_karty():
    hra = nova_hra(2)
    nastav_cile(hra, 5, 5)
    dej_do_ruky(hra, 0, "Král", "Mág", "Mág")
    hra.vyloz(0, 0, 0)
    assert hra.pohled(1)["sloupce"][0][0]["karta"] is None
    assert hra.pohled(0)["sloupce"][0][0]["karta"] == "Král"
    assert hra.pohled(1)["ruka"] == hra.hraci[1]["ruka"]
    assert "balicek" not in json.dumps(hra.pohled(1))


# ------------------------------------------------------- vyhodnoceni

def test_soucet_a_mordyr_pul_bodu():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Mordýř", 0), ("Bouře", 1), ("Panoš", 2)])
    vysledek = vyhodnot(hra, 0)
    assert vysledek["soucty"] == {0: 9.5, 1: 9, 2: 2}
    assert vysledek["vitez"] == 0


def test_specialista_bonus():
    hra = nova_hra(2)
    nastav_sloupec(hra, 0, [("Trubadúr", 0), ("Kupec", 1)])
    assert vyhodnot(hra, 0)["soucty"] == {0: 12, 1: 8}


def test_mag_odstrani_silne_karty():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Král", 0), ("Mág", 1), ("Mordýř", 2)])
    vysledek = vyhodnot(hra, 0)
    assert vysledek["soucty"] == {1: 7, 2: 9.5}
    assert vysledek["vitez"] == 2


def test_mag_odstrani_i_posilene_karty():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Trubadúr", 0), ("Mág", 1), ("Kupec", 2)])
    assert vyhodnot(hra, 0)["soucty"] == {1: 7, 2: 8}


def test_carodejnice_odstrani_slabe_karty():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Čarodějnice", 0), ("Bouře", 1), ("Mordýř", 2)])
    assert vyhodnot(hra, 0)["soucty"] == {0: 1, 2: 9.5}


def test_mag_a_carodejnice_pusobi_oba():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Král", 0), ("Mág", 1), ("Čarodějnice", 2),
                            ("Mordýř", 0)])
    # Mag odstrani Krale, Carodejnice Maga; prezije Mordyr a Carodejnice
    assert vyhodnot(hra, 0)["soucty"] == {0: 9.5, 2: 1}


def test_dva_magove_se_zrusi():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Král", 0), ("Mág", 1), ("Mág", 2)])
    assert vyhodnot(hra, 0)["soucty"] == {0: 20, 1: 7, 2: 7}


def test_dve_carodejnice_se_zrusi():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Bouře", 0), ("Čarodějnice", 1),
                            ("Čarodějnice", 2)])
    assert vyhodnot(hra, 0)["soucty"] == {0: 9, 1: 1, 2: 1}


def test_musketyri_ruseji_schopnosti():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Král", 0), ("Mág", 1), ("Mušketýři", 2),
                            ("Trubadúr", 1)])
    vysledek = vyhodnot(hra, 0)
    assert vysledek["soucty"] == {0: 20, 1: 7 + 8, 2: 11}
    assert vysledek["vitez"] == 0


def test_princ_a_panos():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Král", 0), ("Princ", 1), ("Panoš", 1)])
    assert vyhodnot(hra, 0)["vitez"] == 1


def test_princ_a_panos_nejvyse_vyhrava():
    hra = nova_hra(4)
    nastav_sloupec(hra, 0, [("Panoš", 1), ("Princ", 0),
                            ("Panoš", 0), ("Princ", 1)])
    assert vyhodnot(hra, 0)["vitez"] == 1


def test_zebrak_nejnizsi_vyhrava():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Žebrák", 0), ("Král", 1), ("Panoš", 2)])
    vysledek = vyhodnot(hra, 0)
    assert vysledek["nejnizsi_vyhrava"]
    assert vysledek["vitez"] == 2


def test_remiza_vyhrava_karta_nejbliz_cilove_karte():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Kupec", 1), ("Statkář", 0), ("Král", 2)])
    hra.sloupce[0][2] = karta("Kardinál", 2)
    assert vyhodnot(hra, 0)["vitez"] == 1


def test_remiza_se_zebrakem_vyhrava_karta_nejdal():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Žebrák", 0), ("Žebrák", 1), ("Král", 2)])
    assert vyhodnot(hra, 0)["vitez"] == 1


def test_drak_ubira_soupearum():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Drak", 0), ("Král", 1), ("Bouře", 1)])
    assert vyhodnot(hra, 0)["soucty"] == {0: 11, 1: 25}


def test_drak_nesnizi_hodnotu_pod_nulu():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Drak", 0), ("Čarodějnice", 1), ("Převlek", 2)])
    # Carodejnice odstrani Prevlek (0); jeji 1 klesne jen na 0
    assert vyhodnot(hra, 0)["soucty"] == {0: 11, 1: 0}


def test_palecek_a_poustevnik_pocitaji_vsechny_ostatni_karty():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Panoš", 2), ("Paleček", 0), ("Poustevník", 1)])
    assert vyhodnot(hra, 0)["soucty"] == {0: 2 + 6, 1: 12 - 2, 2: 2}


def test_romeo_a_julie():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Romeo", 0), ("Julie", 0), ("Romeo", 1)])
    assert vyhodnot(hra, 0)["soucty"] == {0: 15 + 14, 1: 5}


def test_dvojnik_kopiruje_kartu_tesne_pod_sebou():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Dvojník", 0), ("Dvojník", 1), ("Kupec", 2)])
    vysledek = vyhodnot(hra, 0)
    assert vysledek["soucty"] == {0: 8, 1: 8, 2: 8}
    assert vysledek["vitez"] == 0


def test_dvojnik_bez_karty_pod_sebou_nema_hodnotu():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Žebrák", 0), ("Král", 1), ("Dvojník", 2)])
    vysledek = vyhodnot(hra, 0)
    # hrac jen s Dvojnikem bez hodnoty nemuze vyhrat ani se Zebrakem
    assert vysledek["soucty"] == {0: 4, 1: 20}
    assert vysledek["vitez"] == 0


def test_prazdny_prevlek_se_zebrakem_vyhrava():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Žebrák", 0), ("Převlek", 1)])
    assert vyhodnot(hra, 0)["vitez"] == 1


def test_prevlek_se_promeni():
    hra = nova_hra(3)
    nastav_sloupec(hra, 0, [("Král", 0), ("Panoš", 1), ("Převlek", 2)])
    hra.sloupce[0][2]["pod_prevlekem"] = "Mág"
    # skryty Mag odstranil Krale
    assert vyhodnot(hra, 0)["soucty"] == {1: 2, 2: 7}


def test_prazdny_sloupec_nikdo_nevyhraje():
    hra = nova_hra(2)
    nastav_sloupec(hra, 0, [])
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
