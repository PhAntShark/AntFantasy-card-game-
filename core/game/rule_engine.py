from core.game.turn_manager import TurnManager
from .game_state import GameState
from core.player import Player
from core.cards.card import Card
from core.cards.monster_card import MonsterCard
from typing import Tuple, List


class RuleEngine:
    def __init__(self, game_state: GameState, turn_manager: TurnManager):
        self.game_state = game_state
        self.turn_manager = turn_manager

    def can_draw(self, player):
        current_player = self.game_state.turn_manager.get_current_player()
        return (
            current_player == player
            and len(player.held_cards) < 15)

    def can_summon(self,
                   player: Player,
                   card: Card,
                   matrix: List[List[None | Card]],
                   pos: Tuple[int, int]):
        current_player = self.game_state.turn_manager.get_current_player()
        return (
            current_player == player
            and card in player.held_cards
            and not player.has_summoned
            and matrix[pos[1]][pos[0]] is not None
            and sum(1 for row in matrix for card in row if card.owner == player) < 10
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
        current_player = self.game_state.turn_manager.get_current_player()
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
