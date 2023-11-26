from PIL import Image, ImageDraw, ImageFont

barvy = []
barva = {"barva": "#ECECEC", "nazev": "bila"}
barvy.append(barva)
barva = {"barva": "#FFF451", "nazev": "zluta"}
barvy.append(barva)
barva = {"barva": "#00D10E", "nazev": "zelena"}
barvy.append(barva)
barva = {"barva": "#FF0000", "nazev": "cervena"}
barvy.append(barva)
barva = {"barva": "#1A00FF", "nazev": "modra"}
barvy.append(barva)
barva = {"barva": "#000000", "nazev": "cerna"}
barvy.append(barva)
karty = []
karta = {"nazev": "Alchymista", "cesta": "alchymista", "hodnota": 8}
karty.append(karta)
karta = {"nazev": "Šermíř", "cesta": "sermir", "hodnota": 8}
karty.append(karta)
karta = {"nazev": "Statkář", "cesta": "statkar", "hodnota": 8}
karty.append(karta)
karta = {"nazev": "Kupec", "cesta": "kupec", "hodnota": 8}
karty.append(karta)
karta = {"nazev": "Kardinál", "cesta": "kardinal", "hodnota": 8}
karty.append(karta)
karta = {"nazev": "Trubadúr", "cesta": "trubadur", "hodnota": 8}
karty.append(karta)
for barva in barvy:
    for karta in karty:

        # nacitani fotek
        hlavni_obrazek = Image.open("zdroje/obrazky/karty_podklady/"+karta["cesta"]+".png")
        novy_hlavni_obrazek = hlavni_obrazek.resize((750, 750))
        ramecek = Image.open("zdroje/obrazky/karty_podklady/ramecek.png")
        pozadi_kratke1 = Image.open("zdroje/obrazky/karty_podklady/paper32.png")
        pozadi_kratke2 = Image.open("zdroje/obrazky/karty_podklady/paper33.png")
        pozadi_dlouhe = Image.open("zdroje/obrazky/karty_podklady/paper2.png")
        znak = Image.open("zdroje/obrazky/karty_podklady/"+karta["cesta"]+"_znak.png")

        # vkladani fotek
        novy_hlavni_obrazek.paste(ramecek, (0, 0), ramecek)
        novy_hlavni_obrazek.paste(pozadi_kratke1, (30, 30))
        novy_hlavni_obrazek.paste(pozadi_kratke2, (580, 30))
        novy_hlavni_obrazek.paste(pozadi_kratke2, (580, 175))
        novy_hlavni_obrazek.paste(pozadi_dlouhe, (30, 620))
        novy_hlavni_obrazek.paste(znak, (580, 176), znak)

        # vkladani textu
        draw = ImageDraw.Draw(novy_hlavni_obrazek)
        myFont = ImageFont.truetype("zdroje/fonty/Canterbury.ttf", 70)

        # Definice rozměrů a pozice obdélníku
        sirka_obdelniku = 400
        vyska_obdelniku = 15
        obdelnik_pozice = (339 // 2, 30)
        pravy_dolni_roh = (obdelnik_pozice[0] + sirka_obdelniku, obdelnik_pozice[1] + vyska_obdelniku)

        # Vykreslení obdélníku
        draw.rectangle([obdelnik_pozice, pravy_dolni_roh], fill=barva["barva"])

        draw.text((80, 70), "8", font=myFont, fill=(0, 0, 0))
        draw.text((610, 70), "12", font=myFont, fill=(0, 0, 0))
        # draw.text((230, 643), karta["nazev"], font=myFont, fill=(0, 0, 0))

        text = karta["nazev"]
        text_rozmery = draw.textbbox((0, 0), text, font=myFont)

        # Výpočet pozice pro vycentrování textu v rámci obdélníku
        text_pozice_x = obdelnik_pozice[0] + (sirka_obdelniku - text_rozmery[2]) // 2
        text_pozice_y = 643

        # Vykreslení textu
        draw.text((text_pozice_x, text_pozice_y), text, font=myFont, fill=(0, 0, 0))

        novy_hlavni_obrazek.save(f"zdroje/obrazky/karty/"+karta["cesta"]+"_"+barva["nazev"]+".png")

karty = []
karta = {"nazev": "Král", "cesta": "kral", "hodnota": 20}
karty.append(karta)
karta = {"nazev": "Královna", "cesta": "kralovna", "hodnota": 16}
karty.append(karta)
karta = {"nazev": "Julie", "cesta": "julie", "hodnota": 14}
karty.append(karta)
karta = {"nazev": "Objevitel", "cesta": "objevitel", "hodnota": 13}
karty.append(karta)
karta = {"nazev": "Mordýř", "cesta": "mordyr", "hodnota": 9.5}
karty.append(karta)
karta = {"nazev": "Bouře", "cesta": "boure", "hodnota": 9}
karty.append(karta)
karta = {"nazev": "Převlek", "cesta": "prevlek", "hodnota": 0}
karty.append(karta)
karta = {"nazev": "Zrádce", "cesta": "zradce", "hodnota": 10}
karty.append(karta)
karta = {"nazev": "Mušketýři", "cesta": "musketyri", "hodnota": 11}
karty.append(karta)
karta = {"nazev": "Mág", "cesta": "mag", "hodnota": 7}
karty.append(karta)
karta = {"nazev": "Čarodějnice", "cesta": "carodejnice", "hodnota": 1}
karty.append(karta)
karta = {"nazev": "Princ", "cesta": "princ", "hodnota": 14}
karty.append(karta)
karta = {"nazev": "Panoš", "cesta": "panos", "hodnota": 2}
karty.append(karta)
karta = {"nazev": "Poustevník", "cesta": "poustevnik", "hodnota": 12}
karty.append(karta)
karta = {"nazev": "Paleček", "cesta": "palecek", "hodnota": 2}
karty.append(karta)
karta = {"nazev": "Dvojník", "cesta": "dvojnik", "hodnota": "X"}
karty.append(karta)
karta = {"nazev": "Drak", "cesta": "drak", "hodnota": 11}
karty.append(karta)
karta = {"nazev": "Romeo", "cesta": "romeo", "hodnota": 5}
karty.append(karta)
karta = {"nazev": "Žebrák", "cesta": "zebrak", "hodnota": 4}
karty.append(karta)
for barva in barvy:
    for karta in karty:

        # nacitani fotek
        hlavni_obrazek = Image.open("zdroje/obrazky/karty_podklady/"+karta["cesta"]+".png")
        novy_hlavni_obrazek = hlavni_obrazek.resize((750, 750))
        ramecek = Image.open("zdroje/obrazky/karty_podklady/ramecek.png")
        pozadi_kratke1 = Image.open("zdroje/obrazky/karty_podklady/paper32.png")
        pozadi_kratke2 = Image.open("zdroje/obrazky/karty_podklady/paper33.png")
        pozadi_dlouhe = Image.open("zdroje/obrazky/karty_podklady/paper2.png")

        # vkladani fotek
        novy_hlavni_obrazek.paste(ramecek, (0, 0), ramecek)
        novy_hlavni_obrazek.paste(pozadi_kratke1, (30, 30))
        novy_hlavni_obrazek.paste(pozadi_kratke2, (580, 30))
        novy_hlavni_obrazek.paste(pozadi_dlouhe, (30, 620))

        # vkladani textu
        draw = ImageDraw.Draw(novy_hlavni_obrazek)
        myFont = ImageFont.truetype("zdroje/fonty/Canterbury.ttf", 70)

        # Definice rozměrů a pozice obdélníku
        sirka_obdelniku = 400
        vyska_obdelniku = 15
        obdelnik_pozice = (339 // 2, 30)
        pravy_dolni_roh = (obdelnik_pozice[0] + sirka_obdelniku, obdelnik_pozice[1] + vyska_obdelniku)

        # Vykreslení obdélníku
        draw.rectangle([obdelnik_pozice, pravy_dolni_roh], fill=barva["barva"])

        draw.text((80, 70), str(karta["hodnota"]), font=myFont, fill=(0, 0, 0))
        draw.text((610, 70), str(karta["hodnota"]), font=myFont, fill=(0, 0, 0))
        # draw.text((230, 643), karta["nazev"], font=myFont, fill=(0, 0, 0))

        text = karta["nazev"]
        text_rozmery = draw.textbbox((0, 0), text, font=myFont)

        # Výpočet pozice pro vycentrování textu v rámci obdélníku
        text_pozice_x = obdelnik_pozice[0] + (sirka_obdelniku - text_rozmery[2]) // 2
        text_pozice_y = 643

        # Vykreslení textu
        draw.text((text_pozice_x, text_pozice_y), text, font=myFont, fill=(0, 0, 0))

        novy_hlavni_obrazek.save("zdroje/obrazky/karty/"+karta["cesta"]+"_"+barva["nazev"]+".png")

for x in range(6):
    podklad = Image.new("RGB", (750, 750), color=barvy[x]["barva"])

    profil = Image.open("zdroje/obrazky/karty_podklady/hrac"+str(x)+".png")
    profil_novy = profil.resize((250, 250))
    podklad.paste(profil_novy, (250, 250))

    podklad.save("zdroje/obrazky/karty/zadni_strana_hrac"+str(x)+".png")
    

# cilove karty alchymie
for x in range(5):
    podklad = Image.open("zdroje/obrazky/karty_podklady/podklad_cilove_karty.png")
    ramecek = Image.open("zdroje/obrazky/karty_podklady/ramecek.png")
    ramecek_novy = ramecek.resize((250, 100))
    podklad.paste(ramecek_novy, (0, 0), ramecek_novy)
    znak = Image.open("zdroje/obrazky/karty_podklady/alchymista_znak.png")
    znak_novy = znak.resize((100, 100))
    podklad.paste(znak_novy, (130, 0), znak_novy)

    # vkladani textu
    draw = ImageDraw.Draw(podklad)
    myFont = ImageFont.truetype("zdroje/fonty/Canterbury.ttf", 70)

    draw.text((30, 25), str(x+1), font=myFont, fill=(0, 0, 0))

    podklad.save("zdroje/obrazky/karty/cilova_karta_alchymie_"+str(x+1)+".png")


# cilove karty serm
for x in range(5):
    podklad = Image.open("zdroje/obrazky/karty_podklady/podklad_cilove_karty.png")
    ramecek = Image.open("zdroje/obrazky/karty_podklady/ramecek.png")
    ramecek_novy = ramecek.resize((250, 100))
    podklad.paste(ramecek_novy, (0, 0), ramecek_novy)
    znak = Image.open("zdroje/obrazky/karty_podklady/sermir_znak.png")
    znak_novy = znak.resize((100, 100))
    podklad.paste(znak_novy, (130, 0), znak_novy)

    # vkladani textu
    draw = ImageDraw.Draw(podklad)
    myFont = ImageFont.truetype("zdroje/fonty/Canterbury.ttf", 70)

    draw.text((30, 25), str(x+1), font=myFont, fill=(0, 0, 0))

    podklad.save("zdroje/obrazky/karty/cilova_karta_serm_"+str(x+1)+".png")


# cilove karty rolnictvi
for x in range(5):
    podklad = Image.open("zdroje/obrazky/karty_podklady/podklad_cilove_karty.png")
    ramecek = Image.open("zdroje/obrazky/karty_podklady/ramecek.png")
    ramecek_novy = ramecek.resize((250, 100))
    podklad.paste(ramecek_novy, (0, 0), ramecek_novy)
    znak = Image.open("zdroje/obrazky/karty_podklady/statkar_znak.png")
    znak_novy = znak.resize((100, 100))
    podklad.paste(znak_novy, (130, 0), znak_novy)

    # vkladani textu
    draw = ImageDraw.Draw(podklad)
    myFont = ImageFont.truetype("zdroje/fonty/Canterbury.ttf", 70)

    draw.text((30, 25), str(x+1), font=myFont, fill=(0, 0, 0))

    podklad.save("zdroje/obrazky/karty/cilova_karta_rolnictvi_"+str(x+1)+".png")

# cilove karty obchod
for x in range(5):
    podklad = Image.open("zdroje/obrazky/karty_podklady/podklad_cilove_karty.png")
    ramecek = Image.open("zdroje/obrazky/karty_podklady/ramecek.png")
    ramecek_novy = ramecek.resize((250, 100))
    podklad.paste(ramecek_novy, (0, 0), ramecek_novy)
    znak = Image.open("zdroje/obrazky/karty_podklady/kupec_znak.png")
    znak_novy = znak.resize((100, 100))
    podklad.paste(znak_novy, (130, 0), znak_novy)

    # vkladani textu
    draw = ImageDraw.Draw(podklad)
    myFont = ImageFont.truetype("zdroje/fonty/Canterbury.ttf", 70)

    draw.text((30, 25), str(x+1), font=myFont, fill=(0, 0, 0))

    podklad.save("zdroje/obrazky/karty/cilova_karta_obchod_"+str(x+1)+".png")

# cilove karty nabozenstvi
for x in range(5):
    podklad = Image.open("zdroje/obrazky/karty_podklady/podklad_cilove_karty.png")
    ramecek = Image.open("zdroje/obrazky/karty_podklady/ramecek.png")
    ramecek_novy = ramecek.resize((250, 100))
    podklad.paste(ramecek_novy, (0, 0), ramecek_novy)
    znak = Image.open("zdroje/obrazky/karty_podklady/kardinal_znak.png")
    znak_novy = znak.resize((100, 100))
    podklad.paste(znak_novy, (130, 0), znak_novy)

    # vkladani textu
    draw = ImageDraw.Draw(podklad)
    myFont = ImageFont.truetype("zdroje/fonty/Canterbury.ttf", 70)

    draw.text((30, 25), str(x+1), font=myFont, fill=(0, 0, 0))

    podklad.save("zdroje/obrazky/karty/cilova_karta_nabozenstvi_"+str(x+1)+".png")

# cilove karty hudba
for x in range(5):
    podklad = Image.open("zdroje/obrazky/karty_podklady/podklad_cilove_karty.png")
    ramecek = Image.open("zdroje/obrazky/karty_podklady/ramecek.png")
    ramecek_novy = ramecek.resize((250, 100))
    podklad.paste(ramecek_novy, (0, 0), ramecek_novy)
    znak = Image.open("zdroje/obrazky/karty_podklady/trubadur_znak.png")
    znak_novy = znak.resize((100, 100))
    podklad.paste(znak_novy, (130, 0), znak_novy)

    # vkladani textu
    draw = ImageDraw.Draw(podklad)
    myFont = ImageFont.truetype("zdroje/fonty/Canterbury.ttf", 70)

    draw.text((30, 25), str(x+1), font=myFont, fill=(0, 0, 0))

    podklad.save("zdroje/obrazky/karty/cilova_karta_hudba_"+str(x+1)+".png")
