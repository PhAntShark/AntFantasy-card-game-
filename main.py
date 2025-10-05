import pygame
from core.player import Player
from gui.gui_info.matrix_field import Matrix
from core.handle_game_logic.game_engine import GameEngine
from core.handle_logic_gui.render_engine import RenderEngine
from core.handle_logic_gui.input_manager import InputManager
from gui.effects.manager import EffectManager


pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0


'''PLAYER FOR TESTING'''

# Players creation
player1 = Player(0, 'Binh')
player2 = Player(1, 'An', is_opponent=True)

game_engine = GameEngine([player1, player2])
game_engine.give_init_cards(5)

render_engine = RenderEngine(screen)
field_matrix = Matrix(screen, game_engine.game_state)

input_manager = InputManager(field_matrix, game_engine, render_engine)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        input_manager.handle_event(event)

        # TODO: change this with a real turn end button
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            game_engine.end_turn()

    screen.fill((30, 30, 30))

    render_engine.update(game_engine,
                         game_engine.game_state,
                         field_matrix,
                         game_engine.event_logger)
    render_engine.animation_mgr.update(dt)
    render_engine.draw()

    EffectManager.update()
    EffectManager.draw(screen)

    input_manager.draw(screen)
    field_matrix.draw()

    pygame.display.flip()

    # Delta time for rate limit
    dt = clock.tick(60) / 1000

    if game_engine.game_state.is_game_over():
        pygame.time.wait(1000)  # pause to show message
        running = False

pygame.quit()
