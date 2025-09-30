from typing import Tuple, Dict, List
from core.player import Player
from core.cards.card import Card
from typing import Literal
from gui.hand import CollectionInfo


modifyMode = Literal["add", "remove"]


class GameState:
    def __init__(self, players: List[Player]):
        self.players: List[Player] = players

        self.player_info = {player:
                            {
                                "has_summoned": False,
                                "has_toggled": False,
                                "held_cards": CollectionInfo([], player),
                                "graveyard_cards": CollectionInfo([], player),
                                "deck_cards": CollectionInfo([], player),
                                "active_traps": None,  # Track active trap effects
                            }
                            for player in players}

        # Game log (optional)
        self.log: List[str] = []

        # Game over state
        self.game_over = False

        # TODO: make board size dynamic
        self.field_matrix = []
        for _ in range(4):
            self.field_matrix.append([None for _ in range(5)])

        # TODO: refactor this later
        self.field_matrix_ownership = []
        for _ in range(2):
            self.field_matrix_ownership.append([players[1] for _ in range(5)])
        for _ in range(2):
            self.field_matrix_ownership.append([players[0] for _ in range(5)])

        self._player_cards = {player: [] for player in players}

    # def add_to_chain(self, effect: Dict):
    #     """Add an effect to the global chain"""
    #     self.chain.append(effect)

    def get_winner(self) -> Player | None:
        """Return the winning player if the game is over"""  # check is it inneed ?
        alive_players = [p for p in self.players if p.life_points > 0]
        if len(alive_players) == 1:
            return alive_players[0]
        return None

    def is_game_over(self):
        """Check if a player's life points reached 0"""
        for player in self.players:
            if player.life_points <= 0:
                self.game_over = True
                print(f"Game over! {player.name} lost.")
        return self.game_over

    def modify_field(self, mode: modifyMode, card: Card, pos: Tuple[int, int]):
        if mode == "add":
            '''add set pos for card in matrix'''
            self.field_matrix[pos[0]][pos[1]] = card
            self._player_cards[card.owner].append(card)
            card.pos_in_matrix = pos
        else:
            '''clear pos when remove'''
            card = self.field_matrix[pos[0]][pos[1]]
            if card is not None:
                self._player_cards[card.owner].remove(card)
            card.pos_in_matrix = None
            self.field_matrix[pos[0]][pos[1]] = None

    def get_player_cards(self, player):
        return self._player_cards[player]


'''check should put this inside effect tracker get effect tracker in this'''
