from core.cards.card import Card
from core.player import Player
from typing import Any


class SpellCard(Card):
    def __init__(self,
                 name: str,
                 description: str,
                 owner: Player,
                 ability: str,
                 image_path: str | None = None,
                 **kwargs: Any
                 ):
        super().__init__(
            name=name,
            description=description,
            ctype="spell",
            ability=ability,
            owner=owner,
            is_placed=False,  # Spells are not placed on field
            **kwargs
        )
        self.image_path = image_path

    def __str__(self):
        return f"Spell: {self.name} - {self.description} (Ability: {self.ability})"

    def can_target(self, target) -> bool:
        """Check if this spell can target the given target"""
        if self.ability in ["draw_two_cards"]:
            return True  # No target needed
        elif self.ability in ["buff_attack", "buff_defense"]:
            return hasattr(target, 'atk') and hasattr(target, 'defend')
        elif self.ability == "destroy_spell_trap":
            return hasattr(target, 'type') and target.type in ["spell", "trap"]
        elif self.ability == "summon_monster_from_hand":
            return hasattr(target, 'type') and target.type == "monster"
        return False


class TrapCard(Card):
    def __init__(self,
                 name: str,
                 description: str,
                 owner: Player,
                 ability: str,
                 image_path: str | None = None,
                 **kwargs: Any
                 ):
        super().__init__(
            name=name,
            description=description,
            ctype="trap",
            ability=ability,
            owner=owner,
            is_placed=True,  # Traps are placed on field
            is_face_down=True,  # Traps start face-down
            **kwargs
        )
        self.image_path = image_path

    def __str__(self):
        return f"Trap: {self.name} - {self.description} (Ability: {self.ability})"

    def can_trigger(self, attacker, defender) -> bool:
        """Check if this trap can be triggered by the given attack"""
        if self.ability in ["debuff_enemy_atk", "debuff_enemy_def", "dodge_attack", "reflect_attack"]:
            return True  # Triggered by any attack
        elif self.ability == "debuff_summon":
            return False  # Triggered by summon, not attack
        return False

    def reveal(self):
        """Reveal the trap (flip face-up)"""
        self.is_face_down = False
