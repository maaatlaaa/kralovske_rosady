# kralovske_rosady

Královské rošády jsou karetní hra, která se před lety přestala prodávat. Projekt z ní dělá digitální verzi pro rodinu a přátele, která se má hrát stejně příjemně jako originál.

Hra běží jako webová aplikace na domácím serveru a hráči se připojují z prohlížeče v tailnetu. Nic se neinstaluje a každý vidí jen svoje karty v ruce. Hraje se na počítači nebo tabletu. Mobil zatím vyladěný není: při 4–6 hráčích jsou karty na úzkém displeji malé.

- Brief projektu (cíl, publikum, priority, rozhodnutí): [docs/PROJEKT.md](docs/PROJEKT.md)
- Zadání (role, scénáře, API, protokol, formát dat): [docs/SPECIFIKACE.md](docs/SPECIFIKACE.md), architektura: [docs/ARCHITEKTURA.md](docs/ARCHITEKTURA.md)
- Provoz (nasazení, správa her, testování): [docs/wiki/](docs/wiki/README.md)
- Pravidla pro práci v repozitáři: [CLAUDE.md](CLAUDE.md)

## Spuštění na serveru (Docker)

```bash
cd /srv/projects/kralovske_rosady
docker compose up -d --build
```

- Kontejner poslouchá jen na `127.0.0.1:8000`. Ven ho pustí `tailscale serve` a hráči otevřou `http://server:8000`. Celý postup včetně aktualizace je v [docs/wiki/nasazeni.md](docs/wiki/nasazeni.md).
- Zmenšené obrázky pro web se připraví už při sestavení obrazu (`Dockerfile`).
- Rozehrané hry a Sál slávy se ukládají do `data/` vedle `docker-compose.yml`, takže restart ani aktualizace hru nepřeruší. Zálohy se nedělají.

## Přístup pro rodinu přes Tailscale

