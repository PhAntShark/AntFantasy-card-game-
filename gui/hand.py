from pygame import Rect
from pygame import draw


class Hand:
    def __init__(self, x, y, w, h, color, lwidth, player):
        self.rect = Rect(x, y, w, h)
        self.color = color
        self.lwidth = lwidth
        self.player = player

    def draw(self, screen):
        self.draw_outline(screen)

    def draw_outline(self, screen):
        draw.rect(screen, self.color, self.rect, self.lwidth)

    def draw_cards(self):
        for index, card in enumerate(self.player.held_cards):
            card.rect.topleft = (self.rect.x + index *
                                 card.rect.w, self.rect.y)
