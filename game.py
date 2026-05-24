"""
Main game logic with equipment, bosses, item drops, shops, and autosave
"""

import pygame
import random
from characters import create_character
from equipment import Equipment, Weapon, Armor
from enemies import EnemySpawner, BossArena, ItemDrop, MiniBoss, Boss
from shops import ShopManager


class Area:
    """Represents a game area/level"""
    
    def __init__(self, name, color, difficulty, description):
        self.name = name
        self.color = color
        self.difficulty = difficulty
        self.description = description
        self.enemies = []
        

class Game:
    """Main game class"""
    
    def __init__(self, save_manager, width=1200, height=800):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Action Game - Adventure Quest")
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Save manager
        self.save_manager = save_manager
        self.autosave_counter = 0
        self.autosave_interval = 300  # Autosave every 5 seconds
        
        # Game states
        self.state = "MAIN_MENU"  # MAIN_MENU, CHARACTER_SELECT, AREA_SELECT, SHOP, GAME, PAUSED, GAME_OVER
        self.player = None
        self.current_area = None
        self.equipment = None
        self.enemies = []
        self.mini_boss = None
        self.boss = None
        self.boss_arena = None
        self.item_drops = []
        self.running = True
        self.shop_manager = ShopManager()
        self.available_shops = []
        
        # Define areas
        self.areas = {
            'human': {
                'name': 'Ancient Castle',
                'color': (100, 100, 100),
                'difficulty': 1,
                'description': 'A mysterious castle filled with ancient secrets'
            },
            'frog': {
                'name': 'Swamp Marshlands',
                'color': (76, 110, 60),
                'difficulty': 1,
                'description': 'A murky swamp where danger lurks'
            },
            'dragon': {
                'name': 'Volcanic Peak',
                'color': (180, 100, 50),
                'difficulty': 1,
                'description': 'A dangerous volcanic mountain with molten lava'
            }
        }
        
        self.keys_pressed = set()
        self.notification = ""
        self.notification_timer = 0
        
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                self.handle_input(event)
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
    
    def handle_input(self, event):
        """Handle keyboard input based on game state"""
        if self.state == "MAIN_MENU":
            if event.key == pygame.K_1:
                # Check for autosave
                if self.save_manager.has_autosave():
                    self.load_autosave()
                else:
                    self.state = "CHARACTER_SELECT"
            elif event.key == pygame.K_2:
                self.state = "CHARACTER_SELECT"
            elif event.key == pygame.K_q:
                self.running = False
        
        elif self.state == "CHARACTER_SELECT":
            if event.key == pygame.K_1:
                self.select_character("human")
            elif event.key == pygame.K_2:
                self.select_character("frog")
            elif event.key == pygame.K_3:
                self.select_character("dragon")
            elif event.key == pygame.K_ESCAPE:
                self.state = "MAIN_MENU"
        
        elif self.state == "AREA_SELECT":
            if event.key == pygame.K_RETURN:
                self.start_game()
            elif event.key == pygame.K_ESCAPE:
                self.state = "CHARACTER_SELECT"
                self.player = None
        
        elif self.state == "GAME":
            self.handle_game_input(event)
        
        elif self.state == "SHOP":
            self.handle_shop_input(event)
        
        elif self.state == "PAUSED":
            if event.key == pygame.K_ESCAPE:
                self.state = "GAME"
    
    def handle_game_input(self, event):
        """Handle in-game input"""
        if event.key == pygame.K_ESCAPE:
            self.state = "PAUSED"
        elif event.key == pygame.K_SPACE:
            if self.player:
                self.perform_attack()
        elif event.key == pygame.K_LSHIFT:
            if self.player:
                self.perform_special_ability()
        elif event.key == pygame.K_q:
            self.state = "AREA_SELECT"
        elif event.key == pygame.K_u:
            # Upgrade weapon
            success, msg = self.equipment.upgrade_weapon()
            self.show_notification(msg)
        elif event.key == pygame.K_i:
            # Upgrade armor
            success, msg = self.equipment.upgrade_armor()
            self.show_notification(msg)
        elif event.key == pygame.K_s:
            # Open shop if available
            self.available_shops = self.shop_manager.get_available_shops(self.player.level)
            if self.available_shops:
                self.state = "SHOP"
                self.show_notification(f"Opened {self.available_shops[0].name}!")
    
    def handle_shop_input(self, event):
        """Handle shop input"""
        if event.key == pygame.K_ESCAPE:
            self.state = "GAME"
            self.shop_manager.current_shop = None
    
    def show_notification(self, text):
        """Show a notification on screen"""
        self.notification = text
        self.notification_timer = 120  # 2 seconds at 60 FPS
    
    def select_character(self, character_type):
        """Select a character and show area selection"""
        try:
            self.player = create_character(character_type)
            self.equipment = Equipment()
            self.equipment.initialize_equipment(character_type)
            self.state = "AREA_SELECT"
        except ValueError as e:
            print(f"Error: {e}")
    
    def load_autosave(self):
        """Load the autosave file"""
        success, save_data, msg = self.save_manager.load_game()
        
        if success and save_data:
            # Load player
            player_data = save_data['player']
            self.player = create_character(player_data['character_type'])
            self.player.level = player_data['level']
            self.player.experience = player_data['experience']
            self.player.exp_to_level = player_data['exp_to_level']
            self.player.health = player_data['health']
            self.player.max_health = player_data['max_health']
            self.player.x = player_data['x']
            self.player.y = player_data['y']
            self.player.attack_damage_mult = player_data['attack_damage_mult']
            self.player.health_mult = player_data['health_mult']
            
            # Load equipment
            self.equipment = Equipment()
            self.equipment.initialize_equipment(player_data['character_type'])
            self.equipment.gold = save_data['equipment']['gold']
            
            # Recreate owned weapons and armor
            self.equipment.owned_weapons = []
            for w_data in save_data['equipment']['owned_weapons']:
                weapon = Weapon(
                    w_data['name'],
                    w_data['base_damage'],
                    w_data['crit_chance'],
                    w_data['attack_speed'],
                    w_data['rarity']
                )
                weapon.level = w_data['level']
                weapon.current_damage = w_data['current_damage']
                self.equipment.owned_weapons.append(weapon)
            
            self.equipment.current_weapon = self.equipment.owned_weapons[0]
            
            self.equipment.owned_armor = []
            for a_data in save_data['equipment']['owned_armor']:
                armor = Armor(
                    a_data['name'],
                    a_data['base_defense'],
                    a_data['health_bonus'],
                    a_data['rarity']
                )
                armor.level = a_data['level']
                armor.current_defense = a_data['current_defense']
                self.equipment.owned_armor.append(armor)
            
            self.equipment.current_armor = self.equipment.owned_armor[0]
            
            # Load area
            area_data = save_data['area']
            self.current_area = Area(
                area_data['name'],
                self.areas[player_data['character_type']]['color'],
                area_data['difficulty'],
                self.areas[player_data['character_type']]['description']
            )
            
            self.state = "GAME"
            self.spawn_enemies()
            self.show_notification("✨ Game loaded! Welcome back! ✨")
        else:
            self.show_notification("Failed to load save!")
            self.state = "CHARACTER_SELECT"
    
    def start_game(self):
        """Start the game with selected character"""
        if self.player:
            area_info = self.areas[self.player.character_type]
            self.current_area = Area(
                area_info['name'],
                area_info['color'],
                area_info['difficulty'],
                area_info['description']
            )
            
            # Spawn player
            if self.player.character_type == 'human':
                self.player.x = 600
                self.player.y = 400
            elif self.player.character_type == 'frog':
                self.player.x = 300
                self.player.y = 600
            else:
                self.player.x = 900
                self.player.y = 200
            
            # Apply equipment bonuses
            self.player.max_health += self.equipment.current_armor.health_bonus
            self.player.health = self.player.max_health
            
            self.state = "GAME"
            self.spawn_enemies()
    
    def spawn_enemies(self):
        """Spawn enemies based on area difficulty"""
        self.enemies = []
        self.mini_boss = None
        self.boss = None
        
        # Check for boss spawn
        if EnemySpawner.should_spawn_boss(self.current_area.difficulty):
            self.boss = EnemySpawner.spawn_boss(
                self.player.character_type,
                self.current_area.difficulty,
                self.width // 2,
                100
            )
            self.boss_arena = BossArena(self.boss, self.width, self.height)
            self.show_notification(f"⚔️ BOSS APPEARED: {self.boss.name}! ⚔️")
            return
        
        # Check for mini-boss spawn
        if EnemySpawner.should_spawn_mini_boss(self.current_area.difficulty):
            self.mini_boss = EnemySpawner.spawn_mini_boss(
                self.player.character_type,
                self.current_area.difficulty,
                random.randint(200, self.width - 200),
                100
            )
            self.show_notification(f"⚠️ MINI-BOSS: {self.mini_boss.name}! ⚠️")
        
        # Spawn regular enemies
        num_enemies = 3 + (self.current_area.difficulty - 1)
        for _ in range(num_enemies):
            enemy = {
                'x': random.randint(100, self.width - 100),
                'y': random.randint(100, self.height - 200),
                'health': 30 + (10 * (self.current_area.difficulty - 1)),
                'max_health': 30 + (10 * (self.current_area.difficulty - 1)),
                'damage': 5 + (2 * (self.current_area.difficulty - 1)),
                'radius': 15,
                'color': (200, 50, 50),
                'stun_duration': 0
            }
            self.enemies.append(enemy)
    
    def perform_attack(self):
        """Perform player attack on nearby enemies"""
        attack_data = self.player.attack()
        attack_range = attack_data['range']
        damage = attack_data['damage'] * self.equipment.current_weapon.attack_speed
        
        # Attack regular enemies
        for enemy in self.enemies:
            dx = enemy['x'] - self.player.x
            dy = enemy['y'] - self.player.y
            distance = (dx**2 + dy**2)**0.5
            
            if distance < attack_range:
                enemy['health'] -= damage
                if enemy['health'] <= 0:
                    self.player.gain_experience(50 * self.current_area.difficulty)
                    self.equipment.add_gold(10 * self.current_area.difficulty)
        
        # Attack mini-boss
        if self.mini_boss:
            dx = self.mini_boss.x - self.player.x
            dy = self.mini_boss.y - self.player.y
            distance = (dx**2 + dy**2)**0.5
            
            if distance < attack_range:
                self.mini_boss.health -= damage
                if self.mini_boss.health <= 0:
                    self.on_mini_boss_defeated()
        
        # Attack boss
        if self.boss:
            dx = self.boss.x - self.player.x
            dy = self.boss.y - self.player.y
            distance = (dx**2 + dy**2)**0.5
            
            if distance < attack_range and not self.boss.invulnerable:
                self.boss.health -= damage
                if self.boss.health <= 0:
                    self.on_boss_defeated()
    
    def perform_special_ability(self):
        """Perform player's special ability"""
        ability_data = self.player.special_ability()
        if ability_data:
            damage = ability_data['damage'] * self.equipment.current_weapon.attack_speed
            ability_range = ability_data.get('range', 100)
            
            # Hit regular enemies
            for enemy in self.enemies:
                dx = enemy['x'] - self.player.x
                dy = enemy['y'] - self.player.y
                distance = (dx**2 + dy**2)**0.5
                
                if distance < ability_range:
                    enemy['health'] -= damage
                    if ability_data['type'] == 'stun':
                        enemy['stun_duration'] = ability_data['duration'] * 60
                    if enemy['health'] <= 0:
                        self.player.gain_experience(75 * self.current_area.difficulty)
                        self.equipment.add_gold(15 * self.current_area.difficulty)
            
            # Hit mini-boss
            if self.mini_boss:
                dx = self.mini_boss.x - self.player.x
                dy = self.mini_boss.y - self.player.y
                distance = (dx**2 + dy**2)**0.5
                
                if distance < ability_range:
                    self.mini_boss.health -= damage
                    if ability_data['type'] == 'stun':
                        self.mini_boss.stun_duration = ability_data['duration'] * 60
                    if self.mini_boss.health <= 0:
                        self.on_mini_boss_defeated()
            
            # Hit boss
            if self.boss and not self.boss.invulnerable:
                dx = self.boss.x - self.player.x
                dy = self.boss.y - self.player.y
                distance = (dx**2 + dy**2)**0.5
                
                if distance < ability_range:
                    self.boss.health -= damage
                    if self.boss.health <= 0:
                        self.on_boss_defeated()
    
    def on_mini_boss_defeated(self):
        """Handle mini-boss defeat"""
        self.player.gain_experience(500)
        self.equipment.add_gold(self.mini_boss.gold_drop)
        
        # Drop legendary items
        if random.random() < 0.5:
            weapon = self.equipment.get_legendary_weapon(self.player.character_type)
            if weapon:
                drop = ItemDrop(weapon, self.mini_boss.x, self.mini_boss.y, "legendary")
                self.item_drops.append(drop)
                self.show_notification(f"⭐ Legendary Weapon: {weapon.name}!")
        else:
            armor = self.equipment.get_legendary_armor(self.player.character_type)
            if armor:
                drop = ItemDrop(armor, self.mini_boss.x, self.mini_boss.y, "legendary")
                self.item_drops.append(drop)
                self.show_notification(f"⭐ Legendary Armor: {armor.name}!")
        
        self.mini_boss = None
    
    def on_boss_defeated(self):
        """Handle boss defeat"""
        self.player.gain_experience(2000)
        self.equipment.add_gold(self.boss.gold_drop)
        
        # Drop mythical items
        if random.random() < 0.5:
            weapon = self.equipment.get_mythical_weapon(self.player.character_type)
            if weapon:
                drop = ItemDrop(weapon, self.boss.x, self.boss.y, "mythical")
                self.item_drops.append(drop)
                self.show_notification(f"✨ MYTHICAL WEAPON: {weapon.name}! ✨")
        else:
            armor = self.equipment.get_mythical_armor(self.player.character_type)
            if armor:
                drop = ItemDrop(armor, self.boss.x, self.boss.y, "mythical")
                self.item_drops.append(drop)
                self.show_notification(f"✨ MYTHICAL ARMOR: {armor.name}! ✨")
        
        # Advance to next difficulty
        self.current_area.difficulty += 1
        self.boss = None
        self.boss_arena = None
        self.spawn_enemies()
    
    def update_player_position(self):
        """Update player position based on keys pressed"""
        speed = self.player.speed * 0.5
        
        if pygame.K_w in self.keys_pressed:
            self.player.y -= speed
        if pygame.K_s in self.keys_pressed:
            self.player.y += speed
        if pygame.K_a in self.keys_pressed:
            self.player.x -= speed
        if pygame.K_d in self.keys_pressed:
            self.player.x += speed
        
        self.player.x = max(0, min(self.width, self.player.x))
        self.player.y = max(0, min(self.height - 150, self.player.y))
    
    def update(self):
        """Update game logic"""
        if self.state == "GAME":
            if self.player:
                self.update_player_position()
                
                if self.player.ability_cooldown > 0:
                    self.player.ability_cooldown -= 1
                
                if self.notification_timer > 0:
                    self.notification_timer -= 1
                
                # Autosave
                self.autosave_counter += 1
                if self.autosave_counter >= self.autosave_interval:
                    self.save_manager.save_game(self.player, self.equipment, self.current_area, self.current_area.difficulty)
                    self.autosave_counter = 0
                
                # Remove dead enemies
                self.enemies = [e for e in self.enemies if e['health'] > 0]
                
                # Update item drops
                for drop in self.item_drops[:]:
                    drop.update()
                    if drop.check_collection(self.player.x, self.player.y):
                        if isinstance(drop.item, Weapon):
                            self.equipment.add_weapon(drop.item)
                        else:
                            self.equipment.add_armor(drop.item)
                        self.item_drops.remove(drop)
                        self.show_notification(f"Collected: {drop.item.name}!")
                
                # Boss updates
                if self.boss:
                    self.boss_arena.update()
                    self.boss.update_invulnerability()
                    
                    # Boss AI
                    if not self.boss.invulnerable:
                        dx = self.player.x - self.boss.x
                        dy = self.player.y - self.boss.y
                        distance = (dx**2 + dy**2)**0.5
                        
                        if distance > 20:
                            self.boss.x += (dx / distance) * self.boss.speed
                            self.boss.y += (dy / distance) * self.boss.speed
                        
                        if distance < (self.boss.radius + 15):
                            damage = self.boss.damage * 0.016
                            reduced_damage = self.equipment.current_armor.reduce_damage(damage)
                            self.player.take_damage(reduced_damage)
                
                # Mini-boss updates
                if self.mini_boss:
                    if self.mini_boss.stun_duration > 0:
                        self.mini_boss.stun_duration -= 1
                    else:
                        dx = self.player.x - self.mini_boss.x
                        dy = self.player.y - self.mini_boss.y
                        distance = (dx**2 + dy**2)**0.5
                        
                        if distance > 20:
                            self.mini_boss.x += (dx / distance) * self.mini_boss.speed
                            self.mini_boss.y += (dy / distance) * self.mini_boss.speed
                        
                        if distance < (self.mini_boss.radius + 15):
                            damage = self.mini_boss.damage * 0.016
                            reduced_damage = self.equipment.current_armor.reduce_damage(damage)
                            self.player.take_damage(reduced_damage)
                
                # Regular enemy updates
                for enemy in self.enemies:
                    if enemy['stun_duration'] > 0:
                        enemy['stun_duration'] -= 1
                        continue
                    
                    dx = self.player.x - enemy['x']
                    dy = self.player.y - enemy['y']
                    distance = (dx**2 + dy**2)**0.5
                    
                    if distance > 20:
                        enemy['x'] += (dx / distance) * 1.5
                        enemy['y'] += (dy / distance) * 1.5
                    
                    if distance < (enemy['radius'] + 15):
                        damage = enemy['damage'] * 0.016
                        reduced_damage = self.equipment.current_armor.reduce_damage(damage)
                        self.player.take_damage(reduced_damage)
                
                # Check game over
                if not self.player.is_alive():
                    self.state = "GAME_OVER"
                
                # Check level completion
                if not self.enemies and not self.mini_boss and not self.boss:
                    self.player.gain_experience(300)
                    self.current_area.difficulty += 1
                    self.spawn_enemies()
    
    def draw(self):
        """Draw game elements"""
        if self.state == "MAIN_MENU":
            self.draw_main_menu()
        elif self.state == "CHARACTER_SELECT":
            self.draw_character_select()
        elif self.state == "AREA_SELECT":
            self.draw_area_select()
        elif self.state == "GAME":
            self.draw_game()
        elif self.state == "SHOP":
            self.draw_shop()
        elif self.state == "PAUSED":
            self.draw_paused()
        elif self.state == "GAME_OVER":
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_main_menu(self):
        """Draw main menu"""
        self.screen.fill((20, 20, 40))
        
        font_large = pygame.font.Font(None, 100)
        font_medium = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 36)
        
        # Title
        title = font_large.render("ACTION QUEST", True, (255, 200, 100))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 80))
        
        # Menu options
        y_pos = 300
        if self.save_manager.has_autosave():
            continue_text = font_medium.render("1 - Continue (Load Autosave)", True, (100, 255, 100))
            self.screen.blit(continue_text, (self.width // 2 - continue_text.get_width() // 2, y_pos))
            y_pos += 80
        
        new_game = font_medium.render("2 - New Game", True, (100, 200, 255))
        self.screen.blit(new_game, (self.width // 2 - new_game.get_width() // 2, y_pos))
        y_pos += 80
        
        quit_text = font_medium.render("Q - Quit", True, (255, 100, 100))
        self.screen.blit(quit_text, (self.width // 2 - quit_text.get_width() // 2, y_pos))
    
    def draw_character_select(self):
        """Draw character selection screen"""
        self.screen.fill((20, 20, 40))
        
        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 36)
        
        title = font_large.render("SELECT YOUR CHARACTER", True, (255, 255, 255))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))
        
        y_pos = 200
        characters_info = [
            ("1 - HUMAN", "Balanced stats • Medium speed & strength", (100, 255, 100)),
            ("2 - FROG", "Fast & agile • High speed, low strength", (100, 200, 255)),
            ("3 - DRAGON", "Powerful force • Low speed, high strength", (255, 150, 100))
        ]
        
        for char_text, desc_text, color in characters_info:
            char_label = font_medium.render(char_text, True, color)
            desc_label = font_small.render(desc_text, True, (200, 200, 200))
            self.screen.blit(char_label, (100, y_pos))
            self.screen.blit(desc_label, (120, y_pos + 50))
            y_pos += 150
        
        instr = font_small.render("Press 1, 2, or 3 to select", True, (255, 255, 100))
        self.screen.blit(instr, (self.width // 2 - instr.get_width() // 2, self.height - 100))
    
    def draw_area_select(self):
        """Draw area selection screen"""
        self.screen.fill((20, 20, 40))
        
        font_large = pygame.font.Font(None, 64)
        font_medium = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 32)
        
        if self.player:
            area_info = self.areas[self.player.character_type]
            
            title = font_large.render(f"Welcome, {self.player.name}!", True, (255, 200, 100))
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))
            
            area_name = font_medium.render(area_info['name'], True, (100, 255, 100))
            self.screen.blit(area_name, (self.width // 2 - area_name.get_width() // 2, 150))
            
            desc = font_small.render(area_info['description'], True, (200, 200, 200))
            self.screen.blit(desc, (self.width // 2 - desc.get_width() // 2, 250))
            
            stats_text = f"HP: {self.player.max_health} | Speed: {int(self.player.speed)} | Damage: {int(self.player.strength)}"
            stats = font_small.render(stats_text, True, (100, 200, 255))
            self.screen.blit(stats, (self.width // 2 - stats.get_width() // 2, 350))
            
            start = font_medium.render("Press ENTER to start", True, (255, 255, 100))
            self.screen.blit(start, (self.width // 2 - start.get_width() // 2, 500))
            
            back = font_small.render("Press ESC to go back", True, (150, 150, 150))
            self.screen.blit(back, (self.width // 2 - back.get_width() // 2, 600))
    
    def draw_shop(self):
        """Draw shop interface"""
        self.screen.fill((40, 40, 60))
        
        font_large = pygame.font.Font(None, 64)
        font_medium = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 32)
        
        if self.available_shops:
            shop = self.available_shops[0]
            
            # Title
            title = font_large.render(shop.name, True, (255, 200, 100))
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 20))
            
            # Description
            desc = font_small.render(shop.description, True, (200, 200, 200))
            self.screen.blit(desc, (50, 100))
            
            # Discount info
            discount = font_small.render(f"Discount: {shop.discount * 100:.0f}%", True, (100, 255, 100))
            self.screen.blit(discount, (self.width - 300, 100))
            
            # Player gold
            gold_text = font_medium.render(f"Gold: {self.equipment.gold}", True, (255, 215, 0))
            self.screen.blit(gold_text, (50, 150))
            
            # Weapons section
            weapons_label = font_medium.render("Weapons:", True, (255, 100, 100))
            self.screen.blit(weapons_label, (50, 220))
            
            y_pos = 270
            for i, weapon in enumerate(shop.weapons):
                base_price = 100 if weapon[4] == 'common' else 120 if weapon[4] == 'uncommon' else 250
                price = shop.get_discounted_price(base_price)
                weapon_text = f"{i+1}. {weapon[0]} - DMG:{weapon[1]:.0f} - {price}g"
                weapon_label = font_small.render(weapon_text, True, (200, 200, 200))
                self.screen.blit(weapon_label, (70, y_pos))
                y_pos += 40
            
            # Armor section
            armor_label = font_medium.render("Armor:", True, (100, 150, 255))
            self.screen.blit(armor_label, (self.width // 2 + 50, 220))
            
            y_pos = 270
            for i, armor in enumerate(shop.armor):
                base_price = 100 if armor[3] == 'common' else 120 if armor[3] == 'uncommon' else 250
                price = shop.get_discounted_price(base_price)
                armor_text = f"{i+1}. {armor[0]} - DEF:{armor[1]:.0f} - {price}g"
                armor_label = font_small.render(armor_text, True, (200, 200, 200))
                self.screen.blit(armor_label, (self.width // 2 + 70, y_pos))
                y_pos += 40
            
            # Instructions
            instr = font_small.render("Press ESC to return to game", True, (255, 255, 100))
            self.screen.blit(instr, (self.width // 2 - instr.get_width() // 2, self.height - 50))
    
    def draw_game(self):
        """Draw the main game"""
        if self.current_area and self.player:
            self.screen.fill(self.current_area.color)
            
            pygame.draw.rect(self.screen, (50, 150, 50), (0, self.height - 150, self.width, 150))
            
            # Draw item drops
            for drop in self.item_drops:
                color = drop.get_color()
                pygame.draw.circle(self.screen, color, (int(drop.x), int(drop.y)), 8)
            
            # Draw enemies
            for enemy in self.enemies:
                pygame.draw.circle(self.screen, enemy['color'], 
                                 (int(enemy['x']), int(enemy['y'])), enemy['radius'])
                
                health_ratio = enemy['health'] / enemy['max_health']
                bar_width = 30
                pygame.draw.rect(self.screen, (255, 0, 0), 
                               (enemy['x'] - bar_width // 2, enemy['y'] - 30, bar_width, 5))
                pygame.draw.rect(self.screen, (0, 255, 0), 
                               (enemy['x'] - bar_width // 2, enemy['y'] - 30, bar_width * health_ratio, 5))
            
            # Draw mini-boss
            if self.mini_boss:
                color = (100, 100, 200) if self.mini_boss.stun_duration > 0 else self.mini_boss.color
                pygame.draw.circle(self.screen, color, 
                                 (int(self.mini_boss.x), int(self.mini_boss.y)), self.mini_boss.radius)
                
                health_ratio = self.mini_boss.health / self.mini_boss.max_health
                bar_width = 50
                pygame.draw.rect(self.screen, (255, 100, 0), 
                               (self.mini_boss.x - bar_width // 2, self.mini_boss.y - 40, bar_width, 8))
                pygame.draw.rect(self.screen, (0, 255, 0), 
                               (self.mini_boss.x - bar_width // 2, self.mini_boss.y - 40, bar_width * health_ratio, 8))
            
            # Draw boss
            if self.boss:
                color = (200, 200, 200) if self.boss.invulnerable else self.boss.color
                pygame.draw.circle(self.screen, color, 
                                 (int(self.boss.x), int(self.boss.y)), self.boss.radius)
                
                health_ratio = self.boss.health / self.boss.max_health
                bar_width = 80
                pygame.draw.rect(self.screen, (255, 0, 0), 
                               (self.boss.x - bar_width // 2, self.boss.y - 50, bar_width, 10))
                pygame.draw.rect(self.screen, (255, 100, 0), 
                               (self.boss.x - bar_width // 2, self.boss.y - 50, bar_width * health_ratio, 10))
                
                # Boss phase indicator
                phase_text = f"Phase {self.boss.phase}"
                font_small = pygame.font.Font(None, 24)
                phase_label = font_small.render(phase_text, True, (255, 0, 255))
                self.screen.blit(phase_label, (int(self.boss.x - 30), int(self.boss.y + 50)))
            
            # Draw player
            player_color = (100, 150, 255) if self.player.character_type == 'human' else \
                          (100, 255, 100) if self.player.character_type == 'frog' else (255, 180, 0)
            pygame.draw.circle(self.screen, player_color, 
                             (int(self.player.x), int(self.player.y)), 15)
            
            # Draw UI
            font_large = pygame.font.Font(None, 36)
            font_small = pygame.font.Font(None, 24)
            
            # Player info
            info_text = f"{self.player.name} Lv.{self.player.level} | HP: {self.player.health:.0f}/{self.player.max_health}"
            info_label = font_large.render(info_text, True, (255, 255, 255))
            self.screen.blit(info_label, (10, 10))
            
            # Health bar
            bar_width = 300
            health_ratio = self.player.health / self.player.max_health
            pygame.draw.rect(self.screen, (255, 0, 0), (10, 50, bar_width, 30))
            pygame.draw.rect(self.screen, (0, 255, 0), (10, 50, bar_width * health_ratio, 30))
            
            # Experience bar
            exp_ratio = self.player.experience / self.player.exp_to_level
            pygame.draw.rect(self.screen, (100, 100, 100), (10, 90, bar_width, 15))
            pygame.draw.rect(self.screen, (255, 255, 0), (10, 90, bar_width * exp_ratio, 15))
            
            exp_text = f"EXP: {self.player.experience}/{self.player.exp_to_level}"
            exp_label = font_small.render(exp_text, True, (255, 255, 100))
            self.screen.blit(exp_label, (10, 110))
            
            # Equipment info
            weapon_text = self.equipment.current_weapon.get_stats_string()
            weapon_label = font_small.render(weapon_text, True, self.equipment.current_weapon.get_rarity_color())
            self.screen.blit(weapon_label, (10, 135))
            
            armor_text = self.equipment.current_armor.get_stats_string()
            armor_label = font_small.render(armor_text, True, self.equipment.current_armor.get_rarity_color())
            self.screen.blit(armor_label, (10, 160))
            
            # Gold
            gold_text = f"Gold: {self.equipment.gold}"
            gold_label = font_small.render(gold_text, True, (255, 215, 0))
            self.screen.blit(gold_label, (10, 185))
            
            # Area info
            area_text = f"Area: {self.current_area.name} | Difficulty: {self.current_area.difficulty}"
            area_label = font_small.render(area_text, True, (200, 200, 200))
            self.screen.blit(area_label, (10, self.height - 140))
            
            # Controls
            controls = [
                "W/A/S/D - Move | SPACE - Attack",
                "SHIFT - Special | U - Upgrade Weapon",
                "I - Upgrade Armor | S - Shop",
                "Q - Change Area | ESC - Pause"
            ]
            for i, control in enumerate(controls):
                label = font_small.render(control, True, (150, 150, 150))
                self.screen.blit(label, (self.width - 480, self.height - 110 + i * 25))
            
            # Notification
            if self.notification_timer > 0:
                notification = pygame.font.Font(None, 32).render(self.notification, True, (255, 100, 100))
                self.screen.blit(notification, (self.width // 2 - notification.get_width() // 2, 400))
    
    def draw_paused(self):
        """Draw pause screen"""
        dim_surface = pygame.Surface((self.width, self.height))
        dim_surface.set_alpha(150)
        dim_surface.fill((0, 0, 0))
        self.screen.blit(dim_surface, (0, 0))
        
        font = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 36)
        
        pause_text = font.render("PAUSED", True, (255, 255, 255))
        self.screen.blit(pause_text, (self.width // 2 - pause_text.get_width() // 2, self.height // 2 - 100))
        
        resume = font_small.render("Press ESC to resume", True, (200, 200, 200))
        self.screen.blit(resume, (self.width // 2 - resume.get_width() // 2, self.height // 2 + 20))
    
    def draw_game_over(self):
        """Draw game over screen"""
        dim_surface = pygame.Surface((self.width, self.height))
        dim_surface.set_alpha(200)
        dim_surface.fill((0, 0, 0))
        self.screen.blit(dim_surface, (0, 0))
        
        font_large = pygame.font.Font(None, 100)
        font_medium = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 36)
        
        game_over_text = font_large.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(game_over_text, (self.width // 2 - game_over_text.get_width() // 2, 
                                         self.height // 2 - 150))
        
        stats_text = f"Final Level: {self.player.level} | Gold Earned: {self.equipment.gold}"
        stats_label = font_medium.render(stats_text, True, (200, 200, 200))
        self.screen.blit(stats_label, (self.width // 2 - stats_label.get_width() // 2, 
                                      self.height // 2 - 20))
        
        best_item = "Best Item: " + self.equipment.current_weapon.name
        item_label = font_small.render(best_item, True, (255, 200, 100))
        self.screen.blit(item_label, (self.width // 2 - item_label.get_width() // 2, 
                                     self.height // 2 + 60))
        
        restart = font_small.render("Press ESC to return to menu", True, (255, 255, 100))
        self.screen.blit(restart, (self.width // 2 - restart.get_width() // 2, 
                                  self.height // 2 + 120))
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
        
        pygame.quit()
