import pygame

# inicializace
pygame.init()

# Nastavení režimu a vytvoření okna
fullscreen = True  # Nastavte na True pro fullscreen
if fullscreen:
    obrazovka = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    sirka, vyska = pygame.display.get_surface().get_size()
    obdelnik = pygame.Rect(20, 20, sirka-40, vyska-40)
    print(sirka, vyska)
else:
    # vytvoreni obrazovky
    sirka = 1500
    vyska = 1050
    obdelnik = pygame.Rect(50, 50, 1400, 900)
    obrazovka = pygame.display.set_mode((sirka, vyska))

stred = sirka // 2
fps = 60
clock = pygame.time.Clock()

# definice barev
cerna = (0, 0, 0)
seda = (50, 50, 50)
bila = (255, 255, 255)

# nastaveni fontu
vedlejsi_font = pygame.font.SysFont("kokila", 40)

obrazovka.fill(bila)

# pocet_hracu = int(input())
pocet_hracu = 5
vyska = vyska - 40

velikost_karet = 150

pomocna = 150

while True:
    pocet_karet_vejdou = vyska // pomocna

    if pocet_karet_vejdou < pocet_hracu + 1:
        velikost_karet = pomocna
        break

    pomocna += 5
    if pomocna == 250:
        velikost_karet = pomocna
        break
    print(pomocna)

print("velikost karet" + str(velikost_karet))

cilova_karta = pygame.image.load("zdroje/obrazky/cilova_karta.png").convert()
karta_vlivu = pygame.image.load("zdroje/obrazky/karta_vlivu_zakryta.png").convert()

cilova_karta = pygame.transform.scale(cilova_karta, (velikost_karet, 0.75*velikost_karet))
cilova_karta_rect = cilova_karta.get_rect()

karta_vlivu = pygame.transform.scale(karta_vlivu, (velikost_karet, velikost_karet))
karta_vlivu_rect = karta_vlivu.get_rect()

konec = False
# hlavni herni cyklus
while not konec:

    sirka_dil = sirka // pocet_hracu  # 1200 // 5 = 240
    sirka_pomocna = sirka_dil // 2 + 400  # 240 // 2 = 120

    for _ in range(pocet_hracu):
        sirka_pomocna = sirka_pomocna + velikost_karet+40
        cilova_karta_rect.center = (sirka_pomocna, velikost_karet/2+10)
        obrazovka.blit(cilova_karta, cilova_karta_rect)

    for x in range(pocet_hracu):
        sirka_dil = sirka // pocet_hracu  # 1200 // 5 = 240
        sirka_pomocna = sirka_dil // 2 + 400  # 240 // 2 = 120
        zaklad = velikost_karet + velikost_karet/2 + 5
        for _ in range(pocet_hracu):
            # stary zpusob : sirka_pomocna = sirka_pomocna + sirka_dil
            sirka_pomocna = sirka_pomocna + velikost_karet + 40
            karta_vlivu_rect.center = (sirka_pomocna, zaklad + (velikost_karet * x))
            obrazovka.blit(karta_vlivu, karta_vlivu_rect)

    # obrazovka.blit(sipka, (stred-155, 10))
    # pygame.draw.rect(obrazovka, ramec_barva, ramec, ramec_tloustka)

    # obnova obrazovky
    pygame.display.update()
    clock.tick(fps)

# konec
pygame.quit()
