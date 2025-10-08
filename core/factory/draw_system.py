import random
from core.factory.monster_factory import MonsterFactory
from core.factory.spell_factory import SpellFactory
from core.factory.trap_factory import TrapFactory


class DrawSystem:
    def __init__(self):
        # Overall chance to draw each card type (total weight doesn't have to be 100)
        self.generic_draw = {
            'monster': 60,  # 60% chance roughly
            'spell': 25,    # 25%
            'trap': 15      # 15%
        }

        self.monster_factory = MonsterFactory()
        self.monster_factory.build()
        self.spell_factory = SpellFactory()
        self.spell_factory.build()
        self.trap_factory = TrapFactory()
        self.trap_factory.build()

        # Probabilities for specific cards within each type
        self.draw_table = {
            "monster": {
                1: 99,  # Level 1 monsters are common
                2: 1
            },
            "spell": {
                "Mystical Space Typhoon": 15,
                "Call of the Brave": 20,
                "Maniac War": 20,
                "Aura Shield": 25,
                "Reinforcement": 20
            },
            "trap": {
                "Shattered Guard": 20,
                "Crippling Curse": 20,
                "Phantom Dodge": 25,
                "Mirror Strike": 20,
                "Weaken Summon": 15
            }
        }


    def rate(self, table):
        # Allow tables whose weights don't sum to 100. Use total weight and
        # pick a random value in [0, total) so any positive weights work.
        items = list(table.items())
        total = 0
        for _, w in items:
            try:
                total += float(w)
            except Exception:
                total += 0

        if total <= 0:
            # fallback: uniform random choice of keys
            return random.choice([k for k, _ in items])

        r = random.uniform(0, total)
        cumulative = 0.0
        for k, w in items:
            try:
                cumulative += float(w)
            except Exception:
                continue
            if r <= cumulative:
                return k
        # Fallback to last key
        return items[-1][0]

    def rate_card_draw(self, player):
        card_type = self.rate(self.generic_draw)
        k = self.rate(self.draw_table[card_type])
        card = None
        if card_type == 'monster':
            monster_type = random.choice(
                ["Scholar", "Conqueror", "Forest Monster", "Demon", "Forest Guard"])
            card = self.monster_factory.load_by_type_and_level(
                player, monster_type, k)
            if not card:
                card_gay = random.choice(
                    list(self.monster_factory.get_cards().keys()))
                card = self.monster_factory.load(player, card_gay)
        elif card_type == "spell":
            card = self.spell_factory.load(player, k)
        elif card_type == "trap":
            card = self.trap_factory.load(player, k)
        if not card:
            print(card_type, k)
        return card

    #debug function find card missing
    def check_draw_issues(self, player, attempts=1000):
        """
        Try drawing cards repeatedly and report any failures.
        """
        failures = []
        for _ in range(attempts):
            card_type = self.rate(self.generic_draw)
            card_key = self.rate(self.draw_table[card_type])
            card = None
            if card_type == 'monster':
                monster_type = random.choice(
                    ["Scholar", "Conqueror", "Forest Monster", "Demon", "Forest Guard"])
                card = self.monster_factory.load_by_type_and_level(player, monster_type, card_key)
                if not card:
                    # fallback
                    for fallback_key in self.monster_factory.get_cards().keys():
                        card = self.monster_factory.load(player, fallback_key)
                        if card:
                            break
            elif card_type == "spell":
                card = self.spell_factory.load(player, card_key)
            elif card_type == "trap":
                card = self.trap_factory.load(player, card_key)

            if not card:
                failures.append((card_type, card_key))

        if failures:
            print(f"Found {len(failures)} problematic draws:")
            for f in failures:
                print(f" - Failed to draw {f[0]} card with key '{f[1]}'")
        else:
            print("No draw issues found after", attempts, "attempts.")