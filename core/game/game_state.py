from typing import Tuple, Dict, List
from core.player import Player
from core.cards.card import Card
from typing import Literal

modifyMode = Literal["add", "remove"]


class GameState:
    def __init__(self, players: List[Player]):
        self.players: List[Player] = players

        # Global effect stack (chain)
        # Each dict can store effect info, source card, targets, etc.
        self.chain: List[Dict] = []

        # Global flags or statuses
        self.flags: Dict[str, bool] = {}  # e.g. {"end_phase_skipped": False}

        # Game log (optional)
        self.log: List[str] = []

        # Game over state
        self.game_over = False

        #TODO: make board size dynamic
        self.field_matrix = []
        for _ in range(4):
            self.field_matrix.append([None for _ in range(5)])

    def add_to_chain(self, effect: Dict):
        """Add an effect to the global chain"""
        self.chain.append(effect)

    def get_winner(self) -> Player | None:
        """Return the winning player if the game is over"""
        alive_players = [p for p in self.players if p.life_points > 0]
        if len(alive_players) == 1:
            return alive_players[0]
        return None

    def is_game_over(self, player: Player):
        """Check if a player's life points reached 0"""
        if player.life_points <= 0:
            self.game_over = True
            print(f"Game over! {player.name} lost.")
        return self.game_over

    def modify_field(self, mode: modifyMode, card: Card, pos: Tuple[int, int]):
        if mode == "add":
            self.field_matrix[pos[0]][pos[1]] = card
            '''add set pos for card in matrix'''
            card.pos_in_matrix = pos
        else:
            '''clear pos when remove'''
            self.field_matrix[pos[0]][pos[1]] = None
            card.pos_in_matrix = None