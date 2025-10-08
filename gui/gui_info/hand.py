import pygame
from gui.gui_info.game_area import GameArea


class CollectionInfo:
    def __init__(self, cards, player):
        self.cards = cards
        self.player = player

    def add(self, card):
        self.cards.append(card)

    def remove(self, card):
        self.cards.remove(card)


class HandUI(GameArea):
    def __init__(self, player, hand_info, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hand_info = hand_info
        self.player = player

        image_path = "assets/deck.png"
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, self.rect.size)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    # TODO: this might not be the best choice
    def align(self, sprites):
        for index, card_info in enumerate(self.hand_info.cards):
            card = sprites.get(card_info, None)
            if card:
                card.rect.topleft = (self.rect.x + index *
                                     card.rect.w, self.rect.y)
