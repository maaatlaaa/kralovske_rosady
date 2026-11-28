Stav: doplněno v Claude session s Matoušem (2026-11-28), popisuje `staging` v commitu `2311b24`

# kralovske_rosady: architektura

Jak je systém rozdělený, aby šel rozšiřovat bez přepisování (PRAVIDLA-VYVOJE §3). Změna hranic modulu = úprava tabulky Moduly a nový záznam v oddílu Rozhodnutí.

## Stack
- Python 3.12, FastAPI a uvicorn (jeden proces), Pillow na přípravu obrázků.
- Data jsou JSON soubory v `DATA_DIR` (formát: SPECIFIKACE §3).
- Web je čisté HTML, CSS a JS bez sestavování a bez závislostí (`web/`).
- Běží v jednom Docker kontejneru (`Dockerfile`, `docker-compose.yml`) na domácím serveru, ven jen přes Tailscale.
- Testy: pytest a `fastapi.testclient` (`requirements-dev.txt`).

## Moduly
Závislosti jdou jedním směrem: `server` → (`mistnosti`, `uloziste`) → `engine` → `karty`. `obrazky` závisí jen na `karty`. Engine ani karty neznají server, soubory ani síť.

### Dnes [kód]
| Modul | Odpovědnost | Veřejné API | Data | Závisí na |
|---|---|---|---|---|
| `rosady/karty.py` | definice karet, kategorií, barev hráčů a konstant hry | `KARTY`, `KATEGORIE`, `SPECIALISTE`, `BARVY_HRACU`, `MIN_HRACU`, `MAX_HRACU`, `POCET_KOL`, `BONUS_SPECIALISTY`, `novy_balicek(rng)`, `nove_cilove_karty(rng)`, `katalog()` | konstanty v kódu | – |
| `rosady/engine.py` | pravidla hry, **bez vstupu a výstupu** | `Hra(jmena, rng=None)`; akce `vyloz`, `prevlek`, `zradce`, `pokracovat`; `pohled(ja)`, `skore(hrac)`, `splneny(sloupec)`, `do_slovniku()`, `Hra.ze_slovniku(data)`; fáze `TAH`, `VOLBA`, `VYHODNOCENI`, `KONEC`; výjimka `ChybaHry` (text pro hráče) | stav v objektu, náhoda přes předané `rng` | `karty` |
| `rosady/server.py` | dnes tři věci v jednom souboru (327 ř.): místnost (`Mistnost`), úložiště (`Uloziste`), HTTP a WebSocket (`vytvor_aplikaci`) | `vytvor_aplikaci(data_dir, obrazky_dir, priprav_obrazky)` → FastAPI; REST a WS podle SPECIFIKACE §4 | `data/mistnosti/*.json`, `data/sal_slavy.json` | `engine`, `karty`, `obrazky` |
| `rosady/obrazky.py` | zmenšení ilustrací, symbolů kategorií a pozadí na WebP; už hotové přeskočí | `priprav(zdroje, cil)` → počet nových obrázků; CLI `python -m rosady.obrazky [cil]` | čte `zdroje/obrazky/karty_podklady/`, píše `OBRAZKY_DIR` | `karty` |
| `web/app.js` | klient: směrování podle `#KOD`, REST, WebSocket, vykreslení | – (jeden skript) | `localStorage` (SPECIFIKACE §3.4) | REST a WS serveru |

Mimo běh aplikace (neměnit bez úkolu): `generovani_ilustraci.py` (Mac, Ollama, jen `POVOLENE_MODELY`), `generovani_karet.py` a `puvodni_pygame/` (historie).

### Cíl po refaktoringu KR-014 (před novými funkcemi M1)
`server.py` se rozdělí podle vrstev (PRAVIDLA §3.2 a §3.6: nejdřív refaktoring, pak rozšíření). Chování a API se nemění, testy musí projít beze změny.

