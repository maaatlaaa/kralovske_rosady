# Nasazení a provoz

Stav 2026-11-28: trvalá instance zatím **neběží** (kontejner `kralovske-rosady` ani `data/` na serveru nejsou). Běží jen náhled ze `staging`. Nasazuje jen Matouš.

## Přehled
| Instance | Větev | Adresa | Data |
|---|---|---|---|
| trvalá | `main` | `http://server:8000` (tailnet) | `/srv/projects/kralovske_rosady/data/` |
| náhled | `staging` | `http://server.tail0a0509.ts.net:8204` (rozcestník) | Docker volume náhledu, oddělené od trvalé |

Obě běží ze stejného `docker-compose.yml`. Náhled k němu přidává `self_hosting/server/services/preview/projects/kralovske_rosady/override.yml` s jiným jménem kontejneru (`preview-kralovske-rosady`), portem 8204 a vlastním volume.

## První nasazení trvalé instance
Předpoklad: `main` obsahuje `ports: "127.0.0.1:8000:8000"` v `docker-compose.yml`. K 2026-11-28 to je jen ve `staging` (commit `2311b24`). S `8000:8000` by hra byla dostupná z celé domácí sítě (ZASADY §3.4).

```bash
ssh server
cd /srv/projects/kralovske_rosady
sudo -n -u matous -H git pull --ff-only          # main
grep -n 127.0.0.1:8000 docker-compose.yml         # musí najít řádek
docker compose up -d --build                      # obrázky se připraví při sestavení
curl -s http://127.0.0.1:8000/health              # {"ok":true}
sudo tailscale serve --bg --http=8000 http://127.0.0.1:8000
tailscale serve status | grep -A2 :8000
```

Hráči pak otevřou `http://server:8000` na zařízení v tailnetu. Kdo má vlastní účet Tailscale, tomu se server nasdílí (administrace Tailscale: *Machines → server → Share*). HTTPS certifikáty se nezapínají (rozhodnutí 2026-11-28), proto na `http://` nefunguje zápis odkazu do schránky (řeší KR-020).

Zapsat do `self_hosting/server/CHANGELOG.md`.

## Aktualizace
Až Matouš sloučí `staging` do `main`:
```bash
cd /srv/projects/kralovske_rosady
sudo -n -u matous -H git pull --ff-only
docker compose up -d --build
curl -s http://127.0.0.1:8000/health
```
Rozehrané hry přežijí: stav je v `data/` a po startu se načte. Hráčům se spojení na chvíli přeruší a web se sám připojí znovu.

## Vypnutí
```bash
docker compose down                      # data/ zůstane
sudo tailscale serve --http=8000 off
```

## Náhled ze staging
- Spouští a zastavuje se v rozcestníku na přehledu (`http://server:7100`). Popis je v `self_hosting/server/services/preview/README.md`.
- Hry v náhledu jsou jen na zkoušení. Úplný úklid včetně dat: `docker compose -p preview-kralovske_rosady down -v`.

## Logy
- `docker logs kralovske-rosady`.
- **Pozor do KR-015:** přístupový log uvicornu obsahuje IP hráčů a tokeny (`"WebSocket /ws/KOD?token=…"`). Log nikam nekopíruj, neposílej a nevkládej do chatu s LLM. Po KR-015 log obsahuje jen kód místnosti a událost.

## Data a zálohy
- `data/mistnosti/<KOD>.json` je jedna místnost (hráči a tokeny, stav hry), `data/sal_slavy.json` je Sál slávy. Formát popisuje SPECIFIKACE §3.
- Soubory obsahují jména a tokeny, proto se nečtou do výstupu a nepatří do gitu (`data/` je v `.gitignore`).
- **Zálohy se nedělají** (rozhodnutí 2026-11-28). Ztráta disku nebo smazání `data/` znamená ztrátu rozehraných her a Sálu slávy.
- Místnost, která se 14 dní nezměnila, server smaže při startu.
