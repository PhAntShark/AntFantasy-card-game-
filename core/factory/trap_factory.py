from core.cards.trap_card import TrapCard
from pathlib import Path
from core.factory.card_registry import CardRegistry


class TrapFactory:
    DATA_FILE = Path("./assets/data/trapInfo.json")

    def build(self):
        CardRegistry.build_from_file(
            card_type="trap",
            path=self.DATA_FILE,
            CardClass=TrapCard
        )

    def load(self, player, name=None):
        return CardRegistry.create("trap", owner=player, name=name)

    def get_cards(self):
        return CardRegistry.list_cards("trap")
