import pygame
# from core.arrow import DragArrow
from core.player import Player
from gui.gui_info.matrix_field import Matrix
from core.game.game_engine import GameEngine
# from gui.attack_control import AttackControl
from core.manager_logic_gui.render_engine import RenderEngine
from core.manager_logic_gui.input_manager import InputManager


pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0


'''PLAYER FOR TESTING'''

# Monster factory for generating new cards

# Players creation
player1 = Player(0, 'Binh')
player2 = Player(1, 'An', is_opponent=True)


game_engine = GameEngine([player1, player2])
game_engine.give_init_cards(5)

render_engine = RenderEngine(screen)
# Matrix field creation
# TODO: fix this
field_matrix = Matrix(screen, game_engine.game_state)

# attack_control = AttackControl(game_engine.game_state, field_matrix)

input_manager = InputManager(field_matrix, game_engine, render_engine)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        input_manager.handle_event(event)

        # TODO: change this with a real turn end button
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            game_engine.turn_manager.end_turn()

    screen.fill((30, 30, 3e0))

    render_engine.update(game_engine.game_state, field_matrix)
    render_engine.draw()
    input_manager.draw(screen)
    field_matrix.draw()

    pygame.display.flip()

    # Delta time for rate limit
    dt = clock.tick(60) / 1000

pygame.quit()
