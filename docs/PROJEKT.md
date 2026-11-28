Stav: doplněno v Claude session s Matoušem (2026-11-28)

# kralovske_rosady: brief projektu

Brief čte worker před každým úkolem a vedoucí podle něj odpovídá na otázky workerů místo Matouše. Co tu chybí, vedoucí předá Matoušovi.
Obecná pravidla: `self_hosting/docs/ZASADY.md` a `PRAVIDLA-VYVOJE.md`. Specifika repozitáře: [CLAUDE.md](../CLAUDE.md).

## Vize
Královské rošády jsou česká verze karetní hry Ruse & Bruise (Gambit Royale), která se přestala prodávat. Projekt z ní dělá webovou hru, kterou si rodina a přátelé zahrají z prohlížeče stejně příjemně jako s papírovými kartami: nic se neinstaluje a každý vidí jen svou ruku.

## Cíl a publikum
- **Pro koho:** Matouš, rodina a přátelé. Hráči nejsou technici (README: „když třeba babička odběhla od stolu“).
- **K čemu:** zahrát si celou partii pro 2–6 hráčů u jednoho stolu i na dálku, bez papírových karet a bez počítání bodů.
- **Kdo má přístup:** jen tailnet (ZASADY §3.4). Hosté potřebují Tailscale nebo sdílení stroje.
- **Veřejnost:** zatím ne. Rozhodne se později samostatně. Do té doby se architektura nemá zbytečně zavírat (např. žádné předpoklady „všichni jsou rodina“ v bezpečnosti), ale nic se pro veřejnost nestaví.

## MVP a mimo rozsah
- **Hotové jádro (stav 2026-11-28):**
  - kompletní pravidla s testy (90 testů prošlo na `staging`),
  - místnosti se čtyřpísmenným kódem, lobby, hra přes WebSocket,
  - ukládání rozehraných her, obnova po restartu, Sál slávy,
  - náhled ze `staging` v rozcestníku (port 8204).
- **Mimo rozsah teď:**
  - mobilní úpravy plochy a instalace na plochu (KR-009, KR-010 odloženy),
  - AI protihráč (jen návrh po partiích) a další sady karet,
  - veřejný přístup, uživatelské účty, hesla a e-maily,
  - zálohy `data/`,
  - nativní aplikace a PWA se service workerem.

## Co je „hotovo“
- **Nejbližší milník:** M1 „Rodinná partie“.
- **Hotovo znamená:**
  - úkoly M1 v `TASKS.md` jsou sloučené do `main`,
  - trvalá instance z `main` běží na `http://server:8000` (viz wiki),
  - odehrané 2–3 partie na více zařízeních.
- **Úspěch poznáme podle:** partie doběhnou bez zaseknutí a bez zásahu na serveru. Odpojený hráč se vrátí, zaseknutou hru ukončí zakladatel z aplikace.

Pro každý úkol vždy platí: prošly testy (`run-tests`) a jsou splněná kritéria z `TASKS.md` (PRAVIDLA-VYVOJE §7).

## Roadmapa
Nejbližší milník rozepisuje [SPECIFIKACE.md](SPECIFIKACE.md), kroky jsou úkoly v `_state/kralovske_rosady/TASKS.md`. Pořadí a obsah mění jen Matouš (zápis do tabulky Rozhodnutí).

| Milník | Obsah | Stav | Orientačně kdy |
|---|---|---|---|
| M1 | Rodinná partie: pozadí s motivem obálky pryč, bezpečnost a odolnost (logy, limity, návratový odkaz, správa hry zakladatelem), trvalá instance z `main`, 2–3 partie | rozpracovaný | neurčeno |
| M2 | Nová grafika s doloženou licencí (ilustrace karet, generuje Matouš na Macu) | čeká na M1 | neurčeno |
| M3 | Úpravy podle zkušeností z partií | později | po M1 |
| později | mobil (KR-009, KR-010), AI protihráč | odloženo | samostatné rozhodnutí |

## Priority
Při střetu cílů (schváleno 2026-11-28):
1. Bezpečnost a soukromí: nic veřejného, tokeny a IP mimo logy.
2. Neztratit data hry: rozehrané hry a Sál slávy.
3. Spolehlivá a pohodlná partie pro rodinu.
4. Jednoduchost: žádné účty ani hesla, malé kroky.
5. Nové funkce.

