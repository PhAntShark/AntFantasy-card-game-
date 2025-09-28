# Spell and Trap System Integration Guide

## Overview
This guide explains how to integrate the new spell and trap system into your Yu-Gi-Oh style game.

## Files Added/Modified

### New Files
- `core/factory/spell_factory.py` - Creates spell cards from JSON data
- `core/factory/trap_factory.py` - Creates trap cards from JSON data  
- `core/game/effect_tracker.py` - Tracks active effects and their duration
- `test_spell_trap_system.py` - Test script for the system
- `demo_spell_trap_system.py` - Comprehensive demonstration

### Modified Files
- `core/cards/card.py` - Added `is_face_down` property for traps
- `core/game/game_engine.py` - Added spell/trap methods and effect tracking
- `core/game/game_state.py` - Added active traps tracking

## Key Features

### Spell Cards
- **Immediate Resolution**: Spells resolve instantly when cast
- **Targeted Effects**: Some spells require valid targets (monsters for buffs)
- **Duration Effects**: Buff spells last for 3 rounds
- **Instant Effects**: Cards like Pot of Greed resolve immediately

### Trap Cards  
- **Face-Down Placement**: Traps are set face-down on the field
- **Automatic Triggering**: Traps activate when conditions are met
- **Attack Triggers**: Most traps trigger when opponent attacks
- **Various Effects**: Debuffs, dodges, reflections, and summon effects

### Effect Tracking
- **3-Round Duration**: Most effects last for 3 rounds
- **Automatic Expiration**: Effects are removed when duration expires
- **Stackable**: Multiple effects can be applied to the same target
- **Round-Based**: Effects update at the end of each turn

## Usage Examples

### Creating Spell Cards
```python
# Get spell factory
spell_factory = game_engine.spell_factory

# Create a spell card
pot_of_greed = spell_factory.create_card("Pot of Greed", player)

# Cast the spell
game_engine.cast_spell(pot_of_greed)
```

### Creating Trap Cards
```python
# Get trap factory
trap_factory = game_engine.trap_factory

# Create a trap card
crippling_curse = trap_factory.create_card("Crippling Curse", player)

# Set the trap face-down
game_engine.set_trap(crippling_curse, (2, 0))
```

### Effect Tracking
```python
# Effects are automatically tracked
# Check active effects
effects = game_engine.effect_tracker.active_effects

# Update effects (call at end of each turn)
game_engine.update_effects()
```

## Integration Steps

1. **Update Card Creation**: Use the new factories to create spell/trap cards
2. **Add UI Elements**: Create UI for spell/trap card display and interaction
3. **Update Drag-Drop**: Handle spell casting and trap setting in drag-drop logic
4. **Add Effect Display**: Show active effects on monsters/cards
5. **Update Turn System**: Call `update_effects()` at the end of each turn

## Available Spells

- **Pot of Greed**: Draw 2 cards
- **Maniac War**: +300 ATK for 3 rounds
- **Holy Shield**: +300 DEF for 3 rounds  
- **Mystical Space Typhoon**: Destroy 1 spell/trap
- **Call of the Brave**: Summon monster from hand

## Available Traps

- **Crippling Curse**: -300 ATK for 3 rounds when attacked
- **Shattered Guard**: -300 DEF for 3 rounds when attacked
- **Phantom Dodge**: Negate first attack this turn
- **Mirror Strike**: Destroy attacking monster
- **Weaken Summon**: -500 ATK/DEF on next summon

## Testing

Run the test scripts to verify everything works:

```bash
python test_spell_trap_system.py
python demo_spell_trap_system.py
```

The system is fully integrated and ready for use in your game!
