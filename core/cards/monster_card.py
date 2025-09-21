from core.cards.card import Card
from core.player import Player
from typing import Literal

cardMode = Literal["attack", "defense"]


class MonsterCard(Card):
    def __init__(self,
                 name: str,
                 description: str,
                 owner: Player,
                 ability: str | None = None,
                 attack_points: int = 0,
                 defense_points: int = 0,
                 level_star: int = 1,
                 mode: cardMode = 'attack',
                 image_path: str | None = None,
                 **kwargs,
                 ):
        super().__init__(name, description, "monster", ability, owner, **kwargs)
        self.atk = attack_points
        self.defend = defense_points
        self.level_star = level_star
        self.mode = mode  # 'attack' or 'defense'
        self.image_path = image_path
        self.is_summoned = False
        self.is_alive = True

    def __str__(self):
        return f"Name: {self.name} \
                Owner: {self.owner} \
                ATK: {self.atk} \
                DEF: {self.defend} \
                Star: {self.level_star}\
                Mode: {self.mode} \
                Type: {self.type}"

    def switch_position(self):
        """Change the card mode to either attack or defense."""
        self.mode = 'defense' if self.mode == 'attack' else 'attack'
        print(f"{self.name} switched to {self.mode} position.")
