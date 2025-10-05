from gui.cards_gui.card_gui import CardGUI
from core.cards.spell_card import SpellCard as LogicSpellCard


class SpellCardGUI(CardGUI):
    def __init__(self, spell_info: LogicSpellCard, *args, **kwargs):
        super().__init__(spell_info, *args, **kwargs)

    def on_drop(self, matrix, game_engine):
        cell = matrix.get_slot_at_pos(self.rect.center)

        if cell:
            card_info = matrix.game_state.field_matrix[cell[0]][cell[1]]
            if self.logic_card.can_target(card_info):
                self.on_activate(game_engine, card_info)

        self.is_selected = False

    def on_activate(self, game_engine, target):
        game_engine.cast_spell(self.logic_card, target)
        # Once activated, spell is usually sent to graveyard
        self.kill()
