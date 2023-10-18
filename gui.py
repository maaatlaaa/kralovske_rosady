import pygame

# inicializace
pygame.init()

# vytvoreni obrazovky
sirka = 1500
vyska = 1000
obrazovka = pygame.display.set_mode((sirka, vyska))
pygame.display.set_caption("Královské rošády")

# definice barev
cerna = (0, 0, 0)
bila = (255, 255, 255)

# definice pozadi
obrazovka.fill(bila)

# nastaveni fontu
fonts = pygame.font.get_fonts()
for font in fonts:
    print(font)
systemovy_font = pygame.font.SysFont("kokila", 64)
def vyber_font():
    pass

konec = False
# hlavni herni cyklus
while not konec:
    for udalost in pygame.event.get():
        if udalost.type == pygame.QUIT:
            konec = True
        # print(udalost)
    # obnova obrazovky
    pygame.display.update()


# konec
pygame.quit()
