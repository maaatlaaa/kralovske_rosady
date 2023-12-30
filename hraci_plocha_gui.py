import pygame


class HraciPlochaGui:
    def __init__(self, pocet_hracu, data_fronta):
        self.pocet_hracu = pocet_hracu
        self.data_fronta = data_fronta
        # inicializace
        pygame.init()
        print("Ahoj")

        # Nastavení režimu a vytvoření okna
        fullscreen = True  # Nastavte na True pro fullscreen
        if fullscreen:
            self.obrazovka = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.sirka, self.vyska = pygame.display.get_surface().get_size()
        else:
            # vytvoreni obrazovky
            self.sirka = 1500
            self.vyska = 1050
            self.obrazovka = pygame.display.set_mode((self.sirka, self.vyska))

        self.fps = 60
        self.clock = pygame.time.Clock()

        # definice barev
        self.cerna = (0, 0, 0)
        self.bila = (255, 255, 255)

        # nastaveni fontu
        self.vedlejsi_font = pygame.font.SysFont("kokila", 40)

        self.obrazovka.fill(self.bila)
        self.vyska = self.vyska - 40
        self.velikost_karet = 150

        pomocna = 150

        while True:
            pocet_karet_vejdou = self.vyska // pomocna

            if pocet_karet_vejdou < pocet_hracu + 1:
                self.velikost_karet = pomocna
                break

            pomocna += 5
            if pomocna == 250:
                self.velikost_karet = pomocna
                break
            print(pomocna)

        print("velikost karet" + str(self.velikost_karet))
        self.start()

    def zpracuj_data(self, data):
        print("data" + str(data))

    def nacitani_karet(self):
        cilova_karta = pygame.image.load("zdroje/obrazky/karty/cilova_karta_serm_1.png").convert()
        karta_vlivu = pygame.image.load("zdroje/obrazky/karty/zadni_strana_hrac5.png").convert()

        cilova_karta = pygame.transform.scale(cilova_karta, (self.velikost_karet, (self.velikost_karet - 150)))
        cilova_karta_rect = cilova_karta.get_rect()

        karta_vlivu = pygame.transform.scale(karta_vlivu, (self.velikost_karet, self.velikost_karet))
        karta_vlivu_rect = karta_vlivu.get_rect()

    def start(self):
        konec = False
        # hlavni herni cyklus
        while not konec:
            text = self.vedlejsi_font.render('Ahoj hraci', True, self.cerna)
            text_rect = text.get_rect()
            text_rect.center = (100, 200)
            self.obrazovka.blit(text, text_rect)

            while not self.data_fronta.empty():
                self.zpracuj_data(self.data_fronta.get())

            # obrazovka.blit(sipka, (stred-155, 10))
            # pygame.draw.rect(obrazovka, ramec_barva, ramec, ramec_tloustka)

            # obnova obrazovky
            pygame.display.update()
            self.clock.tick(self.fps)


# konec
pygame.quit()
