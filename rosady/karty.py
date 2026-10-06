"""
Definice karet hry Královské rošády.

Každý hráč má vlastní balíček 25 karet vlivu (od každé karty jednu).
Cílové karty jsou společné - 6 kategorií, v každé hodnoty 1-5 a jedna 3 navíc.
"""

# barvy hracu v poradi, v jakem je ma generovani_karet.py (index = cislo hrace)
BARVY_HRACU = [
    {"nazev": "bila", "hex": "#ECECEC", "popis": "bílá"},
    {"nazev": "zluta", "hex": "#FFF451", "popis": "žlutá"},
    {"nazev": "zelena", "hex": "#00D10E", "popis": "zelená"},
    {"nazev": "cervena", "hex": "#FF0000", "popis": "červená"},
    {"nazev": "modra", "hex": "#1A00FF", "popis": "modrá"},
    {"nazev": "cerna", "hex": "#000000", "popis": "černá"},
]

MIN_HRACU = 2
MAX_HRACU = len(BARVY_HRACU)
POCET_KOL = 6

# hodnota specialisty, pokud lezi ve sloupci sve kategorie
BONUS_SPECIALISTY = 12

# kategorie cilovych karet: nazev -> soubor obrazku a specialista, ktery v ni ma bonus
KATEGORIE = {
    "Alchymie": {"soubor": "alchymie", "specialista": "Alchymista"},
    "Šerm": {"soubor": "serm", "specialista": "Šermíř"},
    "Rolnictví": {"soubor": "rolnictvi", "specialista": "Statkář"},
    "Obchod": {"soubor": "obchod", "specialista": "Kupec"},
    "Náboženství": {"soubor": "nabozenstvi", "specialista": "Kardinál"},
    "Hudba": {"soubor": "hudba", "specialista": "Trubadúr"},
}


def _specialista(kategorie):
    return (f"Ve sloupci s cílovou kartou {kategorie} má hodnotu "
            f"{BONUS_SPECIALISTY}.")


