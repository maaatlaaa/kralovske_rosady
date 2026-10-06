"""Generování návrhů ilustrací karet lokálně přes Ollamu (REST API /api/generate).

Prompty se berou ze zdroje/obrazky/prompty_ilustraci.md: výsledný prompt =
základ + " Now: " + popis karty. Výstupy jdou do ilustrace_navrhy/<model>/<soubor>_seed<N>.png,
parametry každého obrázku do ilustrace_navrhy/log.json (jde podle nich zopakovat)
a náhledy do ilustrace_navrhy/prehled.html.

Generování obrázků má Ollama jen do verze 0.32.5 (v 0.32.6 bylo odstraněno).

Příklady:
    python3 generovani_ilustraci.py --model x/z-image-turbo --karty kral mag --seedy 1 2
    python3 generovani_ilustraci.py --model x/z-image-turbo            # všech 25 karet, seedy 1 2 3
    python3 generovani_ilustraci.py --jen-prehled
"""

import argparse
import base64
import html
import json
import os
import re
import shutil
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

KOREN = Path(__file__).resolve().parent
PROMPTY = KOREN / "zdroje" / "obrazky" / "prompty_ilustraci.md"
PODKLADY = KOREN / "zdroje" / "obrazky" / "karty_podklady"
NAVRHY = KOREN / "ilustrace_navrhy"
LOG = NAVRHY / "log.json"
PREHLED = NAVRHY / "prehled.html"
SROVNANI = Path.home() / "Downloads" / "kral_chatgpt.png"
OLLAMA = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
if not OLLAMA.startswith("http"):
    OLLAMA = "http://" + OLLAMA

# Jen modely s licencí Apache 2.0 (flux2-klein:9b má nekomerční licenci).
POVOLENE_MODELY = ("x/z-image-turbo", "x/flux2-klein:4b")
NAHRAZOVANY_TEXT = "single character centered"


def nacti_karty():
    """Vrátí (základní prompt, seznam karet) z prompty_ilustraci.md."""
    text = PROMPTY.read_text(encoding="utf-8")
    zaklad = re.search(r"## Základ.*?```\n(.*?)\n```", text, re.S).group(1).strip()
    karty = []
    for radek in text.splitlines():
        m = re.match(r"\|\s*([^|]+?)\s*\|\s*`([a-z0-9_]+)`\s*\|\s*(.+?)\s*\|\s*$", radek)
        if not m:
            continue
        nazev, soubor, popis = m.groups()
        zaklad_karty = zaklad
        poznamka = re.match(r"\*\(místo „single character centered“:\s*(.+?)\)\*\s*(.*)", popis)
        if poznamka:
            nahrada, popis = poznamka.groups()
            zaklad_karty = zaklad.replace(NAHRAZOVANY_TEXT, nahrada)
        karty.append({
            "karta": nazev,
            "soubor": soubor,
            "prompt": f"{zaklad_karty} Now: {popis}",
        })
    return zaklad, karty


def slozka_modelu(model):
    return model.split("/")[-1].replace(":", "-")


def verze_ollamy():
    with urllib.request.urlopen(OLLAMA + "/api/version", timeout=10) as r:
        return json.load(r)["version"]


def generuj(model, prompt, seed, sirka, vyska, kroky=None):
    """Vygeneruje jeden obrázek. Vrací (png bajty, počet kroků, sekundy)."""
    telo = {
        "model": model,
        "prompt": prompt,
        "width": sirka,
        "height": vyska,
        "stream": True,
        "options": {"seed": seed},
    }
    if kroky:
        telo["steps"] = kroky
    pozadavek = urllib.request.Request(
        OLLAMA + "/api/generate",
        data=json.dumps(telo).encode(),
        headers={"Content-Type": "application/json"},
    )
    start = time.time()
    obrazek, celkem_kroku = None, kroky
    with urllib.request.urlopen(pozadavek, timeout=1800) as odpoved:
        for radek in odpoved:
            if not radek.strip():
                continue
            zprava = json.loads(radek)
            if "error" in zprava:
                raise RuntimeError(zprava["error"])
            if zprava.get("total"):
                celkem_kroku = zprava["total"]
            obrazek = zprava.get("image") or (zprava.get("images") or [None])[0] or obrazek
    if not obrazek:
        raise RuntimeError("Ollama nevrátila žádný obrázek")
    return base64.b64decode(obrazek), celkem_kroku, time.time() - start


