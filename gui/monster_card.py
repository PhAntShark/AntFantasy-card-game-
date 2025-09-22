from core.cards.monster_card import MonsterCard as LogicMonsterCard
from gui.sprite import Sprite
from typing import Tuple
from core.player import Player
from core.cards.monster_card import cardMode
from pathlib import Path
from pygame.draw import rect
from .draggable import Draggable


class MonsterCard(LogicMonsterCard, Sprite, Draggable):
    def __init__(
        self,
        name: str,
        description: str,
        owner: Player,
        image_path: str | Path,
        pos: Tuple[float, float] = [0, 0],
        size: Tuple[float, float] = [0, 0],
        ability: str | None = None,
        attack_points: int = 0,
        defense_points: int = 0,
        level_star: int = 1,
        mode: cardMode = 'attack',
        **kwargs
    ):
        # Initialize the logic part of the card
        LogicMonsterCard.__init__(
            self,
            name=name,
            description=description,
            owner=owner,
            ability=ability,
            attack_points=attack_points,
            defense_points=defense_points,
            level_star=level_star,
            mode=mode,
            **kwargs
        )

        # Initialize the visual part of the card
        Sprite.__init__(
            self,
            pos=pos,
            size=size,
            image_path=image_path,
            **kwargs
        )

        Draggable.__init__(self, self.rect)
        self.is_selected = False

    def update(self):
        if self.is_selected:
            rect(self.image, (255, 255, 0), self.rect, 3)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
