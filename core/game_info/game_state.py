from typing import Tuple, List, Optional, Literal
from random import choice
from core.player import Player
from core.cards.card import Card
from gui.gui_info.hand import CollectionInfo
import logging

ModifyMode = Literal["add", "remove"]


class GameState:
    def __init__(self, players: List[Player], rows: int = 4, cols: int = 5):
        self.players: List[Player] = players
        self.game_over: bool = False
        self.max_cards: int = 10

        self.logger = logging.getLogger("GameEngine")
        self.rows = rows
        self.cols = cols

        self.reset()
        self.logger.info(f"GameState initialized: {rows}x{
                         cols} field, {len(players)} players")

    # -------------------------
    # Game state utilities
    # -------------------------
    def reset(self):
        # Initialize player-related info
        self.player_info = {
            player: {
                "has_summoned_trap": False,
                "has_summoned_monster": False,
                "has_toggled": False,
                "held_cards": CollectionInfo([], player),
                "graveyard_cards": CollectionInfo([], player),
                "deck_cards": CollectionInfo([], player),
                "active_traps": [],
            }
            for player in self.players
        }
        self.game_over = False

        # Initialize the field
        self.field_matrix: List[List[Optional[Card]]] = [
            [None for _ in range(self.cols)] for _ in range(self.rows)]

        # Ownership matrix (top half = players[1], bottom half = players[0])
        self.field_matrix_ownership: List[List[Player]] = [
            [self.players[1] for _ in range(self.cols)] for _ in range(self.rows // 2)
        ] + [
            [self.players[0] for _ in range(self.cols)] for _ in range(self.rows // 2)
        ]

        # Track which cards each player has on the field
        self._player_cards: dict[Player, List[Card]] = {
            player: [] for player in self.players}

    def is_game_over(self) -> bool:
        """Check if any player's life points reached 0 and mark the game as over."""
        for player in self.players:
            if player.life_points <= 0:
                self.game_over = True
                self.logger.info(f"{'='*60}")
                self.logger.info(
                    f"GAME OVER! {player.name} defeated (LP: {player.life_points})")

                # Log winner
                winner = [p for p in self.players if p != player][0] if len(
                    self.players) == 2 else None
                if winner:
                    self.logger.info(
                        f"Winner: {winner.name} (LP: {winner.life_points})")
                self.logger.info(f"{'='*60}")
                break
        return self.game_over

    def modify_field(self, mode: ModifyMode, card: Card, pos: Tuple[int, int]) -> None:
        """Add or remove a card from the field."""
        row, col = pos

        if mode == "add":
            # Validation checks with logging
            if not (0 <= row < self.rows and 0 <= col < self.cols):
                self.logger.error(f"❌ FIELD MODIFY FAILED: Invalid position {
                                  pos} for field size {self.rows}x{self.cols}")
                return

            if self.field_matrix[row][col] is not None:
                existing = self.field_matrix[row][col]
                self.logger.warning(f"⚠️ FIELD MODIFY WARNING: Position {pos} already occupied by {
                                    existing.name} (Owner: {existing.owner.name})")
                return

            # Check ownership
            expected_owner = self.field_matrix_ownership[row][col]
            if card.owner != expected_owner:
                self.logger.error(f"❌ FIELD MODIFY FAILED: {card.owner.name} trying to place {
                                  card.name} at {pos}, but position belongs to {expected_owner.name}")
                return

            self.field_matrix[row][col] = card
            self._player_cards[card.owner].append(card)
            card.pos_in_matrix = pos

            self.logger.info(f"  ➕ Field modified: {card.name} placed at {
                             pos} by {card.owner.name}")

        elif mode == "remove":
            if not (0 <= row < self.rows and 0 <= col < self.cols):
                self.logger.error(f"❌ FIELD MODIFY FAILED: Invalid position {
                                  pos} for removal")
                return

            existing_card = self.field_matrix[row][col]
            if existing_card:
                try:
                    self._player_cards[existing_card.owner].remove(
                        existing_card)
                    self.logger.info(f"  ➖ Field modified: {existing_card.name} removed from {
                                     pos} (Owner: {existing_card.owner.name})")
                except ValueError:
                    self.logger.error(f"❌ FIELD MODIFY ERROR: {existing_card.name} at {
                                      pos} not found in {existing_card.owner.name}'s field cards")
                existing_card.pos_in_matrix = None
            else:
                self.logger.warning(
                    f"⚠️ FIELD MODIFY WARNING: Attempted to remove card from empty position {pos}")

            self.field_matrix[row][col] = None

    def get_player_cards(self, player: Player) -> List[Card]:
        """Return all cards a player currently has on the field."""
        cards = self._player_cards[player]
        return cards

    def get_random_empty_slot(self, player: Player) -> Optional[Tuple[int, int]]:
        """Return a random empty slot in the field owned by the player, or None if full."""
        empty_slots = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if self.field_matrix[r][c] is None and self.field_matrix_ownership[r][c] == player
        ]

        if not empty_slots:
            self.logger.warning(
                f"⚠️ No empty slots available for {player.name}")
            return None

        slot = choice(empty_slots)
        self.logger.debug(f"Random empty slot selected for {player.name}: {
                          slot} (from {len(empty_slots)} available)")
        return slot

    def get_opponent(self, player):
        """Get the opponent of the given player."""
        for gplayer in self.players:
            if player != gplayer:
                return gplayer
        return None

    def get_cards_typed(self, player, ctype):
        """Get all cards of a specific type for a player."""
        cards = [card for card in self.get_player_cards(
            player) if isinstance(card, ctype)]
        return cards

    def get_field_summary(self, player: Player) -> dict:
        """Get a summary of a player's field state for logging."""
        from core.cards.monster_card import MonsterCard
        from core.cards.trap_card import TrapCard

        cards = self.get_player_cards(player)
        monsters = [c for c in cards if isinstance(c, MonsterCard)]
        traps = [c for c in cards if isinstance(c, TrapCard)]

        return {
            "total_cards": len(cards),
            "monsters": len(monsters),
            "traps": len(traps),
            "hand_size": len(self.player_info[player]["held_cards"].cards),
            "graveyard_size": len(self.player_info[player]["graveyard_cards"].cards),
            "has_summoned_monster": self.player_info[player]["has_summoned_monster"],
            "has_summoned_trap": self.player_info[player]["has_summoned_trap"],
            "has_toggled": self.player_info[player]["has_toggled"],
        }

    def log_field_state(self):
        """Log the current field state in a readable format."""
        self.logger.info(f"\n{'='*60}")
        self.logger.info("FIELD STATE")
        self.logger.info(f"{'='*60}")

        for r in range(self.rows):
            row_str = []
            for c in range(self.cols):
                card = self.field_matrix[r][c]
                owner = self.field_matrix_ownership[r][c]
                if card:
                    row_str.append(f"[{card.name[:10]:10s}|{owner.name[:3]}]")
                else:
                    row_str.append(f"[{'Empty':10s}|{owner.name[:3]}]")
            self.logger.info(f"Row {r}: {' '.join(row_str)}")

        self.logger.info(f"{'='*60}\n")

    def validate_card_placement(self, card: Card, pos: Tuple[int, int]) -> Tuple[bool, str]:
        """Validate if a card can be placed at a given position. Returns (valid, reason)."""
        row, col = pos

        # Check bounds
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return False, f"Position {pos} out of bounds (field size: {self.rows}x{self.cols})"

        # Check if slot is empty
        if self.field_matrix[row][col] is not None:
            existing = self.field_matrix[row][col]
            return False, f"Position {pos} occupied by {existing.name} (Owner: {existing.owner.name})"

        # Check ownership
        expected_owner = self.field_matrix_ownership[row][col]
        if card.owner != expected_owner:
            return False, f"Position {pos} belongs to {expected_owner.name}, not {card.owner.name}"

        # Check if player has reached max cards
        player_card_count = len(self._player_cards[card.owner])
        if player_card_count >= self.max_cards:
            return False, f"{card.owner.name} already has max cards on field ({player_card_count}/{self.max_cards})"

        return True, "Valid placement"

    def has_slot_available(self, player):
        return len(self._player_cards[player]) < self.max_cards

    def get_card_by_id(self, player, id):
        for card in self._player_cards[player]:
            if id == card.id:
                return card
        return None
