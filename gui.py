import pygame
import pygame_gui
import main
from button import Button
# inicializace
pygame.init()

# vytvoreni obrazovky
sirka = 900
vyska = 700
obrazovka = pygame.display.set_mode((sirka, vyska))
manager = pygame_gui.UIManager((sirka, vyska))
fps = 60
clock = pygame.time.Clock()

# definice barev
cerna = (0, 0, 0)
bila = (255, 255, 255)
tmave_cervena = (189, 11, 0)

# nastaveni fontu
vedlejsi_font = pygame.font.SysFont("kokila", 40)
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
    tlacitko_hrat_lokal = Button(obrazovka, pozadi_tlacitko, 200, 250,
                                 "Hrát lokál", hlavni_font_maly, cerna, tmave_cervena)
    tlacitko_hrat_multi = Button(obrazovka, pozadi_tlacitko, 200, 350,
                                 "Hrát multiplayer", hlavni_font_maly, cerna, tmave_cervena)
    tlacitko_sin_slavy = Button(obrazovka, pozadi_tlacitko, 200, 450,
                                "Sál slávy", hlavni_font_maly, cerna, tmave_cervena)
    tlacitko_odejit = Button(obrazovka, pozadi_tlacitko, 200, 550,
                             "Odejít", hlavni_font_maly, cerna, tmave_cervena)

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
                    hrat_lokalne()
                if tlacitko_hrat_multi.check_for_input(mys_pozice):
                    print("jdeme hrat multiplayer")
                if tlacitko_sin_slavy.check_for_input(mys_pozice):
                    sal_slavy()
                if tlacitko_odejit.check_for_input(mys_pozice):
                    pygame.quit()

        # obnova obrazovky
        obrazovka.blit(nadpis, nadpis_rect)
        pygame.display.update()
        clock.tick(fps)


def hrat_lokalne():
    pygame.display.set_caption("Královské rošády - Hra lokálně")
    pozadi_hlavni = pygame.image.load("zdroje/obrazky/pozadi_vyber.png")
    pozadi_tlacitko = pygame.image.load("zdroje/obrazky/pozadi_tlacitko.png")

    # texty
    nadpis = hlavni_font.render("Kdo hraje", True, cerna)
    nadpis_rect = nadpis.get_rect()
    nadpis_rect.center = (sirka // 2, vyska // 2 - 245)

    podnadpis = vedlejsi_font.render("Pořadí hráčů od nejmladšího", True, cerna)
    podnadpis_rect = nadpis.get_rect()
    podnadpis_rect.center = (sirka // 2, 200)

    error_text = vedlejsi_font.render("", True, cerna)
    error_text_rect = nadpis.get_rect()
    error_text_rect.center = (sirka // 2, 620)

    # tlacitkaaa
    tlacitko_zpet = Button(obrazovka, pozadi_tlacitko, 70, 100, "Zpátky", hlavni_font_maly, cerna, tmave_cervena)
    tlacitko_start = Button(obrazovka, pozadi_tlacitko, 450, 650, "Start", hlavni_font_maly, cerna, tmave_cervena)

    text_pole_1 = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((250, 200), (400, 50)),
                                                      manager=manager, object_id="#hrac1")
    text_pole_2 = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((250, 260), (400, 50)),
                                                      manager=manager, object_id="#hrac2")
    text_pole_3 = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((250, 320), (400, 50)),
                                                      manager=manager, object_id="#hrac3")
    text_pole_4 = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((250, 380), (400, 50)),
                                                      manager=manager, object_id="#hrac4")
    text_pole_5 = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((250, 450), (400, 50)),
                                                      manager=manager, object_id="#hrac5")
    text_pole_6 = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((250, 510), (400, 50)),
                                                      manager=manager, object_id="#hrac6")
    textova_pole = [text_pole_1, text_pole_2, text_pole_3, text_pole_4, text_pole_5, text_pole_6]

    konec = False
    # hlavni herni cyklus
    while not konec:
        obrazovka.blit(pozadi_hlavni, (0, 0))

        ui_refresh_rate = clock.tick(fps)/1000
        mys_pozice = pygame.mouse.get_pos()

        for tlacitko in [tlacitko_zpet, tlacitko_start]:
            tlacitko.change_color(mys_pozice)
            tlacitko.update()

        for udalost in pygame.event.get():
            if udalost.type == pygame.QUIT:
                konec = True
            if udalost.type == pygame.MOUSEBUTTONDOWN:
                if tlacitko_zpet.check_for_input(mys_pozice):
                    hlavni_menu()
                if tlacitko_start.check_for_input(mys_pozice):
                    hraci = []
                    for text_pole in textova_pole:
                        if len(text_pole.get_text()) > 3:
                            hraci.append(text_pole.get_text())
                    if len(hraci) < 2:
                        error_text = vedlejsi_font.render("Malo hracu", True, cerna)
                    else:
                        main.Hra(hraci)

            manager.process_events(udalost)
        # obnova obrazovky
        obrazovka.blit(nadpis, nadpis_rect)
        obrazovka.blit(podnadpis, podnadpis_rect)
        obrazovka.blit(error_text, error_text_rect)

        manager.draw_ui(obrazovka)
        manager.update(ui_refresh_rate)
        pygame.display.update()
        clock.tick(fps)


