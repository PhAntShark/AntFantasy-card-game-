import pygame


class InputManager:
    def __init__(self, matrix, game_engine, render_engine):
        self.matrix = matrix
        self.game_engine = game_engine
        self.dragging_card = None
        self.render_engine = render_engine

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left click → start drag
                self._handle_left_click(event.pos)
            elif event.button == 3:  # right click → toggle
                self._handle_right_click(event.pos)

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_card:
                self.dragging_card.on_drag(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging_card:
                self.dragging_card.on_drop(self.matrix, self.game_engine)
                self.dragging_card = None
                self.render_engine.align_cards(self.matrix)

    def _handle_left_click(self, pos):
        # Check hands from top-most first
        for hand in reversed(self.matrix.hands):
            for card_info in hand.hand_info.cards:
                card = self.render_engine.sprites[card_info]
                if card.rect.collidepoint(pos) and card.is_draggable:
                    self.dragging_card = card
                    card.on_drag_start()
                    return  # stop after first draggable card is found

    def _handle_right_click(self, pos):
        # Check all cards on the field
        for row in self.game_engine.game_state.field_matrix:
            for card_info in row:
                if not card_info:
                    continue
                card = self.render_engine.sprites[card_info]
                if card.rect.collidepoint(pos):
                    card.on_toggle(self.game_engine)
                    return  # stop after first card is toggled
