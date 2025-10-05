from typing import Tuple, List, Any
from core.factory.draw_system import DrawSystem
from core.cards.card import Card
from core.cards.monster_card import MonsterCard
from core.cards.spell_card import SpellCard
from core.cards.trap_card import TrapCard
from core.player import Player
from core.factory.monster_factory import MonsterFactory
from core.factory.spell_factory import SpellFactory
from core.factory.trap_factory import TrapFactory
from core.game_info.game_state import GameState
from .rule_engine import RuleEngine
from .turn_manager import TurnManager
from core.game_info.effect_tracker import EffectTracker, EffectType


class GameEngine:
    def __init__(self, players: List[Player]):
        self.game_state = GameState(players)
        self.effect_tracker = EffectTracker()
        self.turn_manager = TurnManager(self.game_state, self.effect_tracker)
        self.rule_engine = RuleEngine(self.game_state, self.turn_manager)
        self.draw_system = DrawSystem()
        self.players = players

        self.monster_factory = MonsterFactory()
        self.monster_factory.build()

        self.spell_factory = SpellFactory()
        self.spell_factory.build()

        self.trap_factory = TrapFactory()
        self.trap_factory.build()

    def give_init_cards(self, number: int):
        for player in self.players:
            for _ in range(number):
                self.draw_card(player, check=False)

    def draw_card(self, player: Player, check=True):
        """Player draws a card if allowed"""
        if not check or self.rule_engine.can_draw(player):
            card = self.draw_system.rate_card_draw(player)
            self.game_state.player_info[player]["held_cards"].add(card)
            return True
        print(f"{player.name} cannot draw a card now.")
        return False
                # cards = [self.monster_factory.load(player),
                #         self.spell_factory.load(player),
                #         self.trap_factory.load(player)]
                # card = random.choice(cards)
    def toggle_card(self, card):
        if self.rule_engine.can_toggle(card.owner, card) and card.ctype == "monster":
            card.switch_position()
            self.game_state.player_info[card.owner]["has_toggled"] = True

    def summon_card(self,
                    player: Player,
                    card: Card,
                    cell: Tuple[int, int]):
        """Player summons a card from hand if allowed"""
        if self.rule_engine.can_summon(player, card, self.game_state.field_matrix, cell):
            self.game_state.player_info[player]["held_cards"].remove(card)
            self.game_state.player_info[player]["has_summoned_monster"] = True
            self.game_state.modify_field("add", card, cell)
            card.is_placed = True
            # TODO: the fuck does this do
            card.pos_in_matrix = cell
            print(f"{player.name} summoned {card.name}.")
            self.check_summon_trap(card)
            return True
        print(f"{player.name} cannot summon {card.name}.")
        return False

    def attack(self,
               attacker: Player,
               defender: Player,
               card: MonsterCard,
               target: MonsterCard | Player
               ):
        if self.rule_engine.can_attack(attacker, defender, card, target):
            # Check for trap triggers before resolving battle
            # self.resolve_battle(attacker, card, target)

            if isinstance(target, MonsterCard):
                if self.check_trap_triggers(card, defender):
                    return True
            
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

    def upgrade_monster(self, player: Player, own_card: MonsterCard, target_card: MonsterCard):
        """Upgrade monsters of the same type to a higher level"""
        if not self.rule_engine.can_upgrade(player, own_card, target_card):
            print(f"{player.name} cannot upgrade {
                  own_card} monsters to level {target_card}.")
            return False

        # Determine which monsters to remove based on upgrade requirements
        else:
            upgrade_position = target_card.pos_in_matrix

            # Remove the base monsters from the field and move them to graveyard
            self.move_card_to_graveyard(own_card)
            self.move_card_to_graveyard(target_card)

            # Create the upgraded monster
            # Request the next level when creating the upgraded monster
            upgraded_monster = self.monster_factory.load_by_type_and_level(
                player, own_card.type, own_card.level_star + 1)

            if upgraded_monster is None:
                print(f"Could not create upgraded {
                      own_card} monster of level {target_card}.")
                return False

            # Place the upgraded monster on the field
            if upgrade_position:
                self.game_state.modify_field(
                    "add", upgraded_monster, upgrade_position)
                upgraded_monster.is_placed = True
                upgraded_monster.pos_in_matrix = upgrade_position
                print(f"{player.name} upgraded {
                      own_card} monsters to {upgraded_monster.name}!")
                return True

            return False

    def get_mergeable_cards(self, player: Player):
        """Get cards that can be merged for upgrades (pure logic)"""
        player_monsters = self.game_state.get_player_cards(player)
        mergeable_groups = self.rule_engine.get_mergeable_groups(
            player_monsters)

        # Flatten all mergeable cards into a set
        highlighted_cards = set()
        for group in mergeable_groups:
            highlighted_cards.update(group)

        return highlighted_cards

    def cast_spell(self, spell: SpellCard, target: Any = None):
        """Cast a spell card immediately"""
        if not isinstance(spell, SpellCard):
            return False
        
            # Resolve spell based on ability
        if spell.ability == "draw_two_cards":
            self.draw_card(spell.owner, check=False)
            self.draw_card(spell.owner, check=False)

        elif spell.ability == "buff_attack":
            self.effect_tracker.add_effect(
                EffectType.BUFF, target, "atk", 300, 3)

        elif spell.ability == "buff_defense":
            self.effect_tracker.add_effect(
                EffectType.BUFF, target, "defend", 300, 3)

        elif spell.ability == "destroy_trap":
            if target and target.ctype in ["trap"]:
                self.move_card_to_graveyard(target)
            else:
                return False

        elif spell.ability == "summon_monster_from_hand":
            self.rule_engine.game_state.player_info[spell.owner]['has_summoned_monster'] = False
            print('{spell.owner.name} summon extra nigga get on the field ')
            #return False

        # Move spell to graveyard after use
        self.game_state.player_info[spell.owner]["held_cards"].remove(spell)
        self.game_state.player_info[spell.owner]["graveyard_cards"].add(spell)

        return True

    def set_trap(self, trap: TrapCard, position: Tuple[int, int]):
        """Set a trap card face-down on the field"""
        if not isinstance(trap, TrapCard):
            return False

        if not self.rule_engine.can_summon(trap.owner, trap, self.game_state.field_matrix, position):
            return False


        # Place trap face-down
        self.game_state.player_info[trap.owner]["held_cards"].remove(trap)
        self.game_state.modify_field("add", trap, position)
        self.game_state.player_info[trap.owner]["has_summoned_trap"] = True
        trap.is_placed = True
        trap.is_face_down = True
        trap.pos_in_matrix = position

        return True

    def resolve_trap(self, trap: TrapCard, attacker: MonsterCard):
        """Resolve a trap card when triggered"""
        if not isinstance(trap, TrapCard) or not trap.is_face_down:
            return False

        trap.is_face_down = False  # Reveal the trap

        if trap.ability == "debuff_enemy_atk":
            self.effect_tracker.add_effect(
                EffectType.DEBUFF, attacker, "atk", 500, 3)

        elif trap.ability == "debuff_enemy_def":
            self.effect_tracker.add_effect(
                EffectType.DEBUFF, attacker, "defend", 500, 3)

        elif trap.ability == "dodge_attack":
            attacker.has_attack = True
            print(f'bo may ne/ dc r nhe con ch0/')
            self.move_card_to_graveyard(trap)
            return True  # Attack is negated
      
            
        elif trap.ability == "reflect_attack":
            # self.game_state.player_info[trap.owner]["active_traps"] = trap
            self.move_card_to_graveyard(attacker)
            self.move_card_to_graveyard(trap)
            print(f"{attacker.name}'s phai gi a phai phai phai chjuuuuu")
            return True  # Attacker is destroyed

        elif trap.ability == "debuff_summon":
            self.effect_tracker.add_effect(
                EffectType.DEBUFF, attacker, "atk", 500, 4
            )
            self.effect_tracker.add_effect(
                EffectType.DEBUFF, attacker, "defend", 500, 4
            )
            print(f"{attacker.name} is weakened by trap {trap.name} on summon")
            # Move trap to graveyard after activation
            self.move_card_to_graveyard(trap)
            return True

          
        return False  # Attack continues normally

    def check_trap_triggers(self, attacker: MonsterCard, defender: Player):
        """Check if any traps should be triggered by an attack"""
        # Get all face-down traps on the defender's field
        defender_cards = self.game_state.get_player_cards(defender)
        traps = [card for card in defender_cards
                 if isinstance(card, TrapCard) and card.is_face_down]

        for trap in traps:
            if self.resolve_trap(trap, attacker):
                return True  # Attack was negated or reflected
        return False  # Attack continues

    
    def check_summon_trap(self, card_summon: MonsterCard):
        card_summon_owner = card_summon.owner
        opponents = [player for player in self.players if player != card_summon_owner]

        for opponent in opponents:
            # Get all face-down traps on the opponent's field
            opponent_cards = self.game_state.get_player_cards(opponent)
            traps = [card for card in opponent_cards if isinstance(card, TrapCard) and card.is_face_down]
            for trap in traps[:]:
                if trap.ability == 'debuff_summon':
                    self.resolve_trap(trap, card_summon)
    
    def update_effects(self):
        """Update all active effects (call at end of each turn)"""
        self.effect_tracker.update_round()

    def end_turn(self):
        """End current player's turn"""
        for card in self.game_state.get_player_cards(self.turn_manager.get_current_player()):
            if isinstance(card, MonsterCard):
                card.has_attack = False
        self.update_effects()  # Update effects before ending turn
        self.turn_manager.end_turn()
        self.draw_card(self.turn_manager.get_current_player())
        print(f"Turn {self.turn_manager.turn_count} ended.")
