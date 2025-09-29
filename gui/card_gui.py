from core.cards.monster_card import MonsterCard as LogicMonsterCard
from gui.sprite import Sprite
from typing import Tuple
from pygame.draw import rect
from .draggable import Draggable
from pygame.transform import rotate


from gui.sprite import Sprite
from typing import Tuple
from pygame.draw import rect
from .draggable import Draggable


class CardGUI(Sprite, Draggable):
    def __init__(
        self,
        logic_card,
        pos: Tuple[float, float] = [0, 0],
        size: Tuple[float, float] = [0, 0],
        **kwargs
    ):
        Sprite.__init__(
            self,
            pos=pos,
            size=size,
            image_path=logic_card.image_path,
            **kwargs
        )
        Draggable.__init__(self, self.rect)

        self.logic_card = logic_card
        self.is_selected = False
        self.highlight = False
        self.highlight_color = (255, 255, 0)  # Yellow outline

    def update(self):
        if self.is_selected:
            rect(self.image, (255, 255, 0), self.rect, 3)

    def update(self):
        if self.is_selected:
            rect(self.image, (255, 255, 0), self.rect, 3)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
        # Draw highlight outline if enabled
        if self.highlight:
            import pygame
            pygame.draw.rect(surface, self.highlight_color, self.rect, 4)

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

        # Check if dropped on another monster card for upgrade
        if cell and self.logic_card.owner:
            # Original summon logic
            if game_engine.game_state.field_matrix_ownership[cell[0]][cell[1]] == self.logic_card.owner:
                if game_engine.summon_card(self.logic_card.owner, self.logic_card, cell):
                    self.is_draggable = False

        self.is_selected = False

