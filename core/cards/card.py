from typing import Literal, Optional, Tuple

cardType = Literal["monster", "spell", "trap"]


class Card:
    def __init__(self,
                 name: str,
                 description: str,
                 ctype: cardType,
                 ability: str,
                 owner,
                 is_placed: bool = False
                 ):
        self.name = name
        self.description = description
        self.ability = ability
        self.ctype = ctype
        self.owner = owner
        self.is_placed = is_placed
        self.pos_in_matrix: Optional[Tuple[int, int]] = None
