from typing import Tuple

from core.cards.card import Card
from core.cards.monster_card import MonsterCard
from core.player import Player
from core.factory.monster_factory import MonsterFactory
from .game_state import GameState
from .rule_engine import RuleEngine
from .turn_manager import TurnManager


class GameEngine:
    def __init__(self, players: list[Player]):
        self.game_state = GameState(players)
        self.turn_manager = TurnManager(self.game_state)
        self.rule_engine = RuleEngine(self.game_state, self.turn_manager)

        self.players = players

        self.monster_factory = MonsterFactory()
        self.monster_factory.build()

    def give_init_cards(self, number: int):
        for player in self.players:
            for _ in range(number):
                self.draw_card(player, check=False)

    def draw_card(self, player: Player, check=True):
        """Player draws a card if allowed"""
        if not check or self.rule_engine.can_draw(player):
            card = self.monster_factory.load(player)
            self.game_state.player_info[player]["held_cards"].add(card)
            return True
        print(f"{player.name} cannot draw a card now.")
        return False

    def toggle_card(self, card):
        if self.rule_engine.can_toggle(card.owner, card):
            card.switch_position()
            self.game_state.player_info[card.owner]["has_toggled"] = True

    def summon_card(self, player: Player, card: Card, cell: Tuple[int, int]):
        """Player summons a card from hand if allowed"""
        if self.rule_engine.can_summon(player, card, self.game_state.field_matrix, cell):
            self.game_state.player_info[player]["held_cards"].remove(card)
            self.game_state.player_info[player]["has_summoned"] = True
            self.game_state.modify_field("add", card, cell)
            card.is_placed = True
            # TODO: the fuck does this do
            card.pos_in_matrix = cell
            print(f"{player.name} summoned {card.name}.")
            return True
        print(f"{player.name} cannot summon {card.name}.")
        return False

    def attack(self,
               attacker: Player,
               defender: Player,
               card: MonsterCard,
               target: MonsterCard | Player
               ):
        print(1)
        if self.rule_engine.can_attack(attacker, defender, card, target):
            self.resolve_battle(attacker, card, target)
            return True
        print(f"{card.name} cannot attack {
            target.name if isinstance(target, Player) else target.name}.")
        return False

    def move_card_to_graveyard(self, card):
        self.game_state.modify_field("remove", card, card.pos_in_matrix)
        self.game_state.player_info[card.owner]["graveyard_cards"].add(card)
        print(self.game_state.field_matrix)
        print(self.game_state.player_info[card.owner]["graveyard_cards"].cards)

    def resolve_battle(self,
                       attacker: Player,
                       card: MonsterCard,
                       target: MonsterCard | Player,
                       ):
        """Resolve a battle between a card and a target (card or player)"""
        if isinstance(target, MonsterCard):
            defender = target.owner
            if target.mode == 'attack':
                if card.atk > target.atk:
                    damage = abs(card.atk - target.atk)
                    defender.life_points -= damage
                    self.move_card_to_graveyard(target)
                    print(f"{target.name} destroyed! {
                        defender.name} loses {damage} LP")
                elif card.atk < target.atk:
                    damage = abs(target.atk - card.atk)
                    attacker.life_points -= damage
                    self.move_card_to_graveyard(card)
                    print(f"{card.name} destroyed! {
                        attacker.name} loses {damage} LP")
                else:
                    self.move_card_to_graveyard(card)
                    self.move_card_to_graveyard(target)
                    print(f"Both {card.name} and {target.name} destroyed.")
            else:  # defense position
                if card.atk > target.defend:
                    self.move_card_to_graveyard(target)
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
        card.has_attack = True

    def end_turn(self):
        """End current player's turn"""
        self.turn_manager.end_turn()
        self.draw_card(self.turn_manager.get_current_player())
        self.turn_manager.turn_count += 1
        print(f"Turn {self.turn_manager.turn_count} ended.")

    @staticmethod
    def buff_effect(card: MonsterCard, buff_value: int):
        """Apply a buff to a card"""
        card.atk += buff_value
        print(f"{card.name} gains {buff_value} ATK.")

    @staticmethod
    def debuff_effect(card: MonsterCard, debuff_value: int):
        """Apply a debuff to a card"""
        card.atk -= debuff_value
        print(f"{card.name} loses {debuff_value} ATK.")

    def upgrade_monster(self, player: Player, own_card: MonsterCard, target_card: MonsterCard):
        """Upgrade monsters of the same type to a higher level"""
        if not self.rule_engine.can_upgrade(player, own_card, target_card):
            print(f"{player.name} cannot upgrade {own_card} monsters to level {target_card}.")
            return False
              
        # Determine which monsters to remove based on upgrade requirements
        else:
            upgrade_position = target_card.pos_in_matrix
            
            # Remove the base monsters from the field and move them to graveyard
            self.move_card_to_graveyard(own_card)
            self.move_card_to_graveyard(target_card)
            
            # Create the upgraded monster
            upgraded_monster = self.monster_factory.load_by_type_and_level(
                player, own_card.type, own_card.level_star)
            
            if upgraded_monster is None:
                print(f"Could not create upgraded {own_card} monster of level {target_card}.")
                return False
            
            # Place the upgraded monster on the field
            if upgrade_position:
                self.game_state.modify_field("add", upgraded_monster, upgrade_position)
                upgraded_monster.is_placed = True
                upgraded_monster.pos_in_matrix = upgrade_position
                print(f"{player.name} upgraded {own_card} monsters to {upgraded_monster.name}!")
                return True
            
            return False

    def update_highlighted_cards(self, render_engine):
        """Update which cards should be highlighted for merging"""
        # Get all monsters on the field for the current player
        current_player = self.turn_manager.get_current_player()
        player_monsters = self.game_state.get_player_cards(current_player)
        
        # Get mergeable groups
        mergeable_groups = self.rule_engine.get_mergeable_groups(player_monsters)
        
        # Flatten all mergeable cards into a set
        highlighted_cards = set()
        for group in mergeable_groups:
            highlighted_cards.update(group)
        
        # Update highlight status for all matrix sprites
        for card, sprite in render_engine.sprites["matrix"].items():
            if hasattr(sprite, 'highlight'):
                sprite.highlight = card in highlighted_cards