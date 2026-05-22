"""
Main game logic and state management with areas and level progression
"""

import pygame
import random
from characters import create_character


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
    
    def __init__(self, width=1200, height=800):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Action Game - Adventure Quest")
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Game states
        self.state = "CHARACTER_SELECT"  # CHARACTER_SELECT, AREA_SELECT, GAME, PAUSED, GAME_OVER
        self.player = None
        self.current_area = None
        self.enemies = []
        self.running = True
        
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
        if self.state == "CHARACTER_SELECT":
            if event.key == pygame.K_1:
                self.select_character("human")
            elif event.key == pygame.K_2:
                self.select_character("frog")
            elif event.key == pygame.K_3:
                self.select_character("dragon")
        elif self.state == "AREA_SELECT":
            if event.key == pygame.K_RETURN:
                self.start_game()
            elif event.key == pygame.K_ESCAPE:
                self.state = "CHARACTER_SELECT"
                self.player = None
        elif self.state == "GAME":
            self.handle_game_input(event)
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
    
    def select_character(self, character_type):
        """Select a character and show area selection"""
        try:
            self.player = create_character(character_type)
            self.state = "AREA_SELECT"
            print(f"Selected: {self.player.name}")
        except ValueError as e:
            print(f"Error: {e}")
    
    def start_game(self):
        """Start the game with selected character"""
        if self.player:
            # Get character's starting area
            area_info = self.areas[self.player.character_type]
            self.current_area = Area(
                area_info['name'],
                area_info['color'],
                area_info['difficulty'],
                area_info['description']
            )
            
            # Spawn player in starting position based on character
            if self.player.character_type == 'human':
                self.player.x = 600
                self.player.y = 400
            elif self.player.character_type == 'frog':
                self.player.x = 300
                self.player.y = 600
            else:  # dragon
                self.player.x = 900
                self.player.y = 200
            
            self.state = "GAME"
            self.spawn_enemies()
    
    def spawn_enemies(self):
        """Spawn enemies based on area difficulty"""
        self.enemies = []
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
        damage = attack_data['damage']
        
        for enemy in self.enemies:
            dx = enemy['x'] - self.player.x
            dy = enemy['y'] - self.player.y
            distance = (dx**2 + dy**2)**0.5
            
            if distance < attack_range:
                enemy['health'] -= damage
                if enemy['health'] <= 0:
                    self.player.gain_experience(50 * self.current_area.difficulty)
    
    def perform_special_ability(self):
        """Perform player's special ability"""
        ability_data = self.player.special_ability()
        if ability_data:
            damage = ability_data['damage']
            ability_range = ability_data.get('range', 100)
            
            if ability_data['type'] == 'stun':
                for enemy in self.enemies:
                    dx = enemy['x'] - self.player.x
                    dy = enemy['y'] - self.player.y
                    distance = (dx**2 + dy**2)**0.5
                    
                    if distance < ability_range:
                        enemy['health'] -= damage
                        enemy['stun_duration'] = ability_data['duration'] * 60
            
            elif ability_data['type'] == 'aoe':
                radius = ability_data['radius']
                for enemy in self.enemies:
                    dx = enemy['x'] - self.player.x
                    dy = enemy['y'] - self.player.y
                    distance = (dx**2 + dy**2)**0.5
                    
                    if distance < radius:
                        enemy['health'] -= damage
                        if enemy['health'] <= 0:
                            self.player.gain_experience(75 * self.current_area.difficulty)
    
    def update_player_position(self):
        """Update player position based on keys pressed"""
        speed = self.player.speed * 0.5  # Scale down for gameplay balance
        
        if pygame.K_w in self.keys_pressed:
            self.player.y -= speed
        if pygame.K_s in self.keys_pressed:
            self.player.y += speed
        if pygame.K_a in self.keys_pressed:
            self.player.x -= speed
        if pygame.K_d in self.keys_pressed:
            self.player.x += speed
        
        # Keep player in bounds
        self.player.x = max(0, min(self.width, self.player.x))
        self.player.y = max(0, min(self.height - 150, self.player.y))
    
    def update(self):
        """Update game logic"""
        if self.state == "GAME":
            if self.player:
                # Update player position
                self.update_player_position()
                
                # Update ability cooldowns
                if self.player.ability_cooldown > 0:
                    self.player.ability_cooldown -= 1
                
                # Remove dead enemies and check for level completion
                self.enemies = [e for e in self.enemies if e['health'] > 0]
                if not self.enemies:
                    # Gain bonus experience for clearing area
                    self.player.gain_experience(300)
                    self.current_area.difficulty += 1
                    self.spawn_enemies()
                
                # Update enemies
                for enemy in self.enemies:
                    # Reduce stun duration
                    if enemy['stun_duration'] > 0:
                        enemy['stun_duration'] -= 1
                        continue
                    
                    # Simple enemy AI - move towards player
                    dx = self.player.x - enemy['x']
                    dy = self.player.y - enemy['y']
                    distance = (dx**2 + dy**2)**0.5
                    
                    if distance > 20:
                        enemy['x'] += (dx / distance) * 1.5
                        enemy['y'] += (dy / distance) * 1.5
                    
                    # Check collision with player
                    if distance < (enemy['radius'] + 15):
                        self.player.take_damage(enemy['damage'] * 0.016)  # Per frame
                
                # Check game over
                if not self.player.is_alive():
                    self.state = "GAME_OVER"
    
    def draw(self):
        """Draw game elements"""
        if self.state == "CHARACTER_SELECT":
            self.draw_character_select()
        elif self.state == "AREA_SELECT":
            self.draw_area_select()
        elif self.state == "GAME":
            self.draw_game()
        elif self.state == "PAUSED":
            self.draw_paused()
        elif self.state == "GAME_OVER":
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_character_select(self):
        """Draw character selection screen"""
        self.screen.fill((20, 20, 40))
        
        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 36)
        
        # Title
        title = font_large.render("SELECT YOUR CHARACTER", True, (255, 255, 255))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))
        
        # Character options
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
            
            # Title
            title = font_large.render(f"Welcome, {self.player.name}!", True, (255, 200, 100))
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))
            
            # Area description
            area_name = font_medium.render(area_info['name'], True, (100, 255, 100))
            self.screen.blit(area_name, (self.width // 2 - area_name.get_width() // 2, 150))
            
            desc = font_small.render(area_info['description'], True, (200, 200, 200))
            self.screen.blit(desc, (self.width // 2 - desc.get_width() // 2, 250))
            
            # Stats
            stats_text = f"HP: {self.player.max_health} | Speed: {int(self.player.speed)} | Damage: {int(self.player.strength)}"
            stats = font_small.render(stats_text, True, (100, 200, 255))
            self.screen.blit(stats, (self.width // 2 - stats.get_width() // 2, 350))
            
            # Instructions
            start = font_medium.render("Press ENTER to start", True, (255, 255, 100))
            self.screen.blit(start, (self.width // 2 - start.get_width() // 2, 500))
            
            back = font_small.render("Press ESC to go back", True, (150, 150, 150))
            self.screen.blit(back, (self.width // 2 - back.get_width() // 2, 600))
    
    def draw_game(self):
        """Draw the main game"""
        if self.current_area and self.player:
            # Draw area background
            self.screen.fill(self.current_area.color)
            
            # Draw ground/safe zone at bottom
            pygame.draw.rect(self.screen, (50, 150, 50), (0, self.height - 150, self.width, 150))
            
            # Draw enemies
            for enemy in self.enemies:
                # Change color if stunned
                color = (100, 100, 200) if enemy['stun_duration'] > 0 else enemy['color']
                pygame.draw.circle(self.screen, color, 
                                 (int(enemy['x']), int(enemy['y'])), enemy['radius'])
                
                # Enemy health bar
                health_ratio = enemy['health'] / enemy['max_health']
                bar_width = 30
                pygame.draw.rect(self.screen, (255, 0, 0), 
                               (enemy['x'] - bar_width // 2, enemy['y'] - 30, bar_width, 5))
                pygame.draw.rect(self.screen, (0, 255, 0), 
                               (enemy['x'] - bar_width // 2, enemy['y'] - 30, bar_width * health_ratio, 5))
            
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
            
            # Area info
            area_text = f"Area: {self.current_area.name} | Difficulty: {self.current_area.difficulty}"
            area_label = font_small.render(area_text, True, (200, 200, 200))
            self.screen.blit(area_label, (10, self.height - 140))
            
            # Controls
            controls = [
                "W/A/S/D - Move",
                "SPACE - Attack",
                "SHIFT - Special Ability",
                "Q - Change Area",
                "ESC - Pause"
            ]
            for i, control in enumerate(controls):
                label = font_small.render(control, True, (150, 150, 150))
                self.screen.blit(label, (self.width - 250, self.height - 140 + i * 25))
    
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
        
        menu = font_small.render("Press Q to change area", True, (200, 200, 200))
        self.screen.blit(menu, (self.width // 2 - menu.get_width() // 2, self.height // 2 + 70))
    
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
        
        stats_text = f"Final Level: {self.player.level} | Experience Gained: {self.player.experience}"
        stats_label = font_medium.render(stats_text, True, (200, 200, 200))
        self.screen.blit(stats_label, (self.width // 2 - stats_label.get_width() // 2, 
                                      self.height // 2 - 20))
        
        restart = font_small.render("Press ESC to return to menu", True, (255, 255, 100))
        self.screen.blit(restart, (self.width // 2 - restart.get_width() // 2, 
                                  self.height // 2 + 80))
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
        
        pygame.quit()
