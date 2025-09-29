from gui.card_gui import CardGUI


class RenderEngine:
    def __init__(self, screen):
        self.screen = screen
        self.sprites = {
            "hand": {},
            "matrix": {},
        }  # logic_card -> sprite

    def update(self, game_state, matrix):
        self.register_cards(game_state, matrix)

    def register_cards(self, game_state, matrix):
        self.register_hand(game_state, matrix)
        self.register_matrix(game_state, matrix)

    @staticmethod
    def sync_sprites(desired_set, sprite_dict, create_sprite, align_fn=None):
        """
        Ensure that sprite_dict matches desired_set by adding/removing as needed.

        - desired_set: set of cards from game state
        - sprite_dict: dict of current sprites for that zone
        - create_sprite: function(card) -> sprite
        - align_fn: optional function() called after changes
        """

        existing_set = set(sprite_dict.keys())

        to_add = desired_set - existing_set
        to_remove = existing_set - desired_set

        # Remove old sprites
        for card in to_remove:
            sprite = sprite_dict.pop(card)
            sprite.kill()

        # Add new sprites
        for card in to_add:
            sprite_dict[card] = create_sprite(card)

        # Run alignment if provided
        if align_fn and (to_add or to_remove):
            align_fn()

    def register_hand(self, game_state, matrix):
        current_cards = set()
        for player in game_state.players:
            current_cards.update(
                game_state.player_info[player]["held_cards"].cards)

        def make_hand_sprite(card):
            return CardGUI(card, size=(
                matrix.grid["slot_width"] / 2,
                matrix.grid["slot_height"]
            ))

        self.sync_sprites(
            desired_set=current_cards,
            sprite_dict=self.sprites["hand"],
            create_sprite=make_hand_sprite,
            align_fn=lambda: self.align_cards(matrix)
        )

    def register_matrix(self, game_state, matrix):
        current_cards = {
            card for row in game_state.field_matrix for card in row if card is not None
        }

        def make_matrix_sprite(card):
            # TODO: move monster card to generic card
            sprite = CardGUI(card, size=(
                matrix.grid["slot_width"] / 2,
                matrix.grid["slot_height"]
            ))
            sprite.rect.center = matrix.get_slot_rect(
                *card.pos_in_matrix).center
            return sprite

        self.sync_sprites(
            desired_set=current_cards,
            sprite_dict=self.sprites["matrix"],
            create_sprite=make_matrix_sprite
        )

    def align_cards(self, matrix):
        for hand in matrix.hands:
            hand.align(self.sprites["hand"])

    def draw(self):
        for group in self.sprites.values():
            for sprite in group.values():
                sprite.draw(self.screen)
