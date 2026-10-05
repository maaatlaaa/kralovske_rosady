"""
Příprava obrázků pro web.

Originální karty mají 750x750 px a kolem 1 MB, což je na mobil přes VPN
zbytečně moc. Tady se z nich udělají malé WebP verze (desítky kB).
Hotové obrázky se znovu negenerují, takže start serveru je pak rychlý.

Ruční spuštění:  python -m rosady.obrazky [cilova_slozka]
"""

import sys
from pathlib import Path

from PIL import Image

VELIKOST_KARTY = 320
SIRKA_POZADI = 1600


def _uloz(zdroj, cil, max_rozmer):
    if cil.exists() and cil.stat().st_mtime >= zdroj.stat().st_mtime:
        return False
    cil.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(zdroj) as obrazek:
        obrazek = obrazek.convert("RGBA" if obrazek.mode in ("RGBA", "P")
                                  else "RGB")
        obrazek.thumbnail(max_rozmer, Image.LANCZOS)
        obrazek.save(cil, "WEBP", quality=82, method=6)
    return True


def priprav(zdroje, cil):
    """zdroje = zdroje/obrazky, cil = slozka pro webove obrazky"""
    zdroje, cil = Path(zdroje), Path(cil)
    pocet = 0
    for soubor in sorted((zdroje / "karty").glob("*.png")):
        pocet += _uloz(soubor, cil / "karty" / f"{soubor.stem}.webp",
                       (VELIKOST_KARTY, VELIKOST_KARTY))
    pocet += _uloz(zdroje / "pozadi_hlavni_menu.png", cil / "pozadi.webp",
                   (SIRKA_POZADI, SIRKA_POZADI))
    return pocet


if __name__ == "__main__":
    KOREN = Path(__file__).resolve().parent.parent
    CIL = Path(sys.argv[1]) if len(sys.argv) > 1 else KOREN / "data" / "obrazky"
    print(f"vytvořeno {priprav(KOREN / 'zdroje' / 'obrazky', CIL)} obrázků v {CIL}")
