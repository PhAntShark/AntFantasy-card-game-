from core.cards.card import Card
from core.player import Player


class TrapCard(Card):
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
