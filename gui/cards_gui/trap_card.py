from gui.cards_gui.card_gui import CardGUI
from core.cards.trap_card import TrapCard as LogicTrapCard


class TrapCardGUI(CardGUI):
    def __init__(self, trap_info: LogicTrapCard, *args, **kwargs):
        super().__init__(trap_info, *args, **kwargs)

    def on_set(self, game_engine):
        game_engine.set_trap(self.logic_card)
        # Trap stays face-down until triggered

    def on_drop(self, matrix, game_engine):
        cell = matrix.get_slot_at_pos(self.rect.center)
        if cell and self.logic_card.owner:
            ownership = game_engine.game_state.field_matrix_ownership[cell[0]][cell[1]]
            if ownership == self.logic_card.owner:
                if game_engine.set_trap(self.logic_card, cell):
                    self.is_draggable = False

        self.is_selected = False
        self.is_face_down = True

    def on_trigger(self, game_engine):
        game_engine.resolve_trap(self.logic_card)
        self.kill()
