import pygame  # main pygame module
from pygame.sprite import Sprite as PySprite # if you want to use sprite groups
from pygame.image import load    # to load images
from pygame.transform import scale  # to resize images
from typing import Tuple         # optional, for type hints like size/position


class Sprite(PySprite):
    def __init__(self, pos: Tuple[float, float], size:Tuple[float, float] ,image_path: str):
        PySprite.__init__(self)
        self.image = load(image_path).convert_alpha()
        self.image = scale(self.image, size)
        
        self.rect = self.image.get_rect()   
        self.rect.x = pos[0]
        self.rect.y = pos[1]

        



