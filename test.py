import pygame
# from core.cards.card import Card
# from pathlib import Path
from core.arrow import DragArrow
from gui.monster_card import MonsterCard
from core.player import Player
from pathlib import Path
from gui.matrix_field import Matrix
from gui.game_control import GameControl


pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0


'''PLAYER FOR TESTING'''
player = Player(0, 'Binh', [], [], [])

all_sprites = pygame.sprite.Group()

field = Matrix(screen)
gc = GameControl(field)

bd_path = Path("./assets/card1.jpg")
blue_dragon = MonsterCard('dragon', ' blue', player,
                          (0, 0), (field.slot_width / 2, field.slot_height), bd_path, 'gay', 100, 150, 1)

all_sprites.add(blue_dragon)


drag_arrow = DragArrow()

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # drag_arrow.handle_event(event)
        for card in all_sprites.sprites():
            card.handle_event(event)

    screen.fill((30, 30, 30))

    field.draw()

    all_sprites.update()
    all_sprites.draw(screen)

    drag_arrow.draw(screen)

    for card in all_sprites.sprites():
        gc.handle_drop(card)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for frame rate
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()