## Tón a styl textů pro uživatele
- Oslovení: **tykání** (ZASADY §9, interní hra pro rodinu).
- Tón: přátelský a krátký, jako u stolu („Nejsi na tahu.“, „Hra už začala.“). Názvy karet a pojmy podle README.
- Co nikdy: technické hlášky a výjimky hráčům, angličtina v rozhraní, výčitky.

## Tabu a hranice
Co vždy rozhoduje Matouš: ZASADY §4. Navíc pro tento projekt:
- Pravidla hry (README, oddíl Pravidla, a `rosady/engine.py`) se nemění bez rozhodnutí Matouše.
- Ilustrace a obrázky obálky bez doložené licence se nezveřejňují, nekopírují na nová místa a neposílají do externích služeb. Nová grafika jen s doloženou licencí.
- Nemazat `data/` trvalé instance ani podklady v `zdroje/`.
- Repo zůstává soukromé a bez licence. Zveřejnění repa, hry nebo grafiky je samostatné rozhodnutí.
- Žádné osobní údaje kromě jmen, která hráči sami zadají. Žádné účty, e-maily ani sledování.

## Technické konvence
Viz [CLAUDE.md](../CLAUDE.md) (příkazy, struktura, data, výjimka: kód a commity česky) a [ARCHITEKTURA.md](ARCHITEKTURA.md).

## Rozhodnutí
Novější rozhodnutí nahrazuje starší.

| Datum | Rozhodnutí | Zdroj |
|---|---|---|
| 2026-11-25 | Úkoly se po testech a validaci slučují automaticky do `staging`, do `main` slučuje jen Matouš | `_state/kralovske_rosady/config` |
| 2026-11-26 | Mobilní verze zatím nebude (KR-009, KR-010 odloženy) | Matouš, `TASKS.md`, ZASADY příloha |
| 2026-11-26 | R1 B: nová sada grafiky s doloženou licencí, do té doby stávající obrázky jen pro soukromé hraní; generuje se na Macu, ne worker | Matouš, `TASKS.md` (KR-003, KR-013), ZASADY příloha |
| 2026-11-26 | R2 A: trvalá instance běží z `main`, přístup přes Tailscale | Matouš, ZASADY příloha |
| 2026-11-26 | R3: návratový odkaz do rozehrané hry vydává zakladatel | Matouš, `TASKS.md` (KR-008), ZASADY příloha |
| 2026-11-27 | Texty pro hráče tykají (interní nástroj) | ZASADY §9 |
| 2026-11-27 | Úkoly mají řadu `KR`; worker nezačne, dokud povinné dokumenty nejsou kompletní (`require_brief`) | `_state/kralovske_rosady/config` |
| 2026-11-28 | Publikum: rodina a přátelé v tailnetu; veřejnost později samostatným rozhodnutím, architektura ji nemá zbytečně zavírat | Matouš (chat) |
| 2026-11-28 | Repo zůstává soukromé a záměrně bez licence (digitální verze vydané hry) | Matouš (chat) |
| 2026-11-28 | Grafika do výměny: stávající ilustrace zůstávají pro soukromé hraní, pozadí s motivem obálky pryč (KR-013); Canterbury mimo Docker obraz, ze zdrojů nemazat | Matouš (chat) |
| 2026-11-28 | Roadmapa: M1 Rodinná partie (bezpečnost, odolnost, správa hry zakladatelem, trvalá instance z main, 2–3 partie) → M2 nová grafika s licencí → M3 úpravy podle partií; mobil a AI později | Matouš (chat) |
| 2026-11-28 | Priority: bezpečnost a soukromí > data hry > spolehlivá a pohodlná partie > jednoduchost > nové funkce | Matouš (chat) |

## Otevřené otázky pro Matouše
Neblokují práci, vedoucí postupuje podle doporučení.
1. Jména v Sálu slávy: „Matouš“ a „Matous“ jsou dva hráči. Doporučení: zatím nechat, sloučení se dělá ručně podle wiki ([wiki/sprava-her.md](wiki/sprava-her.md)). Jiná varianta je pevný seznam hráčů v konfiguraci.
2. Platnost návratového odkazu (KR-008): doporučení 24 hodin a jen jedno použití.
