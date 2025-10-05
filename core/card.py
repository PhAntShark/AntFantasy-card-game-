from pygame.sprite import Sprite
from pygame.image import load
from pygame.transform import scale


class Card(Sprite):
    def __init__(self, name, description, ability, size, pos, image_path):
        Sprite.__init__(self)
        self.name = name
        self.description = description
        self.ability = ability

        self.image = load(image_path).convert_alpha()
        self.image = scale(self.image, size)
        
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        
    def update(self):
        pass