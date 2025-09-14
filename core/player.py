from card import Card


class Player:
    # held_card = 0
    # field = 0
    def __init__( self, held_cards, grave_yard, field_cards, player_index, life_points=5000, name = None):  # argument MUST front of parameter
        self.player_index = player_index
        self.life_points = life_points
        self.held_cards = []
        self.grave_yard = []
        self.field_cards = []
        self.name = name if name else f'Player {player_index}'
    def draw_card(self, card):
        if len(self.held_cards) <= 15:
            self.held_cards.append(card)
            self.held_cards += 1
            # print('you draw the card')
        else:
            return "your card on hand is full"

    def player_card(self):
        return {
            "hand": self.held_cards,
            "field": self.field_cards,
            "graveyard": self.grave_yard,
        }

    def card_field_summon(self, card):
        if len(self.field_cards) < 10:  # if field < 10
            self.field_cards.append(card)  # append the card from the held_Card list
            # field += 1  # field = +1
            self.held_cards.remove(card)  # pop the card from the list
            # held_card -= 1  # held_card = -1
            return f"success for summon {card} on the field"
        else:
            return "your field is full"

    def add_grave_yard(self, card):
        if card in self.field_cards:
            self.field_cards.remove(card)
            self.grave_yard.append(card)

    def change_mon_pos(self, card, attacker, defender, pos="attack"):
        {"action": "attack", "attack": attacker, "defender": defender}
        if card in self.field_cards:
            card.set_pos(pos)
            return {"action": "change_position", "card": card.name, "new_pos": pos}
        else:
            return f"{card} not in the field"
