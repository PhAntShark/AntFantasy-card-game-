import random
import json
from pathlib import Path
from gui.monster_card import MonsterCard


class MonsterFactory:
    DATA_FILE = Path("./assets/data/monsterInfo.json")
    _card_index = None

    def build(self):
        """Load all cards into a lookup table."""
        if not self.DATA_FILE.exists():
            raise FileNotFoundError(f"{self.DATA_FILE} not found")

        with open(self.DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Flatten and index by name
        # TODO: utilize category attribute later on
        self._card_index = {
            card_info["name"]: card_info
            for _, card_infos in data.items()
            for card_info in card_infos
            if card_info.get("texture") is not None
        }

    def load(self, player, size, name=None):
        if self._card_index is None:
            raise RuntimeError(
                "MonsterFactory not initialized. Call build() first.")

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

        return MonsterCard(
            name=card_info["name"],
            description=card_info.get("description", ""),
            owner=player,
            image_path=path,
            size=size,
            attack_points=card_info.get("attack_points", 0),
            defense_points=card_info.get("defense_points", 0),
            level_star=card_info.get("level_star", 1)
        )

    def get_cards(self):
        return self._card_index
