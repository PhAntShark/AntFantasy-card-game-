from core.arrow import DragArrow
class AttackControl:
        def __init__(self, matrix, game_engine):
                self.matrix = matrix
                self.game_engine = game_engine
                self.attacking_card = None
                self.arrow = None
                
        def start_attack(self,card):
                if card in self.matrix.get_slot_at_pos() and card.is_opponent == False and card in card.mode == 'attack':
                        self.attacking_card = card
                        self.arrow = DragArrow()
                        self.arrow_start = card.rect.center
                        self.arrow_end = card.rect.center
        

        def update_attack(self, pos):
                if self.arrow:
                        self.arrow.end_pos = pos 
        
        # def release_attack(self,pos):
        #         if self.arrow:
        #                 if pos[0] in self.matrix.get_slot_at_pos[0,1]:
        #                         .is_opponent == True
                           
                        
                        
        
                        

                
        
        
                