from core.handle_game_logic.turn_manager import TurnManager
from core.game_info.game_state import GameState
from core.player import Player
from core.cards.card import Card
from core.cards.monster_card import MonsterCard
from typing import Tuple, List
import logging


class RuleEngine:
    def __init__(self, game_state: GameState, turn_manager: TurnManager):
        self.turn_manager = turn_manager
        self.game_state = game_state
        self.max_hand_cards = 10
        self.max_stats = 9999

        self.logger = logging.getLogger("GameEngine")
        self.logger.info("RuleEngine initialized")

    def can_draw(self, player) -> bool:
        """Check if player can draw a card."""
        current_player = self.turn_manager.get_current_player()
        hand_size = len(
            self.game_state.player_info[player]["held_cards"].cards)

        # Validation checks
        if current_player != player:
            self.logger.debug(f"[RULE] {player.name} cannot draw: Not their turn (current: {
                              current_player.name})")
            return False

        if hand_size >= self.max_hand_cards:
            self.logger.debug(f"[RULE] {player.name} cannot draw: Hand full ({
                              hand_size}/{self.max_hand_cards})")
            return False

        return True

    def can_summon(self,
                   player: Player,
                   card: Card,
                   matrix: List[List[None | Card]],
                   pos: Tuple[int, int]) -> bool:
        """Check if player can summon a card."""
        current_player = self.turn_manager.get_current_player()

        # Check if it's player's turn
        if current_player != player:
            self.logger.debug(f"[RULE] {player.name} cannot summon {
                              card.name}: Not their turn (current: {current_player.name})")
            return False

        # Check if card is in hand
        if card not in self.game_state.player_info[player]["held_cards"].cards:
            self.logger.debug(f"[RULE] {player.name} cannot summon {
                              card.name}: Card not in hand")
            return False

        # Check summon type restrictions
        if card.ctype == "monster":
            if self.game_state.player_info[player]["has_summoned_monster"]:
                self.logger.debug(f"[RULE] {player.name} cannot summon {
                                  card.name}: Already summoned monster this turn")
                return False
        elif card.ctype == "trap":
            if self.game_state.player_info[player]["has_summoned_trap"]:
                self.logger.debug(f"[RULE] {player.name} cannot summon {
                                  card.name}: Already summoned trap this turn")
                return False
        else:
            self.logger.warning(f"[RULE] Unknown card type for {
                                card.name}: {card.ctype}")
            return False

        # Check position validity
        if pos is None:
            # Pos of None is handled by caller wrapper
            return False

        row, col = pos
        if not (0 <= row < len(matrix) and 0 <= col < len(matrix[0])):
            self.logger.debug(f"[RULE] {player.name} cannot summon {
                              card.name}: Position {pos} out of bounds")
            return False

        if matrix[row][col] is not None:
            existing = matrix[row][col]
            self.logger.debug(f"[RULE] {player.name} cannot summon {
                              card.name}: Position {pos} occupied by {existing.name}")
            return False

        # Check max cards on field
        player_card_count = sum(1 for row in matrix for cell_card in row
                                if cell_card is not None and cell_card.owner == player)
        if player_card_count >= 10:
            self.logger.debug(f"[RULE] {player.name} cannot summon {
                              card.name}: Field full ({player_card_count}/10)")
            return False

        self.logger.debug(f"[RULE] ✓ {player.name} can summon {
                          card.name} at {pos}")
        return True

    def can_change_mode(self, player, card) -> bool:
        """Check if player can change card mode."""
        current_player = self.turn_manager.get_current_player()

        if current_player != player:
            self.logger.debug(
                f"[RULE] {player.name} cannot change mode: Not their turn")
            return False

        if card not in player.field_cards:
            self.logger.debug(f"[RULE] {player.name} cannot change mode for {
                              card.name}: Card not in field")
            return False

        return True

    def can_attack(self,
                   attacker: Player,
                   defender: Player,
                   card: MonsterCard,
                   target: MonsterCard | Player) -> bool:
        """Check if an attack is valid."""
        current_player = self.turn_manager.get_current_player()

        # Cannot attack on first turn
        if self.turn_manager.turn_count == 1 and current_player:
            self.logger.debug(f"[RULE] {attacker.name} cannot attack with {
                              card.name}: Cannot attack on turn 1")
            return False

        # Must be attacker's turn
        if current_player != attacker:
            self.logger.debug(f"[RULE] {
                              attacker.name} cannot attack: Not their turn (current: {current_player.name})")
            return False

        # Card must belong to attacker
        if card.owner != attacker:
            self.logger.debug(f"[RULE] {attacker.name} cannot attack with {
                              card.name}: Card belongs to {card.owner.name}")
            return False

        # Card must be in attack position
        if card.mode != "attack":
            self.logger.debug(f"[RULE] {attacker.name} cannot attack with {
                              card.name}: Card in {card.mode} mode")
            return False

        # Card cannot have already attacked
        if card.has_attack:
            self.logger.debug(f"[RULE] {attacker.name} cannot attack with {
                              card.name}: Already attacked this turn")
            return False

        # If attacking a monster
        if isinstance(target, MonsterCard):
            if target.owner != defender:
                self.logger.debug(f"[RULE] {attacker.name} cannot attack {
                                  target.name}: Target belongs to {target.owner.name}, not defender {defender.name}")
                return False
            self.logger.debug(f"[RULE] ✓ {attacker.name} can attack {
                              target.name} with {card.name}")
            return True

        # If direct attack to player
        if target == defender:
            # Check if defender has any monsters
            defender_cards = self.game_state.get_player_cards(defender)
            for def_card in defender_cards:
                if def_card.ctype == "monster":
                    self.logger.debug(f"[RULE] {attacker.name} cannot direct attack: {
                                      defender.name} has monsters on field")
                    return False

            self.logger.debug(f"[RULE] ✓ {attacker.name} can direct attack {
                              defender.name} with {card.name}")
            return True

        self.logger.debug(
            f"[RULE] {attacker.name} cannot attack: Invalid target")
        return False

    def can_toggle(self, player, card) -> bool:
        """Check if player can toggle card position."""
        current_player = self.turn_manager.get_current_player()

        if current_player != player:
            self.logger.debug(f"[RULE] {player.name} cannot toggle {
                              card.name}: Not their turn")
            return False

        if card.owner != player:
            self.logger.debug(f"[RULE] {player.name} cannot toggle {
                              card.name}: Card belongs to {card.owner.name}")
            return False

        if self.game_state.player_info[player]["has_toggled"]:
            self.logger.debug(f"[RULE] {player.name} cannot toggle {
                              card.name}: Already toggled this turn")
            return False

        self.logger.debug(f"[RULE] ✓ {player.name} can toggle {card.name}")
        return True

    def can_upgrade(self, player: Player, own_card: MonsterCard, target_card: MonsterCard) -> bool:
        """Check if player can upgrade monsters of given type to target level."""
        current_player = self.turn_manager.get_current_player()

        if current_player != player:
            self.logger.debug(f"[RULE] {
                              player.name} cannot upgrade: Not their turn (current: {current_player.name})")
            return False

        if own_card.ctype != 'monster' or target_card.ctype != 'monster':
            self.logger.debug(f"[RULE] {player.name} cannot upgrade: Cards are not monsters ({
                              own_card.ctype}, {target_card.ctype})")
            return False

        if own_card.level_star != target_card.level_star:
            self.logger.debug(f"[RULE] {player.name} cannot upgrade {own_card.name} + {target_card.name}: "
                              f"Level mismatch (Lv{own_card.level_star} vs Lv{target_card.level_star})")
            return False

        if own_card.owner != player or target_card.owner != player:
            owners = f"{own_card.owner.name}, {target_card.owner.name}"
            self.logger.debug(f"[RULE] {
                              player.name} cannot upgrade: Cards don't belong to player (owners: {owners})")
            return False

        if not isinstance(own_card, MonsterCard) or not isinstance(target_card, MonsterCard):
            self.logger.debug(
                f"[RULE] {player.name} cannot upgrade: Cards are not MonsterCard instances")
            return False

        if own_card.type != target_card.type:
            self.logger.debug(f"[RULE] {player.name} cannot upgrade {own_card.name} + {target_card.name}: "
                              f"Type mismatch ({own_card.type} vs {target_card.type})")
            return False

        if own_card == target_card:
            self.logger.debug(
                f"[RULE] {player.name} cannot upgrade: Same card instance")
            return False

        self.logger.debug(f"[RULE] ✓ {player.name} can upgrade {own_card.name} + {target_card.name} "
                          f"(Type: {own_card.type}, Lv{own_card.level_star} → Lv{own_card.level_star + 1})")
        return True

    @staticmethod
    def get_mergeable_groups(player, monsters):
        """Get groups of monsters that can be merged for upgrades."""
        if not monsters:
            return {}

        logger = logging.getLogger("GameEngine")

        # Group monsters by type and level
        groups = {}
        for monster in monsters:
            if isinstance(monster, MonsterCard):
                key = (player, monster.type, monster.level_star)
                if key not in groups:
                    groups[key] = []
                groups[key].append(monster)

        # Log mergeable groups
        mergeable_count = sum(
            1 for group in groups.values() if len(group) >= 2)
        if mergeable_count > 0:
            logger.debug(f"[RULE] Found {
                         mergeable_count} mergeable groups for {player.name}:")
            for (p, mtype, level), cards in groups.items():
                if len(cards) >= 2:
                    card_names = ", ".join([c.name for c in cards])
                    logger.debug(
                        f"  - Type: {mtype}, Lv{level}: {len(cards)} cards ({card_names})")

        return groups

    def next_turn(self):
        """Advance to next turn and reset turn-based flags."""
        # Reset toggles for all players at the start of a new turn
        self.has_toggled = {
            player: False for player in self.turn_manager.players}

        self.logger.info("[RULE] Turn advanced, flags reset")
        self.turn_manager.end_turn()

    def validate_game_rules(self) -> List[str]:
        """Validate overall game rules and return any violations found."""
        violations = []

        # Check each player's state
        for player in self.game_state.players:
            info = self.game_state.player_info[player]

            # Check hand size
            hand_size = len(info["held_cards"].cards)
            if hand_size > self.max_hand_cards:
                violations.append(f"{player.name} has {
                                  hand_size} cards in hand (max: {self.max_hand_cards})")

            # Check field card count
            field_count = len(self.game_state.get_player_cards(player))
            if field_count > 10:
                violations.append(f"{player.name} has {
                                  field_count} cards on field (max: 10)")

            # Validate card positions
            for card in self.game_state.get_player_cards(player):
                if card.pos_in_matrix is None:
                    violations.append(
                        f"{card.name} on field but pos_in_matrix is None")
                else:
                    row, col = card.pos_in_matrix
                    field_card = self.game_state.field_matrix[row][col]
                    if field_card != card:
                        violations.append(f"{card.name} position mismatch: reports {
                                          card.pos_in_matrix} but field has {field_card.name if field_card else 'None'}")

        if violations:
            self.logger.warning(f"[RULE] ⚠️ Game rule violations detected:")
            for violation in violations:
                self.logger.warning(f"  - {violation}")

        return violations
