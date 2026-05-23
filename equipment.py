"""
Equipment system with rare items, weapons, and armor
"""

class Weapon:
    """Weapon class with upgradable stats"""
    
    def __init__(self, name, base_damage, crit_chance=0.1, attack_speed=1.0, rarity="common"):
        self.name = name
        self.base_damage = base_damage
        self.current_damage = base_damage
        self.crit_chance = crit_chance
        self.attack_speed = attack_speed
        self.level = 1
        self.upgrade_cost = 100
        self.rarity = rarity  # common, uncommon, rare, legendary, mythical
        self.rarity_colors = {
            'common': (200, 200, 200),
            'uncommon': (100, 255, 100),
            'rare': (100, 150, 255),
            'legendary': (255, 150, 0),
            'mythical': (255, 0, 255)
        }
        
    def upgrade(self):
        """Upgrade weapon damage and stats"""
        self.level += 1
        self.current_damage = self.base_damage * (1.0 + (self.level - 1) * 0.2)
        self.crit_chance = min(0.5, self.crit_chance + 0.05)
        self.attack_speed = 1.0 + (self.level - 1) * 0.1
        self.upgrade_cost = int(100 * (1.5 ** (self.level - 1)))
        return self.upgrade_cost
    
    def get_damage(self):
        """Get weapon damage (with crit chance)"""
        import random
        if random.random() < self.crit_chance:
            return self.current_damage * 1.5  # 50% crit damage
        return self.current_damage
    
    def get_stats_string(self):
        """Return weapon stats as string"""
        return f"{self.name} Lv.{self.level} | DMG: {self.current_damage:.1f} | CRIT: {self.crit_chance*100:.0f}%"
    
    def get_rarity_color(self):
        """Get color based on rarity"""
        return self.rarity_colors.get(self.rarity, (200, 200, 200))


class Armor:
    """Armor class with upgradable stats"""
    
    def __init__(self, name, base_defense, health_bonus=0, rarity="common"):
        self.name = name
        self.base_defense = base_defense
        self.current_defense = base_defense
        self.health_bonus = health_bonus
        self.level = 1
        self.upgrade_cost = 100
        self.rarity = rarity  # common, uncommon, rare, legendary, mythical
        self.rarity_colors = {
            'common': (200, 200, 200),
            'uncommon': (100, 255, 100),
            'rare': (100, 150, 255),
            'legendary': (255, 150, 0),
            'mythical': (255, 0, 255)
        }
        
    def upgrade(self):
        """Upgrade armor defense and bonuses"""
        self.level += 1
        self.current_defense = self.base_defense * (1.0 + (self.level - 1) * 0.15)
        self.health_bonus = int(20 * self.level)
        self.upgrade_cost = int(100 * (1.5 ** (self.level - 1)))
        return self.upgrade_cost
    
    def reduce_damage(self, incoming_damage):
        """Calculate damage reduction from armor"""
        damage_reduction = min(0.8, self.current_defense / 100.0)
        return incoming_damage * (1.0 - damage_reduction)
    
    def get_stats_string(self):
        """Return armor stats as string"""
        defense_percent = min(80, (self.current_defense / 100.0) * 100)
        return f"{self.name} Lv.{self.level} | DEF: {defense_percent:.0f}% | HP+: {self.health_bonus}"
    
    def get_rarity_color(self):
        """Get color based on rarity"""
        return self.rarity_colors.get(self.rarity, (200, 200, 200))


