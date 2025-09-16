from player import Player
from game_state import Game_State
from turn_manager import TurnManager
from rule_engine import RuleEngine
from card_unit import CardUnit

class GameEngine:
    def __init__(self, players: list[Player]):
        self.game_state = Game_State(players)
        self.turn_manager = TurnManager(players)
        self.rule_engine = RuleEngine(self.game_state)
        self.game_over = False
        self.players = players


    def draw_card(self, player: Player):
        """Player draws a card if allowed"""
        if self.rule_engine.can_draw(player):
            player.draw_random_card()
            print(f"{player.name} drew a card.")
            return True
        print(f"{player.name} cannot draw a card now.")
        return False

    def summon_card(self, player: Player, card: CardUnit):
        """Player summons a card from hand if allowed"""
        if self.rule_engine.can_summon(player, card):
            player.card_field_summon(card)
            print(f"{player.name} summoned {card.name}.")
            return True
        print(f"{player.name} cannot summon {card.name}.")
        return False
    
    def attack(self, attacker: Player, defender:Player, card: CardUnit, target):
        if self.rule_engine.can_attack(attacker, defender, card, target):
            #damage = card.atk
            self.resolve_battle(attacker, defender, target, card)
            return True
        print(f"{card.name} cannot attack {target.name if isinstance(target, Player) else target.name}.")
        return False

    def resolve_battle(self, attacker: Player, card: CardUnit, target):
        damage = card.atk
        """Resolve a battle between a card and a target (card or player)"""
        if isinstance(target, CardUnit):
            defender = target.owner
            if target.pos == 'attack':
                if card.atk > target.atk:
                    defender.life_points -= card.atk - target.atk
                    defender.add_grave_yard(target)
                    print(f"{target.name} destroyed! {defender.name} loses {damage} LP")
                elif card.atk < target.atk:
                    damage = target.atk - card.atk
                    attacker.life_points -= damage
                    attacker.add_grave_yard(card)
                    print(f"{card.name} destroyed! {attacker.name} loses {damage} LP")
                else:
                    attacker.add_grave_yard(card)
                    defender.add_grave_yard(target)
                    print(f"Both {card.name} and {target.name} destroyed.")
            else:  # defense position
                if card.atk > target.defe:
                    defender.add_grave_yard(target)
                    print(f"{target.name} destroyed in defense. No LP damage.")
                elif card.atk < target.defe:
                    damage = target.defe - card.atk
                    attacker.life_points -= damage
                    print(f"Attack failed. {attacker.name} loses {damage} LP.")
                else:
                    print("Attack tied defense. No effect.")
        else:  # direct attack to player
            target.life_points -= damage
            print(f"Direct attack! {target.name} loses {damage} LP.")


    def end_turn(self):
        """End current player's turn"""
        self.turn_manager.next_turn()
        self.game_state.next_turn()
        print(f"Turn {self.turn_manager.turn_count} ended.")



    def buff_effect(self, card: CardUnit, buff_value: int):
        """Apply a buff to a card"""
        card.atk += buff_value
        print(f"{card.name} gains {buff_value} ATK.")

    def debuff_effect(self, card: CardUnit, debuff_value: int):
        """Apply a debuff to a card"""
        card.atk -= debuff_value
        print(f"{card.name} loses {debuff_value} ATK.")

    def check_game_over(self, player: Player):
        """Check if a player's life points reached 0"""
        if player.life_points <= 0:
            self.game_over = True
            print(f"Game over! {player.name} lost.")
            return True
        return False

