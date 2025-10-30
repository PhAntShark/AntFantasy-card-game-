from core.player import Player
from core.cards.monster_card import MonsterCard
from core.cards.spell_card import SpellCard
from core.cards.trap_card import TrapCard
from typing import Tuple, List, Dict, Any


class LegalActionResolver:
    def resolve(self, env, player: Player) -> Tuple[List[str], Dict[str, Any]]:
        raise NotImplementedError


class SummonResolver(LegalActionResolver):
    def resolve(self, env, player: Player) -> Tuple[List[str], Dict[str, Any]]:
        gs = env.engine.game_state
        cards = gs.player_info[player]["held_cards"].cards
        summonable = [i for i, c in enumerate(
            cards) if isinstance(c, MonsterCard)]
        if summonable \
                and not gs.player_info[player].get("has_summoned_monster", False) \
                and gs.has_slot_available(player):
            return ["summon"], {"summon": {"monsters": summonable}}
        return [], {}


class AttackResolver(LegalActionResolver):
    def resolve(self, env, player: Player) -> Tuple[List[str], Dict[str, Any]]:
        gs = env.engine.game_state
        tm = env.engine.turn_manager
        opp = gs.get_opponent(player)
        my_monsters = [c for c in gs.get_player_cards(player)
                       if isinstance(c, MonsterCard)
                       and c.mode == "attack"
                       and not c.has_attack]
        opp_monsters = [c for c in gs.get_player_cards(
            opp) if isinstance(c, MonsterCard)]
        if my_monsters and tm.turn_count > 1:
            attack_info = {
                "attack": {
                    "attackers": list(range(len(my_monsters))),
                    "targets": list(range(len(opp_monsters))) if opp_monsters else [-1],
                }
            }
            return ["attack"], attack_info
        return [], {}


class CastSpellResolver(LegalActionResolver):
    def resolve(self, env, player: Player) -> Tuple[List[str], Dict[str, Any]]:
        gs = env.engine.game_state
        cards = gs.player_info[player]["held_cards"].cards
        castable = [i for i, c in enumerate(
            cards) if isinstance(c, SpellCard)]
        if not castable:
            return [], {}
        spell_targets: Dict[int, List[int]] = {}
        my_monsters = gs.get_cards_typed(player, MonsterCard)

        for spell_idx in castable:
            ability = getattr(cards[spell_idx], "ability", None)
            valid_targets: List[int] = []

            if ability in ("buff_attack", "buff_defense"):
                valid_targets = list(range(len(my_monsters)))

            elif ability == "destroy_trap":
                opp = gs.get_opponent(player)
                opp_traps = [c for c in gs.get_cards_typed(opp, TrapCard)]
                valid_targets = list(range(len(opp_traps)))

            else:
                valid_targets = []

            spell_targets[spell_idx] = valid_targets

        to_remove = []
        for key, value in spell_targets.items():
            if len(value) <= 0:
                to_remove.append(key)

        for key in to_remove:
            spell_targets.pop(key)
            castable.remove(key)

        if castable and spell_targets:
            return ["cast_spell"], {"cast_spell": {"spells": castable, "targets": spell_targets}}
        return [], {}


class SetTrapResolver(LegalActionResolver):
    def resolve(self, env, player: Player) -> Tuple[List[str], Dict[str, Any]]:
        gs = env.engine.game_state
        cards = gs.player_info[player]["held_cards"].cards
        traps = [i for i, c in enumerate(
            cards) if getattr(c, "ctype", None) == "trap"]
        if traps \
                and not gs.player_info[player].get("has_summoned_trap", False) \
                and gs.has_slot_available(player):
            return ["set_trap"], {"set_trap": {"traps": traps}}
        return [], {}


class ToggleResolver(LegalActionResolver):
    def resolve(self, env, player: Player) -> Tuple[List[str], Dict[str, Any]]:
        gs = env.engine.game_state
        my_monsters = [c for c in gs.get_player_cards(
            player) if isinstance(c, MonsterCard)]
        toggles = list(range(len(my_monsters)))
        if toggles \
                and not gs.player_info[player].get("has_toggled", False):
            return ["toggle"], {"toggle": {"toggles": toggles}}
        return [], {}


class CombineResolver(LegalActionResolver):
    def resolve(self, env, player: Player) -> Tuple[List[str], Dict[str, Any]]:
        mergeable_groups = env.engine.get_mergeable_groups(player)
        combine_pairs: List[Tuple[int, int]] = []
        for group in mergeable_groups.values():
            if len(group) >= 2:
                for i in range(len(group)):
                    for j in range(i + 1, len(group)):
                        combine_pairs.append((group[i].id, group[j].id))
        if combine_pairs:
            return ["combine"], {"combine": {"pairs": combine_pairs}}
        return [], {}


class EndTurnResolver(LegalActionResolver):
    def resolve(self, env, player: Player) -> Tuple[List[str], Dict[str, Any]]:
        return ["end_turn"], {"end_turn": {}}
