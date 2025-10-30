import logging
import math
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from core.player import Player
from core.cards.monster_card import MonsterCard
from core.cards.trap_card import TrapCard


@dataclass
class RewardConfig:
    """Configuration for reward values."""
    # Action rewards
    deploy_monster: float = 0.8
    deploy_trap: float = 0.15  # Reduced since main reward is from triggering
    attack_destroy: float = 0.6
    survive_attack: float = 0.25
    monster_destroyed: float = -0.5
    use_spell: float = 0.35
    merge_base: float = 1.0

    # Damage-based rewards (logarithmic scaling)
    damage_scale_factor: float = 0.05   

    # Field advantage
    field_advantage_multiplier: float = 0.5  # Normalized multiplier
    field_advantage_cap: float = 0.5
    # Smooth sudden swings (0.9-0.99 range)
    field_advantage_decay: float = 0.95
    board_control_bonus: float = 0.2
    no_monsters_penalty: float = -0.3
    trap_advantage: float = 0.1

    # Penalties
    skip_turn: float = -0.25
    premature_end_penalty: float = -0.75
    invalid_action: float = -0.5
    valid_action_bonus: float = 0.1

    # Terminal rewards
    win: float = 2.0
    lose: float = -2.0

    # Bonus rewards
    direct_attack_bonus: float = 0.5
    trap_trigger_base: float = 0.5  # Base reward per trap trigger
    trap_trigger_log_scale: float = 1.0  # Controls logarithmic steepness
    max_trap_trigger_reward: float = 1.5  # Cap for multiple traps
    spell_combo_bonus: float = 0.3
    high_level_summon_bonus: float = 0.1
    bait_block_bonus: float = 0.3

    # Strength-based scaling
    strength_scale_factor: float = 0.1
    
    # Toggle reward (reduce toggle spam)
    toggle_optimal: float = 0.2
    toggle_suboptimal: float = -0.3
    
    # Reward clamping
    max_step_reward: float = 2.0
    min_step_reward: float = -2.0


@dataclass
class RewardBreakdown:
    """Detailed breakdown of rewards for logging."""
    total: float = 0.0
    components: Dict[str, float] = field(default_factory=dict)
    action_type: str = ""

    def add(self, component_name: str, value: float):
        """Add a reward component."""
        if value != 0:
            self.components[component_name] = value
            self.total += value

    def clamp(self, min_val: float, max_val: float):
        """Clamp total reward to prevent extreme values."""
        if self.total > max_val:
            self.components["_clamped_excess"] = self.total - max_val
            self.total = max_val
        elif self.total < min_val:
            self.components["_clamped_deficit"] = self.total - min_val
            self.total = min_val

    def get_summary(self) -> str:
        """Get a formatted summary of the reward."""
        if not self.components:
            return f"Total: {self.total:.4f}"

        parts = [f"{name}={val:+.4f}" for name, val in self.components.items()]
        return f"Total: {self.total:+.4f} ({', '.join(parts)})"


