from pygame.transform import rotate
from gui.card_gui import CardGUI
from core.cards.monster_card import MonsterCard as LogicMonsterCard


class MonsterCardGUI(CardGUI):
    def __init__(self, monster_info: LogicMonsterCard, *args, **kwargs):
        super().__init__(monster_info, *args, **kwargs)

    def on_toggle(self, game_engine):
        game_engine.toggle_card(self.logic_card)
        if self.logic_card.mode == "defense":
            self.image = rotate(self.original_image, 90)
        else:
            self.image = rotate(self.original_image, 0)

    def on_drop(self, matrix, game_engine):
        cell = matrix.get_slot_at_pos(self.rect.center)

        if cell and self.logic_card.owner:
            ownership = game_engine.game_state.field_matrix_ownership[cell[0]][cell[1]]
            if ownership == self.logic_card.owner:
                if game_engine.summon_card(self.logic_card.owner, self.logic_card, cell):
                    self.is_draggable = False

        self.is_selected = False
