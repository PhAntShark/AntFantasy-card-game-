from pygame.sprite import Sprite as PySprite
from pygame.image import load
from pygame.transform import scale
from typing import Tuple


class Sprite(PySprite):
    def __init__(self, pos: Tuple[float, float], size: Tuple[float, float], image_path: str):
        PySprite.__init__(self)
        self.image = load(image_path).convert_alpha()
        self.image = scale(self.image, size)
        self.original_image = self.image

        self.rect = self.image.get_rect()
        self.rect.x = int(pos[0])
        self.rect.y = int(pos[1])
