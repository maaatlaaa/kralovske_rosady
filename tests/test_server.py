import pytest
from fastapi.testclient import TestClient

from rosady.server import vytvor_aplikaci


@pytest.fixture
def slozka(tmp_path):
    (tmp_path / "obrazky").mkdir()
    return tmp_path


def klient(slozka):
    return TestClient(vytvor_aplikaci(data_dir=slozka / "data",
                                      obrazky_dir=slozka / "obrazky",
                                      priprav_obrazky=False))


def zaloz_hru(c, jmena):
    odpoved = c.post("/api/mistnosti", json={"jmeno": jmena[0]}).json()
    kod, tokeny = odpoved["kod"], [odpoved["token"]]
    for jmeno in jmena[1:]:
        tokeny.append(c.post(f"/api/mistnosti/{kod}/pripojit",
                             json={"jmeno": jmeno}).json()["token"])
    return kod, tokeny


def posledni_stav(ws):
    zprava = ws.receive_json()
    assert zprava["typ"] == "stav", zprava
    return zprava["stav"]


def test_lobby_a_start(slozka):
    c = klient(slozka)
    kod, tokeny = zaloz_hru(c, ["Matouš", "Šárinka"])

    duplicitni = c.post(f"/api/mistnosti/{kod}/pripojit", json={"jmeno": "matouš"})
    assert duplicitni.status_code == 409
    assert c.post("/api/mistnosti/XXXX/pripojit",
                  json={"jmeno": "a"}).status_code == 404

    with c.websocket_connect(f"/ws/{kod}?token={tokeny[1]}") as ws:
        stav = posledni_stav(ws)
        assert stav["ja"] == 1 and stav["hra"] is None
        ws.send_json({"akce": "start"})
        assert ws.receive_json()["typ"] == "chyba"

    with c.websocket_connect(f"/ws/{kod}?token={tokeny[0]}") as ws:
        posledni_stav(ws)
        ws.send_json({"akce": "start"})
        stav = posledni_stav(ws)
        assert stav["hra"]["faze"] == "tah"
        assert len(stav["hra"]["ruka"]) == 3

    assert c.post(f"/api/mistnosti/{kod}/pripojit",
                  json={"jmeno": "Nikola"}).status_code == 409


def test_cizi_token_neprojde(slozka):
    c = klient(slozka)
    kod, _ = zaloz_hru(c, ["A", "B"])
    with c.websocket_connect(f"/ws/{kod}?token=spatny") as ws:
        assert ws.receive_json()["typ"] == "neplatne"


def test_tah_a_ulozeni_po_restartu(slozka):
    c = klient(slozka)
    kod, tokeny = zaloz_hru(c, ["A", "B"])
    with c.websocket_connect(f"/ws/{kod}?token={tokeny[0]}") as ws:
        posledni_stav(ws)
        ws.send_json({"akce": "start"})
        posledni_stav(ws)
        ws.send_json({"akce": "vyloz", "karta": 0, "sloupec": 1})
        stav = posledni_stav(ws)
        assert stav["hra"]["plocha"][0][1]["hrac"] == 0
        ws.send_json({"akce": "vyloz", "karta": 0, "sloupec": 1})
        assert ws.receive_json()["typ"] == "chyba"
        ws.send_json({"akce": "nesmysl"})
        assert ws.receive_json()["typ"] == "chyba"

    # novy server nad stejnymi daty
    c2 = klient(slozka)
    with c2.websocket_connect(f"/ws/{kod}?token={tokeny[1]}") as ws:
        stav = posledni_stav(ws)
        assert stav["hra"]["na_tahu"] == 1
        pole = stav["hra"]["plocha"][0][1]
        assert pole["hrac"] == 0 and pole["karta"] is None


def test_opusteni_lobby(slozka):
    c = klient(slozka)
    kod, tokeny = zaloz_hru(c, ["A", "B"])
    with c.websocket_connect(f"/ws/{kod}?token={tokeny[0]}") as ws:
        posledni_stav(ws)
        ws.send_json({"akce": "opustit"})
    with c.websocket_connect(f"/ws/{kod}?token={tokeny[1]}") as ws:
        stav = posledni_stav(ws)
        assert stav["ja"] == 0 and stav["zakladatel"]
        assert [h["jmeno"] for h in stav["hraci"]] == ["B"]
        ws.send_json({"akce": "opustit"})
    assert kod not in c.app.state.uloziste.mistnosti


def test_katalog_a_index(slozka):
    c = klient(slozka)
    assert "Král" in c.get("/api/katalog").json()["karty"]
    assert c.get("/").status_code == 200
    assert c.get("/api/sal-slavy").json() == []