class RewardCalculator:
    """Centralized reward calculation with comprehensive logging."""

    def __init__(self, config: Optional[RewardConfig] = None, max_stats: float = 9999.0):
        self.config = config or RewardConfig()
        self.max_stats = max_stats
        self.logger = logging.getLogger("GameEngine")

        # Track rewards per episode for analysis
        self.episode_rewards: Dict[str, List[float]] = {}

        # Temporal tracking for advantage smoothing
        self.prev_field_advantage: float = 0.0
        self.turns_skipped: int = 0

        # Trap trigger tracking
        self.traps_triggered_this_step: int = 0
        self.traps_rewarded_this_step: set = set()  # Track to prevent double-counting

        self.reset_episode_tracking()

    def reset_episode_tracking(self):
        """Reset episode-level reward tracking."""
        self.episode_rewards = {
            "total": [],
            "action_rewards": [],
            "damage_rewards": [],
            "field_rewards": [],
            "terminal_rewards": [],
        }
        self.prev_field_advantage = 0.0
        self.turns_skipped = 0
        self.traps_triggered_this_step = 0
        self.traps_rewarded_this_step = set()

    def set_trap_triggers(self, num_triggers: int, trap_ids: Optional[List[int]] = None):
        """Set the number of traps triggered this step for reward calculation.

        Args:
            num_triggers: Number of traps triggered
            trap_ids: Optional list of trap object IDs to prevent double-counting
        """
        self.traps_triggered_this_step = num_triggers

        # Track trap IDs to prevent double-counting with spell destruction
        if trap_ids:
            self.traps_rewarded_this_step.update(trap_ids)

    def calculate_action_reward(
        self,
        action_name: str,
        player: Player,
        params: Optional[Dict],
        success: bool,
        before_snapshot: Dict[str, Any],
        after_snapshot: Dict[str, Any],
        has_valid_moves: bool = False
    ) -> RewardBreakdown:
        """Calculate reward for a specific action with detailed breakdown."""
        breakdown = RewardBreakdown(action_type=action_name)

        # Valid action exploration bonus
        if success:
            breakdown.add("valid_action", self.config.valid_action_bonus)
        else:
            breakdown.add("invalid_action", self.config.invalid_action)
            breakdown.clamp(self.config.min_step_reward,
                            self.config.max_step_reward)
            self._log_reward(player, breakdown)
            return breakdown

        # Dispatch to specific action reward calculators
        if action_name == "summon":
            self._calculate_summon_reward(
                breakdown, player, params, before_snapshot, after_snapshot)
        elif action_name == "attack":
            self._calculate_attack_reward(
                breakdown, player, params, before_snapshot, after_snapshot)
        elif action_name == "cast_spell":
            self._calculate_spell_reward(
                breakdown, player, params, before_snapshot, after_snapshot)
        elif action_name == "set_trap":
            self._calculate_trap_reward(breakdown, player, params)
        elif action_name == "toggle":
            self._calculate_toggle_reward(
                breakdown, player, params, before_snapshot, after_snapshot)
        elif action_name == "combine":
            self._calculate_combine_reward(
                breakdown, player, params, before_snapshot, after_snapshot)
        elif action_name == "end_turn":
            # Clear trap tracking at end of turn
            self.traps_rewarded_this_step.clear()

            # Check if player did nothing this turn
        elif action_name == "end_turn":
            # Clear trap tracking at end of turn
            self.traps_rewarded_this_step.clear()

            if self._is_passive_turn(before_snapshot, after_snapshot):
                # Player did nothing this turn
                self.turns_skipped += 1
                my_field_empty = len(after_snapshot.get("my_monsters", [])) == 0

                if my_field_empty:
                    breakdown.add("skip_empty_field_penalty", -0.4)
                    print("[REWARD DEBUG] Passive turn with empty field → big penalty")
                else:
                    breakdown.add("skip_turn_penalty", -0.05 * self.turns_skipped)
                    print(f"[REWARD DEBUG] Passive turn but field not empty → penalty scales: -0.05*{self.turns_skipped}")

            else:
                # Player did something meaningful
                # Reset skip counter
                self.turns_skipped = 0

                # Optional: small bonus for meaningful action
                meaningful_action = len(after_snapshot.get("my_monsters", [])) > len(before_snapshot.get("my_monsters", []))
                if meaningful_action:
                    breakdown.add("active_play_bonus", 0.1)
                    print("[REWARD DEBUG] Ended turn with meaningful action → small bonus")

            # Premature end penalty if valid moves exist
            if has_valid_moves and not self._is_passive_turn(before_snapshot, after_snapshot):
                breakdown.add("premature_end_penalty", self.config.premature_end_penalty)


        # Add trap trigger rewards if any traps were triggered
        if self.traps_triggered_this_step > 0:
            trap_reward = self._calculate_trap_trigger_reward(
                self.traps_triggered_this_step)
            breakdown.add("trap_trigger", trap_reward)
            self.traps_triggered_this_step = 0  # Reset for next step

        # Add normalized field advantage reward with temporal smoothing
        field_reward = self._calculate_field_advantage(player, after_snapshot)
        if field_reward != 0:
            breakdown.add("field_advantage", field_reward)

        # Board control bonus
        board_bonus = self._calculate_board_control(player, after_snapshot)
        if board_bonus != 0:
            breakdown.add("board_control", board_bonus)

        # Clamp to prevent extreme rewards (BEFORE logging)
        breakdown.clamp(self.config.min_step_reward,
                        self.config.max_step_reward)

        self._log_reward(player, breakdown)
        self.episode_rewards["action_rewards"].append(breakdown.total)
        return breakdown

    def _calculate_trap_trigger_reward(self, num_triggers: int) -> float:
        """Calculate reward for trap triggers with adjustable logarithmic scaling.

        Args:
            num_triggers: Number of traps triggered this step

        Returns:
            Scaled reward, capped at max_trap_trigger_reward

        Note:
            trap_trigger_log_scale controls curve steepness:
            - 1.0 = standard log scaling (default)
            - 0.5 = gentler curve (reduces spike for 3-4 traps)
            - 2.0 = steeper curve (rewards multiple traps more)
        """
        if num_triggers <= 0:
            return 0.0

        # Adjustable logarithmic scaling to reduce spikes
        # log1p(x^scale) creates a tunable curve
        scaled_triggers = num_triggers ** self.config.trap_trigger_log_scale
        reward = self.config.trap_trigger_base * math.log1p(scaled_triggers)

        # Cap the maximum trap trigger reward
        reward = min(reward, self.config.max_trap_trigger_reward)

        return reward

    def _calculate_summon_reward(
        self,
        breakdown: RewardBreakdown,
        player: Player,
        params: Optional[Dict],
        before: Dict[str, Any],
        after: Dict[str, Any]
    ):
        """Calculate reward for summoning a monster or trap."""
        # Check if a monster was actually summoned
        if len(after["my_monsters"]) > len(before["my_monsters"]):
            new_monster = [m for m in after["my_monsters"]
                           if m not in before["my_monsters"]]
            if new_monster:
                monster = new_monster[0]
                base_reward = self.config.deploy_monster
                breakdown.add("deploy_monster", base_reward)

                # Bonus for summoning stronger monsters (scaled)
                strength_bonus = (monster.atk / self.max_stats) * \
                    self.config.strength_scale_factor
                breakdown.add("strength_bonus", strength_bonus)

                # High-level monster bonus (2+ stars)
                if hasattr(monster, 'level_star') and monster.level_star >= 2:
                    breakdown.add("high_level_summon",
                                  self.config.high_level_summon_bonus)

    def _calculate_attack_reward(
        self,
        breakdown: RewardBreakdown,
        player: Player,
        params: Optional[Dict],
        before: Dict[str, Any],
        after: Dict[str, Any],
    ):
        """Reward based on actual damage dealt and monsters destroyed."""
        opp_lp_damage = before["opp_lp"] - after["opp_lp"]
        my_lp_damage = before["my_lp"] - after["my_lp"]

        # Damage dealt reward (logarithmic)
        if opp_lp_damage > 0:
            reward = math.log(1 + opp_lp_damage) * self.config.damage_scale_factor
            breakdown.add("damage_dealt", reward)

            # Direct attack bonus if no monsters on either side
            if not before["opp_monsters"] and not after["opp_monsters"]:
                breakdown.add("direct_attack_bonus", self.config.direct_attack_bonus)

        # Damage taken penalty
        if my_lp_damage > 0:
            penalty = -math.log(1 + my_lp_damage) * self.config.damage_scale_factor
            breakdown.add("damage_taken", penalty)

        # Monsters destroyed
        opp_destroyed = [m for m in before["opp_monsters"] if m not in after["opp_monsters"]]
        my_destroyed = [m for m in before["my_monsters"] if m not in after["my_monsters"]]

        for m in opp_destroyed:
            breakdown.add("attack_destroy", self.config.attack_destroy)
            stat = m.atk if m.mode == "attack" else m.defend
            breakdown.add("destroy_strength_bonus", (stat / self.max_stats) * self.config.strength_scale_factor)

        if my_destroyed:
            breakdown.add("monster_destroyed", self.config.monster_destroyed * len(my_destroyed))

        # Attack survived with no consequences
        if opp_lp_damage == 0 and my_lp_damage == 0 and not opp_destroyed:
            breakdown.add("survive_attack", self.config.survive_attack)

    def _calculate_spell_reward(
        self,
        breakdown: RewardBreakdown,
        player: Player,
        params: Optional[Dict],
        before: Dict[str, Any],
        after: Dict[str, Any]
    ):
        """Calculate reward for casting a spell.

        Note: Prevents double-counting trap destruction with trap trigger rewards.
        """
        breakdown.add("use_spell", self.config.use_spell)

        # Detect buffed monsters (spell combo)
        try:
            cards_changed = []
            for i, before_mon in enumerate(before.get("my_monsters", [])):
                if i < len(after.get("my_monsters", [])):
                    after_mon = after.get("my_monsters", [])[i]
                    if after_mon.atk > before_mon.atk or after_mon.defend > before_mon.defend:
                        cards_changed.append(after_mon)

            if len(cards_changed) >= 1:
                breakdown.add("spell_combo",
                              self.config.spell_combo_bonus * len(cards_changed))
        except (IndexError, AttributeError):
            pass  # Ignore if monster lists don't align

        # Check for trap destruction (only reward if not already triggered)
        before_traps = [c for c in before.get("opp_cards", [])
                        if isinstance(c, TrapCard)]
        after_traps = [c for c in after.get("opp_cards", [])
                       if isinstance(c, TrapCard)]

        # Find destroyed traps
        destroyed_traps = [t for t in before_traps if t not in after_traps]

        # Only reward if these traps weren't already rewarded via trigger
        newly_destroyed = [t for t in destroyed_traps
                           if id(t) not in self.traps_rewarded_this_step]

        if newly_destroyed:
            breakdown.add("trap_destroyed_bonus",
                          self.config.bait_block_bonus * len(newly_destroyed))
            # Mark these traps as rewarded
            for trap in newly_destroyed:
                self.traps_rewarded_this_step.add(id(trap))

    def _calculate_trap_reward(
        self,
        breakdown: RewardBreakdown,
        player: Player,
        params: Optional[Dict],
    ):
        """Calculate reward for setting a trap (planning incentive)."""
        breakdown.add("deploy_trap", self.config.deploy_trap)

    def _calculate_toggle_reward(
        self,
        breakdown: RewardBreakdown,
        player: Player,
        params: Optional[Dict],
        before: Dict[str, Any],
        after: Dict[str, Any],
        available_spells: Optional[List[Any]] = None
    ):
        """Strategic toggle with spell-awareness and safe kamikaze logic."""

        if not params or "toggle" not in params:
            return

        idx = params["toggle"]
        if idx >= len(after["my_monsters"]):
            return

        monster = after["my_monsters"][idx]
        opp_monsters = after.get("opp_monsters", [])

        # Step 1: Determine preferred mode for self
        current_atk = getattr(monster, "atk", 0) + getattr(monster, "buff_atk", 0)
        current_def = getattr(monster, "defend", 0) + getattr(monster, "buff_def", 0)
        preferred_mode = "attack" if current_atk >= current_def else "defend"

        best_mode = monster.mode
        best_reward = -float("inf")

        # Step 2: Evaluate each mode
        for mode in ["attack", "defend"]:
            reward = 0.0
            atk = current_atk
            defend = current_def

            # Apply spell buffs if available
            if available_spells:
                for spell in available_spells:
                    atk += getattr(spell, "atk_buff", 0)
                    defend += getattr(spell, "def_buff", 0)

            if opp_monsters:
                max_vs_opp = -float("inf")
                best_target = None

                for opp in opp_monsters:
                    opp_atk = getattr(opp, "atk", 0)
                    opp_def = getattr(opp, "defend", 0)
                    opp_star = getattr(opp, "level_star", 0)
                    temp_reward = 0.0

                    if mode == "attack":
                        if available_spells:
                            # Prefer high-star opponents only if safe kill possible
                            if atk > opp_def and atk >= opp_atk:
                                temp_reward = 0.5 + 0.05 * opp_star
                            else:
                                temp_reward = -0.3  # useless attack
                        else:
                            # Kamikaze logic: only attack if meaningful
                            if atk > opp_def and atk >= opp_atk:
                                temp_reward = 0.5  # safe kill
                            elif atk > opp_atk and atk < opp_def:
                                temp_reward = 0.35  # risky kamikaze
                            else:
                                temp_reward = -0.35  # attacking uselessly is penalized
                    else:  # defend
                        if defend > opp_atk:
                            temp_reward = 0.2  # survive safely
                        else:
                            temp_reward = -0.35  # unsafe defend

                    # Prefer highest reward per opponent
                    if temp_reward > max_vs_opp:
                        max_vs_opp = temp_reward
                        best_target = opp

                reward += max_vs_opp  # Only consider best opponent

            else:
                # No opponents: attack mode is optimal
                if mode == "attack":
                    reward += self.config.toggle_optimal
                else:
                    reward -= 0.1

            # Slight bonus for monster's preferred mode
            if mode == preferred_mode:
                reward += 0.05

            if reward > best_reward:
                best_reward = reward
                best_mode = mode

        # Step 3: Assign reward
        if best_mode != monster.mode:
            breakdown.add("strategic_toggle", best_reward)
        else:
            breakdown.add("suboptimal_toggle", self.config.toggle_suboptimal)



    def _calculate_combine_reward(
        self,
        breakdown: RewardBreakdown,
        player: Player,
        params: Optional[Dict],
        before: Dict[str, Any],
        after: Dict[str, Any]
    ):
        """Calculate reward for combining monsters."""
        before_monsters = before["my_monsters"]
        after_monsters = after["my_monsters"]

        new_monsters = [m for m in after_monsters if m not in before_monsters]
        if new_monsters:
            new_monster = new_monsters[0]
            level = getattr(new_monster, "level_star", 1)

            # Logarithmic reward based on level
            merge_reward = self.config.merge_base * math.log(level + 1)
            breakdown.add("merge_combine", merge_reward)

            # Strength bonus for powerful merged monster
            strength_bonus = (new_monster.atk / self.max_stats) * 0.1
            breakdown.add("merge_strength_bonus", strength_bonus)

    def _calculate_field_advantage(self, player: Player, snapshot: Dict[str, Any]) -> float:
        """Calculate normalized field advantage with temporal smoothing and decay.

        Returns:
            Delta advantage (improvement from previous turn), with smoothed transitions

        Note:
            - Positive delta = improving position (rewarded)
            - Negative delta = declining position (penalized, but smoothed)
            - Decay factor prevents over-reaction to single-turn swings
        """
        my_total_stats = sum(
            m.atk if m.mode == "attack" else m.defend
            for m in snapshot["my_monsters"]
        )

        opp_total_stats = sum(
            m.atk if m.mode == "attack" else m.defend
            for m in snapshot["opp_monsters"]
        )

        # Trap advantage
        my_traps = len([t for t in snapshot["my_cards"]
                       if isinstance(t, TrapCard)])
        opp_traps = len([t for t in snapshot["opp_cards"]
                        if isinstance(t, TrapCard)])
        trap_diff = (my_traps - opp_traps) * self.config.trap_advantage

        # Normalize by total power to get relative advantage
        total_power = my_total_stats + opp_total_stats + 1e-6  # Avoid division by zero
        normalized_advantage = (my_total_stats - opp_total_stats) / total_power

        # Apply multiplier
        advantage = normalized_advantage * \
            self.config.field_advantage_multiplier + trap_diff

        # Cap the advantage to prevent runaway scaling
        advantage = max(min(advantage, self.config.field_advantage_cap),
                        -self.config.field_advantage_cap)

        # Apply decay to previous advantage for smoothing
        # This prevents sudden swings from being over-penalized
        smoothed_prev = self.prev_field_advantage * self.config.field_advantage_decay

        # Temporal smoothing - reward improvement from smoothed baseline
        delta_advantage = advantage - smoothed_prev

        # Update tracking (use actual advantage, not smoothed)
        self.prev_field_advantage = advantage

        return delta_advantage

    def _calculate_board_control(self, player: Player, snapshot: Dict[str, Any]) -> float:
        """Reward maintaining board presence."""
        my_monster_count = len(snapshot["my_monsters"])
        opp_monster_count = len(snapshot["opp_monsters"])

        # Penalty for having no monsters
        if my_monster_count == 0:
            return self.config.no_monsters_penalty

        # Bonus for maintaining board advantage
        if my_monster_count > opp_monster_count:
            return self.config.board_control_bonus

        return 0.0

    def _is_passive_turn(self, before: Dict[str, Any], after: Dict[str, Any]) -> bool:
        """Check if the player did nothing significant this turn."""
        my_monsters_changed = len(before["my_monsters"]) != len(
            after["my_monsters"])
        opp_monsters_changed = len(before["opp_monsters"]) != len(
            after["opp_monsters"])
        lp_changed = before["opp_lp"] != after["opp_lp"]
        hand_changed = len(before.get("my_cards", [])) != len(
            after.get("my_cards", []))

        return not (my_monsters_changed or opp_monsters_changed or lp_changed or hand_changed)

    def calculate_terminal_reward(self, player: Player, won: bool,
                                  final_snapshot: Optional[Dict[str, Any]] = None) -> RewardBreakdown:
        """Calculate reward for game end with optional LP ratio bonus."""
        breakdown = RewardBreakdown(action_type="terminal")

        if won:
            breakdown.add("victory", self.config.win)

            # Optional: LP ratio bonus
            if final_snapshot and final_snapshot.get("my_lp") and final_snapshot.get("opp_lp"):
                lp_ratio = final_snapshot["my_lp"] / \
                    max(final_snapshot["opp_lp"], 1)
                lp_bonus = min(lp_ratio * 0.2, 0.5)  # Cap at 0.5
                breakdown.add("lp_ratio_bonus", lp_bonus)
        else:
            breakdown.add("defeat", self.config.lose)

        # Clamp terminal reward BEFORE logging
        breakdown.clamp(self.config.min_step_reward,
                        self.config.max_step_reward)

        self._log_reward(player, breakdown, terminal=True)
        self.episode_rewards["terminal_rewards"].append(breakdown.total)
        return breakdown

    def _log_reward(self, player: Player, breakdown: RewardBreakdown, terminal: bool = False):
        """Log reward details."""
        if terminal:
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"🏆 TERMINAL REWARD for {player.name}")
            self.logger.info(f"{'='*60}")
            self.logger.info(f"  {breakdown.get_summary()}")
            self.logger.info(f"{'='*60}\n")
        elif breakdown.total != 0:
            emoji = "💰" if breakdown.total > 0 else "📉"
            self.logger.info(f"  {emoji} REWARD ({breakdown.action_type}): {
                             breakdown.get_summary()}")

    def get_episode_summary(self) -> Dict[str, Any]:
        """Get summary statistics for the episode."""
        summary = {}
        for key, rewards in self.episode_rewards.items():
            if rewards:
                summary[key] = {
                    "total": sum(rewards),
                    "mean": sum(rewards) / len(rewards),
                    "min": min(rewards),
                    "max": max(rewards),
                    "count": len(rewards),
                }
        return summary

    def log_episode_summary(self):
        """Log episode reward summary."""
        summary = self.get_episode_summary()

        self.logger.info(f"\n{'='*60}")
        self.logger.info("EPISODE REWARD SUMMARY")
        self.logger.info(f"{'='*60}")

        for category, stats in summary.items():
            self.logger.info(f"\n{category.upper()}:")
            self.logger.info(f"  Total: {stats['total']:+.4f}")
            self.logger.info(f"  Mean:  {stats['mean']:+.4f}")
            self.logger.info(
                f"  Range: [{stats['min']:+.4f}, {stats['max']:+.4f}]")
            self.logger.info(f"  Count: {stats['count']}")

        self.logger.info(f"\n{'='*60}\n")
    


def create_enhanced_snapshot(engine, player: Player) -> Dict[str, Any]:
    """Create an enhanced snapshot with all necessary information for reward calculation."""
    gs = engine.game_state
    opp = gs.get_opponent(player)

    return {
        "my_lp": player.life_points,
        "opp_lp": opp.life_points,
        "my_monsters": list(gs.get_cards_typed(player, MonsterCard)),
        "opp_monsters": list(gs.get_cards_typed(opp, MonsterCard)),
        "my_cards": list(gs.get_player_cards(player)),
        "opp_cards": list(gs.get_player_cards(opp)),
        "my_hand_size": len(gs.player_info[player]["held_cards"].cards),
        "opp_hand_size": len(gs.player_info[opp]["held_cards"].cards),
    }

