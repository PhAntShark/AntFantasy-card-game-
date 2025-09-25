from core.game.turn_manager import TurnManager
from core.player import Player
from core.cards.card import Card
from core.cards.monster_card import MonsterCard
from typing import Tuple, List


class RuleEngine:
    def __init__(self, turn_manager: TurnManager):
        self.turn_manager = turn_manager
        # self.toggle_counts = {player: 0 for player in turn_manager.players}
        self.has_toggle = {player: False for player in turn_manager.players}
        # self.max_toggle = 2

    def can_draw(self, player):
        current_player = self.turn_manager.get_current_player()
        return (
            current_player == player
            and len(player.held_cards) < 15)

    def can_summon(self,
                   player: Player,
                   card: Card,
                   matrix: List[List[None | Card]],
                   pos: Tuple[int, int]):
        current_player = self.turn_manager.get_current_player()
        return (
            current_player == player
            and card in player.held_cards
            and not player.has_summoned
            and matrix[pos[0]][pos[1]] is None
            and sum(1 for row in matrix for card in row
                    if card is not None and card.owner == player) < 10
        )

    def can_change_mode(self, player, card):
        return (
            self.turn_manager.get_current_player() == player
            and card in player.field_cards
        )

    def can_attack(self,
                   attacker: Player,
                   defender: Player,
                   card: MonsterCard,
                   target: MonsterCard | Player):
        current_player = self.turn_manager.get_current_player()
        if current_player != attacker:
            return False

        # check if attacking card is in attacker field
        if card.owner != attacker:
            return False

        if card.mode != "attack":
            return False

        # Checks if target is a monster card on opponent side
        if isinstance(target, MonsterCard):
            return target.owner == defender

        # Checks if the target is the opponent (direct hit)
        return target == defender

    # def can_toggle(self, player):
    #     current_player_toggle_count = self.toggle_counts.get(player, 0)
    #     return current_player_toggle_count < 2

    # def used_toggle(self, player):
    #     self.toggle_counts[player] = self.toggle_counts.get(player, 0) 
    #     if self.toggle_counts[player] < 2:
    #         self.toggle_counts[player] +=1
            

    # def next_turn(self):
    #     current_player = self.turn_manager.get_current_player
    #     self.toggle_counts[current_player] = 0 
    #     self.turn_manager.end_turn()
    
    
    def can_toggle(self, player):
        return not self.has_toggled.get(player, False)

    def used_toggle(self, player):
        self.has_toggled[player] = True

    def next_turn(self):
        # Reset toggles for all players at the start of a new turn
        self.has_toggled = {player: False for player in self.turn_manager.players}
        self.turn_manager.end_turn()
            

