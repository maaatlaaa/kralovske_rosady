Stav: doplněno v Claude session s Matoušem (2026-11-28), popisuje `staging` v commitu `2311b24`

# kralovske_rosady: specifikace (zadání)

Co se staví. Worker podle ní pracuje a nic, co tu není, nedomýšlí. Brief (cíl, priority, rozhodnutí): [PROJEKT.md](PROJEKT.md). Moduly: [ARCHITEKTURA.md](ARCHITEKTURA.md).

**Značky:**
- **[kód]** platí dnes a vyplývá z kódu,
- **[test]** platí dnes a hlídá to test,
- **[KR-0xx]** se teprve staví v uvedeném úkolu milníku M1 (`_state/kralovske_rosady/TASKS.md`).

Hodnoty označené „návrh“ navrhla session. Změna je rozhodnutí Matouše.

## 1. Uživatelé a role
Účty ani hesla nejsou. Hráč se pozná podle **tokenu**: náhodný řetězec, který dostane při založení nebo připojení. Token si uloží prohlížeč (`localStorage`, klíč `rosady_hry`).

| Role | Kdo | Co smí |
|---|---|---|
| **Hráč** | kdo má platný token místnosti | vidět svou ruku a veřejný stav hry [kód] [test `test_pohled_skryva_cizi_karty`]; táhnout, jen když je na tahu [kód `Hra.vyloz`]; rozhodnout jen svůj Převlek nebo Zrádce [kód `_kontrola_volby`]; potvrdit výsledky kola za sebe [kód]; opustit lobby [kód] [test `test_opusteni_lobby`]; převzít roli zakladatele, když je zakladatel odpojený déle než 10 minut [KR-019] |
| **Zakladatel** | hráč, který místnost založil (dnes vždy hráč s indexem 0) | vše jako hráč a navíc: spustit hru [kód] [test `test_lobby_a_start`]; pokračovat po kole za všechny [kód]; odebrat hráče v lobby [KR-018]; ukončit hru v jakékoli fázi [KR-018]; předat roli jinému hráči [KR-019]; vydat návratový odkaz odpojenému hráči [KR-008] |
| **Správce** | Matouš na serveru | nasazení, úprava a mazání souborů v `data/` podle [wiki](wiki/README.md). V aplikaci žádnou roli nemá. |

- Zakladatel nemůže táhnout za jiné, vidět cizí ruku ani rozhodovat cizí Převlek a Zrádce.
- Když zakladatel opustí lobby, roli dostane hráč, který se připojil po něm [kód: role = index 0]. Po [KR-019] stejně: další hráč v pořadí.
- Engine umí pohled diváka (`Hra.pohled(None)`), server ho nepoužívá. Diváci nejsou v rozsahu.

## 2. Scénáře
Každý scénář: kdo, co udělá, co uvidí, co se uloží.

### Dnes (kód)
1. **Založení místnosti.**
   - Hráč zadá jméno a klikne **Založit novou hru**.
   - Server vytvoří místnost se čtyřpísmenným kódem a vrátí kód a token.
   - Prohlížeč uloží `{kód: {token, jmeno, datum}}` a otevře lobby (`/#KOD`).
   - Uloží se `data/mistnosti/KOD.json`.
2. **Připojení.**
   - Hráč otevře odkaz `/#KOD` (tlačítko *Zkopírovat odkaz pro ostatní*) nebo zadá kód, pak jméno a **Připojit se**.
   - Server ho přidá na konec seznamu hráčů a všem pošle nový stav.
   - Připojení jde jen v lobby, do 6 hráčů a s jménem, které v místnosti ještě není (bez ohledu na velikost písmen).
3. **Start.** Zakladatel klikne **Spustit hru** (2–6 hráčů). Vznikne `Hra`, první táhne zakladatel. Všem přijde stav s rukou.
4. **Tah.**
   - Hráč na tahu klepne na kartu v ruce a pak na sloupec.
   - Okamžité schopnosti se provedou podle pravidel (§5). Převlek a Zrádce čekají na rozhodnutí vlastníka (fáze `volba`).
   - Po každé akci se stav uloží a rozešle všem.
5. **Konec kola.**
   - Kolo končí, když jsou splněné všechny sloupce. Všichni vidí výsledky sloupců a klikají **Pokračovat**.
   - Zakladatel může pokračovat za všechny. Nové kolo začne, až potvrdí všichni.
6. **Konec hry a Sál slávy.**
   - Po 6. kole ukáže web konečné pořadí.
   - Server zapíše jeden záznam do `data/sal_slavy.json` (jen jednou, příznak `zapsano_do_salu`).
   - Web na úvodní stránce ukazuje počty vítězství a odehrané hry (`GET /api/sal-slavy`).
