from dataclasses import dataclass
from typing import Union
from core.cards.card import Card
from core.player import Player


@dataclass
class AttackEvent:
    card: Card
    target: Card


@dataclass
class TrapTriggerEvent:
    card: Card
    target: Card


@dataclass
class ToggleEvent:
    card: Card
    mode: str


@dataclass
class SpellActiveEvent:
    spell: Card
    target: Union[Card, Player, None]


@dataclass
class MergeEvent:
    card: Card
    target: Card
    result_card: Card


GameEvent = Union[AttackEvent, TrapTriggerEvent,
                  ToggleEvent, SpellActiveEvent, MergeEvent]


class EventLogger:
    def __init__(self):
        self._events: list[GameEvent] = []

    def get_events(self):
        return self._events

    def add_event(self, event: GameEvent):
        self._events.append(event)

    def clear_events(self):
        self._events.clear()