# nazev -> soubor obrazku, zakladni hodnota a popis schopnosti
KARTY = {
    "Král": {"soubor": "kral", "hodnota": 20,
             "popis": "Nejsilnější karta bez zvláštní schopnosti."},
    "Královna": {"soubor": "kralovna", "hodnota": 16,
                 "popis": "Silná karta bez zvláštní schopnosti."},
    "Julie": {"soubor": "julie", "hodnota": 14,
              "popis": "Bez zvláštní schopnosti. Posiluje tvého Romea."},
    "Alchymista": {"soubor": "alchymista", "hodnota": 8,
                   "popis": _specialista("Alchymie")},
    "Šermíř": {"soubor": "sermir", "hodnota": 8,
               "popis": _specialista("Šerm")},
    "Statkář": {"soubor": "statkar", "hodnota": 8,
                "popis": _specialista("Rolnictví")},
    "Kupec": {"soubor": "kupec", "hodnota": 8,
              "popis": _specialista("Obchod")},
    "Kardinál": {"soubor": "kardinal", "hodnota": 8,
                 "popis": _specialista("Náboženství")},
    "Trubadúr": {"soubor": "trubadur", "hodnota": 8,
                 "popis": _specialista("Hudba")},
    "Objevitel": {"soubor": "objevitel", "hodnota": 13,
                  "popis": "Po otočení se přesune lícem dolů na konec dalšího sloupce "
                           "vpravo (z posledního sloupce do prvního). Tam "
                           "otočí kartu nad sebou, jako by byl nově vyložen."},
    "Mordýř": {"soubor": "mordyr", "hodnota": 9.5,
               "popis": "Po otočení zabije kartu, která byla vyložena pod něj. "
                        "Díky hodnotě 9,5 na něj neplatí Mág ani Čarodějnice."},
    "Bouře": {"soubor": "boure", "hodnota": 9,
              "popis": "Po otočení uzavře sloupec – nelze do něj už nic "
                       "vyložit a počítá se jako splněný."},
    "Převlek": {"soubor": "prevlek", "hodnota": 0,
                "popis": "Po otočení pod něj můžeš skrytě vložit kartu z ruky. "
                         "Při vyhodnocení se Převlek promění v tuto kartu. "
                         "Bez karty pod sebou má hodnotu 0."},
    "Zrádce": {"soubor": "zradce", "hodnota": 10,
               "popis": "Po otočení můžeš vyměnit cílovou kartu jeho sloupce "
                        "za cílovou kartu jiného sloupce."},
    "Mušketýři": {"soubor": "musketyri", "hodnota": 11,
                  "popis": "Ve sloupci s Mušketýři neplatí žádné schopnosti "
                           "vyhodnocované na konci kola (ani bonusy "
                           "specialistů) – počítají se jen základní hodnoty."},
    "Mág": {"soubor": "mag", "hodnota": 7,
            "popis": "Při vyhodnocení odstraní ze sloupce všechny karty "
                     "s hodnotou 10 a více."},
    "Čarodějnice": {"soubor": "carodejnice", "hodnota": 1,
                    "popis": "Při vyhodnocení (až po Mágovi) odstraní ze sloupce "
                             "všechny karty s hodnotou 9 a méně, kromě "
                             "Čarodějnic."},
    "Princ": {"soubor": "princ", "hodnota": 14,
              "popis": "Máš-li ve stejném sloupci Prince i Panoše, "
                       "vyhráváš sloupec automaticky."},
    "Panoš": {"soubor": "panos", "hodnota": 2,
              "popis": "Máš-li ve stejném sloupci Prince i Panoše, "
                       "vyhráváš sloupec automaticky."},
    "Poustevník": {"soubor": "poustevnik", "hodnota": 12,
                   "popis": "Za každou další kartu ve sloupci ztrácí 1 bod."},
    "Paleček": {"soubor": "palecek", "hodnota": 2,
                "popis": "Za každou další kartu ve sloupci získává 3 body."},
    "Dvojník": {"soubor": "dvojnik", "hodnota": 0,
                "popis": "Při vyhodnocení převezme hodnotu karty těsně pod "
                         "sebou (ne její schopnost). Bez karty pod sebou má 0."},
    "Drak": {"soubor": "drak", "hodnota": 11,
             "popis": "Všem kartám soupeřů ve sloupci ubere 2 body."},
    "Romeo": {"soubor": "romeo", "hodnota": 5,
              "popis": "Máš-li ve stejném sloupci i Julii, má Romeo "
                       "hodnotu 15."},
    "Žebrák": {"soubor": "zebrak", "hodnota": 4,
               "popis": "Ve sloupci se Žebrákem vyhrává hráč s nejnižším "
                        "součtem. Při remíze vyhrává karta nejdál od cílové "
                        "karty."},
}

SPECIALISTE = {info["specialista"]: kategorie
               for kategorie, info in KATEGORIE.items()}


def novy_balicek(rng):
    """vytvori zamichany balicek nazvu karet"""
    balicek = list(KARTY)
    rng.shuffle(balicek)
    return balicek


def nove_cilove_karty(rng):
    """vytvori zamichany balicek cilovych karet"""
    cilove = []
    for kategorie in KATEGORIE:
        for hodnota in [1, 2, 3, 3, 4, 5]:
            cilove.append({"kategorie": kategorie, "hodnota": hodnota})
    rng.shuffle(cilove)
    return cilove


def katalog():
    """informace o kartach pro webove rozhrani"""
    return {
        "karty": {nazev: dict(info) for nazev, info in KARTY.items()},
        "kategorie": {nazev: dict(info) for nazev, info in KATEGORIE.items()},
        "barvy": BARVY_HRACU,
        "bonus_specialisty": BONUS_SPECIALISTY,
    }