7. **Návrat po výpadku na stejném zařízení.**
   - Při ztrátě spojení web ukáže pruh *odpojeno* a znovu se připojuje s prodlevou 1 s, zdvojovanou až na 15 s.
   - Po zavření okna hráč otevře stránku a v seznamu **Moje hry** klikne *Pokračovat*.
   - Server pozná hráče podle tokenu. Stav hry se po restartu serveru načte z `data/` [test `test_tah_a_ulozeni_po_restartu`].
8. **Opuštění lobby.** Hráč klikne *Opustit*. Server ho odebere, zavře jeho spojení a místnost bez hráčů smaže. Rozehranou hru opustit nejde.
9. **Neaktivní místnost.** Místnost, která se 14 dní nezměnila, se smaže při dalším startu serveru [kód `Uloziste._nacti`].

### Nově v M1
10. **Návrat z jiného zařízení** [KR-008].
    - Zakladatel u odpojeného hráče klikne **Vydat návratový odkaz** a pošle ho hráči.
    - Hráč odkaz otevře na libovolném zařízení a pokračuje se stejnou rukou, pořadím i body.
    - Starý token přestane platit a všichni v záznamu hry vidí, že zakladatel odkaz vydal.
11. **Odebrání hráče v lobby** [KR-018]. Zakladatel u hráče klikne ✕ a potvrdí. Odebranému se zavře spojení s hláškou a prohlížeč hru zapomene. Ostatní vidí nový seznam.
12. **Ukončení hry** [KR-018].
    - Zakladatel klikne **Ukončit hru** a potvrdí v dialogu.
    - Místnost se smaže a do Sálu slávy se nic nezapíše.
    - Všichni připojení dostanou hlášku „Zakladatel hru ukončil.“ a vrátí se na úvod.
13. **Předání a převzetí role zakladatele** [KR-019].
    - Zakladatel předá roli vybranému hráči.
    - Když zakladatel nemá žádné spojení déle než 10 minut, každý připojený hráč vidí **Převzít roli zakladatele**. Kdo klikne první, je zakladatel.
    - Nový zakladatel pak může původnímu vydat návratový odkaz. Tím se řeší zakladatel, který ztratil zařízení.
14. **Odkaz k ručnímu zkopírování** [KR-020]. Když prohlížeč nepovolí zápis do schránky (na `http://`), odkaz zůstane v poli, které jde označit a zkopírovat. Pole nezmizí po 4 s.

## 3. Datový model
Data jsou JSON soubory v `DATA_DIR` (výchozí `data/`, v Dockeru `/data`). Žádná databáze. Formát je kontrakt (PRAVIDLA §3.5). Nové pole se přidává s výchozí hodnotou pro starší soubory, nic se nepřejmenovává.

### 3.1 `data/mistnosti/<KOD>.json` (jedna místnost) [kód `Mistnost.do_slovniku`]
| Pole | Typ | Význam |
|---|---|---|
| `kod` | řetězec | 4 znaky z `ABCDEFGHJKLMNPQRSTUVWXYZ` (bez I a O), unikátní mezi místnostmi |
| `hraci` | pole `{jmeno, token}` | pořadí = index hráče (0 = zakladatel); `token` je `secrets.token_urlsafe(16)` |
| `zmeneno` | číslo | čas poslední změny (Unix, s) |
| `zapsano_do_salu` | bool | hra už je v Sálu slávy (chybí = `false`) |
| `hra` | `null` nebo objekt 3.2 | `null` = lobby |
| `zakladatel` | celé číslo | [KR-019] index zakladatele, chybí = 0 |
| `navraty` | objekt | [KR-008] `{"<index hráče>": {"hash": sha256 klíče hex, "plati_do": Unix s}}`, chybí = `{}`, pro hráče nejvýš jeden platný |

Zápis jde přes dočasný soubor `.tmp` a přejmenování [kód `Uloziste.uloz`].

