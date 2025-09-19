from core.game.game_state import GameState
from gui.sprite import Sprite
# from pathlib import Path
from pygame.draw import rect
from pygame.display import get_surface
from typing import Tuple


class MatrixField(GameState, Sprite):
    def __init__(self,
                 field_matrix,
                 margin,
                 padding,
                 pos,
                 size,
                 image_path,
                 **kwargs):
        
        GameState.__init__(self, field_matrix)
        Sprite.__init__(self, pos, size, image_path,**kwargs)
        self.margin = margin
        self.padding = padding
        self.cell_height = [1]
        self.cell_width = [0]
        pos = Tuple[0,0]
    
        self.field_matrix = []
        for _ in range(4):
            self.field_matrix.append([None for _ in range(4)])
            
    def calculate_field_matrix(self, pos):
        for self.cell_height in self.field_matrix:
            for self.cell_width in self.field_matrix:
                
                x = self.margin + (len(self.cell_height) - 1 ) * self.cell_height + self.cell_height/2 + (len(self.padding)) * self.padding
                y = self.margin + (len(self.cell_width) - 1 ) * self.cell_width + self.cell_height/2 + (len(self.padding)) * self.padding
                return pos(x,y)
            
    def calculate_resolution_field_matrix(self, pos):
        pass
    
    def update(self):
        rect(self.image, (255, 255, 0), self.image.get_rect(), 3)

    def draw(self, surface):
        surface.blit(self.image)
            


