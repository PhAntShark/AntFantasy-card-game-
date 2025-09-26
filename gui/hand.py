from gui.game_area import GameArea


class CollectionInfo:
    def __init__(self, cards, player):
        self.cards = cards
        self.player = player

    def add(self, card):
        self.cards.append(card)

    def remove(self, card):
        self.cards.remove(card)


class HandUI(GameArea):
    def __init__(self, hand_info, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hand_info = hand_info

    def align(self, sprites):
        for index, card_info in enumerate(self.hand_info.cards):
            card = sprites.get(card_info, None)
            if card:
                card.rect.topleft = (self.rect.x + index *
                                     card.rect.w, self.rect.y)