def sal_slavy():
    pygame.display.set_caption("Královské rošády - Sál slávy")
    pozadi_hlavni = pygame.image.load("zdroje/obrazky/pozadi_vyber.png")
    pozadi_tlacitko = pygame.image.load("zdroje/obrazky/pozadi_tlacitko.png")

    nadpis = hlavni_font.render("Sál slávy", True, cerna)
    nadpis_rect = nadpis.get_rect()
    nadpis_rect.center = (sirka//2, vyska//2-245)

    # tlacitkaaa
    tlacitko_zpet = Button(obrazovka, pozadi_tlacitko, 70, 100, "Zpátky", hlavni_font_maly, cerna, tmave_cervena)
    tlacitko_vsechny_hry = Button(obrazovka, pozadi_tlacitko, 450, 650,
                                  "Všechny hry", hlavni_font_maly, cerna, tmave_cervena)

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
                    vsechny_hry()

        # obnova obrazovky
        obrazovka.blit(nadpis, nadpis_rect)
        pygame.display.update()
        clock.tick(fps)


def vsechny_hry():
    pygame.display.set_caption("Královské rošády - Všechny hry")
    pozadi_hlavni = pygame.image.load("zdroje/obrazky/pozadi_vyber.png")
    pozadi_tlacitko = pygame.image.load("zdroje/obrazky/pozadi_tlacitko.png")

    nadpis = hlavni_font.render("Všechny hry", True, cerna)
    nadpis_rect = nadpis.get_rect()
    nadpis_rect.center = (sirka // 2, vyska // 2 - 245)

    # tlacitkaaa
    tlacitko_zpet = Button(obrazovka, pozadi_tlacitko, 70, 100, "Zpátky", hlavni_font_maly, cerna, tmave_cervena)

    konec = False
    # hlavni herni cyklus
    while not konec:
        obrazovka.blit(pozadi_hlavni, (0, 0))

        mys_pozice = pygame.mouse.get_pos()

        for tlacitko in [tlacitko_zpet]:
            tlacitko.change_color(mys_pozice)
            tlacitko.update()

        for udalost in pygame.event.get():
            if udalost.type == pygame.QUIT:
                konec = True
            if udalost.type == pygame.MOUSEBUTTONDOWN:
                if tlacitko_zpet.check_for_input(mys_pozice):
                    sal_slavy()

        # obnova obrazovky
        obrazovka.blit(nadpis, nadpis_rect)
        pygame.display.update()
        clock.tick(fps)


hlavni_menu()
# konec
pygame.quit()