| Modul | Vrstva | Odpovědnost | Veřejné API |
|---|---|---|---|
| `rosady/mistnosti.py` | service | místnost: hráči a jejich tokeny, role zakladatele, pravidla lobby, `pohled(ja)`, akce místnosti (`start`, `opustit`, později `odebrat`, `ukoncit`, `predat`, `prevzit`, návraty). Bez FastAPI a bez souborů, čas se předává. | `Mistnost`, `ChybaMistnosti` nebo `ChybaHry` |
| `rosady/uloziste.py` | repository | načtení, atomický zápis a mazání místností, Sál slávy, expirace | `Uloziste(slozka)`: `mistnosti`, `nova_mistnost()`, `uloz(m)`, `smaz(m)`, `sal_slavy()` |
| `rosady/server.py` | controller | přečte požadavek, najde hráče podle tokenu, zavolá místnost nebo hru, uloží, rozešle stav, převede výjimky na `chyba` | `vytvor_aplikaci(...)` |

Gateway (cizí služby) projekt nemá.

## Vrstvy
UI (`web/`) → controller (`server.py`) → service (`mistnosti.py`, `engine.py`) → repository (`uloziste.py`).
- Controller nesmí obsahovat pravidla hry ani pravidla místnosti. Dnešní kontroly „jen zakladatel“ v `proved()` se při KR-014 přesunou do `mistnosti.py`.
- Engine a místnost nesahají na soubory, síť, `time.time()` ani `random` bez předání (PRAVIDLA §3.8).
- Texty pro hráče vznikají ve výjimkách `ChybaHry` a v záznamech hry (`_zaznam`), tedy na více místech. PRAVIDLA §10 chtějí texty pohromadě. Zatím je to známý dluh, viz Rozhodnutí.

## Pokrytí obecných pokynů
Hra není portál. Z `self_hosting/docs/portaly/` platí principy z BEZPECNOST a z ZAKLAD jen oblasti, které hra má.

| Oblast | Platí? | Stav v projektu |
|---|---|---|
| BEZPECNOST §1 escapování | ano | web vkládá data jako text (`h()`, `textContent`) [kód], test KR-017 |
| BEZPECNOST §4 tokeny | ano, bez hesel | token hráče `token_urlsafe(16)`, porovnání `compare_digest` [kód]; návratový klíč s hashem, platností a jedním použitím KR-008; token s diakritikou KR-011 |
| BEZPECNOST §5 autorizace | ano | engine hlídá tah a volbu, server zakladatele [kód]; testy odmítnutí KR-017 |
| BEZPECNOST §10 logy | ano | dnes token a IP v přístupovém logu uvicornu → KR-015 |
| BEZPECNOST §13 závislosti | ano | verze nejsou pinované (`>=`) → KR-022 |
| BEZPECNOST §15 limity | ano | velikost zprávy WS, počet místností → KR-016 |
| BEZPECNOST §2, §3, §6, §7, §11 | ne | není SQL, formuláře s cookies, přesměrování, upload ani e-maily. CSRF nehrozí: identita je token v těle a URL, ne cookie. |
| ZAKLAD §2 role | ano, zjednodušeně | hráč, zakladatel (SPECIFIKACE §1) |
| ZAKLAD §12 chyby | částečně | hráč dostane text, ne výjimku [test `test_neplatna_zprava_neshodi_spojeni`] |
| ZAKLAD §16 logy | částečně | jen aplikační log bez osobních údajů (KR-015), žádný audit |
| ZAKLAD §17 limity | částečně | KR-016 |
| ZAKLAD §18 schéma | ano | JSON formát je kontrakt (SPECIFIKACE §3), změny jen přidáním pole s výchozí hodnotou |
| ZAKLAD §19 zálohy | rozhodnuto ne | brief 2026-11-28 |
| ZAKLAD §20 monitoring | minimum | `/health` a `HEALTHCHECK` v `Dockerfile` |
| ZAKLAD §22 staging | ano | náhled ze `staging` na portu 8204, wiki |
| ZAKLAD §1, 3–11, 13–15, 21 | ne | účty, administrace, e-maily, platby, SEO, překlady, cron ani SMS hra nemá |

