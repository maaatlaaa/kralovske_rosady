"""
Webový server Královských rošád.

Spuštění:  uvicorn rosady.server:vytvor_aplikaci --factory --host 0.0.0.0

Hráči se připojují přes prohlížeč. Každá hra má místnost s krátkým kódem,
hráč dostane tajný token (uložený v prohlížeči), díky kterému se může po
výpadku nebo zavření prohlížeče vrátit do hry. Stav místností se ukládá do
složky DATA_DIR, takže restart serveru hru nepřeruší.
"""

import json
import logging
import os
import secrets
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import obrazky
from .engine import KONEC, ChybaHry, Hra
from .karty import MAX_HRACU, MIN_HRACU, katalog

KOREN = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("DATA_DIR", KOREN / "data"))
OBRAZKY_DIR = Path(os.environ.get("OBRAZKY_DIR", KOREN / "data" / "obrazky"))
WEB_DIR = KOREN / "web"
# neaktivni mistnosti se po teto dobe smazou
MAX_STARI_MISTNOSTI = 14 * 24 * 3600

ZNAKY_KODU = "ABCDEFGHJKLMNPQRSTUVWXYZ"  # bez I a O, at se nepletou s 1 a 0

log = logging.getLogger("rosady")


class Mistnost:
    """mistnost s hraci; pred startem je hra None (lobby)"""

    def __init__(self, kod):
        self.kod = kod
        self.hraci = []          # [{"jmeno", "token"}]
        self.hra = None
        self.zapsano_do_salu = False
        self.zmeneno = time.time()
        self.spojeni = {}        # token -> set(WebSocket)

    def hrac_podle_tokenu(self, token):
        for i, hrac in enumerate(self.hraci):
            if secrets.compare_digest(hrac["token"], token or ""):
                return i
        return None

    def pohled(self, ja):
        zakladatel = ja == 0
        data = {
            "kod": self.kod,
            "ja": ja,
            "zakladatel": zakladatel,
            "hraci": [{"jmeno": h["jmeno"],
                       "pripojen": bool(self.spojeni.get(h["token"]))}
                      for h in self.hraci],
            "min_hracu": MIN_HRACU,
            "max_hracu": MAX_HRACU,
            "hra": self.hra.pohled(ja) if self.hra else None,
        }
        return data

    def do_slovniku(self):
        return {"kod": self.kod, "hraci": self.hraci, "zmeneno": self.zmeneno,
                "zapsano_do_salu": self.zapsano_do_salu,
                "hra": self.hra.do_slovniku() if self.hra else None}

    @classmethod
    def ze_slovniku(cls, data):
        mistnost = cls(data["kod"])
        mistnost.hraci = data["hraci"]
        mistnost.zmeneno = data["zmeneno"]
        mistnost.zapsano_do_salu = data.get("zapsano_do_salu", False)
        if data["hra"]:
            mistnost.hra = Hra.ze_slovniku(data["hra"])
        return mistnost


