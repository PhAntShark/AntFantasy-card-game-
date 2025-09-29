from gui.card_gui import CardGUI
from core.cards.trap_card import TrapCard as LogicTrapCard


class TrapCardGUI(CardGUI):
    def __init__(self, trap_info: LogicTrapCard, *args, **kwargs):
        super().__init__(trap_info, *args, **kwargs)

    def on_set(self, game_engine):
        game_engine.set_trap(self.logic_card)
        # Trap stays face-down until triggered

    def on_trigger(self, game_engine):
        game_engine.trigger_trap(self.logic_card)
        self.kill()