### 3.2 Stav hry `hra` [kód `Hra.do_slovniku`]
| Pole | Typ | Význam |
|---|---|---|
| `hraci` | pole `{jmeno, balicek[], ruka[], odhozene[], cilove_karty[]}` | karty vlivu jako názvy z `karty.KARTY`, cílové karty jako `{kategorie, hodnota}` |
| `pocet` | celé číslo | počet hráčů = počet sloupců |
| `cilove_balicek` | pole `{kategorie, hodnota}` | zbylé cílové karty |
| `kolo` | celé číslo | od 0, hra má `POCET_KOL` = 6 |
| `hlavicka` | pole `{kategorie, hodnota}` | cílová karta každého sloupce |
| `sloupce` | pole polí `{karta, hrac, odkryta, pod_prevlekem}` | karty shora dolů; `pod_prevlekem` = název nebo `null` |
| `uzavrene` | pole bool | sloupec uzavřela Bouře |
| `na_tahu` | celé číslo | index hráče |
| `faze` | výčet | `tah`, `volba`, `vyhodnoceni`, `konec` |
| `volba` | `null` nebo `{typ, hrac, sloupec, index}` | `typ` je `prevlek` nebo `zradce` |
| `vysledky_kola` | pole | výsledek sloupce `{sloupec, karty[], poznamky[], soucty{hráč: body}, vitez, nejnizsi_vyhrava}` |
| `potvrdili` | pole indexů | kdo potvrdil výsledky kola |
| `zaznamy` | pole řetězců | průběh hry, nejvýš 200, hráčům se posílá posledních 50 |
| `poradi` | pole `{hrac, body}` | konečné pořadí (po `konec`) |

### 3.3 `data/sal_slavy.json` [kód `Uloziste._zapis_do_salu`]
Pole záznamů `{"datum": "RRRR-MM-DD HH:MM", "poradi": [{"jmeno", "body"}]}` v pořadí odehrání.
- Čas je čas kontejneru. Ten nemá nastavenou zónu, takže je zřejmě v UTC [kód: `Dockerfile` bez `TZ`].
- Hráči se poznají jen podle jména. Při shodě bodů vítězí všichni se shodou.
- Zápis je dnes přímý, ne přes dočasný soubor. Atomický zápis řeší [KR-021].

### 3.4 Prohlížeč (`localStorage`) [kód `web/app.js`]
- `rosady_hry`: `{KOD: {token, jmeno, datum}}`.
- `rosady_jmeno`: naposledy zadané jméno.

## 4. Rozhraní
### 4.1 Obrazovky (`web/index.html`, `web/app.js`)
- **Úvod:** jméno, založení, připojení kódem, **Moje hry**, *Sál slávy* a *Pravidla a karty* (dialogy).
- **Lobby:** kód, seznam hráčů s příznakem připojení, *Zkopírovat odkaz pro ostatní*, *Spustit hru* (zakladatel), *Opustit*.
- **Hra:** cílové karty a sloupce, ruka, rozhodnutí o Převleku a Zrádci, výsledky kola, konečné pořadí, záznam průběhu, hráči s body. Detail karty klepnutím.
- Upozornění na tah: text a tečka v titulku stránky.
- Texty jsou česky a tykají (brief, Tón).

### 4.2 REST API [kód `vytvor_aplikaci`]
Chyby vrací `{"detail": "<text pro hráče>"}`. Chyba validace těla (FastAPI 422) má `detail` jako pole a web pak ukáže „Něco se nepovedlo.“.

| Metoda a cesta | Tělo | Odpověď | Chyby |
|---|---|---|---|
| `GET /api/katalog` | – | `{karty: {název: {soubor, hodnota, kdy, kratky, popis}}, kategorie: {název: {barva, soubor, specialista}}, barvy: [{nazev, hex, popis}], bonus_specialisty}` | – |
| `GET /api/sal-slavy` | – | pole záznamů 3.3 | – |
| `POST /api/mistnosti` | `{jmeno}` | `{kod, token}` | 400 prázdné jméno, 422 délka; [KR-016] 503 při plném serveru |
| `POST /api/mistnosti/{kod}/pripojit` | `{jmeno}` | `{kod, token}`, všem se rozešle stav | 404 kód neexistuje, 409 hra začala / plno / jméno je obsazené, 400, 422 |
| `POST /api/mistnosti/{kod}/navrat` | `{klic}` | [KR-008] `{kod, token, jmeno}` | 404 „Odkaz neplatí. Požádej zakladatele o nový.“ |
| `GET /health` | – | `{"ok": true}` (Docker `HEALTHCHECK`) | – |
| `GET /` | – | `web/index.html` | – |
| `GET /static/…` | – | soubory z `web/` | – |
| `GET /obrazky/…` | – | `ilustrace/<soubor>.webp`, `znaky/<soubor>.webp`, `pozadi.webp` z `OBRAZKY_DIR` | – |

- Kód místnosti se v cestě porovnává bez ohledu na velikost písmen.
- Jméno se ořízne a vnitřní mezery se sloučí. Musí mít 1–20 znaků. [KR-016] navíc odstraní řídicí a neviditelné znaky (Unicode Cc a Cf).

