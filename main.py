import pygame
from core.player import Player
from gui.matrix_field import Matrix
from gui.game_control import GameControl
from core.game.game_engine import GameEngine
from gui.attack_control import AttackControl

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

# Players
player1 = Player(0, 'Binh', [], [], [])
player2 = Player(1, 'An', [], [], [], is_opponent=True)

# Matrix field
field_matrix = Matrix(screen, [player1, player2])

# Game engine
game_engine = GameEngine([player1, player2], field_matrix)
game_engine.give_init_cards(5)  # give starting hand

# Controls
game_control = GameControl(field_matrix, game_engine)
attack_control = AttackControl(game_engine.game_state, field_matrix)

# Place a card for testing (optional)
if player2.held_cards:
    card = player2.held_cards[0]
    player2.summon(card)
    card.is_placed = True
    game_engine.game_state.modify_field("add", card, (0, 0))
    rect = field_matrix.get_slot_rect(0, 0)
    card.rect.center = rect.center
    field_matrix.hands["opponent_hand"].draw_cards()

# Main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Drag / toggle cards
        for card in game_engine.sprite_group.sprites():
            card.handle_drag(event)
            card.handle_toggle(event)

        # Handle attacks
        attack_control.handle_attack(event)

    screen.fill((30, 30, 30))

    # Handle drop and placing cards on field
    for card in game_engine.sprite_group.sprites():
        game_control.handle_drop(card)

    # Draw field, hands, and grid
    field_matrix.draw()

    # Draw attack arrows
    attack_control.draw(screen)

    # Update and draw all card sprites
    game_engine.sprite_group.update()
    game_engine.sprite_group.draw(screen)

    pygame.display.flip()
    clock.tick(60)
