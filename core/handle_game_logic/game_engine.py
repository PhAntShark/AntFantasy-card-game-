from typing import Tuple, List, Any
from core.factory.draw_system import DrawSystem
from core.cards.monster_card import MonsterCard
from core.cards.spell_card import SpellCard
from core.cards.trap_card import TrapCard
from core.player import Player
from core.factory.monster_factory import MonsterFactory
from core.factory.spell_factory import SpellFactory
from core.factory.trap_factory import TrapFactory
from core.game_info.game_state import GameState
from core.handle_game_logic.rule_engine import RuleEngine
from core.handle_game_logic.turn_manager import TurnManager
from core.game_info.effect_tracker import EffectTracker, EffectType
from core.game_info.events import EventLogger, AttackEvent, TrapTriggerEvent, ToggleEvent, SpellActiveEvent, MergeEvent

import logging
from datetime import datetime
import builtins


def disable_print():
    builtins.print = lambda *a, **k: None


def setup_silent_logger(log_path: str = "logs/game_engine.log", level=logging.DEBUG):
    """Redirect all print() calls to a file-based logger instead of stdout."""
    import os
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logger = logging.getLogger("GameEngine")
    logger.setLevel(level)

    # Avoid adding multiple handlers (happens when reloading engine)
    if not logger.handlers:
        handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

    # Redirect built-in print() to logger.info()
    builtins.print = lambda *a, **k: logger.info(" ".join(str(x) for x in a))

    return logger


