import random

class Player:
    def __init__( self, deck, held_cards, grave_yard, field_cards, player_index, life_points=5000, name = None, player_summon = False):  # argument MUST front of parameter
        self.player_index = player_index
        self.life_points = life_points
        self.held_cards = []
        self.grave_yard = []
        self.field_cards = []
        self.deck = []
        self.player_summon = player_summon
        self.name = name if name else f'Player {player_index}'
        
    def draw_card(self, card):
        if len(self.held_cards) <= 15:
            self.held_cards.append(card)
            print('you draw the card')
        else:
            return "your card on hand is full"
    
    def draw_random_card(self):
        if self.deck and len (self.held_cards) < 15:
            card = random.choice(self.deck)
            self.deck.remove(card)
            self.held_cards.append(card)
            print(f'{self.name} drew {card.name}')
            
    @staticmethod
    def first_game_turn_draw(players):
        for player in players:
            for _ in range(5):
                player.draw_random_card()
            

    def player_card(self):
        return {
            "hand": self.held_cards,
            "field": self.field_cards,
            "graveyard": self.grave_yard,
        }

    def card_field_summon(self, card):
        if len(self.field_cards) < 10:  # if field < 10
            self.field_cards.append(card)  # append the card from the held_Card list
            self.held_cards.remove(card)  # pop the card from the list
            self.player_summon = True
            return f"success for summon {card} on the field"
        else:
            return "your field is full"

    def add_grave_yard(self, card):
        if card in self.field_cards:
            self.field_cards.remove(card)
            self.grave_yard.append(card)

    def change_mon_pos(self, card, attacker, defender, pos="attack"):
        #{"action": "attack", "attack": attacker, "defender": defender}
        if card in self.field_cards:
            card.set_pos(pos)
            return {"action": "change_position", "card": card.name, "new_pos": pos}
        else:
            return f"{card} not in the field"
