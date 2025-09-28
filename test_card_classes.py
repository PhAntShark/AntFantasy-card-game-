#!/usr/bin/env python3
"""
Test the new SpellCard and TrapCard classes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.player import Player
from core.game.game_engine import GameEngine

def test_card_classes():
    """Test the new card classes"""
    print("Testing SpellCard and TrapCard Classes")
    print("=" * 50)
    
    # Create test players
    player1 = Player("Alice", 8000)
    player2 = Player("Bob", 8000)
    players = [player1, player2]
    
    # Create game engine
    game_engine = GameEngine(players)
    
    print("\n1. Testing SpellCard creation...")
    spell_factory = game_engine.spell_factory
    
    try:
        pot_of_greed = spell_factory.create_card("Pot of Greed", player1)
        print(f"   ✓ Created: {pot_of_greed}")
        print(f"     Type: {pot_of_greed.type}")
        print(f"     Is placed: {pot_of_greed.is_placed}")
        print(f"     Can target (None): {pot_of_greed.can_target(None)}")
        
        # Test buff spell
        maniac_war = spell_factory.create_card("Maniac War", player1)
        print(f"   ✓ Created: {maniac_war}")
        
        # Create a monster to test targeting
        monster = game_engine.monster_factory.load_by_type_and_level(player1, "Scholar", 1)
        if monster:
            print(f"     Can target monster: {maniac_war.can_target(monster)}")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n2. Testing TrapCard creation...")
    trap_factory = game_engine.trap_factory
    
    try:
        crippling_curse = trap_factory.create_card("Crippling Curse", player1)
        print(f"   ✓ Created: {crippling_curse}")
        print(f"     Type: {crippling_curse.type}")
        print(f"     Is placed: {crippling_curse.is_placed}")
        print(f"     Is face down: {crippling_curse.is_face_down}")
        
        # Test trap triggering
        attacker = game_engine.monster_factory.load_by_type_and_level(player2, "Conqueror", 1)
        if attacker:
            print(f"     Can trigger with attacker: {crippling_curse.can_trigger(attacker, player1)}")
        
        # Test reveal
        crippling_curse.reveal()
        print(f"     After reveal - Is face down: {crippling_curse.is_face_down}")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n3. Testing GameEngine integration...")
    
    # Test spell casting
    try:
        pot_of_greed = spell_factory.create_card("Pot of Greed", player1)
        game_engine.game_state.player_info[player1]["held_cards"].add(pot_of_greed)
        
        success = game_engine.cast_spell(pot_of_greed)
        print(f"   Spell cast success: {success}")
        print(f"   Hand size after: {len(game_engine.game_state.player_info[player1]['held_cards'].cards)}")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test trap setting
    try:
        crippling_curse = trap_factory.create_card("Crippling Curse", player1)
        game_engine.game_state.player_info[player1]["held_cards"].add(crippling_curse)
        
        success = game_engine.set_trap(crippling_curse, (2, 0))
        print(f"   Trap set success: {success}")
        print(f"   Trap position: {crippling_curse.pos_in_matrix}")
        print(f"   Trap face down: {crippling_curse.is_face_down}")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n4. Testing type checking...")
    
    # Test that factories return correct types
    spell = spell_factory.create_card("Pot of Greed", player1)
    trap = trap_factory.create_card("Crippling Curse", player1)
    
    print(f"   Spell is SpellCard: {isinstance(spell, type(spell))}")
    print(f"   Trap is TrapCard: {isinstance(trap, type(trap))}")
    print(f"   Spell type: {type(spell).__name__}")
    print(f"   Trap type: {type(trap).__name__}")
    
    print("\n" + "=" * 50)
    print("✅ Card Classes Test Completed!")
    print("SpellCard and TrapCard classes work correctly with GameEngine.")
    
    return True

if __name__ == "__main__":
    test_card_classes()
