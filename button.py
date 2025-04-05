class Button:
    def __init__(self, obrazovka, image, x_pos, y_pos, text_input, font, barva_vychozi, barva_hover):
        self.obrazovka = obrazovka
        self.image = image
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.font = font
        self.barva_hover = barva_hover
        self.barva = barva_vychozi
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.barva)
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self):
        self.obrazovka.blit(self.image, self.rect)
        self.obrazovka.blit(self.text, self.text_rect)

    def check_for_input(self, position):
        if (position[0] in range(self.rect.left, self.rect.right)
                and position[1] in range(self.rect.top, self.rect.bottom)):
            return True

    def change_color(self, position):
        if (position[0] in range(self.rect.left, self.rect.right)
                and position[1] in range(self.rect.top, self.rect.bottom)):
            self.text = self.font.render(self.text_input, True, self.barva_hover)
        else:
            self.text = self.font.render(self.text_input, True, self.barva)
