# from pygame.sprite import Sprite
# from pygame.image import load
# from pygame.transform import scale
# from typings import Tuple
from typing import Literal

# from core.player import Player

cardType = Literal["monster", "spell", "trap"]


class Card:
    def __init__(self,
                 name: str,
                 description: str,
                 ctype: cardType,
                 ability: str,
                 owner,
                 **kwargs
                 ):
        self.name = name
        self.description = description
        self.ability = ability
        self.type = ctype
        self.owner = owner
        self.extra = kwargs