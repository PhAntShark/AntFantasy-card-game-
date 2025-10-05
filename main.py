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

bd_path = Path("./assets/card1.jpg")
blue_dragon = Card("dragon", 'dragon', 'fire ball', (100, 100), (0,0), bd_path)
blue_dragon2 = Card("dragon", 'dragon', 'fire ball', (100, 100), (300,300), bd_path)

    

# Players creation
player1 = Player(0, 'Binh')
player2 = Player(1, 'An', is_opponent=True)

game_engine = GameEngine([player1, player2])
game_engine.give_init_cards(5)

render_engine = RenderEngine(screen)
field_matrix = Matrix(screen, game_engine.game_state)

input_manager = InputManager(field_matrix, game_engine, render_engine)

drag_arrow = DragArrow()

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        drag_arrow.handle_event(event)

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

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()
