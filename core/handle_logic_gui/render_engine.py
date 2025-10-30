import pygame
from collections import defaultdict
from gui.cards_gui.card_gui import CardGUI
from gui.cards_gui.monster_card import MonsterCardGUI
from gui.cards_gui.spell_card import SpellCardGUI
from gui.cards_gui.trap_card import TrapCardGUI
from gui.cards_gui.stat_overlay import CardStatOverlay
from gui.animations.manager import AnimationManager
from gui.utils import random_color
from core.player import Player
from core.game_info.events import (
    AttackEvent, TrapTriggerEvent, ToggleEvent,
    SpellActiveEvent, MergeEvent
)


class RenderEngine:
    def __init__(self, field_matrix, screen, train_mode=False):
        self.screen = screen
        self.field_matrix = field_matrix
        self.sprites = {
            "hand": {},   # {card.id: CardGUI}
            "matrix": {},  # {card.id: CardGUI}
        }
        self.exisiting_colors = defaultdict(dict)
        self.pending_merges = []
        self.animation_mgr = AnimationManager(train_mode=train_mode)

    def reset(self):
        for value in self.sprites.values():
            value.clear()
        self.exisiting_colors = defaultdict(dict)
        self.pending_merges.clear()

    def update(self, game_engine, game_state, matrix, events):
        self.handle_events(matrix, events)
        self.register_cards(game_state, matrix)
        self.handle_merge(game_engine, game_state)
        self.process_pending_merges()

    def handle_merge(self, game_engine, game_state):
        for player in game_state.players:
            groups = game_engine.get_mergeable_groups(player)
            extc = self.exisiting_colors[player]

            for key, group in groups.items():
                if len(group) < 2:
                    continue

                color = extc.get(key, None)
                if color is None:
                    color = random_color()
                    while color in extc.values():
                        color = random_color()
                    extc[key] = color

                for card in group:
                    card_ui = self.sprites["matrix"].get(card.id)
                    if card_ui:
                        card_ui.highlight = True
                        card_ui.highlight_color = color

            removed = [key for key in list(extc.keys()) if key not in groups]
            for key in removed:
                extc.pop(key, None)

    def register_cards(self, game_state, matrix):
        self.register_hand(game_state, matrix)
        self.register_matrix(game_state, matrix,
                             self.animation_mgr.create_place_animation)

    def handle_events(self, matrix, events):
        try:
            for event in events.get_events():
                et = type(event)

                if et is AttackEvent:
                    card = self.sprites["matrix"].get(event.card.id)
                    if not card:
                        continue

                    if isinstance(event.target, Player):
                        opponent_hand = next(
                            (h for h in getattr(self.field_matrix, "hands", [])
                             if getattr(h, "player", None) == event.target),
                            None
                        )
                        if opponent_hand:
                            self.animation_mgr.create_attack_player_animation(
                                card, opponent_hand)
                    else:
                        target = self.sprites["matrix"].get(event.target.id)
                        if target:
                            self.animation_mgr.create_attack_animation(
                                card, target)

                elif et is TrapTriggerEvent:
                    trap = self.sprites["matrix"].get(event.card.id)
                    if trap:
                        self.animation_mgr.create_trigger_animation(trap)
                        matrix.areas["preview_card_table"].set_card(trap)

                elif et is ToggleEvent:
                    card = self.sprites["matrix"].get(event.card.id)
                    if card:
                        self.animation_mgr.create_toggle_animation(
                            card, event.mode)

                elif et is SpellActiveEvent:
                    spell = self.sprites["hand"].get(event.spell.id)
                    if spell:
                        self.animation_mgr.create_spell_animation(spell)

                elif et is MergeEvent:
                    self.pending_merges.append(event)

            events.clear_events()
        except Exception as e:
            print(f"[ERROR] handle_events failed: {e}")

    def process_pending_merges(self):
        still_pending = []
        for event in self.pending_merges:
            card_id = event.card.id
            target_id = event.target.id
            result_id = event.result_card.id

            if (card_id in self.sprites["matrix"] and
                    target_id in self.sprites["matrix"] and
                    result_id in self.sprites["matrix"]):
                card = self.sprites["matrix"][card_id]
                target = self.sprites["matrix"][target_id]
                result = self.sprites["matrix"][result_id]
                self.animation_mgr.create_merge_animation(card, target, result)
            else:
                still_pending.append(event)

        self.pending_merges = still_pending

    def is_pending_merge(self, card_id):
        for event in self.pending_merges:
            if card_id in (event.card.id, event.target.id, event.result_card.id):
                return True
        return False

    def sync_sprites(self, desired_set, sprite_dict, create_sprite,
                     add_animation=None, align_fn=None):
        existing_ids = set(sprite_dict.keys())
        desired_ids = {card.id for card in desired_set}

        to_add = desired_ids - existing_ids
        to_remove = existing_ids - desired_ids

        # Remove old sprites with animation
        for cid in to_remove:
            if not self.is_pending_merge(cid):
                self.animation_mgr.create_death_animation(cid, sprite_dict)

        # Add new sprites
        for card in desired_set:
            if card.id in to_add:
                sprite = create_sprite(card)
                sprite_dict[card.id] = sprite

        if align_fn and (to_add or to_remove):
            align_fn()

        if add_animation and to_add:
            for cid in to_add:
                if not self.is_pending_merge(cid):
                    add_animation(sprite_dict[cid])

    @staticmethod
    def create_gui_card(card, matrix):
        if card.ctype == "monster":
            return CardStatOverlay(MonsterCardGUI(card, size=(
                matrix.grid["slot_width"] / 2,
                matrix.grid["slot_height"]
            )))
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
        else:
            return CardGUI(card, size=(
                matrix.grid["slot_width"] / 2,
                matrix.grid["slot_height"]
            ))

    def register_hand(self, game_state, matrix):
        current_cards = set()
        for player in game_state.players:
            held_cards = game_state.player_info[player]["held_cards"]
            current_cards.update(held_cards.cards)
            if not player.is_opponent:
                self.field_matrix.areas["my_hand_area"].hand_info = held_cards
            else:
                self.field_matrix.areas["opponent_hand_area"].hand_info = held_cards

        def make_hand_sprite(card):
            return self.create_gui_card(card, matrix)

        self.sync_sprites(
            desired_set=current_cards,
            sprite_dict=self.sprites["hand"],
            create_sprite=make_hand_sprite,
            add_animation=lambda sprite: self.animation_mgr.create_draw_animation(
                matrix, sprite),
            align_fn=lambda: self.align_cards(matrix, check=False)
        )

    def register_matrix(self, game_state, matrix, animation=None):
        current_cards = {
            card for row in game_state.field_matrix for card in row if card
        }

        def make_matrix_sprite(card):
            sprite = self.create_gui_card(card, matrix)
            sprite.rect.center = matrix.get_slot_rect(
                *card.pos_in_matrix).center
            sprite.placed_pos = sprite.rect.center

            if isinstance(sprite, TrapCardGUI):
                if card.owner.is_opponent:
                    sprite.is_face_down = True
                    sprite.card_surface = pygame.transform.smoothscale(
                        sprite.image_face_down.copy(), sprite.display_size)
                else:
                    sprite.is_face_down = False
                    sprite._render_card_with_text()
                sprite.update()
            else:
                sprite.is_face_down = False
                sprite._render_card_with_text()
                if card.owner.is_opponent:
                    sprite.card_surface = pygame.transform.flip(
                        sprite.card_surface, False, True)
                sprite.update()
            return sprite

        self.sync_sprites(
            desired_set=current_cards,
            sprite_dict=self.sprites["matrix"],
            add_animation=animation,
            create_sprite=make_matrix_sprite
        )

    def align_cards(self, matrix, check=False):
        for hand in matrix.hands:
            hand.align(self.sprites["hand"], check=check)

    def draw(self):
        for group in self.sprites.values():
            for sprite in group.values():
                sprite.draw(self.screen)
