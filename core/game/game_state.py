from typing import List, Dict
from player import Player
from turn_manager import TurnManager
# from cards.card import Card


class GameState:
    def __init__(self, players: List[Player]):
        self.players: List[Player] = players
        self.turn_manager: TurnManager = TurnManager(players)

        # Global effect stack (chain)
        # Each dict can store effect info, source card, targets, etc.
        self.chain: List[Dict] = []

        # Global flags or statuses
        self.flags: Dict[str, bool] = {}  # e.g. {"end_phase_skipped": False}

        # Game log (optional)
        self.log: List[str] = []

        # Game over state
        self.game_over = False

    def add_to_chain(self, effect: Dict):
        """Add an effect to the global chain"""
        self.chain.append(effect)

    def resolve_chain(self):
        """Resolve all effects in LIFO order"""
        while self.chain:
            effect = self.chain.pop()
            # effect resolution logic goes here
            self.log.append(f"Resolved effect: {effect}")

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
