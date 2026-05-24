"""
Save/Load system for game progression
"""

import json
import os
from datetime import datetime

class SaveManager:
    """Manages game saves and autosaves"""
    
    def __init__(self, save_dir="saves"):
        self.save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
    
    def create_save_data(self, player, equipment, current_area, difficulty):
        """Create a save data dictionary"""
        save_data = {
            'timestamp': datetime.now().isoformat(),
            'player': {
                'name': player.name,
                'character_type': player.character_type,
                'level': player.level,
                'experience': player.experience,
                'exp_to_level': player.exp_to_level,
                'health': player.health,
                'max_health': player.max_health,
                'x': player.x,
                'y': player.y,
                'speed': player.speed,
                'strength': player.strength,
                'attack_damage_mult': player.attack_damage_mult,
                'health_mult': player.health_mult,
            },
            'equipment': {
                'gold': equipment.gold,
                'current_weapon': {
                    'name': equipment.current_weapon.name,
                    'base_damage': equipment.current_weapon.base_damage,
                    'current_damage': equipment.current_weapon.current_damage,
                    'crit_chance': equipment.current_weapon.crit_chance,
                    'attack_speed': equipment.current_weapon.attack_speed,
                    'level': equipment.current_weapon.level,
                    'rarity': equipment.current_weapon.rarity,
                },
                'current_armor': {
                    'name': equipment.current_armor.name,
                    'base_defense': equipment.current_armor.base_defense,
                    'current_defense': equipment.current_armor.current_defense,
                    'health_bonus': equipment.current_armor.health_bonus,
                    'level': equipment.current_armor.level,
                    'rarity': equipment.current_armor.rarity,
                },
                'owned_weapons': [
                    {
                        'name': w.name,
                        'base_damage': w.base_damage,
                        'crit_chance': w.crit_chance,
                        'attack_speed': w.attack_speed,
                        'level': w.level,
                        'rarity': w.rarity,
                    } for w in equipment.owned_weapons
                ],
                'owned_armor': [
                    {
                        'name': a.name,
                        'base_defense': a.base_defense,
                        'health_bonus': a.health_bonus,
                        'level': a.level,
                        'rarity': a.rarity,
                    } for a in equipment.owned_armor
                ],
            },
            'area': {
                'name': current_area.name,
                'difficulty': current_area.difficulty,
            }
        }
        return save_data
    
    def save_game(self, player, equipment, current_area, difficulty, filename="autosave.json"):
        """Save the game to a file"""
        try:
            save_data = self.create_save_data(player, equipment, current_area, difficulty)
            filepath = os.path.join(self.save_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            return True, f"Game saved at {save_data['timestamp']}"
        except Exception as e:
            return False, f"Save failed: {str(e)}"
    
    def load_game(self, filename="autosave.json"):
        """Load a game from file"""
        try:
            filepath = os.path.join(self.save_dir, filename)
            
            if not os.path.exists(filepath):
                return False, None, "Save file not found!"
            
            with open(filepath, 'r') as f:
                save_data = json.load(f)
            
            return True, save_data, "Game loaded successfully!"
        except Exception as e:
            return False, None, f"Load failed: {str(e)}"
    
    def get_save_list(self):
        """Get list of all saves"""
        saves = []
        try:
            for filename in os.listdir(self.save_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.save_dir, filename)
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        saves.append({
                            'filename': filename,
                            'character': data['player']['name'],
                            'level': data['player']['level'],
                            'timestamp': data['timestamp']
                        })
        except Exception as e:
            print(f"Error reading saves: {e}")
        
        return saves
    
    def delete_save(self, filename):
        """Delete a save file"""
        try:
            filepath = os.path.join(self.save_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True, "Save deleted!"
        except Exception as e:
            return False, f"Delete failed: {str(e)}"
    
    def has_autosave(self):
        """Check if autosave exists"""
        filepath = os.path.join(self.save_dir, "autosave.json")
        return os.path.exists(filepath)
