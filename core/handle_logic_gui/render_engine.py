from gui.cards_gui.card_gui import CardGUI
from gui.cards_gui.monster_card import MonsterCardGUI
from gui.cards_gui.spell_card import SpellCardGUI
from gui.cards_gui.trap_card import TrapCardGUI
from gui.animations.manager import AnimationManager
from gui.utils import random_color
from core.game_info.events import (
    AttackEvent, TrapTriggerEvent, ToggleEvent,
    SpellActiveEvent, MergeEvent
)
from collections import defaultdict


class RenderEngine:
    def __init__(self, screen):
        self.screen = screen
        self.sprites = {
            "hand": {},
            "matrix": {},
        }
        self.animation_mgr = AnimationManager()
        self.exisiting_colors = defaultdict(dict)
        self.pending_merges = []

    def update(self, game_engine, game_state, matrix, events):
        self.handle_events(events)
        self.register_cards(game_state, matrix)
        self.handle_merge(game_engine, game_state)

        # After sync, process deferred merge events
        self.process_pending_merges()

    def handle_merge(self, game_engine, game_state):
        for player in game_state.players:
            groups = game_engine.get_mergeable_groups(player)
            extc = self.exisiting_colors[player]

            for key, group in groups.items():
                if len(group) < 2:
                    continue

                if key not in extc.keys():
                    color = random_color()
                    while color in extc.values():
                        color = random_color()
                    extc[key] = color
                else:
                    color = extc[key]

                for card in group:
                    card_ui = self.sprites["matrix"][card]
                    card_ui.highlight = True
                    card_ui.highlight_color = color

            removed = [key for key in extc.keys()
                       if key not in groups.keys()]
            for key in removed:
                extc.pop(key)

    def register_cards(self, game_state, matrix):
        self.register_hand(game_state, matrix)
        self.register_matrix(game_state, matrix,
                             self.animation_mgr.create_place_animation)

    def handle_events(self, events):
        for event in events.get_events():
            if isinstance(event, AttackEvent):
                card1 = self.sprites["matrix"][event.card]
                card2 = self.sprites["matrix"][event.target]
                # FIX: this doesnt handle attacking the player
                self.animation_mgr.create_attack_animation(card1, card2)

            elif isinstance(event, TrapTriggerEvent):
                trap = self.sprites["matrix"][event.card]
                self.animation_mgr.create_trigger_animation(trap)

            elif isinstance(event, ToggleEvent):
                card = self.sprites["matrix"][event.card]
                self.animation_mgr.create_toggle_animation(card, event.mode)

            elif isinstance(event, SpellActiveEvent):
                spell = self.sprites["hand"][event.spell]
                self.animation_mgr.create_spell_animation(spell)

            elif isinstance(event, MergeEvent):
                # Defer merge until sprites are synced
                self.pending_merges.append(event)

        events.clear_events()

    def process_pending_merges(self):
        """Try to run merge animations once result sprite exists."""
        still_pending = []
        for event in self.pending_merges:
            if event.card in self.sprites["matrix"] \
               and event.target in self.sprites["matrix"] \
               and event.result_card in self.sprites["matrix"]:
                card = self.sprites["matrix"][event.card]
                target = self.sprites["matrix"][event.target]
                result = self.sprites["matrix"][event.result_card]
                self.animation_mgr.create_merge_animation(card, target, result)
            else:
                # keep waiting
                still_pending.append(event)
        self.pending_merges = still_pending

    def is_pending_merge(self, card):
        for event in self.pending_merges:
            if card in vars(event).values():
                return True
        return False

    def sync_sprites(self, desired_set, sprite_dict, create_sprite,
                     add_animation=None, align_fn=None):
        existing_set = set(sprite_dict.keys())
        to_add = desired_set - existing_set
        to_remove = existing_set - desired_set

        # Remove old sprites (death anim instead of instant removal)
        for card in to_remove:
            if not self.is_pending_merge(card):
                self.animation_mgr.create_death_animation(card, sprite_dict)

        # Add new sprites
        for card in to_add:
            card_ui = create_sprite(card)
            sprite_dict[card] = card_ui

        if align_fn and (to_add or to_remove):
            align_fn()

        if add_animation and to_add:
            for card in to_add:
                if not self.is_pending_merge(card):
                    add_animation(sprite_dict[card])

    def create_gui_card(self, card, matrix):
        if card.ctype == "monster":
            return MonsterCardGUI(card, size=(
                matrix.grid["slot_width"] / 2,
                matrix.grid["slot_height"]
            ))
        elif card.ctype == "spell":
            return SpellCardGUI(card, size=(
                matrix.grid["slot_width"] / 2,
                matrix.grid["slot_height"]
            ))
        elif card.ctype == "trap":
            return TrapCardGUI(card, size=(
                matrix.grid["slot_width"] / 2,
                matrix.grid["slot_height"]
            ))
        else:  # fallback
            return CardGUI(card, size=(
                matrix.grid["slot_width"] / 2,
                matrix.grid["slot_height"]
            ))

    def register_hand(self, game_state, matrix):
        current_cards = set()
        for player in game_state.players:
            current_cards.update(
                game_state.player_info[player]["held_cards"].cards)

        def make_hand_sprite(card):
            return self.create_gui_card(card, matrix)

        self.sync_sprites(
            desired_set=current_cards,
            sprite_dict=self.sprites["hand"],
            create_sprite=make_hand_sprite,
            add_animation=self.animation_mgr.create_draw_animation,
            align_fn=lambda: self.align_cards(matrix)
        )

    def register_matrix(self, game_state, matrix, animation=None):
        current_cards = {
            card for row in game_state.field_matrix for card in row if card is not None
        }

        def make_matrix_sprite(card):
            sprite = self.create_gui_card(card, matrix)
            sprite.rect.center = matrix.get_slot_rect(
                *card.pos_in_matrix).center
            return sprite

        self.sync_sprites(
            desired_set=current_cards,
            sprite_dict=self.sprites["matrix"],
            add_animation=animation,
            create_sprite=make_matrix_sprite
        )

    def align_cards(self, matrix):
        for hand in matrix.hands:
            hand.align(self.sprites["hand"])

    def draw(self):
        for group in self.sprites.values():
            for sprite in group.values():
                sprite.draw(self.screen)
