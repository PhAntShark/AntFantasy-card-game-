import json
from pathlib import Path
from cards.monsterCard import MonsterCard
from player import Player


class CardFactory:
    DATA_FILE = Path("../../assets/data/monsterInfo.json")

    @staticmethod
    def load(name: str, owner: Player):
        """Load a single card by its unique name from the JSON file."""
        if not CardFactory.DATA_FILE.exists():
            raise FileNotFoundError(f"{CardFactory.DATA_FILE} not found")

        with open(CardFactory.DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Flatten all cards across all genres and subcategories
        for category, cards in data.items():
            for card in cards:
                # TODO: turn this into a map later
                if card.get("name") == name:
                    return MonsterCard(
                        name=card["name"],
                        description=card.get("description", ""),
                        owner=owner,
                        attack_points=card.get("attack_points", 0),
                        defense_points=card.get("defense_points", 0),
                        level_star=card.get("level_star", 1)
                    )

        # If card not found
        raise ValueError(f"Card '{name}' not found in {CardFactory.DATA_FILE}")
