from core.game.effect_tracker import EffectTracker
from core.cards.monster_card import MonsterCard

''' Rewrite this shit and check'''
class AbilityRegistry:
    """Central registry for all abilities. Designed to work with GameEngine & EffectTracker."""

    # --- Ability Implementations ---
    @staticmethod
    def draw_two_cards(game_engine, effect_tracker: EffectTracker, player, **kwargs):
        """Draw 2 cards for the player."""
        for _ in range(2):
            game_engine.draw_card(player)

    @staticmethod
    def buff_attack(game_engine, effect_tracker: EffectTracker, player, target_monster, **kwargs):
        """Buff target monster's attack by 500 for 2 turns."""
        effect_tracker.apply_buff(target_monster, 'attack', 500, duration=2)

    @staticmethod
    def buff_defense(game_engine, effect_tracker: EffectTracker, player, target_monster, **kwargs):
        """Buff target monster's defense by 500 for 2 turns."""
        effect_tracker.apply_buff(target_monster, 'defense', 500, duration=2)

    @staticmethod
    def debuff_attack(game_engine, effect_tracker: EffectTracker, player, target_monster, **kwargs):
        """Debuff target monster's attack by 500 for 2 turns."""
        effect_tracker.apply_debuff(target_monster, 'attack', 500, duration=2)

    @staticmethod
    def debuff_defense(game_engine, effect_tracker: EffectTracker, player, target_monster, **kwargs):
        """Debuff target monster's defense by 500 for 2 turns."""
        effect_tracker.apply_debuff(target_monster, 'defense', 500, duration=2)

    @staticmethod
    def destroy_spell_trap(game_engine, effect_tracker: EffectTracker, player, target_card, **kwargs):
        """Destroy target spell/trap card."""
        if target_card.ctype in ('spell', 'trap'):
            game_engine.move_card_to_graveyard(target_card)

    @staticmethod
    def debuff_enemy_atk(game_engine, effect_tracker: EffectTracker, player, target_monster, **kwargs):
        """When an opponent's monster attacks, reduce its ATK by 300 points."""
        if hasattr(target_monster, 'atk'):
            effect_tracker.add_effect('debuff_attack', target_monster, 300, duration=1, source_card=None)

    @staticmethod
    def debuff_enemy_def(game_engine, effect_tracker: EffectTracker, player, target_monster, **kwargs):
        """When an opponent's monster attacks, reduce its DEF by 300 points."""
        if hasattr(target_monster, 'defend'):
            effect_tracker.add_effect('debuff_defense', target_monster, 300, duration=1, source_card=None)

    @staticmethod
    def debuff_summon(game_engine, effect_tracker: EffectTracker, player, summoned_monster, **kwargs):
        """When an opponent summons a monster, it loses 500 ATK and DEF."""
        if hasattr(summoned_monster, 'atk'):
            effect_tracker.add_effect('debuff_attack', summoned_monster, 500, duration=1, source_card=None)
        if hasattr(summoned_monster, 'defend'):
            effect_tracker.add_effect('debuff_defense', summoned_monster, 500, duration=1, source_card=None)

    @staticmethod
    def summon_monster_from_hand(game_engine, effect_tracker: EffectTracker, player, **kwargs):
        """Placeholder: summon a monster from the player's hand to the field.
        This normally requires UI selection; here we attempt to summon the first monster in hand.
        """
        hand = game_engine.game_state.player_info[player]["held_cards"].cards
        for card in list(hand):
            if getattr(card, 'ctype', None) == 'monster':
                # Find a free slot on player's side
                for r, row in enumerate(game_engine.game_state.field_matrix):
                    for c, cell in enumerate(row):
                        if cell is None:
                            if game_engine.summon_card(player, card, (r, c)):
                                return True
        return False

    @staticmethod
    def reflect_attack(game_engine, effect_tracker: EffectTracker, attacker, defender, **kwargs):
        """Reflect attack damage back to attacker."""
        if hasattr(attacker, "atk"):
            damage = attacker.atk
            attacker.owner.life_points -= damage
            print(f"{attacker.name} reflected! {attacker.owner.name} loses {damage} LP.")

    @staticmethod
    def dodge_attack(game_engine, effect_tracker: EffectTracker, attacker, defender, **kwargs):
        """Negate an attack (attacker cannot deal damage)."""
        print(f"{attacker.name}'s attack was dodged!")
        # You could implement further logic: e.g., prevent attack in GameEngine

    # --- Registry Mapping ---
    ABILITY_REGISTRY = {
        "draw_two_cards": draw_two_cards,
        "buff_attack": buff_attack,
        "buff_defense": buff_defense,
        "destroy_spell_trap": destroy_spell_trap,
        "debuff_enemy_atk": debuff_enemy_atk,
        "debuff_enemy_def": debuff_enemy_def,
        "debuff_summon": debuff_summon,
        "summon_monster_from_hand": summon_monster_from_hand,
        "reflect_attack": reflect_attack,
        "dodge_attack": dodge_attack
    }

    @classmethod
    def get(cls, ability_name):
        return cls.ABILITY_REGISTRY.get(ability_name)
