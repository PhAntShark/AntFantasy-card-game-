from collections import defaultdict
from .animation import Animation
from .attack import AttackAnimation
from .death import DeathAnimation
from .place import PlaceAnimation
from .move import MoveAnimation
from .queue import AnimationQueue
from .trap_trigger import TrapTriggerAnimation
from .toggle import ToggleRotateAnimation
from .spell_activate import SpellAnimation
from .merge import MergeAnimation
from .attack_player import AttackPlayerAnimation
from gui.effects.manager import EffectManager
from gui.audio_manager import AudioManager


class AnimationManager:
    def __init__(self, train_mode=False):
        self.queues = defaultdict(AnimationQueue)
        self.train_mode = train_mode
        EffectManager.set_train_mode(train_mode)
        AudioManager.set_train_mode(train_mode)

        if train_mode:
            Animation.audio = False

    def _duration(self, value):
        """Return 0 duration if train_mode is True, else the given value."""
        return 0 if self.train_mode else value

    def add_animation(self, animation):
        for sprite in animation.locks:
            self.queues[sprite].add(animation)

    def update(self, dt):
        finished_anims = []
        candidates = {q.peek() for q in self.queues.values() if q.peek()}

        for anim in candidates:
            if all(self.queues[sprite].peek() is anim for sprite in anim.locks):
                if anim.update(dt):
                    finished_anims.append(anim)

        for anim in finished_anims:
            for sprite in anim.locks:
                q = self.queues[sprite]
                if q.peek() is anim:
                    q.pop()
            for sprite in list(self.queues.keys()):
                if len(self.queues[sprite]) == 0:
                    self.queues.pop(sprite)

    # Convenience creators
    def create_death_animation(self, card, sprite_dict, duration=0.2):
        self.add_animation(DeathAnimation(
            sprite_dict[card],
            self._duration(duration),
            on_finish=lambda: self._cleanup(card, sprite_dict)
        ))

    def _cleanup(self, card, sprite_dict):
        sprite = sprite_dict.get(card)
        if sprite:
            sprite.kill()
            sprite_dict.pop(card)

    def create_draw_animation(self, matrix, card, duration=0.3):
        start_pos = matrix.player_zones[card.logic_card.owner]["deck"].rect.center
        self.add_animation(MoveAnimation(
            card, start_pos, card.rect.center, self._duration(duration)))

    def create_place_animation(self, card, duration=0.5):
        self.add_animation(PlaceAnimation(
            card, card.rect.center, self._duration(duration)))

    def create_attack_animation(self, card1, card2, duration=1):
        self.add_animation(AttackAnimation(
            card1, card2, self._duration(duration)))

    def create_attack_player_animation(self, card, game_area, duration=0.6):
        self.add_animation(AttackPlayerAnimation(
            card, game_area, duration=self._duration(duration)))

    def create_trigger_animation(self, card, duration=1):
        self.add_animation(TrapTriggerAnimation(
            card, duration=self._duration(duration)))

    def create_merge_animation(self, card1, card2, result_card, duration=1):
        self.add_animation(MergeAnimation(
            card1, card2, result_card,
            duration=self._duration(duration),
            on_finish=lambda c: self.create_place_animation(c)))

    def create_toggle_animation(self, card, mode, duration=0.3):
        if mode == "attack":
            start_angle = 90
            end_angle = 0
            file = "assets/sounds/sword-slice.mp3"
        else:
            start_angle = 0
            end_angle = 90
            file = "assets/sounds/shield-guard.mp3"

        self.add_animation(ToggleRotateAnimation(
            card,
            start_angle=start_angle,
            end_angle=end_angle,
            duration=self._duration(duration),
            on_finished=lambda: AudioManager.play_sound(file)
        ))

    def create_spell_animation(self, spell, duration=0.2):
        self.add_animation(SpellAnimation(spell, self._duration(duration)))
