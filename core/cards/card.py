from typing import Literal, Optional, Tuple
import uuid

cardType = Literal["monster", "spell", "trap"]


class Card:
    def __init__(self,
                 name: str,
                 description: str,
                 ctype: cardType,
                 ability: str,
                 owner,
                 is_placed: bool = False,
                 is_face_down: bool = False
                 ):
        self.id = uuid.uuid4()
        self.name = name
        self.description = description
        self.ability = ability
        self.ctype = ctype
        self.owner = owner
        self.is_placed = is_placed
        self.is_face_down = is_face_down
        self.pos_in_matrix: Optional[Tuple[int, int]] = None
