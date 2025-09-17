# from pygame.sprite import Sprite
# from pygame.image import load
# from pygame.transform import scale
# from typings import Tuple
from typing import Literal

from core.player import Player

cardType = Literal["monster", "spell", "trap"]


class Card:
    def __init__(self,
                 name: str,
                 description: str,
                 ctype: cardType,
                 ability: str,
                 owner: Player,

                 # size: Tuple[int, int],
                 # pos: Tuple[int, int],
                 # image_path: str,
                 ):
        # Sprite.__init__(self)
        self.name = name
        self.description = description
        self.ability = ability
        self.type = ctype
        self.owner = owner

        # self.image = load(image_path).convert_alpha()
        # self.image = scale(self.image, size)

        # self.rect = self.image.get_rect()
        # self.rect.x = pos[0]
        # self.rect.y = pos[1]
