from game_state import Game_State
from player import Player
from card_unit import CardUnit

class RuleEngine():
    def __init__(self, game_state:Game_State):
        self.game_state = game_state
        #self.card_alive = alive

    def can_draw(self, player):
        return( 
               self.game_state.current_player() == player 
               and len(player.held_cards) < 15)
            
    def can_summon(self, player:Player , card: CardUnit):
        return(
            self.game_state.current_player() == player 
            and card in player.held_cards
            and not player.player_summon 
            and len(player.field_cards) < 10
            )
  
    def can_change_position(self, player, card, new_pos):
        return(
            self.game_state.current_player() == player and 
            card in player.field_cards and 
            new_pos in ['attack', 'defense']
        )
    
    #def can_attack(self, attacker: Player, defender: Player, card: CardUnit, target):
            #return (
            #self.game_state.current_player() == 'attacker' and card in attacker.field_cards and 
            #(target in defender.field_cards or target == defender))
    
    def can_attack(self, attacker: Player, defender: Player, card: CardUnit, target):
        if self.game_state.current_player() != attacker:
            return False
        if card not in attacker.field_cards:
            return False
        if card.pos != "attack":
            return False
        if isinstance(target, CardUnit):
            return target in defender.field_cards
        return target == defender
    
    def can_updrage(self, card: CardUnit):
        return False