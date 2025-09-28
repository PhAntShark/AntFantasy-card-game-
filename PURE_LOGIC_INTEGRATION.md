# Pure Logic Spell and Trap System Integration Guide

## Overview
This guide shows how to integrate the pure logic spell and trap system into your Yu-Gi-Oh game while maintaining strict separation between game logic and GUI.

## Architecture

### ✅ Pure Logic Layer (core/)
- **GameEngine**: Contains only game logic, no GUI dependencies
- **SpellFactory/TrapFactory**: Create cards from JSON data
- **EffectTracker**: Manages 3-round effect duration
- **RuleEngine**: Validates game rules

### ✅ GUI Layer (gui/)
- **Rendering**: Handles all drawing and visual effects
- **Input**: Manages user interactions
- **Animation**: Handles visual feedback

## Core Game Logic Methods

### Spell System
```python
# Create spell cards
spell = game_engine.spell_factory.create_card("Pot of Greed", player)

# Cast spells immediately
success = game_engine.cast_spell(spell, target=None)
success = game_engine.cast_spell(buff_spell, target=monster)
```

### Trap System
```python
# Create trap cards
trap = game_engine.trap_factory.create_card("Crippling Curse", player)

# Set traps face-down
success = game_engine.set_trap(trap, (2, 0))

# Traps auto-trigger on attacks
trap_triggered = game_engine.check_trap_triggers(attacker, defender)
```

### Effect Management
```python
# Update effects at end of turn
game_engine.update_effects()

# Get active effects
effects = game_engine.effect_tracker.active_effects

# Get mergeable cards for upgrades
mergeable = game_engine.get_mergeable_cards(player)
```

## Available Spells

| Spell | Ability | Effect |
|-------|---------|--------|
| Pot of Greed | draw_two_cards | Draw 2 cards immediately |
| Maniac War | buff_attack | +300 ATK for 3 rounds |
| Holy Shield | buff_defense | +300 DEF for 3 rounds |
| Mystical Space Typhoon | destroy_spell_trap | Destroy target spell/trap |
| Call of the Brave | summon_monster_from_hand | Summon from hand (UI required) |

## Available Traps

| Trap | Ability | Effect |
|------|---------|--------|
| Crippling Curse | debuff_enemy_atk | -300 ATK for 3 rounds when attacked |
| Shattered Guard | debuff_enemy_def | -300 DEF for 3 rounds when attacked |
| Phantom Dodge | dodge_attack | Negate first attack this turn |
| Mirror Strike | reflect_attack | Destroy attacking monster |
| Weaken Summon | debuff_summon | -500 ATK/DEF on next summon |

## Integration Examples

### 1. Spell Casting in GUI
```python
# In your GUI drag-drop handler
def on_spell_drop(spell_card, target_position):
    if spell_card.type == "spell":
        # For targeted spells, get target from position
        target = get_target_at_position(target_position)
        
        # Cast the spell
        success = game_engine.cast_spell(spell_card, target)
        
        if success:
            # Update GUI to show spell effect
            update_visual_effects()
            # Remove spell from hand visually
            remove_card_from_hand(spell_card)
```

### 2. Trap Setting in GUI
```python
# In your GUI drag-drop handler
def on_trap_drop(trap_card, field_position):
    if trap_card.type == "trap":
        # Set the trap
        success = game_engine.set_trap(trap_card, field_position)
        
        if success:
            # Show face-down trap on field
            show_face_down_card(trap_card, field_position)
            # Remove from hand
            remove_card_from_hand(trap_card)
```

### 3. Attack with Trap Checking
```python
# In your attack handler
def handle_attack(attacker, target):
    # Check for trap triggers first
    trap_triggered = game_engine.check_trap_triggers(attacker, target.owner)
    
    if trap_triggered:
        # Show trap activation animation
        show_trap_activation()
        # Attack was negated or reflected
        return
    
    # Proceed with normal attack
    game_engine.attack(attacker.owner, target.owner, attacker, target)
```

### 4. Effect Visualization
```python
# Update visual effects each frame
def update_visual_effects():
    # Get active effects
    effects = game_engine.effect_tracker.active_effects
    
    for effect in effects:
        target = effect["target"]
        effect_type = effect["type"]
        value = effect["value"]
        rounds_left = effect["rounds_remaining"]
        
        # Show visual indicator on target
        show_effect_indicator(target, effect_type, value, rounds_left)
```

### 5. Turn Management
```python
# At end of each turn
def end_turn():
    # Update all effects (reduces duration, removes expired)
    game_engine.update_effects()
    
    # End turn in game engine
    game_engine.end_turn()
    
    # Update visual effects
    update_visual_effects()
    
    # Update mergeable cards highlighting
    mergeable = game_engine.get_mergeable_cards(current_player)
    update_card_highlights(mergeable)
```

## Key Design Principles

### ✅ Pure Logic Separation
- **GameEngine**: Only contains game rules and state management
- **No GUI Dependencies**: No pygame, rendering, or visual code
- **Return Values**: Methods return success/failure and data
- **No Print Statements**: Clean logic without console output

### ✅ Effect Tracking
- **3-Round Duration**: All effects last exactly 3 rounds
- **Automatic Expiration**: Effects are removed when duration expires
- **Stackable**: Multiple effects can be applied to same target
- **Round-Based**: Effects update at end of each turn

### ✅ Trap Mechanics
- **Face-Down Placement**: Traps are hidden until triggered
- **Auto-Triggering**: Traps activate when conditions are met
- **Attack Integration**: Traps check during attack resolution
- **Owner Visibility**: Only trap owner can see face-down traps

### ✅ Spell Mechanics
- **Immediate Resolution**: Spells resolve instantly when cast
- **Targeted Effects**: Some spells require valid targets
- **Graveyard Disposal**: Spells go to graveyard after use
- **No Field Placement**: Spells don't stay on field

## Testing

Run the pure logic test to verify everything works:

```bash
python test_pure_logic.py
```

This test verifies all spell and trap mechanics work correctly without any GUI dependencies.

## File Structure

```
core/
├── cards/
│   └── card.py              # Base Card class with is_face_down
├── factory/
│   ├── spell_factory.py     # Creates spell cards from JSON
│   └── trap_factory.py      # Creates trap cards from JSON
├── game/
│   ├── game_engine.py       # Pure game logic only
│   ├── effect_tracker.py    # Manages effect duration
│   ├── rule_engine.py       # Game rules validation
│   └── turn_manager.py      # Turn management
└── player.py                # Player class

gui/                         # GUI layer (separate)
├── monster_card.py          # Visual card representation
├── render_engine.py         # Drawing and rendering
└── input_manager.py         # User input handling
```

The system is now completely separated with pure logic in the core layer and all visual/input handling in the GUI layer!
