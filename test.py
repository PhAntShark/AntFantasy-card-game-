import pygame
# from core.arrow import DragArrow
from core.player import Player
from gui.matrix_field import Matrix
from gui.game_control import GameControl
from core.game.game_engine import GameEngine


pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0


'''PLAYER FOR TESTING'''

# Monster factory for generating new cards

# Players creation
player1 = Player(0, 'Binh', [], [], [])
player2 = Player(1, 'An', [], [], [], is_opponent=True)

# Matrix field creation
# TODO: fix this
field_matrix = Matrix(screen, [player1, player2])

game_engine = GameEngine([player1, player2], field_matrix)
for _ in range(5):
    game_engine.draw_card(player1)

# Handle game control inputs
game_control = GameControl(field_matrix)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle card pick / drag / drop
        for card in game_engine.sprite_group.sprites():
            card.handle_event(event)

    screen.fill((30, 30, 30))

    for card in game_engine.sprite_group.sprites():
        game_control.handle_drop(card)

    field_matrix.draw()

    game_engine.sprite_group.update()
    game_engine.sprite_group.draw(screen)

    pygame.display.flip()

    # Delta time for rate limit
    dt = clock.tick(60) / 1000

pygame.quit()