def nacti_log():
    if LOG.exists():
        return json.loads(LOG.read_text(encoding="utf-8"))
    return {}


def uloz_log(log):
    LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")


def vytvor_prehled(karty, log):
    """Mřížka náhledů: řádek = karta, sloupce = současný podklad + všechny varianty."""
    ref_dir = NAVRHY / "srovnani"
    ref_dir.mkdir(parents=True, exist_ok=True)
    if SROVNANI.exists():
        shutil.copy2(SROVNANI, ref_dir / SROVNANI.name)

    podle_karty = {}
    for cesta, zaznam in sorted(log.items(), key=lambda p: (p[1]["model"], p[1].get("varianta", ""), p[1]["seed"])):
        if (NAVRHY / cesta).exists():
            podle_karty.setdefault(zaznam["soubor"], []).append((cesta, zaznam))

    def dlazdice(src, popisek, trida=""):
        return (
            f'<figure class="{trida}"><a href="{html.escape(src)}" target="_blank">'
            f'<img src="{html.escape(src)}" loading="lazy"></a>'
            f"<figcaption>{popisek}</figcaption></figure>"
        )

    radky = []
    for karta in karty:
        varianty = podle_karty.get(karta["soubor"])
        if not varianty:
            continue
        bunky = []
        podklad = PODKLADY / f"{karta['soubor']}.png"
        if podklad.exists():
            bunky.append(dlazdice(
                os.path.relpath(podklad, NAVRHY), "současný podklad", "ref"))
        # srovnávací obrázky z jiných nástrojů: srovnani/<soubor>_<zdroj>.png
        for ref in sorted(ref_dir.glob(f"{karta['soubor']}_*.png")):
            zdroj = ref.stem[len(karta["soubor"]) + 1:]
            bunky.append(dlazdice(f"srovnani/{ref.name}", f"{html.escape(zdroj)} (srovnání stylu)", "ref"))
        for cesta, z in varianty:
            cas = f" · {z['cas_s']:.0f} s" if z.get("cas_s") else ""
            varianta = f" · <i>{html.escape(z['varianta'])}</i>" if z.get("varianta") else ""
            bunky.append(dlazdice(
                cesta,
                f"<b>{html.escape(slozka_modelu(z['model']))}</b> · seed {z['seed']}{varianta}{cas}"
                f"<br><code>{html.escape(cesta)}</code>",
            ))
        radky.append(
            f'<section><h2>{html.escape(karta["karta"])} <small>{karta["soubor"]}</small></h2>'
            f'<div class="mrizka">{"".join(bunky)}</div></section>'
        )

    PREHLED.write_text(f"""<!doctype html>
<html lang="cs"><head><meta charset="utf-8">
<title>Královské rošády – návrhy ilustrací</title>
<style>
body {{ font-family: -apple-system, sans-serif; background: #1d1a17; color: #eee; margin: 24px; }}
h1 {{ font-weight: 600; }}
h2 {{ margin: 32px 0 8px; border-bottom: 1px solid #444; padding-bottom: 4px; }}
h2 small {{ color: #999; font-weight: 400; font-size: 14px; }}
.mrizka {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 14px; }}
figure {{ margin: 0; background: #2a2622; padding: 6px; border-radius: 6px; }}
figure.ref {{ outline: 2px dashed #8a7a55; }}
figure img {{ width: 100%; aspect-ratio: 1; object-fit: cover; display: block; border-radius: 3px; }}
figure a {{ position: relative; display: block; }}
/* naznačení stuhy s názvem karty přes horní okraj */
figure a::after {{ content: ""; position: absolute; left: 0; right: 0; top: 0; height: 13%;
  background: rgba(150, 30, 30, .35); border-bottom: 1px dashed rgba(255,255,255,.5); pointer-events: none; }}
figcaption {{ font-size: 13px; padding: 6px 2px 2px; line-height: 1.4; }}
code {{ color: #aaa; font-size: 11px; }}
</style></head><body>
<h1>Královské rošády – návrhy ilustrací</h1>
<p>Vygenerováno {datetime.now():%d. %m. %Y %H:%M}. Červený pruh nahoře naznačuje,
kam zhruba zasáhne stuha s názvem karty. Kliknutím otevřeš obrázek v plné velikosti.</p>
{"".join(radky)}
</body></html>
""", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", choices=POVOLENE_MODELY)
    parser.add_argument("--karty", nargs="*", help="soubory karet (např. kral mag); výchozí všechny")
    parser.add_argument("--seedy", nargs="*", type=int, default=[1, 2, 3])
    parser.add_argument("--sirka", type=int, default=1024)
    parser.add_argument("--vyska", type=int, default=1024)
    parser.add_argument("--kroky", type=int, help="počet difuzních kroků; výchozí podle modelu")
    parser.add_argument("--prompt", help="vlastní celý prompt místo promptu z MD (jen s jednou kartou)")
    parser.add_argument("--varianta", help="název varianty promptu, přidá se do názvu souboru")
    parser.add_argument("--prepsat", action="store_true", help="přegenerovat i existující soubory")
    parser.add_argument("--jen-prehled", action="store_true", help="jen znovu vytvořit prehled.html")
    args = parser.parse_args()

    _, karty = nacti_karty()
    NAVRHY.mkdir(exist_ok=True)
    log = nacti_log()

    if not args.jen_prehled:
        if not args.model:
            parser.error("chybí --model")
        vybrane = karty
        if args.karty:
            nezname = set(args.karty) - {k["soubor"] for k in karty}
            if nezname:
                parser.error(f"neznámé karty: {', '.join(sorted(nezname))}")
            vybrane = [k for k in karty if k["soubor"] in args.karty]
        if args.prompt:
            if len(vybrane) != 1 or not args.varianta:
                parser.error("--prompt jde jen s jednou kartou a s --varianta")
            vybrane = [dict(vybrane[0], prompt=args.prompt)]
        verze = verze_ollamy()
        cil = NAVRHY / slozka_modelu(args.model)
        cil.mkdir(parents=True, exist_ok=True)
        ukoly = [(k, s) for k in vybrane for s in args.seedy]
        print(f"Ollama {verze}, model {args.model}, {len(ukoly)} obrázků")
        for i, (karta, seed) in enumerate(ukoly, 1):
            nazev = karta["soubor"] + (f"_{args.varianta}" if args.varianta else "")
            soubor = cil / f"{nazev}_seed{seed}.png"
            klic = str(soubor.relative_to(NAVRHY))
            if soubor.exists() and not args.prepsat:
                print(f"[{i}/{len(ukoly)}] {klic} už existuje, přeskakuji")
                continue
            png, kroky, cas = generuj(args.model, karta["prompt"], seed, args.sirka, args.vyska, args.kroky)
            soubor.write_bytes(png)
            log[klic] = {
                "karta": karta["karta"],
                "soubor": karta["soubor"],
                "model": args.model,
                "seed": seed,
                "varianta": args.varianta or "",
                "width": args.sirka,
                "height": args.vyska,
                "steps": kroky,
                "prompt": karta["prompt"],
                "ollama_version": verze,
                "cas_s": round(cas, 1),
                "vytvoreno": datetime.now().isoformat(timespec="seconds"),
            }
            uloz_log(log)
            print(f"[{i}/{len(ukoly)}] {klic}  {cas:.1f} s  ({kroky} kroků)", flush=True)

    vytvor_prehled(karty, log)
    print(f"Přehled: {PREHLED}")


if __name__ == "__main__":
    sys.exit(main())
