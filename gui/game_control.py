class GameControl:
    def __init__(self, matrix):
        self.matrix = matrix     

    def handle_drop(self, card):
        if card.is_dropped:
            pos = self.matrix.get_slot_at_pos(card.rect.center)

            if pos and card.owner:
                if pos[0] in [2, 3] and card.owner.is_opponent == False:
                    slot_rect = self.matrix.get_slot_rect(*pos)
                    card.rect.center = slot_rect.center
                    card.is_dropped = False
                    card.is_draggable = False
                    return
            
            
            hand = self.matrix.get_all_areas()['my_hand']
            card.rect.topleft = (hand.x, hand.y)
            card.is_dropped = False

                
