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
    "Alchymie": {"barva": "#5b3f8c", "soubor": "alchymie", "specialista": "Alchymista"},
    "Šerm": {"barva": "#4a5d70", "soubor": "serm", "specialista": "Šermíř"},
    "Rolnictví": {"barva": "#4f7a2a", "soubor": "rolnictvi", "specialista": "Statkář"},
    "Obchod": {"barva": "#a8761c", "soubor": "obchod", "specialista": "Kupec"},
    "Náboženství": {"barva": "#8f1f1f", "soubor": "nabozenstvi", "specialista": "Kardinál"},
    "Hudba": {"barva": "#2c5c8f", "soubor": "hudba", "specialista": "Trubadúr"},
}


def _specialista(kategorie):
    return (f"Ve sloupci s cílovou kartou {kategorie} má hodnotu "
            f"{BONUS_SPECIALISTY}.")


def _kratky_specialista(kategorie):
    return f"Ve sloupci {kategorie} má hodnotu {BONUS_SPECIALISTY}."


# nazev -> soubor obrazku, zakladni hodnota a popis schopnosti
KARTY = {
    "Král": {"soubor": "kral", "hodnota": 20,
             "kdy": None, "kratky": '„Poslední slovo má vždy koruna.“',
                "popis": "Nejsilnější karta bez zvláštní schopnosti."},
    "Královna": {"soubor": "kralovna", "hodnota": 16,
                 "kdy": None, "kratky": '„Za trůnem stojí ta, která šeptá.“',
                "popis": "Silná karta bez zvláštní schopnosti."},
    "Julie": {"soubor": "julie", "hodnota": 14,
              "kdy": None, "kratky": '„Kde je Julie, tam je i Romeo.“',
                "popis": "Bez zvláštní schopnosti. Posiluje tvého Romea."},
    "Alchymista": {"soubor": "alchymista", "hodnota": 8,
                   "kdy": "konec", "kratky": _kratky_specialista("Alchymie"),
               "popis": _specialista("Alchymie")},
    "Šermíř": {"soubor": "sermir", "hodnota": 8,
               "kdy": "konec", "kratky": _kratky_specialista("Šerm"),
               "popis": _specialista("Šerm")},
    "Statkář": {"soubor": "statkar", "hodnota": 8,
                "kdy": "konec", "kratky": _kratky_specialista("Rolnictví"),
               "popis": _specialista("Rolnictví")},
    "Kupec": {"soubor": "kupec", "hodnota": 8,
              "kdy": "konec", "kratky": _kratky_specialista("Obchod"),
               "popis": _specialista("Obchod")},
    "Kardinál": {"soubor": "kardinal", "hodnota": 8,
                 "kdy": "konec", "kratky": _kratky_specialista("Náboženství"),
               "popis": _specialista("Náboženství")},
    "Trubadúr": {"soubor": "trubadur", "hodnota": 8,
                 "kdy": "konec", "kratky": _kratky_specialista("Hudba"),
               "popis": _specialista("Hudba")},
    "Objevitel": {"soubor": "objevitel", "hodnota": 13,
                  "kdy": 'otoceni', "kratky": 'Přesune se zakrytý na konec dalšího sloupce vpravo.',
                "popis": "Po otočení se přesune lícem dolů na konec dalšího sloupce "
                           "vpravo (z posledního sloupce do prvního). Tam "
                           "otočí kartu nad sebou, jako by byl nově vyložen."},
    "Mordýř": {"soubor": "mordyr", "hodnota": 9.5,
               "kdy": 'otoceni', "kratky": 'Zabije kartu vyloženou pod něj.',
                "popis": "Po otočení zabije kartu, která byla vyložena pod něj. "
                        "Díky hodnotě 9,5 na něj neplatí Mág ani Čarodějnice."},
    "Bouře": {"soubor": "boure", "hodnota": 9,
              "kdy": 'otoceni', "kratky": 'Uzavře sloupec. Sloupec je splněný.',
                "popis": "Po otočení uzavře sloupec – nelze do něj už nic "
                       "vyložit a počítá se jako splněný."},
    "Převlek": {"soubor": "prevlek", "hodnota": 0,
                "kdy": 'otoceni', "kratky": 'Vlož pod něj skrytě kartu z ruky – stane se jí.',
                "popis": "Po otočení pod něj můžeš skrytě vložit kartu z ruky. "
                         "Při vyhodnocení se Převlek promění v tuto kartu. "
                         "Bez karty pod sebou má hodnotu 0."},
    "Zrádce": {"soubor": "zradce", "hodnota": 10,
               "kdy": 'otoceni', "kratky": 'Vyměň cílovou kartu svého sloupce za jinou.',
                "popis": "Po otočení můžeš vyměnit cílovou kartu jeho sloupce "
                        "za cílovou kartu jiného sloupce."},
    "Mušketýři": {"soubor": "musketyri", "hodnota": 11,
                  "kdy": 'konec', "kratky": 'Ve sloupci neplatí žádné schopnosti.',
                "popis": "Ve sloupci s Mušketýři neplatí žádné schopnosti "
                           "vyhodnocované na konci kola (ani bonusy "
                           "specialistů) – počítají se jen základní hodnoty."},
    "Mág": {"soubor": "mag", "hodnota": 7,
            "kdy": 'konec', "kratky": 'Odstraní karty s hodnotou 10 a více.',
                "popis": "Při vyhodnocení odstraní ze sloupce všechny karty "
                     "s hodnotou 10 a více. Dva Mágové se navzájem zruší."},
    "Čarodějnice": {"soubor": "carodejnice", "hodnota": 1,
                    "kdy": 'konec', "kratky": 'Odstraní karty s hodnotou 9 a méně.',
                "popis": "Při vyhodnocení (až po Mágovi) odstraní ze sloupce "
                             "všechny karty s hodnotou 9 a méně, kromě "
                             "Čarodějnic. Dvě Čarodějnice se navzájem zruší."},
    "Princ": {"soubor": "princ", "hodnota": 14,
              "kdy": 'konec', "kratky": 'S tvým Panošem vyhráváš sloupec.',
                "popis": "Máš-li ve stejném sloupci Prince i Panoše, "
                       "vyhráváš sloupec automaticky."},
    "Panoš": {"soubor": "panos", "hodnota": 2,
              "kdy": 'konec', "kratky": 'S tvým Princem vyhráváš sloupec.',
                "popis": "Máš-li ve stejném sloupci Prince i Panoše, "
                       "vyhráváš sloupec automaticky."},
    "Poustevník": {"soubor": "poustevnik", "hodnota": 12,
                   "kdy": 'konec', "kratky": '−1 za každou další kartu ve sloupci.',
                "popis": "Za každou další kartu ve sloupci ztrácí 1 bod."},
    "Paleček": {"soubor": "palecek", "hodnota": 2,
                "kdy": 'konec', "kratky": '+3 za každou další kartu ve sloupci.',
                "popis": "Za každou další kartu ve sloupci získává 3 body."},
    "Dvojník": {"soubor": "dvojnik", "hodnota": 0,
                "kdy": 'konec', "kratky": 'Má hodnotu karty těsně pod sebou.',
                "popis": "Při vyhodnocení převezme hodnotu karty těsně pod "
                         "sebou (ne její schopnost). Bez karty pod sebou "
                         "nemá žádnou hodnotu."},
    "Drak": {"soubor": "drak", "hodnota": 11,
             "kdy": 'konec', "kratky": 'Kartám soupeřů ve sloupci −2.',
                "popis": "Všem kartám soupeřů ve sloupci ubere 2 body "
                      "(hodnota karty ale neklesne pod 0)."},
    "Romeo": {"soubor": "romeo", "hodnota": 5,
              "kdy": 'konec', "kratky": 'S tvou Julií má hodnotu 15.',
                "popis": "Máš-li ve stejném sloupci i Julii, má Romeo "
                       "hodnotu 15."},
    "Žebrák": {"soubor": "zebrak", "hodnota": 4,
               "kdy": 'konec', "kratky": 'Sloupec vyhrává nejnižší součet.',
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
