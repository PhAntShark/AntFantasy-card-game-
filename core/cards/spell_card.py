from core.cards.card import Card
from core.player import Player


class SpellCard(Card):
    def __init__(self,
                 name: str,
                 description: str,
                 owner: Player,
                 ability: str,
                 image_path: str | None = None,
                 **kwargs
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
