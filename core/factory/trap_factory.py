import json
from pathlib import Path
import random
from core.cards.trap_card import TrapCard


class TrapFactory:
    DATA_FILE = Path("./assets/data/trapInfo.json")
    _card_index = None

    def build(self):
        """Load all trap cards into a lookup table."""
        if not self.DATA_FILE.exists():
            raise FileNotFoundError(f"{self.DATA_FILE} not found")

        with open(self.DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Index by name
        self._card_index = {
            card_info['name']: card_info
            for card_info in data
            if card_info.get("texture") is not None
        }

    def load(self, player, name=None):
        """Create a spell card by name"""
        if self._card_index is None:
            raise RuntimeError(
                "SpellFactory not initialized. Call build() first.")

        if not name:
            card_info = random.choice(list(self._card_index.values()))
        else:
            card_info = self._card_index.get(name)

        if not card_info:
            return None

        path = Path("./assets" + card_info.get("texture", ""))
        if not path.is_file():
            # path = None  # Fallback, maybe use a placeholder
            return

        return TrapCard(
            name=card_info["name"],
            description=card_info.get("description", ""),
            ability=card_info.get("ability", ""),
            owner=player,
            image_path=path,
        )

    def get_cards(self):
        return self._card_index
    
