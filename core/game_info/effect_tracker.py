from core.cards.monster_card import MonsterCard
from dataclasses import dataclass
from enum import Enum, auto
from typing import List


class EffectType(Enum):
    """Different types of effects a spell can apply"""
    BUFF = auto()
    DEBUFF = auto()
    INSTANT = auto()  # one-time effects like destroy, heal, etc.


@dataclass
class Effect:
    """Represents a single active effect"""
    effect_type: EffectType
    stat: str            # e.g. "atk", "defense"
    target: MonsterCard
    value: int
    duration: int        # how many rounds it lasts
    rounds_remaining: int


class EffectTracker:
    """Tracks active spell/ability effects and their duration"""

    def __init__(self):
        self.active_effects: List[Effect] = []

    def add_effect(self,
                   effect_type: EffectType,
                   target: MonsterCard,
                   stat: str,
                   value: int,
                   duration: int = 3):
        """Add a new timed effect and apply it immediately"""
        effect = Effect(
            effect_type=effect_type,
            stat=stat,
            target=target,
            value=value,
            duration=duration,
            rounds_remaining=duration,
        )

        self._apply_effect(effect)
        self.active_effects.append(effect)

    def apply_instant_effect(self, effect_type: EffectType,
                             target: MonsterCard,
                             stat: str = "",
                             value: int = 0):
        """Apply a one-time effect like destroy or heal"""
        if effect_type == EffectType.INSTANT:
            if stat and hasattr(target, stat):
                setattr(target, stat, getattr(target, stat) + value)
            # here you could expand: destroy, heal player LP, draw card, etc.

    def update_round(self):
        """Advance to the next round and expire old effects"""
        expired_effects = []

        for effect in self.active_effects:
            effect.rounds_remaining -= 1
            if effect.rounds_remaining <= 0:
                expired_effects.append(effect)

        # Remove expired
        for effect in expired_effects:
            self._remove_effect(effect)
            self.active_effects.remove(effect)

    def _apply_effect(self, effect: Effect):
        """Apply the effect to the target"""
        print(effect.target, effect.stat)
        if hasattr(effect.target, effect.stat):
            if effect.effect_type == EffectType.BUFF:
                setattr(effect.target, effect.stat,
                        getattr(effect.target, effect.stat) + effect.value)
            elif effect.effect_type == EffectType.DEBUFF:
                setattr(effect.target, effect.stat,
                        getattr(effect.target, effect.stat) - effect.value)

    def _remove_effect(self, effect: Effect):
        """Revert the effect when it expires"""
        if hasattr(effect.target, effect.stat):
            if effect.effect_type == EffectType.BUFF:
                setattr(effect.target, effect.stat,
                        getattr(effect.target, effect.stat) - effect.value)
            elif effect.effect_type == EffectType.DEBUFF:
                setattr(effect.target, effect.stat,
                        getattr(effect.target, effect.stat) + effect.value)

    def get_effects_on_target(self, target: MonsterCard) -> List[Effect]:
        """Get all active effects on a monster"""
        return [e for e in self.active_effects if e.target == target]

    def clear_all_effects(self):
        """Clear all active effects immediately"""
        for effect in self.active_effects:
            self._remove_effect(effect)
        self.active_effects.clear()

    def get_round_info(self):
        return {
            "active_effects_count": len(self.active_effects)
        }
