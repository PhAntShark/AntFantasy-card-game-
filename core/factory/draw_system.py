import random
from core.cards.card import Card
from core.factory.monster_factory import MonsterFactory
from core.factory.spell_factory import SpellFactory
from core.factory.trap_factory import TrapFactory

class DrawSystem:
    def __init__(self):
        
        self.generic_draw = {'monster': 60, 'spell': 50, 'trap':40}
        self.monster_factory = MonsterFactory()
        self.monster_factory.build()
        self.spell_factory = SpellFactory()
        self.spell_factory.build()
        self.trap_factory = TrapFactory()
        self.trap_factory.build()
        self.draw_table = {
            "monster": {
                1:98, 2:0.000001
            }, 
            "spell": {
                "Mystical Space Typhoon": 10, "Call of the Brave": 15, "Maniac War": 25,
                "Holy Shield": 25, "Pot of Greed": 25
            },
            "trap": {
                "Shattered Guard": 25, "Crippling Curse": 25, "Phantom Dodge": 25, 
                "Mirror Strike": 10, "Weaken Summon": 15
            }
        }

    def rate(self, table):
        rand_num = random.randint(1, 100)
        cumulative = 0
        for k, rate in table.items():
            cumulative += rate
            if rand_num <= cumulative:
                return k
        return k


    def rate_card_draw(self, player):
        card_type = self.rate(self.generic_draw)
        k = self.rate(self.draw_table[card_type])
        card = None
        if card_type == 'monster':
            monster_type = random.choice(["Scholar", "Conqueror", "Forest Monster","Demon", "Forest Guard"]) 
            card = self.monster_factory.load_by_type_and_level(player, monster_type, k)
            if not card:
                card_gay = random.choice(list(self.monster_factory.get_cards().keys()))
                card = self.monster_factory.load(player, card_gay)
        elif card_type == "spell":
            card = self.spell_factory.load(player, k)
        elif card_type == "trap":
            card = self.trap_factory.load(player, k)
        return card
    