### 4.3 WebSocket `/ws/{kod}?token=<token>` [kód `soket`, `proved`]
**Připojení:**
- Neznámá místnost nebo cizí token: server pošle `{"typ": "neplatne", "zprava": …}` a zavře spojení [test `test_cizi_token_neprojde`]. Web hru zapomene a vrátí se na úvod.
- Platný token: spojení se přidá k hráči (víc zařízení najednou jde) a všem se rozešle stav.

**Zprávy serveru:**
| `typ` | Obsah | Kdy |
|---|---|---|
| `stav` | `stav`: pohled 4.4 pro adresáta | po připojení, odpojení a každé úspěšné akci, všem připojeným |
| `chyba` | `zprava`: text pro hráče | jen odesílateli neplatné akce; spojení zůstává [test `test_neplatna_zprava_neshodi_spojeni`] |
| `neplatne` | `zprava` | token neplatí; [KR-018] odebrání, ukončení hry; [KR-008] starý token po návratu |
| `navrat` | [KR-008] `hrac`, `odkaz` | jen zakladateli po vydání odkazu |

**Zprávy klienta:** JSON objekt s polem `akce`. Jiný tvar nebo nevalidní JSON vrátí `chyba` „Neplatná akce.“.

| `akce` | Pole | Kdo a kdy |
|---|---|---|
| `start` | – | zakladatel, lobby, 2–6 hráčů |
| `opustit` | – | kdokoli, jen lobby; zavře jeho spojení |
| `vyloz` | `karta` (index v ruce), `sloupec` | hráč na tahu, fáze `tah`, sloupec není uzavřený |
| `prevlek` | `karta` (index) nebo `null` | vlastník otočeného Převleku, fáze `volba` |
| `zradce` | `sloupec` (jiný než vlastní) nebo `null` | vlastník otočeného Zrádce, fáze `volba` |
| `pokracovat` | `za_vsechny` (bool) | kdokoli za sebe ve fázi `vyhodnoceni`; `za_vsechny` jen zakladatel |
| `odebrat` | `hrac` (index) | [KR-018] zakladatel, jen lobby, ne sám sebe |
| `ukoncit` | – | [KR-018] zakladatel, kdykoli |
| `predat` | `hrac` (index) | [KR-019] zakladatel, jiný hráč místnosti |
| `prevzit` | – | [KR-019] kdokoli, když zakladatel nemá spojení déle než 10 minut |
| `vydat_navrat` | `hrac` (index) | [KR-008] zakladatel, pro jiného hráče, který právě není připojený, jen rozehraná hra |

### 4.4 Pohled hráče (`stav`) [kód `Mistnost.pohled`, `Hra.pohled`]
- Místnost: `{kod, ja, zakladatel (bool: jsem zakladatel), hraci: [{jmeno, pripojen}], min_hracu, max_hracu, hra}`. [KR-019] přidá `zakladatel_index` a `lze_prevzit` (bool).
- `hra` je `null` (lobby), nebo pohled hry. Ten obsahuje:
  - `faze`, `kolo`, `pocet_kol`, `na_tahu`, `ja`,
  - `hraci` `[{jmeno, cilove_karty, skore}]`,
  - `hlavicka`, `sloupce`, `uzavrene`, `ruka`, `volba` `{typ, hrac, sloupec}`,
  - `vysledky_kola` (jen ve fázi `vyhodnoceni` a `konec`), `potvrdili`, `poradi`, `zaznamy` (posledních 50).
- **Co hráč nevidí:** zakrytou cizí kartu (`karta: null`), cizí kartu pod Převlekem do konce kola, cizí ruku a balíčky, tokeny.

### 4.5 Návratový odkaz [KR-008]
- Tvar `http://<adresa>/#KOD/<klic>`. Klíč je ve fragmentu, takže se neposílá na server ani do logů.
- Klíč: `secrets.token_urlsafe(16)`. Na serveru se ukládá jen jeho SHA-256. Platí 24 hodin (návrh) a jen jednou. Nové vydání pro stejného hráče zruší předchozí.
- Web po otevření zavolá `POST /api/mistnosti/{kod}/navrat`, uloží nový token a přejde na `/#KOD`.

