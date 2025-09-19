import pygame
# from core.cards.card import Card
# from pathlib import Path
from core.arrow import DragArrow
from gui.monster_card import MonsterCard
from core.player import Player
from pathlib import Path
from gui.matrix_field import MatrixField


pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0


'''PLAYER FOR TESTING'''
player = Player(0, 'Binh', [], [], [])

bd_path = Path("./assets/card1.jpg")
blue_dragon = MonsterCard('dragon', ' blue', player, (0,0), (100,100), bd_path, 'gay', 100, 150, 1)

all_sprites = pygame.sprite.Group() 


bd_path = Path("./assets/table.png")
field_matrix = [[None for _ in range(4)] for _ in range(4)]
field = MatrixField(field_matrix, 1,1, (0,0), (1280, 720), bd_path)
all_sprites.add(field)
all_sprites.add(blue_dragon)


# all_sprites.add(blue_dragon2)



drag_arrow = DragArrow()

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        drag_arrow.handle_event(event)

    screen.fill((30, 30, 30))
    
    all_sprites.update()
    all_sprites.draw(screen)
    
    drag_arrow.draw(screen)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for frame rate
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()