class Uloziste:
    """mistnosti v pameti + jejich ukladani do JSON souboru"""

    def __init__(self, slozka):
        self.slozka = Path(slozka)
        self.slozka_mistnosti = self.slozka / "mistnosti"
        self.soubor_salu = self.slozka / "sal_slavy.json"
        self.slozka_mistnosti.mkdir(parents=True, exist_ok=True)
        self.mistnosti = {}
        self._nacti()

    def _nacti(self):
        for soubor in self.slozka_mistnosti.glob("*.json"):
            try:
                mistnost = Mistnost.ze_slovniku(json.loads(soubor.read_text("utf-8")))
            except (ValueError, KeyError) as chyba:
                log.warning("nelze nacist %s: %s", soubor, chyba)
                continue
            if time.time() - mistnost.zmeneno > MAX_STARI_MISTNOSTI:
                soubor.unlink()
                continue
            self.mistnosti[mistnost.kod] = mistnost

    def nova_mistnost(self):
        while True:
            kod = "".join(secrets.choice(ZNAKY_KODU) for _ in range(4))
            if kod not in self.mistnosti:
                break
        mistnost = Mistnost(kod)
        self.mistnosti[kod] = mistnost
        return mistnost

    def uloz(self, mistnost):
        mistnost.zmeneno = time.time()
        soubor = self.slozka_mistnosti / f"{mistnost.kod}.json"
        docasny = soubor.with_suffix(".tmp")
        docasny.write_text(json.dumps(mistnost.do_slovniku(), ensure_ascii=False),
                           "utf-8")
        docasny.replace(soubor)
        if (mistnost.hra and mistnost.hra.faze == KONEC
                and not mistnost.zapsano_do_salu):
            self._zapis_do_salu(mistnost)

    def smaz(self, mistnost):
        self.mistnosti.pop(mistnost.kod, None)
        (self.slozka_mistnosti / f"{mistnost.kod}.json").unlink(missing_ok=True)

    def sal_slavy(self):
        if not self.soubor_salu.exists():
            return []
        return json.loads(self.soubor_salu.read_text("utf-8"))

    def _zapis_do_salu(self, mistnost):
        hra = mistnost.hra
        zaznamy = self.sal_slavy()
        zaznamy.append({
            "datum": time.strftime("%Y-%m-%d %H:%M"),
            "poradi": [{"jmeno": hra.hraci[p["hrac"]]["jmeno"],
                        "body": p["body"]} for p in hra.poradi],
        })
        self.soubor_salu.write_text(json.dumps(zaznamy, ensure_ascii=False,
                                               indent=1), "utf-8")
        mistnost.zapsano_do_salu = True
        soubor = self.slozka_mistnosti / f"{mistnost.kod}.json"
        soubor.write_text(json.dumps(mistnost.do_slovniku(), ensure_ascii=False),
                          "utf-8")


# ------------------------------------------------------------------ API

class Jmeno(BaseModel):
    jmeno: str = Field(min_length=1, max_length=20)


def ocisti_jmeno(jmeno):
    jmeno = " ".join(jmeno.split())
    if not jmeno:
        raise HTTPException(400, "Zadej jméno.")
    return jmeno


