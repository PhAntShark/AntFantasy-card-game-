import pygame
from gui.gui_info.game_area import GameArea
from gui.cache import load_image


class CollectionInfo:
    def __init__(self, cards, player):
        self.cards = cards
        self.player = player

    def __len__(self):
        return len(self.cards)

    def __iter__(self):
        return iter(self.cards)

    def add(self, card):
        self.cards.append(card)

    def remove(self, card):
        self.cards.remove(card)


class HandUI(GameArea):
    def __init__(self, player, hand_info, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hand_info = hand_info
        self.player = player
        self.last_count = len(self.hand_info.cards)

        image_path = "assets/deck.png"
        self.image = load_image(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, self.rect.size)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def align(self, sprites, check=False):
        # Skip if no card count change
        if check and len(self.hand_info.cards) == self.last_count:
            return

        for idx, card_info in enumerate(self.hand_info.cards):
            sprite = sprites.get(card_info.id)
            if not sprite:
                continue

            sprite.rect.topleft = (
                self.rect.x + idx * sprite.rect.w,
                self.rect.y
            )

        self.last_count = len(self.hand_info.cards)
