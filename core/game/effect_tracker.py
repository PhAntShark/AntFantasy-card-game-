from typing import Dict, List, Any
from core.cards.card import Card
from core.player import Player


class EffectTracker:
    """Tracks active effects and their remaining duration"""
    
    def __init__(self):
        self.active_effects: List[Dict[str, Any]] = []
        self.current_round = 0
    
    def add_effect(self, effect_type: str, target: Any, value: int, duration: int = 3, source_card: Card = None):
        """Add a new effect to track"""
        effect = {
            "type": effect_type,
            "target": target,
            "value": value,
            "duration": duration,
            "rounds_remaining": duration,
            "source_card": source_card,
            "applied_round": self.current_round
        }
        self.active_effects.append(effect)
    
    def update_round(self):
        """Update round counter and remove expired effects"""
        self.current_round += 1
        expired_effects = []
        
        for effect in self.active_effects:
            effect["rounds_remaining"] -= 1
            if effect["rounds_remaining"] <= 0:
                expired_effects.append(effect)
        
        # Remove expired effects
        for effect in expired_effects:
            self._remove_effect(effect)
            self.active_effects.remove(effect)
    
    def _remove_effect(self, effect: Dict[str, Any]):
        """Remove an effect from its target"""
        effect_type = effect["type"]
        target = effect["target"]
        value = effect["value"]
        
        if effect_type == "buff_attack" and hasattr(target, 'atk'):
            target.atk -= value
        elif effect_type == "buff_defense" and hasattr(target, 'defend'):
            target.defend -= value
        elif effect_type == "debuff_attack" and hasattr(target, 'atk'):
            target.atk += value
        elif effect_type == "debuff_defense" and hasattr(target, 'defend'):
            target.defend += value
    
    def get_effects_on_target(self, target: Any) -> List[Dict[str, Any]]:
        """Get all active effects on a specific target"""
        return [effect for effect in self.active_effects if effect["target"] == target]
    
    def has_effect_type(self, target: Any, effect_type: str) -> bool:
        """Check if target has a specific effect type"""
        return any(effect["type"] == effect_type and effect["target"] == target 
                  for effect in self.active_effects)
    
    def remove_effect_type(self, target: Any, effect_type: str):
        """Remove all effects of a specific type from target"""
        effects_to_remove = [effect for effect in self.active_effects 
                           if effect["target"] == target and effect["type"] == effect_type]
        
        for effect in effects_to_remove:
            self._remove_effect(effect)
            self.active_effects.remove(effect)
    
    def clear_all_effects(self):
        """Clear all active effects"""
        for effect in self.active_effects:
            self._remove_effect(effect)
        self.active_effects.clear()
    
    def get_round_info(self) -> Dict[str, int]:
        """Get current round information"""
        return {
            "current_round": self.current_round,
            "active_effects_count": len(self.active_effects)
        }
