from player import Player
from game_state import GameState
from turn_manager import TurnManager
from rule_engine import RuleEngine
from cards.monster_card import MonsterCard
from cards.card import Card


class GameEngine:
    def __init__(self, players: list[Player]):
        self.game_state = GameState(players)
        self.turn_manager = TurnManager(players)
        self.rule_engine = RuleEngine(self.game_state)
        self.players = players

    def draw_card(self, player: Player):
        """Player draws a card if allowed"""
        if self.rule_engine.can_draw(player):
            player.draw_random_card()
            print(f"{player.name} drew a card.")
            return True
        print(f"{player.name} cannot draw a card now.")
        return False

    def summon_card(self, player: Player, card: Card):
        """Player summons a card from hand if allowed"""
        if self.rule_engine.can_summon(player, card):
            player.summon(card)
            print(f"{player.name} summoned {card.name}.")
            return True
        print(f"{player.name} cannot summon {card.name}.")
        return False

    def attack(self,
               attacker: Player,
               defender: Player,
               card: MonsterCard,
               target: MonsterCard | Player):
        if self.rule_engine.can_attack(attacker, defender, card, target):
            self.resolve_battle(attacker, defender, target, card)
            return True
        print(f"{card.name} cannot attack {
              target.name if isinstance(target, Player) else target.name}.")
        return False

    def resolve_battle(self,
                       attacker: Player,
                       card: MonsterCard,
                       target: MonsterCard | Player):
        """Resolve a battle between a card and a target (card or player)"""
        if isinstance(target, MonsterCard):
            defender = target.owner
            if target.mode == 'attack':
                if card.atk > target.atk:
                    damage = abs(card.atk - target.atk)
                    defender.life_points -= damage
                    defender.add_grave_yard(target)
                    print(f"{target.name} destroyed! {
                          defender.name} loses {damage} LP")
                elif card.atk < target.atk:
                    damage = abs(target.atk - card.atk)
                    attacker.life_points -= damage
                    attacker.add_grave_yard(card)
                    print(f"{card.name} destroyed! {
                          attacker.name} loses {damage} LP")
                else:
                    attacker.add_grave_yard(card)
                    defender.add_grave_yard(target)
                    print(f"Both {card.name} and {target.name} destroyed.")
            else:  # defense position
                if card.atk > target.defend:
                    defender.add_grave_yard(target)
                    print(f"{target.name} destroyed in defense. No LP damage.")
                elif card.atk < target.defend:
                    damage = abs(target.defend - card.atk)
                    attacker.life_points -= damage
                    print(f"Attack failed. {attacker.name} loses {damage} LP.")
                else:
                    print("Attack tied defense. No effect.")
        else:  # direct attack to player
            damage = card.atk
            target.life_points -= damage
            print(f"Direct attack! {target.name} loses {damage} LP.")

    def end_turn(self):
        """End current player's turn"""
        self.turn_manager.next_turn()
        # self.game_state.next_turn()
        print(f"Turn {self.turn_manager.turn_count} ended.")

    def buff_effect(self, card: MonsterCard, buff_value: int):
        """Apply a buff to a card"""
        card.atk += buff_value
        print(f"{card.name} gains {buff_value} ATK.")

    def debuff_effect(self, card: MonsterCard, debuff_value: int):
        """Apply a debuff to a card"""
        card.atk -= debuff_value
        print(f"{card.name} loses {debuff_value} ATK.")
