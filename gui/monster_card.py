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
        self.highlight = False
        self.highlight_color = (255, 255, 0)  # Yellow outline

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
        if cell and self.monster_info.owner:
            # Original summon logic
            if game_engine.game_state.field_matrix_ownership[cell[0]][cell[1]] == self.monster_info.owner:
                if game_engine.summon_card(self.monster_info.owner, self.monster_info, cell):
                    self.is_draggable = False

        self.is_selected = False

    def handle_merge(self):
            if cell and self.monster_info.owner:
                target_card = game_engine.game_state.field_matrix[cell[0]][cell[1]]
                
                # Check if there's a monster card at the target position
                if (target_card and 
                    isinstance(target_card, type(self.monster_info)) and
                    target_card.owner == self.monster_info.owner and
                    target_card != self.monster_info):  # Can't upgrade with itself
                    
                    # Check if both cards are highlighted (eligible for merging)
                    target_sprite = None
                    for card, sprite in render_engine.sprites["matrix"].items():
                        if card == target_card and hasattr(sprite, 'highlight'):
                            target_sprite = sprite
                            break
                    
                    # Only allow upgrade if both cards are highlighted
                    if (target_sprite and target_sprite.highlight and self.highlight and
                        target_card.type == self.monster_info.type and 
                        target_card.level_star == self.monster_info.level_star):
                        
                        # Determine target upgrade level
                        target_level = self.monster_info.level_star + 1
                        
                        # Try to upgrade
                        if game_engine.upgrade_monster(self.monster_info.owner, 
                                                    self.monster_info.type, 
                                                    target_level):
                            # Upgrade successful, both cards will be removed
                            self.is_draggable = False
                            self.is_selected = False
                            # Refresh highlights after upgrade
                            game_engine.update_highlighted_cards(game_engine.render_engine)
                            return