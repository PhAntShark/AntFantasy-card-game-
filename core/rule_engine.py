from game_state import Game_State
from player import Player
from card import Card

class RuleEngine():
    def __init__(self, game_state:Game_State):
        self.game_state = game_state
        #self.card_alive = alive

    def can_draw(self, card, player):
        return( 
               self.game_state.current_player() == player 
               and len(player.held_cards) < 15)
            
    def can_summon(self, player:Player , card: Card):
        return(
            self.game_state.current_player() == player 
            and card in player.held_cards() 
            and not player.player_summon() == True 
            and len(player.field_cards) < 10
            )
  
    def can_change_position(self, player, card, new_pos):
        return(
            self.game_state.current_player() == player and 
            card in player.field_cards and 
            new_pos in ['attacker', 'defender']
        )
    
    def can_attack(self, attacker: Player, defender: Player, card: Card, target):
            return (
            self.game_state.current_player() == 'attacker' and card in attacker.field_cards and 
            (target in defender.field_cards or target == defender))
        
    def can_updrage(self, card: Card):
        pass    