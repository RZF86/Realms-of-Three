"""
Character classes for the action game.
Each character has unique stats and abilities.
"""

class Character:
    """Base character class"""
    
    def __init__(self, name, health=100, speed=1, strength=1):
        self.name = name
        self.health = health
        self.max_health = health
        self.speed = speed
        self.strength = strength
        self.x = 0
        self.y = 0
        self.is_attacking = False
        
    def take_damage(self, damage):
        """Reduce health by damage amount"""
        self.health = max(0, self.health - damage)
        return self.health
    
    def heal(self, amount):
        """Increase health"""
        self.health = min(self.max_health, self.health + amount)
        
    def is_alive(self):
        """Check if character is still alive"""
        return self.health > 0
    
    def attack(self):
        """Perform basic attack"""
        raise NotImplementedError
    
    def special_ability(self):
        """Perform character-specific special ability"""
        raise NotImplementedError


class Human(Character):
    """Human character - balanced stats"""
    
    def __init__(self):
        super().__init__(name="Human", health=100, speed=5, strength=8)
        self.ability_cooldown = 0
        
    def attack(self):
        """Sword strike attack"""
        return {
            'damage': self.strength * 1.2,
            'type': 'melee',
            'range': 50,
            'description': 'Tactical sword strike'
        }
    
    def special_ability(self):
        """Shield bash - stuns enemies"""
        if self.ability_cooldown <= 0:
            self.ability_cooldown = 30
            return {
                'damage': self.strength * 0.8,
                'type': 'stun',
                'duration': 2,
                'description': 'Shield bash - stuns for 2 seconds'
            }
        return None


class Frog(Character):
    """Frog character - high speed, low strength"""
    
    def __init__(self):
        super().__init__(name="Frog", health=70, speed=10, strength=4)
        self.ability_cooldown = 0
        self.jump_height = 100
        
    def attack(self):
        """Tongue lash attack"""
        return {
            'damage': self.strength * 1.0,
            'type': 'melee',
            'range': 40,
            'description': 'Quick tongue lash'
        }
    
    def special_ability(self):
        """Jump attack - high agility move"""
        if self.ability_cooldown <= 0:
            self.ability_cooldown = 20
            return {
                'damage': self.strength * 1.5,
                'type': 'jump_attack',
                'height': self.jump_height,
                'description': 'Leap attack - dodge and strike'
            }
        return None


class Dragon(Character):
    """Dragon character - low speed, high strength"""
    
    def __init__(self):
        super().__init__(name="Dragon", health=150, speed=3, strength=12)
        self.ability_cooldown = 0
        
    def attack(self):
        """Melee claw attack"""
        return {
            'damage': self.strength * 1.3,
            'type': 'melee',
            'range': 60,
            'description': 'Powerful claw strike'
        }
    
    def special_ability(self):
        """Fire breath - area of effect attack"""
        if self.ability_cooldown <= 0:
            self.ability_cooldown = 40
            return {
                'damage': self.strength * 1.8,
                'type': 'aoe',
                'radius': 120,
                'description': 'Fire breath - massive AoE damage'
            }
        return None


def create_character(character_type):
    """Factory function to create characters"""
    characters = {
        'human': Human,
        'frog': Frog,
        'dragon': Dragon
    }
    
    character_class = characters.get(character_type.lower())
    if character_class:
        return character_class()
    else:
        raise ValueError(f"Unknown character type: {character_type}")
