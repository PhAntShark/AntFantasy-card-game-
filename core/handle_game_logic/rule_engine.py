from core.handle_game_logic.turn_manager import TurnManager
from core.game_info.game_state import GameState
from core.player import Player
from core.cards.card import Card
from core.cards.monster_card import MonsterCard
from typing import Tuple, List


class RuleEngine:
    def __init__(self, game_state: GameState, turn_manager: TurnManager):
        self.turn_manager = turn_manager
        self.game_state = game_state

    def can_draw(self, player):
        current_player = self.turn_manager.get_current_player()
        return (
            current_player == player
            and len(self.game_state.player_info[player]["held_cards"].cards) < 10)

    def can_summon(self,
                   player: Player,
                   card: Card,
                   matrix: List[List[None | Card]],
                   pos: Tuple[int, int]):
        current_player = self.turn_manager.get_current_player()

        return (
            current_player == player
            and card in self.game_state.player_info[player]["held_cards"].cards
            and ((card.ctype == "monster" and not self.game_state.player_info[player]["has_summoned_monster"])
                 or (card.ctype == "trap" and not self.game_state.player_info[player]["has_summoned_trap"]))
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
                   target: MonsterCard | Player,
                   ):
        current_player = self.turn_manager.get_current_player()

        if current_player != attacker:
            return False

        # check if attacking card is in attacker field
        if card.owner != attacker:
            return False

        if card.mode != "attack":
            return False

        if card.has_attack:
            return False

        # Checks if target is a monster card on opponent side
        if isinstance(target, MonsterCard):
            return target.owner == defender

        # Check when target is the opponent player (direct hit)
        cards = self.game_state.get_player_cards(defender)

        for card in cards:
            if card.ctype == "monster":
                return False

        return target == defender

    def can_toggle(self, player, card):
        if self.turn_manager.get_current_player() != player:
            return False
        if card.owner != player:
            return False
        return not self.game_state.player_info[player]["has_toggled"]

    def can_upgrade(self, player: Player, own_card: MonsterCard, target_card: MonsterCard) -> bool:
        """Check if player can upgrade monsters of given type to target level"""
        current_player = self.turn_manager.get_current_player()
        if current_player != player:
            return False

        if own_card.level_star != target_card.level_star:
            return False

        if own_card.owner != player or target_card.owner != player:
            return False

        if not isinstance(own_card, MonsterCard) or not isinstance(target_card, MonsterCard):
            return False

        if own_card.type != target_card.type:
            return False

        if own_card == target_card:
            return False

        return True

    @staticmethod
    def get_mergeable_groups(player, monsters):
        """Get groups of monsters that can be merged for upgrades"""
        if not monsters:
            return {}

        # Group monsters by type and level
        groups = {}
        for monster in monsters:
            if isinstance(monster, MonsterCard):
                key = (player, monster.type, monster.level_star)
                if key not in groups:
                    groups[key] = []
                groups[key].append(monster)

        return groups

    def next_turn(self):
        # Reset toggles for all players at the start of a new turn
        self.has_toggled = {
            player: False for player in self.turn_manager.players}
        self.turn_manager.end_turn()
