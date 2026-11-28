# kralovske_rosady

Královské rošády: digitální verze karetní hry pro rodinu a přátele. Pravidla jsou v Python enginu, server je FastAPI s WebSockety a web je čisté HTML/CSS/JS.

**Nejdřív čti [docs/PROJEKT.md](docs/PROJEKT.md)** (cíl, publikum, priority, hotovo, tón, rozhodnutí), pak [docs/SPECIFIKACE.md](docs/SPECIFIKACE.md) (co se staví, API, protokol, formát dat) a [docs/ARCHITEKTURA.md](docs/ARCHITEKTURA.md) (moduly a jejich API). Co v nich není, nedomýšlej: zeptej se.
Obecná pravidla platí pro všechny projekty: `/srv/projects/self_hosting/docs/ZASADY.md` (co a kdo rozhoduje) a `/srv/projects/self_hosting/docs/PRAVIDLA-VYVOJE.md` (jak psát kód). Tento soubor obsahuje jen to, co je specifické pro projekt.

## Stack a příkazy
- Python 3.12, FastAPI, uvicorn, Pillow (`requirements.txt`). Web bez sestavování (`web/`). Data jsou JSON soubory, žádná databáze.
- Testy:
  - `run-tests` (worker orchestrátoru),
  - na serveru `server/testing/test.sh kralovske_rosady <větev>` (repozitář `self_hosting`),
  - lokálně `python -m pytest`.
- Lokální spuštění: `uvicorn rosady.server:vytvor_aplikaci --factory --reload --port 8000` (viz README).
- Docker: `docker compose up -d --build`. Obrázky pro web se připraví při sestavení obrazu (`Dockerfile`, `python -m rosady.obrazky`).

## Struktura
| Cesta | Co obsahuje |
|---|---|
| `rosady/karty.py` | definice karet, kategorií a barev hráčů, `katalog()` pro web |
| `rosady/engine.py` | pravidla hry (`Hra`), bez vstupu a výstupu |
| `rosady/server.py` | FastAPI: místnosti, REST API, WebSocket, ukládání do `data/` |
| `rosady/obrazky.py` | zmenšení ilustrací a symbolů na WebP |
| `web/` | rozhraní (`index.html`, `app.js`, `style.css`, písma OFL) |
| `tests/` | `test_engine.py`, `test_nejednoznacna_pravidla.py`, `test_server.py` |
| `zdroje/` | podklady obrázků, prompty ilustrací, font Canterbury (starý generátor) |
| `generovani_ilustraci.py`, `ilustrace_navrhy/` | lokální generování nových ilustrací (Mac, Ollama) |
| `generovani_karet.py`, `puvodni_pygame/` | stará verze, web je nepoužívá; neměnit |

Moduly, jejich API a kam patří nový kód: [docs/ARCHITEKTURA.md](docs/ARCHITEKTURA.md).

## Data a tajemství
- Tajemství projekt nemá. Tokeny hráčů vznikají za běhu a leží jen v `data/mistnosti/*.json` a v prohlížeči hráče.
- `data/` (rozehrané hry a Sál slávy, formát ve SPECIFIKACE §3) není v gitu a nečte se do výstupu: obsahuje jména a tokeny hráčů.
- Testy pracují jen v `tmp_path` se syntetickými jmény, nikdy nad skutečnou složkou `data/`.
- Na serveru: trvalá instance `/srv/projects/kralovske_rosady/data/`, náhled má vlastní Docker volume (viz [docs/wiki/](docs/wiki/README.md)). Zálohy se nedělají (rozhodnutí v briefu).

## Grafika a cizí kód
- Ilustrace v `zdroje/obrazky/karty_podklady/` a obrázky obálky (`main_cz*`, `pozadi_*`) nemají doloženou licenci. Smí se používat jen pro soukromé hraní v tailnetu. Nic z nich se nezveřejňuje, nekopíruje do nových míst ani neposílá do externích služeb.
- Nová grafika jen s doloženou licencí. Generuje se na Macu (`generovani_ilustraci.py`, jen modely z `POVOLENE_MODELY`). Worker obrázky negeneruje.
- `puvodni_pygame/` a `generovani_karet.py` jsou historické a nemění se.
- Nové závislosti jen s permisivní licencí a s pinovanou verzí (PRAVIDLA §9).

## Prostředí, větve a nasazení
- `staging` je integrační větev (automatické sloučení po testech a validaci), `main` je stav trvalé instance a slučuje do ní jen Matouš.
- Náhled ze `staging`: rozcestník náhledů, port 8204 (`self_hosting/server/services/preview/projects.toml`).
- Trvalá instance z `main`: `docker compose up -d --build` v `/srv/projects/kralovske_rosady` a `tailscale serve`, viz [docs/wiki/nasazeni.md](docs/wiki/nasazeni.md). Nasazuje jen Matouš.
- Služba poslouchá jen na `127.0.0.1` (compose `127.0.0.1:8000:8000`), ven jen přes Tailscale.

## Konvence
- **Výjimka z PRAVIDLA-VYVOJE §10, schválená Matoušem 2026-11-28:** identifikátory, komentáře i commit zprávy jsou **česky**. Kód je česky od začátku a pojmy hry (karta, sloupec, kolo, zakladatel) jsou české, překlad by nic nepřinesl. Nový kód taky česky, ať se jazyky nemíchají.
- Texty pro hráče tykají (brief, oddíl Tón).
- Úkoly orchestrátoru `KR-xxx`, commit k úkolu začíná jeho ID (`KR-014: …`). Starší commity mají `T-xxx`.
- Změna chování popsaného ve SPECIFIKACE nebo README se v dokumentaci opraví ve stejné změně.
- Pravidla hry jsou v `README.md` (oddíl Pravidla) a v `rosady/engine.py`. Jejich změna vyžaduje rozhodnutí Matouše a test v `tests/`.
