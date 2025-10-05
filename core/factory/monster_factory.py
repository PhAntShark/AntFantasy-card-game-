import random
import json
from pathlib import Path
from core.cards.monster_card import MonsterCard
import random


class MonsterFactory:
    DATA_FILE = Path("./assets/data/monsterInfo.json")
    _card_index = None

    def build(self):
        """Load all cards into a lookup table."""
        if not self.DATA_FILE.exists():
            raise FileNotFoundError(f"{self.DATA_FILE} not found")

        with open(self.DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Flatten and index by name, adding type information
        self._card_index = {}
        for monster_type, card_infos in data.items():
            for card_info in card_infos:
                if card_info.get("texture") is not None:
                    card_info["type"] = monster_type  # Add type field
                    self._card_index[card_info["name"]] = card_info

    def load(self, player, name=None):
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
            attack_points=card_info.get("attack_points", 0),
            defense_points=card_info.get("defense_points", 0),
            level_star=card_info.get("level_star", 1),
            monster_type=card_info.get("type", "Unknown")
        )

    def load_by_type_and_level(self, player, monster_type: str, level_star: int):
        """Load a monster by type and level star"""
        if self._card_index is None:
            raise RuntimeError(
                "MonsterFactory not initialized. Call build() first.")

        monster_random = []
        # TODO: this shit will return the first (2) start monster that it can find (the second is forgotten)
        # Find a monster of the specified type and level
        for card_info in self._card_index.values():
            if (card_info.get("type") == monster_type and
                card_info.get("level_star") == level_star):

                path = Path("./assets" + card_info.get("texture", ""))
                if not path.is_file():
                    continue  # Skip if texture not found

                card = MonsterCard(
                    name=card_info["name"],
                    description=card_info.get("description", ""),
                    owner=player,
                    image_path=path,
                    attack_points=card_info.get("attack_points", 0),
                    defense_points=card_info.get("defense_points", 0),
                    level_star=card_info.get("level_star", 1),
                    monster_type=card_info.get("type", "Unknown")
                )

                monster_random.append(card)
        if monster_random == []:
            return None

        monster = random.choice(monster_random)
        return monster

    def get_cards(self):
        return self._card_index
