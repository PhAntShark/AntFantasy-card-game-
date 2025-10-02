import pygame


class CardPreview:
    def __init__(self,x, y , width, height, border_color, border_width = 2):
        self.rect = pygame.Rect(x, y, width, height)
        self.border_color = border_color
        self.border_width = border_width
        self.card = None
        
    def set_card(self, card_ui):
        self.card = card_ui

    def draw(self, screen):
        # draw background/border
        pygame.draw.rect(screen, self.border_color, self.rect, self.border_width)

        if self.card:
            card_img = pygame.transform.scale(self.card_image, self.rect.size)
            screen.blits(card_img, self.rect.topleft)