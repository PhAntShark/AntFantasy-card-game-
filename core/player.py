import random
from cards.card import Card
from typing import List


class Player:
    def __init__(self,
                 player_index: int,
                 name: str,
                 deck_cards: List[Card],
                 held_cards: List[Card],
                 grave_yard_cards: List[Card],
                 field_cards: List[Card],
                 life_points: int = 5000,
                 has_summoned: bool = False
                 ):
        self.player_index = player_index
        self.name = name
        self.life_points = life_points

        self.held_cards = held_cards
        self.grave_yard_cards = grave_yard_cards
        self.field_cards = field_cards
        self.deck_cards = deck_cards

        self.has_summoned = has_summoned

    def __str__(self):
        return f"Name: {self.name} \
                 Lifepoint: {self.life_points} \
                 Hand: {self.held_cards} \
                 Field: {self.field_cards} \
                 Graveyard: {self.grave_yard_cards}"

    def draw_specific_card(self, card):
        self.held_cards.append(card)

    def draw_random_card(self):
        card = random.choice(self.deck)
        self.deck.remove(card)
        self.held_cards.append(card)

    @staticmethod
    def first_game_turn_draw(players):
        for player in players:
            for _ in range(5):
                player.draw_random_card()

    def summon(self, card):
        # append the card from the held_Card list
        self.field_cards.append(card)
        self.held_cards.remove(card)
        self.player_summon = True

    def add_grave_yard(self, card):
        self.field_cards.remove(card)
        self.grave_yard_cards.append(card)
