# kralovske_rosady

Královské rošády - karetní hra, která se před lety přestala prodávat. Tento projekt si klade za cíl o vytvoření digitální kopie, která se bude hrát stejně příjemně jako originální hra.

Hra běží jako webová aplikace na domácím serveru. Hráči se připojují z prohlížeče
(počítač, tablet i mobil) – nic se neinstaluje. Každý vidí jen svoje karty v ruce.

## Spuštění na serveru (Docker)

```bash
git clone https://github.com/maaatlaaa/kralovske_rosady.git
cd kralovske_rosady
docker compose up -d --build
```

Hra pak běží na portu **8000**. Rozehrané hry a Sál slávy se ukládají do složky
`data/` vedle `docker-compose.yml`, takže restart ani aktualizace hru nepřeruší.

Aktualizace na novou verzi:

```bash
git pull
docker compose up -d --build
```

## Přístup pro rodinu přes Tailscale

1. Na serveru i na zařízeních rodiny musí běžet [Tailscale](https://tailscale.com/download)
   a všichni musí být ve stejném tailnetu. Kdo má vlastní Tailscale účet, tomu
   můžeš server nasdílet (v administraci Tailscale: *Machines → server → Share*).
2. Hráči otevřou v prohlížeči `http://<jméno-serveru>:8000`, např.
   `http://homeserver:8000` (díky MagicDNS) nebo `http://100.x.y.z:8000`.
3. Volitelně HTTPS a hezčí adresa přes `tailscale serve` (na serveru):

   ```bash
   sudo tailscale serve --bg 8000
   ```

   Hra pak poběží na `https://<jméno-serveru>.<tailnet>.ts.net`. Tailscale vyřeší
   certifikát a funguje to i s WebSockety.

Port 8000 není potřeba otevírat do internetu – stačí, že je dostupný v tailnetu.
Pokud má server firewall, povol port 8000 alespoň na rozhraní `tailscale0`.

## Jak se hraje online

1. Jeden hráč zadá jméno a klikne na **Založit novou hru** – dostane čtyřpísmenný kód.
2. Ostatním pošle odkaz (tlačítko *Zkopírovat odkaz*) nebo kód. Ti zadají jméno a připojí se.
3. Zakladatel spustí hru (2–6 hráčů).
4. Kdo je na tahu, klepne na kartu v ruce a pak na sloupec.
5. Po každém kole se zobrazí výsledky a hráči kliknou na *Pokračovat*. Zakladatel může
   pokračovat za všechny (když třeba babička odběhla od stolu).

Prohlížeč si pamatuje, do kterých her patříš – po zavření okna nebo výpadku Wi-Fi se
stačí vrátit na stránku a vybrat hru v seznamu **Moje hry**.

## Vývoj bez Dockeru

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn rosady.server:vytvor_aplikaci --factory --reload --port 8000
python -m pytest
```

Při prvním spuštění se z obrázků v `zdroje/obrazky/karty` připraví zmenšené WebP verze
do `data/obrazky` (trvá to asi 20 sekund, pak už se jen používají).

## Struktura

| Cesta | Co obsahuje |
|---|---|
| `rosady/karty.py` | definice karet, hodnoty a popisy schopností |
| `rosady/engine.py` | pravidla hry – bez jakéhokoli vstupu/výstupu, dá se testovat |
| `rosady/server.py` | FastAPI server, místnosti, WebSockety, ukládání do `data/` |
| `rosady/obrazky.py` | zmenšení obrázků karet pro web |
| `web/` | webové rozhraní (čisté HTML/CSS/JS, bez sestavování) |
| `tests/` | testy pravidel a serveru |
| `generovani_karet.py` | skript, který vygeneroval obrázky karet |
| `puvodni_pygame/` | původní verze s pygame a ovládáním přes terminál |

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
- **Poustevník** −1 a **Paleček** +3 za každou další kartu ve sloupci, **Dvojník** převezme hodnotu karty
  těsně pod sebou, **Romeo** s Julií má 15, **Drak** ubere 2 body každé kartě soupeřů.
- Remízu vyhrává hráč, jehož karta leží nejblíž cílové kartě; se **Žebrákem** (vyhrává nejnižší součet)
  naopak ten, jehož karta leží nejdál.
- Pořadí hráčů plynule pokračuje i přes konec kola.

Co originální pravidla neříkají jednoznačně (snadno se upraví v `rosady/engine.py`):

- Mág a Čarodějnice posuzují hodnoty už se započtenými bonusy (specialisté 12, Romeo 15, Paleček, Dvojník).
  Po jejich zásahu se Paleček, Poustevník, Romeo a Dvojník přepočítají jen ze zbylých karet a teprve pak
  platí Drak.
- Mušketýři ruší i bonus specialistů (Alchymista, Šermíř, … mají jen 8).
- Objevitel přeskakuje sloupce uzavřené Bouří a během jednoho tahu může cestovat jen jednou
  (jinak by se několik Objevitelů mohlo posílat dokola donekonečna).
- První kolo začíná zakladatel hry.
