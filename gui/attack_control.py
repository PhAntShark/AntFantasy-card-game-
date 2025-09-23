from core.arrow import DragArrow
import pygame


class AttackControl:
    def __init__(self, state, matrix):
        self.state = state
        self.matrix = matrix
        self.arrow = DragArrow()

    def handle_attack(self, event):
        # Problem: How to map GUI with game state matrix
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = self.matrix.get_slot_at_pos(event.pos)  # row, col
            if pos:
                card = self.state.field_matrix[pos[0]][pos[1]]
                if card and card.mode == "attack":
                    self.arrow.dragging = True
                    self.arrow.start_pos = card.rect.center
                    self.arrow.end_pos = card.rect.center

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            pos = self.matrix.get_slot_at_pos(event.pos)
            if pos:
                card = self.state.field_matrix[pos[0]][pos[1]]
                if card and card.owner.is_opponent:
                    self.arrow.dragging = False
                    self.arrow.end_pos = card.rect.center
                    return
            self.arrow.dragging = False
            self.arrow.end_pos = self.arrow.start_pos

        self.arrow.handle_event(event)

    def draw(self, surface):
        self.arrow.draw(surface)
