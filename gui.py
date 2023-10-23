from button import Button
import pygame

# inicializace
pygame.init()

# vytvoreni obrazovky
sirka = 900
vyska = 700
obrazovka = pygame.display.set_mode((sirka, vyska))

# definice barev
cerna = (0, 0, 0)
bila = (255, 255, 255)
tmave_cervena = (189, 11, 0)

# nastaveni fontu
vedlejsi_font = pygame.font.SysFont("kokila", 50)
hlavni_font = pygame.font.Font("zdroje/fonty/Canterbury.ttf", 105)
hlavni_font_maly = pygame.font.Font("zdroje/fonty/Canterbury.ttf", 45)

pozadi_vyber = pygame.image.load("zdroje/obrazky/pozadi_vyber.png")

obrazovka.fill(bila)

# def hlavni menu
def hlavni_menu():
    pygame.display.set_caption("Královské rošády")
    pozadi_hlavni = pygame.image.load("zdroje/obrazky/pozadi_hlavni_menu.png")
    pozadi_tlacitko = pygame.image.load("zdroje/obrazky/pozadi_tlacitko.png")

    nadpis = hlavni_font.render("Královské rošády", True, cerna)
    nadpis_rect = nadpis.get_rect()
    nadpis_rect.center = (sirka//2, vyska//2-245)

    # tlacitkaaa
    tlacitko_hrat_lokal = Button(obrazovka, pozadi_tlacitko, 200, 250, "Hrát lokál", hlavni_font_maly, cerna, tmave_cervena)
    tlacitko_hrat_multi = Button(obrazovka, pozadi_tlacitko, 200, 350, "Hrát multiplayer", hlavni_font_maly, cerna, tmave_cervena)
    tlacitko_sin_slavy = Button(obrazovka, pozadi_tlacitko, 200, 450, "Sál slávy", hlavni_font_maly, cerna, tmave_cervena)
    tlacitko_odejit = Button(obrazovka, pozadi_tlacitko, 200, 550, "Odejít", hlavni_font_maly, cerna, tmave_cervena)

    konec = False
    # hlavni herni cyklus
    while not konec:
        obrazovka.blit(pozadi_hlavni, (0, 0))

        mys_pozice = pygame.mouse.get_pos()

        for tlacitko in [tlacitko_hrat_lokal, tlacitko_hrat_multi, tlacitko_sin_slavy, tlacitko_odejit]:
            tlacitko.change_color(mys_pozice)
            tlacitko.update()

        for udalost in pygame.event.get():
            if udalost.type == pygame.QUIT:
                konec = True
            if udalost.type == pygame.MOUSEBUTTONDOWN:
                if tlacitko_hrat_lokal.check_for_input(mys_pozice):
                    print("jdeme hrat lokalne")
                if tlacitko_hrat_multi.check_for_input(mys_pozice):
                    print("jdeme hrat multiplayer")
                if tlacitko_sin_slavy.check_for_input(mys_pozice):
                    print("lets go do sine slavy")
                    sal_slavy()
                if tlacitko_odejit.check_for_input(mys_pozice):
                    pygame.quit()

        # obnova obrazovky
        obrazovka.blit(nadpis, nadpis_rect)
        pygame.display.update()

def sal_slavy():
    pygame.display.set_caption("Královské rošády - Sál slávy")
    pozadi_hlavni = pygame.image.load("zdroje/obrazky/pozadi_vyber.png")
    pozadi_tlacitko = pygame.image.load("zdroje/obrazky/pozadi_tlacitko.png")

    nadpis = hlavni_font.render("Sál slávy", True, cerna)
    nadpis_rect = nadpis.get_rect()
    nadpis_rect.center = (sirka//2, vyska//2-245)

    # tlacitkaaa
    tlacitko_zpet = Button(obrazovka, pozadi_tlacitko, 70, 100, "Zpátky", hlavni_font_maly, cerna, tmave_cervena)
    tlacitko_vsechny_hry = Button(obrazovka, pozadi_tlacitko, 450, 650, "Všechny hry", hlavni_font_maly, cerna, tmave_cervena)

    konec = False
    # hlavni herni cyklus
    while not konec:
        obrazovka.blit(pozadi_hlavni, (0, 0))

        mys_pozice = pygame.mouse.get_pos()

        for tlacitko in [tlacitko_zpet, tlacitko_vsechny_hry]:
            tlacitko.change_color(mys_pozice)
            tlacitko.update()

        for udalost in pygame.event.get():
            if udalost.type == pygame.QUIT:
                konec = True
            if udalost.type == pygame.MOUSEBUTTONDOWN:
                if tlacitko_zpet.check_for_input(mys_pozice):
                    hlavni_menu()
                if tlacitko_vsechny_hry.check_for_input(mys_pozice):
                    print("jdeme hrat multiplayer")


        # obnova obrazovky
        obrazovka.blit(nadpis, nadpis_rect)
        pygame.display.update()


hlavni_menu()
# konec
pygame.quit()
