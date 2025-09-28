#!/usr/bin/env python3
"""
Comprehensive demonstration of the spell and trap system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.player import Player
from core.game.game_engine import GameEngine
from core.factory.spell_factory import SpellFactory
from core.factory.trap_factory import TrapFactory

def demo_spell_trap_system():
    """Demonstrate the complete spell and trap system"""
    print("Spell and Trap System Demo")
    print("=" * 60)
    print("This demo shows:")
    print("1. Spell cards that resolve immediately")
    print("2. Trap cards that are set face-down and triggered by attacks")
    print("3. Effect tracking with 3-round duration")
    print("4. Different spell and trap abilities")
    print("=" * 60)
    
    # Create test players
    player1 = Player("Alice", 8000)
    player2 = Player("Bob", 8000)
    players = [player1, player2]
    
    # Create game engine
    game_engine = GameEngine(players)
    
    print("\n🎯 PHASE 1: Setting up the battlefield")
    print("-" * 40)
    
    # Create some monsters for both players
    alice_monster = game_engine.monster_factory.load_by_type_and_level(player1, "Scholar", 1)
    bob_monster = game_engine.monster_factory.load_by_type_and_level(player2, "Conqueror", 1)
    
    if alice_monster and bob_monster:
        # Place monsters on field
        game_engine.game_state.modify_field("add", alice_monster, (2, 0))
        game_engine.game_state.modify_field("add", bob_monster, (1, 0))
        alice_monster.is_placed = True
        bob_monster.is_placed = True
        alice_monster.pos_in_matrix = (2, 0)
        bob_monster.pos_in_matrix = (1, 0)
        
        print(f"✓ {player1.name} summons {alice_monster.name} (ATK: {alice_monster.atk}, DEF: {alice_monster.defend})")
        print(f"✓ {player2.name} summons {bob_monster.name} (ATK: {bob_monster.atk}, DEF: {bob_monster.defend})")
    
    print("\n🪄 PHASE 2: Spell Casting")
    print("-" * 40)
    
    # Create and cast various spells
    spell_factory = game_engine.spell_factory
    
    # Pot of Greed - Draw 2 cards
    print("\n📜 Casting Pot of Greed...")
    pot_of_greed = spell_factory.create_card("Pot of Greed", player1)
    game_engine.game_state.player_info[player1]["held_cards"].add(pot_of_greed)
    game_engine.cast_spell(pot_of_greed)
    print(f"   {player1.name}'s hand size: {len(game_engine.game_state.player_info[player1]['held_cards'].cards)}")
    
    # Attack buff spell
    print("\n⚔️ Casting Maniac War (ATK buff)...")
    maniac_war = spell_factory.create_card("Maniac War", player1)
    game_engine.game_state.player_info[player1]["held_cards"].add(maniac_war)
    game_engine.cast_spell(maniac_war, alice_monster)
    print(f"   {alice_monster.name} ATK: {alice_monster.atk}")
    
    # Defense buff spell
    print("\n🛡️ Casting Holy Shield (DEF buff)...")
    holy_shield = spell_factory.create_card("Holy Shield", player1)
    game_engine.game_state.player_info[player1]["held_cards"].add(holy_shield)
    game_engine.cast_spell(holy_shield, alice_monster)
    print(f"   {alice_monster.name} DEF: {alice_monster.defend}")
    
    print("\n🪤 PHASE 3: Trap Setting")
    print("-" * 40)
    
    # Create and set traps
    trap_factory = game_engine.trap_factory
    
    # Crippling Curse trap
    print("\n💀 Setting Crippling Curse...")
    crippling_curse = trap_factory.create_card("Crippling Curse", player1)
    game_engine.game_state.player_info[player1]["held_cards"].add(crippling_curse)
    game_engine.set_trap(crippling_curse, (2, 1))
    print(f"   Trap set face-down at position (2,1)")
    
    # Mirror Strike trap
    print("\n🪞 Setting Mirror Strike...")
    mirror_strike = trap_factory.create_card("Mirror Strike", player1)
    game_engine.game_state.player_info[player1]["held_cards"].add(mirror_strike)
    game_engine.set_trap(mirror_strike, (2, 2))
    print(f"   Trap set face-down at position (2,2)")
    
    print("\n⚔️ PHASE 4: Combat with Trap Triggers")
    print("-" * 40)
    
    # Bob attacks Alice's monster
    print(f"\n🎯 {player2.name} attacks {player1.name}'s {alice_monster.name}!")
    print(f"   Attacker: {bob_monster.name} (ATK: {bob_monster.atk})")
    print(f"   Defender: {alice_monster.name} (ATK: {alice_monster.atk}, DEF: {alice_monster.defend})")
    
    # Check for trap triggers
    print("\n🪤 Checking for trap triggers...")
    trap_triggered = game_engine.check_trap_triggers(bob_monster, player1)
    
    if trap_triggered:
        print("   💥 A trap was activated!")
        print(f"   {bob_monster.name} is affected by the trap!")
    else:
        print("   No traps were triggered")
    
    print("\n⏰ PHASE 5: Effect Duration Tracking")
    print("-" * 40)
    
    # Show current effects
    effects = game_engine.effect_tracker.active_effects
    print(f"\n📊 Current active effects: {len(effects)}")
    for i, effect in enumerate(effects, 1):
        print(f"   {i}. {effect['type']}: {effect['value']} for {effect['rounds_remaining']} rounds")
        print(f"      Target: {effect['target'].name if hasattr(effect['target'], 'name') else effect['target']}")
    
    # Simulate multiple turns to show effect expiration
    print(f"\n🔄 Simulating 4 turns to show effect duration...")
    for turn in range(4):
        print(f"\n   Turn {turn + 1}:")
        game_engine.update_effects()
        
        effects = game_engine.effect_tracker.active_effects
        print(f"     Active effects: {len(effects)}")
        
        if alice_monster:
            print(f"     {alice_monster.name} stats: ATK={alice_monster.atk}, DEF={alice_monster.defend}")
        
        if effects:
            for effect in effects:
                print(f"       - {effect['type']}: {effect['value']} ({effect['rounds_remaining']} rounds left)")
    
    print("\n🎯 PHASE 6: Different Trap Types")
    print("-" * 40)
    
    # Test different trap abilities
    print("\n🪤 Testing different trap types...")
    
    # Dodge Attack trap
    dodge_trap = trap_factory.create_card("Phantom Dodge", player1)
    game_engine.game_state.player_info[player1]["held_cards"].add(dodge_trap)
    game_engine.set_trap(dodge_trap, (2, 3))
    print(f"   Set {dodge_trap.name} - negates first attack")
    
    # Weaken Summon trap
    weaken_trap = trap_factory.create_card("Weaken Summon", player1)
    game_engine.game_state.player_info[player1]["held_cards"].add(weaken_trap)
    game_engine.set_trap(weaken_trap, (2, 4))
    print(f"   Set {weaken_trap.name} - debuffs next summon")
    
    print("\n📋 PHASE 7: System Summary")
    print("-" * 40)
    
    print("\n✅ Spell System Features:")
    print("   • Spells resolve immediately when cast")
    print("   • Buff spells last for 3 rounds")
    print("   • Instant effect spells (like Pot of Greed) resolve and go to graveyard")
    print("   • Spells require valid targets for targeted effects")
    
    print("\n✅ Trap System Features:")
    print("   • Traps are set face-down on the field")
    print("   • Traps trigger automatically when conditions are met")
    print("   • Different trap types have different effects:")
    print("     - Debuff traps: Reduce ATK/DEF for 3 rounds")
    print("     - Dodge traps: Negate attacks")
    print("     - Reflect traps: Destroy attacking monster")
    print("     - Summon traps: Debuff newly summoned monsters")
    
    print("\n✅ Effect Tracking Features:")
    print("   • All effects are tracked with duration counters")
    print("   • Effects automatically expire after their duration")
    print("   • Stackable effects (multiple buffs can be applied)")
    print("   • Round-based system for effect management")
    
    print("\n" + "=" * 60)
    print("🎉 Spell and Trap System Demo Complete!")
    print("The system is fully integrated and ready for use in your Yu-Gi-Oh game!")
    
    return True

if __name__ == "__main__":
    demo_spell_trap_system()
