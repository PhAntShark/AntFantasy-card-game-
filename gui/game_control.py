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
        
    def get_hand_position(self, card, player):
        spacing = self.matrix.get_all_areas()['my_hand'] // player.can_draw()
        hand_rect = spacing + card.rect.topleft
        areas = self.matrix.get_all_areas()
        if card.is_opponent == False:
            hand_rect = areas["my_hand"]
        else:
            hand_rect = areas["opponent_hand"]
        return hand_rect
            
        

        





                