1. Na zařízeních hráčů musí běžet [Tailscale](https://tailscale.com/download) ve stejném tailnetu jako server. Kdo má vlastní účet Tailscale, tomu jde server nasdílet (administrace Tailscale: *Machines → server → Share*).
2. Hráči otevřou `http://server:8000`.
3. Do internetu se nic neotevírá a HTTPS certifikáty tailnetu se nezapínají (rozhodnutí 2026-11-28).

## Jak se hraje online

1. Jeden hráč zadá jméno a klikne na **Založit novou hru**. Dostane čtyřpísmenný kód.
2. Ostatním pošle odkaz (tlačítko *Zkopírovat odkaz pro ostatní*) nebo kód. Ti zadají jméno a připojí se.
3. Zakladatel spustí hru (2–6 hráčů).
4. Kdo je na tahu, klepne na kartu v ruce a pak na sloupec.
5. Po každém kole se zobrazí výsledky a hráči kliknou na *Pokračovat*. Zakladatel může pokračovat za všechny (když třeba babička odběhla od stolu).

Prohlížeč si pamatuje, do kterých her patříš. Po zavření okna nebo výpadku Wi-Fi se stačí vrátit na stránku a vybrat hru v seznamu **Moje hry**. Co dělat se zaseknutou hrou: [docs/wiki/sprava-her.md](docs/wiki/sprava-her.md).

## Vývoj bez Dockeru

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn rosady.server:vytvor_aplikaci --factory --reload --port 8000
```

Při prvním spuštění se z obrázků v `zdroje/obrazky/karty_podklady` a z pozadí připraví zmenšené WebP verze do `data/obrazky`. Trvá to asi 20 sekund, pak se už jen používají.

## Testy

- Lokálně: `python -m pytest`.
- Na serveru (repozitář `self_hosting`): `server/testing/test.sh kralovske_rosady staging`. Worker orchestrátoru spouští `run-tests`.
- Ruční checklist partie: [docs/wiki/testovani.md](docs/wiki/testovani.md).

## Licence a původ podkladů

- Repozitář je soukromý a **záměrně bez licence**: jde o digitální verzi vydané hry pod jejím názvem a s jejími pravidly. Zveřejnění repa, hry nebo grafiky je samostatné rozhodnutí Matouše.
- Písma webu Grenze Gotisch a Alegreya mají licenci SIL OFL (`web/fonty/OFL-*.txt`).
- Ilustrace v `zdroje/obrazky/karty_podklady/`, obrázky v `zdroje/obrazky/karty/` a obrázky s motivem obálky (`main_cz*`, `pozadi_*`) **nemají doloženou licenci**. Smí se používat jen pro soukromé hraní v tailnetu. Pozadí s motivem obálky se z webu odstraní (úkol KR-013) a nová grafika vznikne s doloženou licencí (milník M2).
- Font `zdroje/fonty/Canterbury.ttf` nemá doloženou licenci. Používá ho jen starý `generovani_karet.py`, web ne.
- Nové ilustrace se generují jen modely s licencí Apache 2.0 (`POVOLENE_MODELY` v `generovani_ilustraci.py`).

## Struktura

| Cesta | Co obsahuje |
|---|---|
| `rosady/karty.py` | definice karet, hodnoty a popisy schopností |
| `rosady/engine.py` | pravidla hry – bez jakéhokoli vstupu/výstupu, dá se testovat |
| `rosady/server.py` | FastAPI server, místnosti, WebSockety, ukládání do `data/` |
| `rosady/obrazky.py` | zmenšení obrázků karet pro web |
| `web/` | webové rozhraní (čisté HTML/CSS/JS, bez sestavování) |
| `tests/` | testy pravidel a serveru |
| `web/fonty/` | písma Grenze Gotisch a Alegreya (licence OFL, plná čeština) |
| `generovani_karet.py` | skript, který vygeneroval původní obrázky karet (`zdroje/obrazky/karty`) |
| `puvodni_pygame/` | původní verze s pygame a ovládáním přes terminál |

## Vzhled karet

Karty se kreslí v prohlížeči (`web/app.js` – funkce `karta`, `rubKarty`, `cilovaKarta`, styly v `web/style.css`).
Z obrázků se berou jen ilustrace a symboly kategorií ze `zdroje/obrazky/karty_podklady`; rámeček, název,
hodnota a text schopnosti jsou kód. Krátké texty na kartách jsou v `rosady/karty.py` (`kratky`, `kdy`),
takže změna textu nevyžaduje generování obrázků. Výměna ilustrace = nahradit PNG v `karty_podklady`.

- **Medailon vlevo nahoře** – hodnota karty, **vpravo** u specialistů symbol kategorie s bonusem 12.
- **Štítek nad textem** – kdy schopnost platí: červený *Po otočení*, modrý *Na konci kola*.
- **Barva vnitřního rámečku** a rub karty – barva hráče.
- Název a hodnota jsou nahoře, takže zůstanou vidět i v dlouhých sloupcích, kde se karty překrývají.

## Pravidla

Hra je česká verze hry **Ruse & Bruise** (později **Gambit Royale**, Rio Grande Games).
Pravidla jsou naprogramovaná podle originálu (zdroj: [recenze a pravidla na Geeky Hobbies](https://www.geekyhobbies.com/ruse-and-bruise-card-game-review-and-rules/)):

- V každém kole leží na stole tolik cílových karet, kolik je hráčů. Sloupce nemají pevnou délku –
  kartu lze vyložit na konec libovolného sloupce, i když už má karet dost.
- Kolo **okamžitě končí**, jakmile má každý sloupec aspoň tolik karet, jaká je hodnota jeho cílové karty.
  Sloupec uzavřený **Bouří** se počítá jako splněný a nelze do něj nic dalšího vyložit.
- Karta vyložená pod zakrytou kartu ji otočí. Okamžité akce: **Mordýř** zabije kartu vyloženou pod něj,
  **Objevitel** se přesune lícem dolů na konec dalšího sloupce vpravo (a otočí kartu nad sebou),
  **Převlek** dovolí vlastníkovi skrytě vložit pod něj kartu z ruky, **Zrádce** vymění cílovou kartu
  svého sloupce za cílovou kartu jiného sloupce.
- Na konci kola se všechny karty odkryjí bez okamžitých akcí. Pak platí v tomto pořadí:
  **Mušketýři** (zruší všechny schopnosti ve sloupci), **Mág** (odstraní karty s hodnotou 10+),
  **Čarodějnice** (odstraní karty s hodnotou 9 a méně kromě sebe), **Princ + Panoš** (automatická výhra).
- Dva **Mágové** (nebo dvě **Čarodějnice**) ve stejném sloupci se navzájem zruší.
- **Poustevník** −1 a **Paleček** +3 za každou další kartu ve sloupci, **Dvojník** převezme hodnotu karty
  těsně pod sebou (bez ní nemá žádnou hodnotu), **Romeo** s Julií má 15, **Drak** ubere 2 body každé
  kartě soupeřů (ne pod 0).
- Remízu vyhrává hráč, jehož karta leží nejblíž cílové kartě; se **Žebrákem** (vyhrává nejnižší součet)
  naopak ten, jehož karta leží nejdál. Hráč, který má ve sloupci jen Dvojníka bez hodnoty, vyhrát nemůže.
- Vyložené karty jdou na konci kola na odhazovací balíček, který se zamíchá, až dojde dobírací.
- Pořadí hráčů plynule pokračuje i přes konec kola.

Co originální pravidla neříkají jednoznačně (snadno se upraví v `rosady/engine.py`):

- Mág a Čarodějnice posuzují hodnoty už se započtenými bonusy (specialisté 12, Romeo 15, Paleček, Dvojník).
  Po jejich zásahu se Paleček, Poustevník, Romeo a Dvojník přepočítají jen ze zbylých karet a teprve pak
  platí Drak.
- Mušketýři ruší i bonus specialistů (Alchymista, Šermíř, … mají jen 8).
- Objevitel přeskakuje sloupce uzavřené Bouří a během jednoho tahu může cestovat jen jednou
  (jinak by se několik Objevitelů mohlo posílat dokola donekonečna).
- Tři Mágové ve sloupci: dva se zruší a třetí platí (stejně Čarodějnice).
- První kolo začíná zakladatel hry.
