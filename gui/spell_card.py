from gui.card_gui import CardGUI
from core.cards.spell_card import SpellCard as LogicSpellCard


class SpellCardGUI(CardGUI):
    def __init__(self, spell_info: LogicSpellCard, *args, **kwargs):
        super().__init__(spell_info, *args, **kwargs)

    def on_activate(self, game_engine):
        game_engine.activate_spell(self.logic_card)
        # Once activated, spell is usually sent to graveyard
        self.kill()