class GameEngine:
    def __init__(self,
                 players: List[Player],
                 verbose=True,
                 log_to_file: bool = False):
        self.game_state = GameState(players)
        self.effect_tracker = EffectTracker()
        self.turn_manager = TurnManager(self.game_state, self.effect_tracker)
        self.rule_engine = RuleEngine(self.game_state, self.turn_manager)
        self.draw_system = DrawSystem()
        self.event_logger = EventLogger()

        self.players = players

        self.monster_factory = MonsterFactory()
        self.monster_factory.build()

        self.spell_factory = SpellFactory()
        self.spell_factory.build()

        self.trap_factory = TrapFactory()
        self.trap_factory.build()

        self.start_hand_count = 5

        # --- Control verbosity ---
        if log_to_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H-%M-%S")
            log_path = f"logs/game_run_{timestamp}.log"
            self.logger = setup_silent_logger(log_path)
        elif not verbose:
            disable_print()
        else:
            self.logger = logging.getLogger("GameEngine")

        # Action counter for tracking
        self.action_counter = 0

    def reset(self):
        self.effect_tracker.clear_all_effects()
        self.event_logger.clear_events()
        self.game_state.reset()
        self.action_counter = 0
        for player in self.players:
            player.reset()

    def _log_action(self, action_type: str, player: Player, details: dict, success: bool):
        """Central logging method for all game actions"""
        self.action_counter += 1
        status = "SUCCESS" if success else "FAILED"
        log_msg = f"[Action #{self.action_counter}] [{
            status}] {action_type} by {player.name}"

        # Add relevant details
        detail_parts = []
        for key, value in details.items():
            detail_parts.append(f"{key}={value}")

        if detail_parts:
            log_msg += f" | {', '.join(detail_parts)}"

        if success:
            print(log_msg)
        else:
            print(f"❌ {log_msg}")

    def _log_game_state(self, context: str = ""):
        """Log current game state for debugging"""
        current_player = self.turn_manager.get_current_player()
        print(f"\n{'='*60}")
        print(f"GAME STATE {f'- {context}' if context else ''}")
        print(f"{'='*60}")
        print(f"Turn: {self.turn_manager.turn_count} | Current Player: {
              current_player.name}")

        for player in self.players:
            info = self.game_state.player_info[player]
            print(f"\n{player.name} (LP: {player.life_points}):")
            print(f"  Hand: {len(info['held_cards'])} cards")
            print(f"  Field: {len([c for c in self.game_state.get_player_cards(player) if isinstance(c, MonsterCard)])} monsters, "
                  f"{len([c for c in self.game_state.get_player_cards(player) if isinstance(c, TrapCard)])} traps")
            print(f"  Graveyard: {len(info['graveyard_cards'])} cards")
            print(f"  Has summoned: {info['has_summoned_monster']}")
            print(f"  Has toggled: {info['has_toggled']}")
        print(f"{'='*60}\n")

    def start_game(self):
        print("="*60)
        print("GAME STARTED")
        print("="*60)
        self.give_init_cards(self.start_hand_count)
        self._log_game_state("Initial Setup")

    def give_init_cards(self, number: int):
        for player in self.players:
            for _ in range(number):
                self.draw_card(player, check=False)

    # DEBUG FUNCTION
    def draw_specific_card(self, player, name, ctype):
        if ctype == "monster":
            card = self.monster_factory.load(player, name)
        elif ctype == "trap":
            card = self.trap_factory.load(player, name)
        elif ctype == "spell":
            card = self.spell_factory.load(player, name)
        else:
            return
        self.game_state.player_info[player]["held_cards"].add(card)
        print(f"[DEBUG] {player.name} received specific card: {name}")

    def draw_card(self, player: Player, check=True):
        """Player draws a card if allowed"""
        can_draw = not check or self.rule_engine.can_draw(player)

        if can_draw:
            card = self.draw_system.rate_card_draw(player)
            self.game_state.player_info[player]["held_cards"].add(card)
            card_type = type(card).__name__
            self._log_action("DRAW", player, {
                "card": card.name,
                "type": card_type,
                "hand_size": len(self.game_state.player_info[player]["held_cards"])
            }, True)
            return True

        # self._log_action("DRAW", player, {
            # "reason": "Cannot draw at this time"
        # }, False)
        return False

    def toggle_card(self, card):
        owner = card.owner
        can_toggle = self.rule_engine.can_toggle(
            owner, card) and card.ctype == "monster"

        if can_toggle:
            old_mode = card.mode
            new_mode = card.switch_position()
            self.event_logger.add_event(ToggleEvent(card=card, mode=new_mode))
            self.game_state.player_info[owner]["has_toggled"] = True

            self._log_action("TOGGLE", owner, {
                "card": card.name,
                "position": card.pos_in_matrix,
                "from": old_mode,
                "to": new_mode
            }, True)
            return True

        self.rule_engine.can_toggle(
            owner, card) and card.ctype == "monster"

        self._log_action("TOGGLE", owner, {
            "card": card.name,
            "reason": "Already toggled this turn or invalid card type"
        }, False)
        return False

    def summon_card(self,
                    player: Player,
                    card: MonsterCard | TrapCard,
                    cell: Tuple[int, int] | None,
                    check=True):
        """Player summons a card from hand if allowed"""
        can_summon = self.rule_engine.can_summon(
            player, card, self.game_state.field_matrix, cell) or not check

        if not can_summon:
            reasons = []
            if isinstance(card, MonsterCard):
                if self.game_state.player_info[player]["has_summoned_monster"]:
                    reasons.append("Already summoned monster this turn")
                if card not in self.game_state.player_info[player]["held_cards"]:
                    reasons.append("Card not in hand")

            self._log_action("SUMMON", player, {
                "card": card.name,
                "type": type(card).__name__,
                "target_cell": cell,
                "reason": ", ".join(reasons) if reasons else "Rule check failed"
            }, False)
            return False

        if cell is None:
            cell = self.game_state.get_random_empty_slot(player)
            if cell is None:
                self._log_action("SUMMON", player, {
                    "card": card.name,
                    "reason": "No empty slots available"
                }, False)
                return False

        self.game_state.player_info[player]["held_cards"].remove(card)
        self.game_state.player_info[player]["has_summoned_monster"] = True
        self.game_state.modify_field("add", card, cell)
        card.is_placed = True
        card.pos_in_matrix = cell

        details = {
            "card": card.name,
            "type": type(card).__name__,
            "position": cell
        }
        if isinstance(card, MonsterCard):
            details.update({
                "atk": card.atk,
                "def": card.defend,
                "level": card.level_star
            })

        self._log_action("SUMMON", player, details, True)
        self.check_summon_trap(card)
        return True

    def attack(self,
               attacker: Player,
               defender: Player,
               card: MonsterCard,
               target: MonsterCard | Player
               ):
        can_attack = self.rule_engine.can_attack(
            attacker, defender, card, target)

        if not can_attack:
            self.rule_engine.can_attack(
                attacker, defender, card, target)
            reasons = []
            if card.has_attack:
                reasons.append("Already attacked this turn")
            if not card.is_placed:
                reasons.append("Card not on field")
            if card.owner != attacker:
                reasons.append("Not your card")
            if card.mode != "attack":
                reasons.append("Cards cannot attack in defend mode")

            self._log_action("ATTACK", attacker, {
                "attacker_card": card.name,
                "target": target.name if hasattr(target, 'name') else f"Player {target.name}",
                "reason": ", ".join(reasons) if reasons else "Rule check failed"
            }, False)
            return False

        # Check for trap triggers before resolving battle
        if isinstance(target, MonsterCard):
            if self.check_trap_triggers(card, defender):
                self._log_action("ATTACK", attacker, {
                    "attacker_card": card.name,
                    "target": target.name,
                    "result": "Negated/Reflected by trap"
                }, True)
                return True

        self.resolve_battle(attacker, card, target)
        return True

    def move_card_to_graveyard(self, card):
        self.game_state.modify_field("remove", card, card.pos_in_matrix)
        self.game_state.player_info[card.owner]["graveyard_cards"].add(card)
        print(f"  → {card.name} moved to {card.owner.name}'s graveyard")

    def resolve_battle(self,
                       attacker: Player,
                       card: MonsterCard,
                       target: MonsterCard | Player,
                       ):
        """Resolve a battle between a card and a target (card or player)"""
        self.event_logger.add_event(AttackEvent(card=card, target=target))

        if isinstance(target, MonsterCard):
            defender = target.owner
            battle_details = {
                "attacker_card": f"{card.name} (ATK:{card.atk})",
                "target_card": f"{target.name} ({'ATK' if target.mode == 'attack' else 'DEF'}:{target.atk if target.mode == 'attack' else target.defend})"
            }

            if target.mode == 'attack':
                if card.atk > target.atk:
                    damage = abs(card.atk - target.atk)
                    defender.life_points -= damage
                    self.move_card_to_graveyard(target)
                    battle_details["result"] = f"Target destroyed, {
                        defender.name} -{damage}LP"
                elif card.atk < target.atk:
                    damage = abs(target.atk - card.atk)
                    attacker.life_points -= damage
                    self.move_card_to_graveyard(card)
                    battle_details["result"] = f"Attacker destroyed, {
                        attacker.name} -{damage}LP"
                else:
                    self.move_card_to_graveyard(card)
                    self.move_card_to_graveyard(target)
                    battle_details["result"] = "Both destroyed (tie)"
            else:  # defense position
                if card.atk > target.defend:
                    self.move_card_to_graveyard(target)
                    battle_details["result"] = "Target destroyed (defense pierced)"
                elif card.atk < target.defend:
                    damage = abs(target.defend - card.atk)
                    attacker.life_points -= damage
                    battle_details["result"] = f"Attack got reflected, {
                        attacker.name} -{damage}LP"
                else:
                    battle_details["result"] = "Attack tied defense (no effect)"

            self._log_action("ATTACK", attacker, battle_details, True)
        else:  # direct attack to player
            damage = card.atk
            target.life_points -= damage
            self._log_action("ATTACK", attacker, {
                "attacker_card": f"{card.name} (ATK:{card.atk})",
                "target": f"Player {target.name}",
                "damage": damage,
                "target_remaining_LP": target.life_points
            }, True)

        card.has_attack = True

    def upgrade_monster(self,
                        player: Player,
                        own_card: MonsterCard,
                        target_card: MonsterCard):
        """Upgrade monsters of the same type to a higher level"""
        can_upgrade = self.rule_engine.can_upgrade(
            player, own_card, target_card)

        if not can_upgrade:
            reasons = []
            if own_card.type != target_card.type:
                reasons.append(f"Type mismatch: {own_card.type} vs {
                               target_card.type}")
            if own_card.level_star != target_card.level_star:
                reasons.append(f"Level mismatch: {own_card.level_star} vs {
                               target_card.level_star}")
            if own_card.owner != player or target_card.owner != player:
                reasons.append("Not your cards")

            self._log_action("UPGRADE", player, {
                "card1": f"{own_card.name} (Lv{own_card.level_star})",
                "card2": f"{target_card.name} (Lv{target_card.level_star})",
                "reason": ", ".join(reasons) if reasons else "Rule check failed"
            }, False)
            return False

        upgrade_position = target_card.pos_in_matrix
        old_level = own_card.level_star
        new_level = old_level + 1

        # Remove the base monsters from the field and move them to graveyard
        self.move_card_to_graveyard(own_card)
        self.move_card_to_graveyard(target_card)

        # Create the upgraded monster
        upgraded_monster = self.monster_factory.load_by_type_and_level(
            player, own_card.type, new_level)

        if upgraded_monster is None:
            self._log_action("UPGRADE", player, {
                "type": own_card.type,
                "from_level": old_level,
                "to_level": new_level,
                "reason": f"No monster of type {own_card.type} at level {new_level}"
            }, False)
            return False

        # Place the upgraded monster on the field
        if upgrade_position:
            self.game_state.modify_field(
                "add", upgraded_monster, upgrade_position)
            upgraded_monster.is_placed = True
            upgraded_monster.pos_in_matrix = upgrade_position

            self._log_action("UPGRADE", player, {
                "from": f"{own_card.name} + {target_card.name}",
                "to": f"{upgraded_monster.name} (Lv{new_level})",
                "position": upgrade_position,
                "stats": f"ATK:{upgraded_monster.atk}/DEF:{upgraded_monster.defend}"
            }, True)

            self.event_logger.add_event(MergeEvent(
                own_card, target_card, upgraded_monster))
            return True

        return False

    def get_mergeable_groups(self, player: Player):
        """Get cards that can be merged for upgrades (pure logic)"""
        player_monsters = self.game_state.get_player_cards(player)
        mergeable_groups = self.rule_engine.get_mergeable_groups(
            player, player_monsters)
        return mergeable_groups

    def cast_spell(self, spell: SpellCard, target: Any = None):
        """Cast a spell card immediately"""
        if not isinstance(spell, SpellCard):
            self._log_action("CAST_SPELL", spell.owner if hasattr(spell, 'owner') else None, {
                "reason": "Not a spell card"
            }, False)
            return False

        current_player = self.turn_manager.get_current_player()
        if spell.ability not in ("draw_two_cards", "call_of_brave"):
            if spell.owner != current_player:
                self._log_action("CAST_SPELL", spell.owner, {
                    "spell": spell.name,
                    "reason": f"Not your turn (current: {current_player.name})"
                }, False)
                return False

            if isinstance(target, MonsterCard) and spell.owner != target.owner:
                self._log_action("CAST_SPELL", spell.owner, {
                    "spell": spell.name,
                    "target": target.name,
                    "reason": "Cannot target enemy monsters with buff spells"
                }, False)
                return False

            if isinstance(target, TrapCard) and spell.owner == target.owner:
                self._log_action("CAST_SPELL", spell.owner, {
                    "spell": spell.name,
                    "target": target.name,
                    "reason": "Cannot destroy your own trap"
                }, False)
                return False

        details = {"spell": spell.name, "ability": spell.ability}

        # Resolve spell based on ability
        if spell.ability == "draw_two_cards":
            self.draw_card(spell.owner, check=False)
            self.draw_card(spell.owner, check=False)
            details["effect"] = "Drew 2 cards"

        elif spell.ability == "buff_attack":
            self.effect_tracker.add_effect(
                EffectType.BUFF, target, "atk", spell.value, spell.duration)
            details["target"] = target.name
            details["effect"] = f"+{spell.value} ATK for {spell.duration} turns"

        elif spell.ability == "buff_defense":
            self.effect_tracker.add_effect(
                EffectType.BUFF, target, "defend", spell.value, spell.duration)
            details["target"] = target.name
            details["effect"] = f"+{spell.value} DEF for {spell.duration} turns"

        elif spell.ability == "destroy_trap":
            if target and isinstance(target, TrapCard):
                self.move_card_to_graveyard(target)
                details["target"] = target.name
                details["effect"] = "Trap destroyed"
            else:
                details["reason"] = f"Invalid trap target - {target.name}"
                self._log_action("CAST_SPELL", spell.owner, details, False)
                return False

        elif spell.ability == "summon_monster_from_hand":
            self.rule_engine.game_state.player_info[spell.owner]['has_summoned_monster'] = False
            details["effect"] = "Extra summon enabled"

        # Move spell to graveyard after use
        self.event_logger.add_event(SpellActiveEvent(spell, target))
        self.game_state.player_info[spell.owner]["held_cards"].remove(spell)
        self.game_state.player_info[spell.owner]["graveyard_cards"].add(spell)

        self._log_action("CAST_SPELL", spell.owner, details, True)
        return True

    def set_trap(self, trap: TrapCard, position: Tuple[int, int] | None, check=True):
        """Set a trap card face-down on the field"""
        if not isinstance(trap, TrapCard):
            return False

        can_set = self.rule_engine.can_summon(
            trap.owner, trap, self.game_state.field_matrix, position) or not check

        if not can_set:
            self._log_action("SET_TRAP", trap.owner, {
                "trap": trap.name,
                "position": position,
                "reason": "Cannot set trap (already set one or no space)"
            }, False)
            return False

        if position is None:
            position = self.game_state.get_random_empty_slot(trap.owner)
            if position is None:
                self._log_action("SET_TRAP", trap.owner, {
                    "trap": trap.name,
                    "reason": "No empty slots available"
                }, False)
                return False

        # Place trap face-down
        self.game_state.player_info[trap.owner]["held_cards"].remove(trap)
        self.game_state.modify_field("add", trap, position)
        self.game_state.player_info[trap.owner]["has_summoned_trap"] = True
        trap.is_placed = True
        trap.is_face_down = True
        trap.pos_in_matrix = position

        self._log_action("SET_TRAP", trap.owner, {
            "trap": trap.name,
            "ability": trap.ability,
            "position": position,
            "state": "face-down"
        }, True)
        return True

    def resolve_trap(self, trap: TrapCard, attacker: MonsterCard):
        """Resolve a trap card when triggered"""
        if not isinstance(trap, TrapCard) or not trap.is_face_down:
            return False

        print(f"  🪤 TRAP ACTIVATED: {trap.name} (Owner: {trap.owner.name})")
        print(f"     Trigger: {attacker.name} (Owner: {attacker.owner.name})")

        result = False
        effect_desc = ""

        if trap.ability == "debuff_enemy_atk":
            self.effect_tracker.add_effect(
                EffectType.DEBUFF, attacker, "atk", trap.value, trap.duration)
            trap.reveal()
            self.event_logger.add_event(TrapTriggerEvent(trap, attacker))
            self.move_card_to_graveyard(trap)
            effect_desc = f"{attacker.name} ATK -500 for 3 turns"

        elif trap.ability == "debuff_enemy_def":
            self.effect_tracker.add_effect(
                EffectType.DEBUFF, attacker, "defend", trap.value, trap.duration)
            trap.reveal()
            self.event_logger.add_event(TrapTriggerEvent(trap, attacker))
            self.move_card_to_graveyard(trap)
            effect_desc = f"{attacker.name} DEF -500 for 3 turns"

        elif trap.ability == "dodge_attack":
            attacker.has_attack = True
            self.move_card_to_graveyard(trap)
            effect_desc = "Attack negated"
            result = True
            trap.reveal()
            self.event_logger.add_event(TrapTriggerEvent(trap, attacker))

        elif trap.ability == "reflect_attack":
            self.move_card_to_graveyard(attacker)
            self.move_card_to_graveyard(trap)
            trap.reveal()
            self.event_logger.add_event(TrapTriggerEvent(trap, attacker))
            effect_desc = "Attack reflected, attacker destroyed"
            result = True

        print(f"Effect: {effect_desc}")
        return result

    def check_trap_triggers(self, attacker: MonsterCard, defender: Player):
        """Check if any traps should be triggered by an attack"""
        defender_cards = self.game_state.get_player_cards(defender)
        traps = [card for card in defender_cards
                 if isinstance(card, TrapCard) and card.is_face_down]

        for trap in traps:
            if self.resolve_trap(trap, attacker):
                return True
        return False

    def check_summon_trap(self, card_summon: MonsterCard):
        card_summon_owner = card_summon.owner
        opponents = [
            player for player in self.players if player != card_summon_owner]

        for opponent in opponents:
            opponent_cards = self.game_state.get_player_cards(opponent)
            traps = [card for card in opponent_cards if isinstance(
                card, TrapCard) and card.is_face_down]
            for trap in traps:
                if trap.ability == 'debuff_summon':
                    self.event_logger.add_event(
                        TrapTriggerEvent(trap, card_summon))

                    self.effect_tracker.add_effect(
                        EffectType.DEBUFF, card_summon, "atk", trap.value, trap.duration
                    )

                    self.effect_tracker.add_effect(
                        EffectType.DEBUFF, card_summon, "defend", trap.value, trap.duration
                    )
                    trap.reveal()
                    self.move_card_to_graveyard(trap)

                    return False

    def update_effects(self):
        """Update all active effects (call at end of each turn)"""
        expired = self.effect_tracker.update_round()
        if expired:
            print(f"  ⏰ {len(expired)} effect(s) expired")

    def end_turn(self):
        """End current player's turn"""
        current_player = self.turn_manager.get_current_player()

        for card in self.game_state.get_player_cards(current_player):
            if isinstance(card, MonsterCard):
                card.has_attack = False

        self.update_effects()
        self.turn_manager.end_turn()
        next_player = self.turn_manager.get_current_player()

        print(f"\n{'='*60}")
        print(f"TURN {self.turn_manager.turn_count} ENDED")
        print(f"Next Player: {next_player.name}")
        print(f"{'='*60}\n")

        self.draw_card(next_player)
        self._log_game_state(f"Start of Turn {self.turn_manager.turn_count}")