## 5. Pravidla a výpočty
- **Pravidla hry** jsou kompletní a otestovaná. Zdroj pravdy jsou [README.md, oddíl Pravidla](../README.md#pravidla), `rosady/engine.py` a testy `tests/test_engine.py` a `tests/test_nejednoznacna_pravidla.py`. Tady se nepřepisují. Mapa pravidel na kód a testy je v [archiv/STAV-2026-11-26.md](archiv/STAV-2026-11-26.md) §3.
- Doplnění, která README neuvádí [kód]:
  - mají-li Prince i Panoše dva hráči, vyhrává karta z dvojice nejblíž cílové kartě,
  - při shodě bodů na konci hry vítězí všichni se shodou,
  - Poustevník nemá spodní hranici,
  - hráč bez karet v ruce se přeskakuje, a když nemá karty nikdo, kolo končí.
- **Konstanty** (`rosady/karty.py`, `rosady/engine.py`, `rosady/server.py`):
  - 2–6 hráčů, 6 kol, 3 karty v ruce, bonus specialisty 12,
  - kód místnosti má 4 znaky, místnost se smaže po 14 dnech nečinnosti,
  - jméno má 1–20 znaků.
- **Autorizace** (BEZPECNOST §5): server pro každou zprávu znovu najde hráče podle tokenu. Oprávnění kontroluje server, ne skrytím tlačítka. Kdo smí kterou akci, říká tabulka 4.3. Testy na odmítnutí [KR-017].
- **Escapování** (BEZPECNOST §1): jména hráčů a záznamy se ve webu vkládají jen jako text (`h()`, `textContent`). `innerHTML` se smí použít jen pro konstanty z kódu (dnes `KORUNA`) [kód]. Test [KR-017].

## 6. Nefunkční požadavky
- **Kde běží:**
  - trvalá instance z `main` v Dockeru na domácím serveru, port `127.0.0.1:8000`, ven `http://server:8000` přes `tailscale serve` jako ostatní služby, HTTPS certifikáty se nezapínají,
  - náhled ze `staging` v rozcestníku na portu 8204.

  Postup je ve [wiki/nasazeni.md](wiki/nasazeni.md).
- **Přístup:** jen tailnet. Žádné veřejné adresy ani Funnel.
- **Objem:** jednotky současně rozehraných her. Stav je v paměti procesu, proto běží jeden proces uvicornu (žádné workery navíc).
- **Limity** [KR-016] (BEZPECNOST §15, návrh hodnot):
  - zpráva WebSocketu nejvýš 4096 bajtů, delší dostane `chyba`,
  - nejvýš 50 místností najednou, další založení vrátí 503 „Na serveru je moc rozehraných her, zkus to později.“.
- **Logy** [KR-015] (BEZPECNOST §10, NALEZY N-012):
  - log neobsahuje tokeny, návratové klíče, IP adresy ani jména hráčů,
  - dnes uvicorn loguje `IP - "WebSocket /ws/KOD?token=…"` [spuštěno: uvicorn 0.55.0, `websockets_impl.py`], proto se jeho přístupový log vypne a aplikace loguje jen kód místnosti a událost.
- **Zálohy:** nedělají se (rozhodnutí 2026-11-28). Ztráta `data/` znamená ztrátu rozehraných her a Sálu slávy.
- **Osobní údaje:** jen jména, která hráči sami zadají. Žádné účty, e-maily, analytika ani cookies.
- **Prohlížeče:** současné prohlížeče na PC a tabletu. CSS používá `container-type`, `color-mix` a `<dialog>`, takže prohlížeč musí být zhruba z roku 2023 nebo novější (odhad). Mobil se zatím neladí.
- **Spolehlivost:** restart serveru hru nepřeruší. Poškozený soubor místnosti nesmí zabránit startu [KR-021].

## 7. Mimo rozsah
- Mobilní úpravy plochy (KR-009) a instalace na plochu (KR-010).
- AI protihráč a náhrada hráče botem, další sady karet, diváci.
- Veřejný přístup, účty, hesla, e-maily, HTTPS certifikáty tailnetu.
- Zálohy `data/`, mazání a úpravy Sálu slávy v aplikaci (dělá správce ručně, wiki).
- „Hrát znovu se stejnými lidmi“ (kandidát pro M3).
- Změny pravidel hry.

## 8. Akceptace
**Každý úkol:** `run-tests` projde a má testy podle sloupce „Kdo a kdy“ v tabulce 4.3. U nové akce to je povolený případ a každé odmítnutí.

**M1 je hotový, když:**
1. úkoly M1 jsou v `main`: KR-013, KR-011, KR-014 až KR-022, KR-008, KR-002, KR-005,
2. trvalá instance běží podle wiki a `GET /health` vrací `{"ok": true}`,
3. Matouš odehrál 2–3 partie na aspoň dvou zařízeních a prošel ruční checklist ([wiki/testovani.md](wiki/testovani.md)),
4. v logu kontejneru není token ani IP (`docker logs kralovske-rosady | grep -c token=` vrací 0).

## 9. Otevřené otázky
Žádná neblokuje. Neblokující otázky jsou v briefu (jména v Sálu slávy, platnost odkazu).
