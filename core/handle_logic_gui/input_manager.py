import pygame
from gui.arrow import DragArrow


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
                self._handle_left_click_arrow(event.pos)
                self.handle_click_card(event.pos)
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
            self._handle_release_arrow(event.pos)

    def _handle_left_click(self, pos):
        # Check hands from top-most first
        for hand in reversed(self.matrix.hands):
            for card_info in hand.hand_info.cards:
                card = self.render_engine.sprites["hand"][card_info]
                if card.rect.collidepoint(pos) and card.is_draggable:
                    self.dragging_card = card
                    card.on_drag_start()
                    return  # stop after first draggable card is

    def _handle_release_arrow(self, pos):
        if self.drag_arrow and self.drag_arrow.dragging:
            self.drag_arrow.dragging = False
            # Checking for cards in field matrix
            for row in self.game_engine.game_state.field_matrix:
                for card_info in row:
                    if not card_info:
                        continue
                    card = self.render_engine.sprites["matrix"][card_info]
                    if not card.rect.collidepoint(pos):
                        continue
                    if card_info.owner != self.drag_arrow.targets[0].owner:
                        self.drag_arrow.end_pos = card.rect.center
                        self.drag_arrow.targets[1] = card_info
                        self.game_engine.attack(
                            self.game_engine.turn_manager.get_current_player(),
                            self.game_engine.turn_manager.get_next_player(),
                            self.drag_arrow.targets[0],
                            self.drag_arrow.targets[1],
                        )
                        break
                    else:
                        self.drag_arrow.end_pos = card.rect.center
                        self.drag_arrow.targets[1] = card_info
                        self.game_engine.upgrade_monster(
                            self.game_engine.turn_manager.get_current_player(),
                            self.drag_arrow.targets[0],
                            self.drag_arrow.targets[1],
                        )

            # Checking for player hitbox
            self._handle_arrow_drop_player_hitbox(pos)
            self.drag_arrow = None

    def _handle_arrow_drop_player_hitbox(self, pos):
        current_player_index = self.game_engine.turn_manager.current_player_index

        if current_player_index == 0:
            opponent_hand = self.matrix.areas["opponent_hand_area"]
        else:
            opponent_hand = self.matrix.areas["my_hand_area"]

        if (opponent_hand.rect.collidepoint(pos)):
            self.drag_arrow.end_pos = opponent_hand.rect.center
            self.drag_arrow.targets[1] = self.game_engine.turn_manager.get_next_player(
            )
            self.game_engine.attack(
                self.game_engine.turn_manager.get_current_player(),
                self.game_engine.turn_manager.get_next_player(),
                self.drag_arrow.targets[0],
                self.drag_arrow.targets[1],
            )

    def _handle_left_click_arrow(self, pos):
        for row in self.game_engine.game_state.field_matrix:
            for card_info in row:
                if not card_info:
                    continue
                card = self.render_engine.sprites["matrix"][card_info]
                if (
                    card.rect.collidepoint(pos)
                    and card_info.ctype == "monster"
                    and card_info.mode == "attack"
                    and card_info.owner == self.game_engine.turn_manager.get_current_player()
                ):
                    self.drag_arrow = DragArrow()
                    self.drag_arrow.targets[0] = card_info
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
                card = self.render_engine.sprites["matrix"][card_info]
                if card.rect.collidepoint(pos):
                    # Only call on_toggle when the sprite implements it.
                    # MonsterCardGUI implements on_toggle; generic CardGUI does not.
                    on_toggle = getattr(card, "on_toggle", None)
                    if callable(on_toggle):
                        on_toggle(self.game_engine)
                    return  # stop after first card is toggled

    def handle_click_card(self, pos):
        for card_ui in self.render_engine.sprites["matrix"].values():
            if card_ui.rect.collidepoint(pos):
                self.matrix.areas["preview_card_table"].set_card(card_ui)
                return  # stop after first match

        for card_ui in self.render_engine.sprites["hand"].values():
            if card_ui.rect.collidepoint(pos):
                self.matrix.areas["preview_card_table"].set_card(card_ui)
                return
                
    def draw(self, screen):
        if self.drag_arrow:
            self.drag_arrow.draw(screen)
