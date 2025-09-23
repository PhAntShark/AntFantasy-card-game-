import pygame
# from core.arrow import DragArrow
from core.player import Player
from gui.matrix_field import Matrix
from gui.game_control import GameControl
from core.game.game_engine import GameEngine
from gui.attack_control import AttackControl


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
game_engine.give_init_cards(5)

# Handle game control inputs
game_control = GameControl(field_matrix, game_engine)

attack_control = AttackControl(game_engine.game_state, field_matrix)

# TODO: remove placeholder later
# game_engine.summon_card(player2, player2.held_cards[0], [0, 0])

# print(game_engine.game_state.field_matrix)
card = player2.held_cards[0]
player2.summon(card)
card.is_placed = True
game_engine.game_state.modify_field("add", card, (0, 0))
rect = field_matrix.get_slot_rect(0, 0)
card.rect.center = rect.center
field_matrix.hands["opponent_hand"].draw_cards()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle card pick / drag / drop
        for card in game_engine.sprite_group.sprites():
            card.handle_drag(event)
            card.handle_toggle(event)

        attack_control.handle_attack(event)

    screen.fill((30, 30, 30))

    for card in game_engine.sprite_group.sprites():
        game_control.handle_drop(card)

    field_matrix.draw()
    attack_control.draw(screen)

    game_engine.sprite_group.update()
    game_engine.sprite_group.draw(screen)

    pygame.display.flip()

    # Delta time for rate limit
    dt = clock.tick(60) / 1000

pygame.quit()
