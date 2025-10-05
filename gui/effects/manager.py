import pygame
from .impact import ImpactEffect
from .trap_glow import TrapGlowEffect
from .spell_glow import SpellGlowEffect
from .merge import MergeEffect


class EffectManager:
    effects_group = pygame.sprite.Group()

    @classmethod
    def spawn(cls, effect_type, pos):
        if effect_type == "slam":
            effect = ImpactEffect(pos)
            cls.effects_group.add(effect)
        elif effect_type == "trap-glow":
            effect = TrapGlowEffect(pos)
            cls.effects_group.add(effect)
        elif effect_type == "spell-glow":
            effect = SpellGlowEffect(pos)
            cls.effects_group.add(effect)
        elif effect_type == "merge":
            effect = MergeEffect(pos)
            cls.effects_group.add(effect)

    @classmethod
    def update(cls):
        cls.effects_group.update()

    @classmethod
    def draw(cls, screen):
        cls.effects_group.draw(screen)
