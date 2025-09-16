from game_state import GameState
from player import Player
from cards.card import Card
from cards.monster_card import MonsterCard


class RuleEngine():
    def __init__(self, game_state: GameState):
        self.game_state = game_state

    def can_draw(self, player):
        current_player = self.game_state.turn_manager.get_current_player()
        return (
            current_player == player
            and len(player.held_cards) < 15)

    def can_summon(self, player: Player, card: Card):
        current_player = self.game_state.turn_manager.get_current_player()
        return (
            current_player == player
            and card in player.held_cards
            and not player.has_summoned
            and len(player.field_cards) < 10
        )

    def can_change_mode(self, player, card):
        return (
            self.game_state.current_player() == player
            and card in player.field_cards
        )

    def can_attack(self,
                   attacker: Player,
                   defender: Player,
                   card: Card,
                   target: MonsterCard | Player):
        current_player = self.game_state.turn_manager.get_current_player()
        if current_player != attacker:
            return False

        if card not in attacker.field_cards:
            return False

        if card.mode != "attack":
            return False

        # Checks if target is a monster card on opponent side
        if isinstance(target, MonsterCard):
            return target in defender.field_cards

        # Checks if the target is the opponent (direct hit)
        return target == defender

    def can_updrage(self, card: MonsterCard):
        pass
