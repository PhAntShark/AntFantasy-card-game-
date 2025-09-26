import pygame
from core.arrow import DragArrow
from pygame.rect import Rect


class InputManager:
    def __init__(self, matrix, game_engine, render_engine):
        self.matrix = matrix
        self.game_engine = game_engine
        self.dragging_card = None
        self.drag_arrow = None
        self.render_engine = render_engine

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN: 
            if event.button == 1:  # left click → start drag
                self._handle_left_click(event.pos)
                self.handle_left_click_arrow(event.pos)
            elif event.button == 3:  # right click → toggle
                self._handle_right_click(event.pos)

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_card:
                self.dragging_card.on_drag(event.pos)
            elif self.drag_arrow and self.drag_arrow.dragging:
                self.drag_arrow.end_pos = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging_card:
                self.dragging_card.on_drop(self.matrix, self.game_engine)
                self.dragging_card = None
                self.render_engine.align_cards(self.matrix)
            
            elif self.drag_arrow and self.drag_arrow.dragging:
                self.drag_arrow.dragging = False
                for row in self.game_engine.game_state.field_matrix:
                    for card_info in row:
                        if not card_info:
                            continue
                        card = self.render_engine.sprites[card_info]
                        if card.rect.collidepoint(event.pos):
                            self.drag_arrow.end_pos = card.rect.center
                            # break
                self.drag_arrow = None
                

    def _handle_left_click(self, pos):
        # Check hands from top-most first
        for hand in reversed(self.matrix.hands):
            for card_info in hand.hand_info.cards:
                card = self.render_engine.sprites[card_info]
                if card.rect.collidepoint(pos) and card.is_draggable:
                    self.dragging_card = card
                    card.on_drag_start()
                    return  # stop after first draggable card is 
  
   
    def handle_left_click_arrow(self,pos):
        for row in self.game_engine.game_state.field_matrix:
            for card_info in row:
                if not card_info:
                    continue
                card = self.render_engine.sprites[card_info]
                if card.rect.collidepoint(pos):
                    self.drag_arrow = DragArrow()
                    self.drag_arrow.start_pos = card.rect.center
                    self.drag_arrow.end_pos = card.rect.center
                    self.drag_arrow.dragging = True
                    return  

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

    def draw(self, screen):
        if self.drag_arrow:
            self.drag_arrow.draw(screen)