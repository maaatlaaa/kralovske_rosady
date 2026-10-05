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

## Pravidla tak, jak jsou naprogramovaná

Většina pravidel je převzatá z původního `main.py`. Tam, kde původní kód
obsahoval chybu nebo nebyl jednoznačný, platí toto (snadno se upraví v `rosady/engine.py`):

- **Mordýř** má hodnotu 9,5 a opravdu se počítá (původně se neceločíselné hodnoty ignorovaly).
  Díky tomu na něj neplatí Mág (≥ 10) ani Čarodějnice (≤ 9).
- **Bouře** zablokuje *všechna* místa pod kartou, která ji otočila (původně zůstávalo volné poslední místo,
  takže se 3 hráči neměla Bouře žádný efekt).
- **Poustevník** ztrácí 1 bod za každou kartu pod sebou (původní vzorec `hodnota - hráči - řádek - 1`
  vypadal jako chybějící závorka).
- **Mág / Čarodějnice** fungují, když je ve sloupci alespoň jeden (původně jen když byl právě jeden).
  Jsou-li ve sloupci oba, platí jen Mág.
- **Dvojník** převezme hodnotu nejbližší karty pod sebou ještě před Mágem/Čarodějnicí; pod ním-li nic není, má 0.
- **Specialisté** (Alchymista, Šermíř, …) dostanou bonus 12 podle cílové karty sloupce při vyhodnocení –
  takže **Zrádce** jim prohozením cílových karet může bonus vzít nebo dát.
- Sloupec může vyhrát jen hráč, který v něm má aspoň jednu kartu. Se **Žebrákem** tedy nevyhraje
  hráč, který do sloupce nic nedal.
- Začínající hráč se každé kolo posouvá o jednoho dál.
- Karty v posledním řádku se při vyhodnocení jen odkryjí – jejich akce „po otočení“ se neprovádí
  (stejně jako v původní verzi).
