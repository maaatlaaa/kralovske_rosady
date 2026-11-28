# Testování

## Automatické testy
- Worker: `run-tests`.
- Na serveru (repozitář `self_hosting`): `server/testing/test.sh kralovske_rosady staging` (nebo `main`). Běží pytest v Dockeru (`python:3.12-slim`) nad commitnutým stavem větve, trvá asi 15 s.
- Lokálně: `pip install -r requirements-dev.txt` a `python -m pytest`.
- Výsledek 2026-11-28 na `staging`: **90 prošlo**, 1 varování (`httpx` se Starlette `TestClient` je zastaralé).

| Soubor | Co hlídá |
|---|---|
| `tests/test_engine.py` | pravidla karet, vyhodnocení, skóre, 60 náhodných celých her včetně uložení a načtení |
| `tests/test_nejednoznacna_pravidla.py` | rozhodnutí, která originální pravidla neříkají (README) |
| `tests/test_server.py` | lobby, cizí token, tah, restart, neplatné zprávy, opuštění, katalog |

Nepokryté (stav 2026-11-28): web (`web/`), zápis do Sálu slávy a expirace (KR-002), Převlek, Zrádce a Pokračovat přes server, příprava obrázků, sestavení obrazu.

## Ruční checklist partie
Na náhledu ze `staging` před sloučením do `main`, nebo na trvalé instanci po aktualizaci. Aspoň dvě zařízení (PC a tablet nebo druhý prohlížeč v anonymním okně).

1. Založit hru, druhé zařízení se připojí odkazem i kódem. Duplicitní jméno je odmítnuté.
2. Spustit hru. Každý vidí jen svou ruku a cizí zakryté karty jako rub.
3. Odehrát tah na obou zařízeních a zkusit táhnout mimo pořadí (hláška „Nejsi na tahu.“).
4. Převlek a Zrádce: rozhodnutí vidí jen vlastník, ostatní čekají.
5. Konec kola: výsledky, *Pokračovat*, zakladatel pokračuje za všechny.
6. Vypnout Wi-Fi na jednom zařízení a zapnout: pruh *odpojeno*, pak se samo připojí.
7. Restart kontejneru během hry (`docker compose restart`): hra pokračuje.
8. Po dohrání je hra v Sálu slávy právě jednou.
9. Po M1 navíc: návratový odkaz na třetím zařízení, odebrání hráče v lobby, ukončení hry, předání a převzetí role zakladatele, odkaz k ručnímu zkopírování na `http://`.
10. Po KR-015: `docker logs kralovske-rosady 2>&1 | grep -c "token="` vrací 0.
