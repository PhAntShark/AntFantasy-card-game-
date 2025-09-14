from player import Player


class Game_State:
    def __init__(self, players: list[Player]):
        self.players = players
        self.current_player_index = 0
        self.turn_count = 1
        self.held_card = []
        self.field_card = []
        self.grave_yard = []
        self.global_effect = []

    def current_player(self):
        return self.players[self.current_player_index]

    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

        if self.current_player_index == 0:
            self.turn_count += 1
        return

    def global_effecte(self, card):
        pass

    def add_card_field(self, card):
        self.held_card.pop(card)
        self.field_card.append(card)
        return f"the monster has {card} summon on the field"

    def add_grave_yard(self, card):
        if card in self.field_card:
            self.field_card.pop(card)
            self.grave_yard.append(card)
            return f"monster in the grave yard: {card}"
    
