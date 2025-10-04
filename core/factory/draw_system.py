import random
from core.cards.card import Card
from core.factory.monster_factory import MonsterFactory
from core.factory.spell_factory import SpellFactory
from core.factory.trap_factory import TrapFactory

class DrawSystem:
    def __init__(self):
        self.draw_table = {
            "monster": {
                1: 60, 2:1 
            },
            "spell": {
                "Mystical Space Typhoon": 10, "Call of the Brave": 10, "Maniac War": 15,
                "Holy Shield": 15, "Pot of Greed": 15
            },
            "trap": {
                "Shattered Guard": 15, "Crippling Curse": 15, "Phantom Dodge": 20, 
                "Mirror Strike": 10, "Weaken Summon": 15
            }
        }

    def drop_card(self, card: Card, player):
        """Roll a card type and return category (like star level or subtype)."""
        table = self.drop_table[card]
        rand_num = random.randint(1, 100)
        cumulative = 0
        for k, rate in table.items():
            cumulative += rate
            if rand_num <= cumulative:
                if card.ctype == 'monster':
                    monster_type = random.choice(["Scholar", "Conqueror", "Forest Monster","Demon", "Forest Guard"]) 
                    return MonsterFactory.load_by_type_and_level(player, monster_type, k)
                elif card.ctype == 'spell':
                    return SpellFactory.load(player, k)
                elif card.ctype == 'trap':
                    return TrapFactory.load(player, k)
        return None
             