def vytvor_aplikaci(data_dir=DATA_DIR, obrazky_dir=OBRAZKY_DIR,
                    priprav_obrazky=True):
    if priprav_obrazky:
        obrazky.priprav(KOREN / "zdroje" / "obrazky", obrazky_dir)

    aplikace = FastAPI(title="Královské rošády")
    uloziste = Uloziste(data_dir)
    aplikace.state.uloziste = uloziste

    def najdi(kod):
        mistnost = uloziste.mistnosti.get(kod.upper())
        if mistnost is None:
            raise HTTPException(404, "Hra s tímto kódem neexistuje.")
        return mistnost

    async def rozesli(mistnost):
        """kazdemu pripojenemu hraci posle jeho pohled na hru"""
        for token, sokety in list(mistnost.spojeni.items()):
            ja = mistnost.hrac_podle_tokenu(token)
            zprava = {"typ": "stav", "stav": mistnost.pohled(ja)}
            for soket in list(sokety):
                try:
                    await soket.send_json(zprava)
                except Exception:  # pylint: disable=broad-except
                    sokety.discard(soket)

    @aplikace.get("/api/katalog")
    def api_katalog():
        return katalog()

    @aplikace.get("/api/sal-slavy")
    def api_sal_slavy():
        return uloziste.sal_slavy()

    @aplikace.post("/api/mistnosti")
    def zaloz(telo: Jmeno):
        mistnost = uloziste.nova_mistnost()
        token = secrets.token_urlsafe(16)
        mistnost.hraci.append({"jmeno": ocisti_jmeno(telo.jmeno), "token": token})
        uloziste.uloz(mistnost)
        return {"kod": mistnost.kod, "token": token}

    @aplikace.post("/api/mistnosti/{kod}/pripojit")
    async def pripoj(kod: str, telo: Jmeno):
        mistnost = najdi(kod)
        jmeno = ocisti_jmeno(telo.jmeno)
        if mistnost.hra is not None:
            raise HTTPException(409, "Hra už začala.")
        if len(mistnost.hraci) >= MAX_HRACU:
            raise HTTPException(409, f"Hra je plná (max. {MAX_HRACU} hráčů).")
        if any(h["jmeno"].lower() == jmeno.lower() for h in mistnost.hraci):
            raise HTTPException(409, "Hráč s tímto jménem už ve hře je.")
        token = secrets.token_urlsafe(16)
        mistnost.hraci.append({"jmeno": jmeno, "token": token})
        uloziste.uloz(mistnost)
        await rozesli(mistnost)
        return {"kod": mistnost.kod, "token": token}

    async def proved(mistnost, ja, zprava):
        """provede akci hrace; vraci True, pokud hrac mistnost opustil"""
        akce = zprava.get("akce")
        hra = mistnost.hra
        if akce == "start":
            if ja != 0:
                raise ChybaHry("Hru může spustit jen ten, kdo ji založil.")
            if hra is not None:
                raise ChybaHry("Hra už běží.")
            mistnost.hra = Hra([h["jmeno"] for h in mistnost.hraci])
        elif akce == "opustit":
            if hra is not None:
                raise ChybaHry("Rozehranou hru nelze opustit.")
            token = mistnost.hraci[ja]["token"]
            del mistnost.hraci[ja]
            for soket in mistnost.spojeni.pop(token, set()):
                await soket.close()
            if mistnost.hraci:
                uloziste.uloz(mistnost)
            else:
                uloziste.smaz(mistnost)
            return True
        elif hra is None:
            raise ChybaHry("Hra ještě nezačala.")
        elif akce == "vyloz":
            hra.vyloz(ja, int(zprava["karta"]), int(zprava["sloupec"]))
        elif akce == "prevlek":
            karta = zprava.get("karta")
            hra.prevlek(ja, None if karta is None else int(karta))
        elif akce == "zradce":
            sloupec = zprava.get("sloupec")
            hra.zradce(ja, None if sloupec is None else int(sloupec))
        elif akce == "pokracovat":
            za_vsechny = bool(zprava.get("za_vsechny"))
            if za_vsechny and ja != 0:
                raise ChybaHry("Za všechny může pokračovat jen zakladatel.")
            hra.pokracovat(ja, za_vsechny)
        else:
            raise ChybaHry("Neznámá akce.")
        uloziste.uloz(mistnost)
        return False

    @aplikace.websocket("/ws/{kod}")
    async def soket(websocket: WebSocket, kod: str, token: str = ""):
        await websocket.accept()
        mistnost = uloziste.mistnosti.get(kod.upper())
        ja = mistnost.hrac_podle_tokenu(token) if mistnost else None
        if ja is None:
            await websocket.send_json({"typ": "neplatne",
                                       "zprava": "Do této hry nepatříš "
                                                 "nebo už neexistuje."})
            await websocket.close()
            return

        mistnost.spojeni.setdefault(token, set()).add(websocket)
        await rozesli(mistnost)
        try:
            while True:
                zprava = await websocket.receive_json()
                ja = mistnost.hrac_podle_tokenu(token)
                if ja is None:
                    break
                try:
                    odesel = await proved(mistnost, ja, zprava)
                except (ChybaHry, KeyError, TypeError, ValueError) as chyba:
                    text = str(chyba) if isinstance(chyba, ChybaHry) \
                        else "Neplatná akce."
                    await websocket.send_json({"typ": "chyba", "zprava": text})
                    continue
                if odesel:
                    break
                await rozesli(mistnost)
        except WebSocketDisconnect:
            pass
        finally:
            sokety = mistnost.spojeni.get(token)
            if sokety is not None:
                sokety.discard(websocket)
                if not sokety:
                    del mistnost.spojeni[token]
            if mistnost.kod in uloziste.mistnosti:
                await rozesli(mistnost)

    @aplikace.get("/health")
    def zdravi():
        return {"ok": True}

    aplikace.mount("/obrazky", StaticFiles(directory=obrazky_dir), name="obrazky")
    aplikace.mount("/fonty", StaticFiles(directory=KOREN / "zdroje" / "fonty"),
                   name="fonty")
    aplikace.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

    @aplikace.get("/")
    def index():
        return FileResponse(WEB_DIR / "index.html")

    return aplikace

