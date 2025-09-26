from core.cards.monster_card import MonsterCard as LogicMonsterCard
from gui.sprite import Sprite
from typing import Tuple
from pygame.draw import rect
from .draggable import Draggable
from pygame.transform import rotate


class MonsterCard(Sprite, Draggable):
    def __init__(
        self,
        monster_info: LogicMonsterCard,
        pos: Tuple[float, float] = [0, 0],
        size: Tuple[float, float] = [0, 0],
        **kwargs
    ):
        # Initialize the visual part of the card
        Sprite.__init__(
            self,
            pos=pos,
            size=size,
            image_path=monster_info.image_path,
            **kwargs
        )

        Draggable.__init__(self, self.rect)
        self.is_selected = False
        self.monster_info = monster_info

    def update(self):
        if self.is_selected:
            rect(self.image, (255, 255, 0), self.rect, 3)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def on_toggle(self, game_engine):
        game_engine.toggle_card(self.monster_info)
        if self.monster_info.mode == "defense":
            self.image = rotate(self.original_image, 90)
        else:
            self.image = rotate(self.original_image, 0)

    def on_drag_start(self):
        self.is_selected = True

    def on_drag(self, pos):
        self.rect.center = pos

    def on_drop(self, matrix, game_engine):
        cell = matrix.get_slot_at_pos(self.rect.center)

        # TODO: rewrite this
        if cell and self.monster_info.owner:
            if game_engine.game_state.field_matrix_ownership[cell[0]][cell[1]] == self.monster_info.owner:
                if game_engine.summon_card(self.monster_info.owner, self.monster_info, cell):
                    slot_rect = matrix.get_slot_rect(*cell)
                    self.rect.center = slot_rect.center
                    self.is_draggable = False

        self.is_selected = False
