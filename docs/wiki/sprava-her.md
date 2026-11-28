# Správa her

Co dělat, když se hra zasekne nebo se někdo nemůže vrátit. Po dokončení úkolů M1 se většina řeší v aplikaci. Do té doby pomůže jen zásah na serveru.

## Zaseknutá hra (hráč chybí a nevrátí se)
**Po KR-018:** zakladatel klikne *Ukončit hru* a potvrdí. Hra se smaže a do Sálu slávy se nezapíše.

**Do té doby (na serveru):**
```bash
cd /srv/projects/kralovske_rosady
docker compose stop                         # server drží stav v paměti, soubor smaž jen při zastaveném
rm data/mistnosti/<KOD>.json                # KOD = kód hry z lobby, velkými písmeny
docker compose start
```
Smazání je nevratné. Hráčům zůstane hra v *Moje hry*, po kliknutí dostanou „Do této hry nepatříš nebo už neexistuje.“ a hra ze seznamu zmizí.

## Hráč se nemůže vrátit
- **Stejné zařízení a prohlížeč:** stačí otevřít stránku a v *Moje hry* kliknout *Pokračovat*. Web se po výpadku Wi-Fi připojuje sám.
- **Jiné zařízení nebo smazaná data prohlížeče:**
  - **Po KR-008:** zakladatel u hráče klikne *Vydat návratový odkaz* a pošle ho. Odkaz platí 24 hodin a jen jednou. Starý klíč hráče přestane platit.
  - **Do té doby:** návrat nejde. Hru je potřeba ukončit (viz výše).
- Tlačítko ✕ v *Moje hry* smaže klíč bez potvrzení. Po KR-008 ho vrátí návratový odkaz.

## Zakladatel chybí nebo ztratil zařízení
**Po KR-019:**
- Když zakladatel nemá spojení déle než 10 minut, kterýkoli hráč klikne *Převzít roli zakladatele*.
- Nový zakladatel pak může původnímu vydat návratový odkaz.
- Zakladatel, který odchází, může roli předat sám.

**Do té doby:** ukončit hru na serveru (viz výše).

## Sál slávy
- Soubor `data/sal_slavy.json` je pole záznamů `{datum, poradi: [{jmeno, body}]}`. Datum je v UTC.
- **Sloučení jmen** („Matouš“ a „Matous“ jsou pro hru dva hráči) nebo smazání záznamu: zastavit kontejner, opravit JSON v editoru a ověřit, že je platný. Pak kontejner spustit.
  ```bash
  docker compose stop
  cp data/sal_slavy.json data/sal_slavy.json.puvodni      # pro jistotu
  nano data/sal_slavy.json
  python3 -m json.tool data/sal_slavy.json > /dev/null && echo OK
  docker compose start
  ```
  Kopii `.puvodni` po kontrole na webu smaž. Data se nezálohují, takže je to jediná pojistka.
- Nedohrané a ukončené hry se do Sálu slávy nezapisují.
