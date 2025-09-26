from gui.monster_card import MonsterCard


class RenderEngine:
    def __init__(self, screen):
        self.screen = screen
        self.sprites = {}  # logic_card -> sprite

    def update(self, game_state, matrix):
        self.register_cards(game_state, matrix)

    def register_cards(self, game_state, matrix):
        for _, info in game_state.player_info.items():
            for card in info["held_cards"].cards:
                if card not in self.sprites:
                    sprite = MonsterCard(card, size=(
                        matrix.grid["slot_width"]/2, matrix.grid["slot_height"]))
                    self.sprites[card] = sprite
                    self.align_cards(matrix)

    def align_cards(self, matrix):
        for hand in matrix.hands:
            hand.align(self.sprites)

    def draw(self):
        for sprite in self.sprites.values():
            sprite.draw(self.screen)
