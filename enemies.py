"""
Bosses and Mini-bosses for the action game
"""

class Enemy:
    """Base enemy class"""
    
    def __init__(self, name, health, damage, speed, radius, color, x, y):
        self.name = name
        self.health = health
        self.max_health = health
        self.damage = damage
        self.speed = speed
        self.radius = radius
        self.color = color
        self.x = x
        self.y = y
        self.stun_duration = 0
        self.is_boss = False
        self.is_mini_boss = False
        self.gold_drop = 0
        self.item_drops = []


class MiniBoss(Enemy):
    """Mini-boss enemy - drops legendary items"""
    
    def __init__(self, name, health, damage, speed, x, y):
        super().__init__(name, health, damage, speed, 25, (255, 150, 0), x, y)
        self.is_mini_boss = True
        self.gold_drop = 500
        self.rage_mode = False
        self.rage_cooldown = 0
        
    def activate_rage(self):
        """Activate rage mode for increased damage"""
        self.rage_mode = True
        self.damage *= 1.5
        self.rage_cooldown = 300  # 5 seconds at 60 FPS
        
    def update_rage(self):
        """Update rage mode status"""
        if self.rage_cooldown > 0:
            self.rage_cooldown -= 1
        else:
            self.rage_mode = False
            self.damage /= 1.5


class Boss(Enemy):
    """Boss enemy - drops mythical items"""
    
    def __init__(self, name, health, damage, speed, x, y):
        super().__init__(name, health, damage, speed, 35, (255, 0, 255), x, y)
        self.is_boss = True
        self.gold_drop = 1500
        self.phase = 1  # Boss has multiple phases
        self.attack_pattern = 0
        self.invulnerable = False
        self.invulnerable_duration = 0
        
    def enter_next_phase(self):
        """Boss enters next phase when health is low"""
        health_percent = self.health / self.max_health
        if health_percent < 0.66 and self.phase == 1:
            self.phase = 2
            self.damage *= 1.3
            self.speed *= 1.2
            return True
        elif health_percent < 0.33 and self.phase == 2:
            self.phase = 3
            self.damage *= 1.5
            self.speed *= 1.5
            return True
        return False
    
    def activate_invulnerability(self):
        """Become invulnerable temporarily"""
        self.invulnerable = True
        self.invulnerable_duration = 120  # 2 seconds at 60 FPS
        
    def update_invulnerability(self):
        """Update invulnerability status"""
        if self.invulnerable_duration > 0:
            self.invulnerable_duration -= 1
        else:
            self.invulnerable = False


class EnemySpawner:
    """Spawns regular enemies, mini-bosses, and bosses"""
    
    # Mini-boss templates
    mini_bosses = {
        'human': [
            {'name': 'Shadow Knight', 'health': 200, 'damage': 15, 'speed': 3},
            {'name': 'Iron Juggernaut', 'health': 250, 'damage': 18, 'speed': 2.5},
            {'name': 'Cursed Warrior', 'health': 180, 'damage': 20, 'speed': 3.5}
        ],
        'frog': [
            {'name': 'Poison Toad King', 'health': 160, 'damage': 12, 'speed': 5},
            {'name': 'Swamp Leviathan', 'health': 200, 'damage': 14, 'speed': 4},
            {'name': 'Venomous Amphibian', 'health': 170, 'damage': 16, 'speed': 4.5}
        ],
        'dragon': [
            {'name': 'Wyvern Lord', 'health': 280, 'damage': 22, 'speed': 2.5},
            {'name': 'Fire Drake', 'health': 250, 'damage': 25, 'speed': 2},
            {'name': 'Obsidian Dragon', 'health': 300, 'damage': 20, 'speed': 2.8}
        ]
    }
    
    # Boss templates
    bosses = {
        'human': {
            'name': 'The Ancient Guardian',
            'health': 600,
            'damage': 30,
            'speed': 2.5,
            'description': 'A colossal warrior protecting ancient secrets'
        },
        'frog': {
            'name': 'Swamp Tyrant',
            'health': 500,
            'damage': 25,
            'speed': 3.5,
            'description': 'Ruler of the poisoned marshlands'
        },
        'dragon': {
            'name': 'Primordial Dragon',
            'health': 800,
            'damage': 40,
            'speed': 2,
            'description': 'An ancient dragon of immense power'
        }
    }
    
    @staticmethod
    def spawn_mini_boss(character_type, difficulty, x, y):
        """Spawn a mini-boss for the character type"""
        mini_boss_data = EnemySpawner.mini_bosses.get(character_type, [])
        if mini_boss_data:
            import random
            base_data = random.choice(mini_boss_data)
            
            # Scale stats by difficulty
            health = int(base_data['health'] * (1 + difficulty * 0.3))
            damage = base_data['damage'] * (1 + difficulty * 0.2)
            speed = base_data['speed']
            
            return MiniBoss(
                base_data['name'],
                health,
                damage,
                speed,
                x,
                y
            )
        return None
    
    @staticmethod
    def spawn_boss(character_type, difficulty, x, y):
        """Spawn a boss for the character type"""
        boss_data = EnemySpawner.bosses.get(character_type)
        if boss_data:
            # Scale stats by difficulty
            health = int(boss_data['health'] * (1 + difficulty * 0.5))
            damage = boss_data['damage'] * (1 + difficulty * 0.3)
            speed = boss_data['speed']
            
            return Boss(
                boss_data['name'],
                health,
                damage,
                speed,
                x,
                y
            )
        return None
    
    @staticmethod
    def should_spawn_mini_boss(difficulty):
        """Determine if a mini-boss should spawn"""
        # Mini-boss spawns every 5 difficulty levels
        return difficulty > 0 and difficulty % 5 == 0
    
    @staticmethod
    def should_spawn_boss(difficulty):
        """Determine if a boss should spawn"""
        # Boss spawns every 10 difficulty levels
        return difficulty > 0 and difficulty % 10 == 0


class BossArena:
    """Manages boss arena and special effects"""
    
    def __init__(self, boss, width, height):
        self.boss = boss
        self.width = width
        self.height = height
        self.is_active = False
        self.warning_text = ""
        self.warning_timer = 0
        
    def display_warning(self, text, duration=60):
        """Display a warning text"""
        self.warning_text = text
        self.warning_timer = duration
        
    def update(self):
        """Update arena state"""
        if self.warning_timer > 0:
            self.warning_timer -= 1
        
        if self.boss:
            self.boss.enter_next_phase()
            self.boss.update_invulnerability()
    
    def get_boss_intensity(self):
        """Get intensity value for visual effects (0-1)"""
        if self.boss:
            health_percent = max(0, self.boss.health / self.boss.max_health)
            return 1.0 - health_percent
        return 0


class ItemDrop:
    """Represents a dropped item"""
    
    def __init__(self, item, x, y, rarity="common"):
        self.item = item
        self.x = x
        self.y = y
        self.rarity = rarity
        self.rotation = 0
        self.collected = False
        self.rarity_colors = {
            'common': (200, 200, 200),
            'uncommon': (100, 255, 100),
            'rare': (100, 150, 255),
            'legendary': (255, 150, 0),
            'mythical': (255, 0, 255)
        }
    
    def get_color(self):
        """Get color based on rarity"""
        return self.rarity_colors.get(self.rarity, (200, 200, 200))
    
    def update(self):
        """Update item animation"""
        self.rotation = (self.rotation + 2) % 360
    
    def check_collection(self, player_x, player_y, collection_range=50):
        """Check if player collected the item"""
        dx = self.x - player_x
        dy = self.y - player_y
        distance = (dx**2 + dy**2)**0.5
        return distance < collection_range