class Equipment:
    """Equipment system managing weapons and armor"""
    
    def __init__(self):
        # Available weapons
        self.weapon_templates = {
            'human': {
                'name': 'Iron Sword',
                'base_damage': 15,
                'crit_chance': 0.15,
                'attack_speed': 1.0,
                'rarity': 'common'
            },
            'frog': {
                'name': 'Poison Dart',
                'base_damage': 10,
                'crit_chance': 0.25,
                'attack_speed': 1.3,
                'rarity': 'common'
            },
            'dragon': {
                'name': 'Dragon Claw',
                'base_damage': 20,
                'crit_chance': 0.1,
                'attack_speed': 0.8,
                'rarity': 'common'
            }
        }
        
        # Available armor
        self.armor_templates = {
            'human': {
                'name': 'Knight Plate',
                'base_defense': 20,
                'health_bonus': 30,
                'rarity': 'common'
            },
            'frog': {
                'name': 'Leaf Mail',
                'base_defense': 12,
                'health_bonus': 15,
                'rarity': 'common'
            },
            'dragon': {
                'name': 'Scale Mail',
                'base_defense': 25,
                'health_bonus': 40,
                'rarity': 'common'
            }
        }
        
        # Alternate weapons (can be switched to)
        self.alternate_weapons = {
            'human': [
                {'name': 'Steel Sword', 'base_damage': 18, 'crit_chance': 0.12, 'attack_speed': 0.9, 'rarity': 'uncommon'},
                {'name': 'Hammer', 'base_damage': 22, 'crit_chance': 0.05, 'attack_speed': 0.7, 'rarity': 'uncommon'},
                {'name': 'Dagger', 'base_damage': 10, 'crit_chance': 0.3, 'attack_speed': 1.3, 'rarity': 'uncommon'}
            ],
            'frog': [
                {'name': 'Shuriken', 'base_damage': 12, 'crit_chance': 0.3, 'attack_speed': 1.4, 'rarity': 'uncommon'},
                {'name': 'Spear', 'base_damage': 14, 'crit_chance': 0.15, 'attack_speed': 1.1, 'rarity': 'uncommon'},
                {'name': 'Boomerang', 'base_damage': 11, 'crit_chance': 0.2, 'attack_speed': 1.2, 'rarity': 'uncommon'}
            ],
            'dragon': [
                {'name': 'Great Sword', 'base_damage': 25, 'crit_chance': 0.08, 'attack_speed': 0.6, 'rarity': 'uncommon'},
                {'name': 'Fire Breath', 'base_damage': 18, 'crit_chance': 0.12, 'attack_speed': 1.0, 'rarity': 'uncommon'},
                {'name': 'Tail Whip', 'base_damage': 16, 'crit_chance': 0.15, 'attack_speed': 0.9, 'rarity': 'uncommon'}
            ]
        }
        
        # Alternate armor (can be switched to)
        self.alternate_armor = {
            'human': [
                {'name': 'Leather Armor', 'base_defense': 15, 'health_bonus': 20, 'rarity': 'uncommon'},
                {'name': 'Mithril Plate', 'base_defense': 28, 'health_bonus': 35, 'rarity': 'uncommon'},
                {'name': 'Robe', 'base_defense': 8, 'health_bonus': 50, 'rarity': 'uncommon'}
            ],
            'frog': [
                {'name': 'Chitinous Armor', 'base_defense': 14, 'health_bonus': 18, 'rarity': 'uncommon'},
                {'name': 'Mud Coat', 'base_defense': 10, 'health_bonus': 25, 'rarity': 'uncommon'},
                {'name': 'Silk Vest', 'base_defense': 9, 'health_bonus': 30, 'rarity': 'uncommon'}
            ],
            'dragon': [
                {'name': 'Hardened Scales', 'base_defense': 30, 'health_bonus': 50, 'rarity': 'uncommon'},
                {'name': 'Crystal Armor', 'base_defense': 22, 'health_bonus': 60, 'rarity': 'uncommon'},
                {'name': 'Ancient Dragonplate', 'base_defense': 35, 'health_bonus': 45, 'rarity': 'uncommon'}
            ]
        }
        
        # Legendary weapons from mini-bosses
        self.legendary_weapons = {
            'human': [
                {'name': 'Excalibur', 'base_damage': 35, 'crit_chance': 0.25, 'attack_speed': 1.1, 'rarity': 'legendary'},
                {'name': 'Holy Blade', 'base_damage': 32, 'crit_chance': 0.20, 'attack_speed': 1.0, 'rarity': 'legendary'}
            ],
            'frog': [
                {'name': 'Venomfang', 'base_damage': 25, 'crit_chance': 0.40, 'attack_speed': 1.5, 'rarity': 'legendary'},
                {'name': 'Swift Blade', 'base_damage': 22, 'crit_chance': 0.35, 'attack_speed': 1.6, 'rarity': 'legendary'}
            ],
            'dragon': [
                {'name': 'Inferno Claws', 'base_damage': 45, 'crit_chance': 0.15, 'attack_speed': 0.9, 'rarity': 'legendary'},
                {'name': 'Draconic Scythe', 'base_damage': 42, 'crit_chance': 0.18, 'attack_speed': 0.85, 'rarity': 'legendary'}
            ]
        }
        
        # Legendary armor from mini-bosses
        self.legendary_armor = {
            'human': [
                {'name': 'Plate of Champions', 'base_defense': 40, 'health_bonus': 80, 'rarity': 'legendary'},
                {'name': 'Aegis Armor', 'base_defense': 38, 'health_bonus': 90, 'rarity': 'legendary'}
            ],
            'frog': [
                {'name': 'Swamp Sage Robes', 'base_defense': 20, 'health_bonus': 120, 'rarity': 'legendary'},
                {'name': 'Amphibian Guardian', 'base_defense': 22, 'health_bonus': 100, 'rarity': 'legendary'}
            ],
            'dragon': [
                {'name': 'Dragon Sovereign Plate', 'base_defense': 50, 'health_bonus': 150, 'rarity': 'legendary'},
                {'name': 'Obsidian Scales', 'base_defense': 48, 'health_bonus': 130, 'rarity': 'legendary'}
            ]
        }
        
        # Mythical weapons from bosses (super rare!)
        self.mythical_weapons = {
            'human': {'name': 'Sword of Eternity', 'base_damage': 60, 'crit_chance': 0.35, 'attack_speed': 1.2, 'rarity': 'mythical'},
            'frog': {'name': 'Quantum Needle', 'base_damage': 50, 'crit_chance': 0.50, 'attack_speed': 2.0, 'rarity': 'mythical'},
            'dragon': {'name': 'Apocalypse Fang', 'base_damage': 75, 'crit_chance': 0.25, 'attack_speed': 1.0, 'rarity': 'mythical'}
        }
        
        # Mythical armor from bosses (super rare!)
        self.mythical_armor = {
            'human': {'name': 'Immortal Plate', 'base_defense': 60, 'health_bonus': 200, 'rarity': 'mythical'},
            'frog': {'name': 'Void Mantle', 'base_defense': 40, 'health_bonus': 250, 'rarity': 'mythical'},
            'dragon': {'name': 'Primal Carapace', 'base_defense': 70, 'health_bonus': 300, 'rarity': 'mythical'}
        }
        
        self.current_weapon = None
        self.current_armor = None
        self.owned_weapons = []
        self.owned_armor = []
        self.gold = 0
    
    def initialize_equipment(self, character_type):
        """Initialize equipment for a character"""
        weapon_data = self.weapon_templates[character_type]
        armor_data = self.armor_templates[character_type]
        
        self.current_weapon = Weapon(
            weapon_data['name'],
            weapon_data['base_damage'],
            weapon_data['crit_chance'],
            weapon_data['attack_speed'],
            weapon_data['rarity']
        )
        
        self.current_armor = Armor(
            armor_data['name'],
            armor_data['base_defense'],
            armor_data['health_bonus'],
            armor_data['rarity']
        )
        
        # Add starting equipment to inventory
        self.owned_weapons = [self.current_weapon]
        self.owned_armor = [self.current_armor]
        self.gold = 50  # Starting gold
    
    def get_legendary_weapon(self, character_type):
        """Get a random legendary weapon drop"""
        weapons = self.legendary_weapons.get(character_type, [])
        if weapons:
            import random
            weapon_data = random.choice(weapons)
            return Weapon(
                weapon_data['name'],
                weapon_data['base_damage'],
                weapon_data['crit_chance'],
                weapon_data['attack_speed'],
                weapon_data['rarity']
            )
        return None
    
    def get_legendary_armor(self, character_type):
        """Get a random legendary armor drop"""
        armors = self.legendary_armor.get(character_type, [])
        if armors:
            import random
            armor_data = random.choice(armors)
            return Armor(
                armor_data['name'],
                armor_data['base_defense'],
                armor_data['health_bonus'],
                armor_data['rarity']
            )
        return None
    
    def get_mythical_weapon(self, character_type):
        """Get mythical weapon drop"""
        weapon_data = self.mythical_weapons.get(character_type)
        if weapon_data:
            return Weapon(
                weapon_data['name'],
                weapon_data['base_damage'],
                weapon_data['crit_chance'],
                weapon_data['attack_speed'],
                weapon_data['rarity']
            )
        return None
    
    def get_mythical_armor(self, character_type):
        """Get mythical armor drop"""
        armor_data = self.mythical_armor.get(character_type)
        if armor_data:
            return Armor(
                armor_data['name'],
                armor_data['base_defense'],
                armor_data['health_bonus'],
                armor_data['rarity']
            )
        return None
    
    def switch_weapon(self, weapon_index):
        """Switch to a different weapon"""
        if 0 <= weapon_index < len(self.owned_weapons):
            self.current_weapon = self.owned_weapons[weapon_index]
            return True
        return False
    
    def switch_armor(self, armor_index):
        """Switch to a different armor"""
        if 0 <= armor_index < len(self.owned_armor):
            self.current_armor = self.owned_armor[armor_index]
            return True
        return False
    
    def add_weapon(self, weapon):
        """Add a weapon to inventory"""
        if weapon and weapon not in self.owned_weapons:
            self.owned_weapons.append(weapon)
            return True
        return False
    
    def add_armor(self, armor):
        """Add armor to inventory"""
        if armor and armor not in self.owned_armor:
            self.owned_armor.append(armor)
            return True
        return False
    
    def buy_weapon(self, weapon_data):
        """Buy a new weapon"""
        cost = 150
        if self.gold >= cost:
            self.gold -= cost
            new_weapon = Weapon(
                weapon_data['name'],
                weapon_data['base_damage'],
                weapon_data['crit_chance'],
                weapon_data['attack_speed'],
                weapon_data.get('rarity', 'uncommon')
            )
            self.owned_weapons.append(new_weapon)
            return True, f"Purchased {weapon_data['name']}!"
        return False, f"Need {cost - self.gold} more gold!"
    
    def buy_armor(self, armor_data):
        """Buy new armor"""
        cost = 150
        if self.gold >= cost:
            self.gold -= cost
            new_armor = Armor(
                armor_data['name'],
                armor_data['base_defense'],
                armor_data['health_bonus'],
                armor_data.get('rarity', 'uncommon')
            )
            self.owned_armor.append(new_armor)
            return True, f"Purchased {armor_data['name']}!"
        return False, f"Need {cost - self.gold} more gold!"
    
    def upgrade_weapon(self):
        """Upgrade current weapon"""
        upgrade_cost = self.current_weapon.upgrade_cost
        if self.gold >= upgrade_cost:
            self.gold -= upgrade_cost
            new_cost = self.current_weapon.upgrade()
            return True, f"{self.current_weapon.name} upgraded to Lv.{self.current_weapon.level}!"
        return False, f"Need {upgrade_cost - self.gold} more gold!"
    
    def upgrade_armor(self):
        """Upgrade current armor"""
        upgrade_cost = self.current_armor.upgrade_cost
        if self.gold >= upgrade_cost:
            self.gold -= upgrade_cost
            new_cost = self.current_armor.upgrade()
            return True, f"{self.current_armor.name} upgraded to Lv.{self.current_armor.level}!"
        return False, f"Need {upgrade_cost - self.gold} more gold!"
    
    def add_gold(self, amount):
        """Add gold from defeating enemies"""
        self.gold += amount
