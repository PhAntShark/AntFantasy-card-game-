class GameControl:
    def __init__(self, matrix, game_engine):
        self.matrix = matrix
        self.game_engine = game_engine

    def handle_drop(self, card):
        if card.is_dropped:
            card.is_dropped = False
            pos = self.matrix.get_slot_at_pos(card.rect.center)
                    
            if pos and card.owner:
                # TODO: add handler for opponent also
                if pos[0] in [2, 3] and card.owner.is_opponent == False:
                    slot_rect = self.matrix.get_slot_rect(*pos)
                    card.rect.center = slot_rect.center
                    self.game_engine.summon_card(card.owner, card, pos)
                    card.is_dropped = False
                    card.is_draggable = False

            hands = [self.matrix.hands['my_hand'],
                     self.matrix.hands["opponent_hand"]]
            for hand in hands:
                hand.draw_cards()

            print(self.game_engine.game_state.field_matrix)