## Rozšiřovací body
| Kde se čeká růst | Jak se přidává dnes | Kdy se změní |
|---|---|---|
| **Nová akce hráče** | větev v `proved()` (po KR-014 metoda `Mistnost` nebo `Hra`), řádek v SPECIFIKACE §4.3 a test povoleného i odmítnutého případu | – |
| **Nové pole v uloženém stavu** | přidat do `do_slovniku` / `ze_slovniku` s výchozí hodnotou pro starší soubory, popsat v SPECIFIKACE §3 | – |
| **Nové ilustrace** | nahradit PNG v `zdroje/obrazky/karty_podklady/` se stejným názvem (`soubor` v `KARTY`), licence zapsaná v README | M2 |
| **Texty na kartách** | `kratky`, `kdy`, `popis` v `karty.KARTY`, bez generování obrázků | – |
| **Nové sady karet** (mimo rozsah) | schopnosti jsou v kódu podle jmen: `_otoc` (okamžité: Objevitel, Mordýř, Bouře, Převlek, Zrádce), `_spocitej_hodnoty` (Poustevník, Paleček, Romeo, Dvojník, specialisté) a `_vyhodnot_sloupec` (Mušketýři, Mág, Čarodějnice, Princ a Panoš, Drak, Žebrák) | před první novou sadou refaktoring na registr schopností (název → obsluha otočení a vyhodnocení) s testy celé hry; teď ne (PRAVIDLA §3.4: obecnost „pro každý případ“ ne) |
| **AI protihráč** (mimo rozsah) | hráč se stejným API jako člověk: `Hra.pohled(ja)` dává jen to, co hráč smí vidět, a akce jdou přes `vyloz`/`prevlek`/`zradce`/`pokracovat`. `test_cela_hra_dobehne` už hraje náhodné platné tahy. | samostatný modul `rosady/bot.py` (strategie jako funkce `pohled → akce`) a spouštění tahu bota v serveru po rozeslání stavu; až po rozhodnutí (KR-023) |

## Rozhodnutí (ADR)
| Datum | Rozhodnutí | Proč | Zvažované varianty |
|---|---|---|---|
| 2026-10-05 (commit `9bd72f7`) | Webová hra: FastAPI a WebSockety, web bez sestavování, místo původní verze v pygame | hraje se z prohlížeče bez instalace, každý vidí jen svou ruku | pygame a terminál (`puvodni_pygame/`) |
| tamtéž | Engine bez vstupu a výstupu, server posílá každému jen jeho `pohled` | pravidla jdou testovat bez serveru, nikdo nevidí cizí karty | logika v serveru nebo v klientu |
| tamtéž | Data jako JSON soubory, stav v paměti jednoho procesu, zápis při každé akci | jednotky her, žádná databáze k provozu; restart hru nepřeruší | SQLite (zbytečné při tomto objemu) |
| tamtéž | Identita hráče = náhodný token v prohlížeči, bez účtů | rodina se nemá registrovat; token v souboru místnosti je čitelný jen správci serveru | účty a hesla (ZAKLAD §1, zbytečně těžké) |
| „Redesign karet: kresli se v prohlížeci“ | Karty kreslí prohlížeč, z obrázků se berou jen ilustrace a symboly | změna textu bez generování obrázků, menší data přes VPN | hotové obrázky karet (`generovani_karet.py`) |
| 2026-11-27 | Port jen na `127.0.0.1`, ven `tailscale serve` (commit `2311b24`) | ZASADY §3.4 | `8000:8000` na všech rozhraních |
| 2026-11-28 | Kód, komentáře a commity česky (výjimka z PRAVIDLA §10, Matouš) | pojmy hry jsou české, kód je česky od začátku | nový kód anglicky, přepis |
| 2026-11-28 | Před novými funkcemi M1 rozdělit `server.py` na `mistnosti`, `uloziste`, `server` (KR-014) | PRAVIDLA §3.2, §3.6; M1 přidá 5 akcí a soubor by přerostl 400 ř. | přidávat do `server.py` |
| 2026-11-28 | Token zůstává v URL WebSocketu, přístupový log uvicornu se vypne (KR-015) | nemění protokol ani klienta, řeší únik do logu | token v první zprávě (změna protokolu) |
| 2026-11-28 | Návratový klíč ve fragmentu URL, na serveru jen SHA-256, 24 h, jedno použití (KR-008) | BEZPECNOST §4; fragment se neposílá na server | klíč v query (skončí v logu) |
| 2026-11-28 | Texty pro hráče zůstávají ve výjimkách a záznamech (známý dluh vůči PRAVIDLA §10) | jen čeština, jeden jazyk; přesun by byl refaktoring bez užitku pro M1 | modul `texty.py` (až při překladu nebo velké změně textů) |
