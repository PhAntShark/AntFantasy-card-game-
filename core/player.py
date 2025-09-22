import random
from core.cards.card import Card
from typing import List


class Player:
    def __init__(self,
                 player_index: int,
                 name: str,
                 deck_cards: List[Card],
                 held_cards: List[Card],
                 grave_yard_cards: List[Card],
                 life_points: int = 5000,
                 has_summoned: bool = False,
                 is_opponent: bool = False
                 ):
        self.player_index = player_index
        self.name = name
        self.life_points = life_points

        self.held_cards = held_cards
        self.grave_yard_cards = grave_yard_cards
        self.deck_cards = deck_cards

        self.has_summoned = has_summoned
        self.is_opponent = is_opponent

    def __str__(self):
        return f"Name: {self.name} \
                 Life-point: {self.life_points} \
                 Hand: {self.held_cards} \
                 Graveyard: {self.grave_yard_cards}"

    def draw_card(self, card):
        # self.deck_cards.remove(card)
        self.held_cards.append(card)

    def summon(self, card):
        self.held_cards.remove(card)
        self.has_summoned = True

    def add_grave_yard(self, card):
        self.grave_yard_cards.append(card)
