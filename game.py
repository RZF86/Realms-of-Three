"""
Main game logic and state management
"""

import pygame
from characters import create_character


class Game:
    """Main game class"""
    
    def __init__(self, width=1200, height=800):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Action Game - Character Selection")
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Game states
        self.state = "CHARACTER_SELECT"  # CHARACTER_SELECT, GAME, PAUSED, GAME_OVER
        self.player = None
        self.enemies = []
        self.running = True
        
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handle_input(event)
    
    def handle_input(self, event):
        """Handle keyboard input based on game state"""
        if self.state == "CHARACTER_SELECT":
            if event.key == pygame.K_1:
                self.select_character("human")
            elif event.key == pygame.K_2:
                self.select_character("frog")
            elif event.key == pygame.K_3:
                self.select_character("dragon")
        elif self.state == "GAME":
            self.handle_game_input(event)
    
    def handle_game_input(self, event):
        """Handle in-game input"""
        if event.key == pygame.K_ESCAPE:
            self.state = "PAUSED"
        elif event.key == pygame.K_SPACE:
            if self.player:
                self.player.attack()
        elif event.key == pygame.K_LSHIFT:
            if self.player:
                self.player.special_ability()
    
    def select_character(self, character_type):
        """Select a character and start the game"""
        try:
            self.player = create_character(character_type)
            self.state = "GAME"
            print(f"Selected: {self.player.name}")
        except ValueError as e:
            print(f"Error: {e}")
    
    def update(self):
        """Update game logic"""
        if self.state == "GAME":
            if self.player:
                # Update player
                self.player.health = min(self.player.max_health, self.player.health + 0.1)
    
    def draw(self):
        """Draw game elements"""
        self.screen.fill((0, 0, 0))  # Black background
        
        if self.state == "CHARACTER_SELECT":
            self.draw_character_select()
        elif self.state == "GAME":
            self.draw_game()
        elif self.state == "PAUSED":
            self.draw_paused()
        
        pygame.display.flip()
    
    def draw_character_select(self):
        """Draw character selection screen"""
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
        
        # Instructions
        instr = font_small.render("Press 1, 2, or 3 to select", True, (255, 255, 100))
        self.screen.blit(instr, (self.width // 2 - instr.get_width() // 2, self.height - 100))
    
    def draw_game(self):
        """Draw the main game"""
        if self.player:
            font = pygame.font.Font(None, 36)
            
            # Draw player info
            info_text = f"{self.player.name} | HP: {self.player.health:.0f}/{self.player.max_health}"
            info_label = font.render(info_text, True, (255, 255, 255))
            self.screen.blit(info_label, (20, 20))
            
            # Draw health bar
            bar_width = 300
            bar_height = 30
            health_ratio = self.player.health / self.player.max_health
            pygame.draw.rect(self.screen, (255, 0, 0), (20, 70, bar_width, bar_height))
            pygame.draw.rect(self.screen, (0, 255, 0), (20, 70, bar_width * health_ratio, bar_height))
            
            # Draw controls
            small_font = pygame.font.Font(None, 24)
            controls = [
                "SPACE - Attack",
                "SHIFT - Special Ability",
                "ESC - Pause"
            ]
            for i, control in enumerate(controls):
                label = small_font.render(control, True, (150, 150, 150))
                self.screen.blit(label, (20, self.height - 100 + i * 30))
    
    def draw_paused(self):
        """Draw pause screen"""
        # Dim the background
        dim_surface = pygame.Surface((self.width, self.height))
        dim_surface.set_alpha(128)
        dim_surface.fill((0, 0, 0))
        self.screen.blit(dim_surface, (0, 0))
        
        # Draw pause text
        font = pygame.font.Font(None, 72)
        pause_text = font.render("PAUSED", True, (255, 255, 255))
        self.screen.blit(pause_text, (self.width // 2 - pause_text.get_width() // 2, self.height // 2 - 50))
        
        small_font = pygame.font.Font(None, 36)
        resume_text = small_font.render("Press ESC to resume", True, (200, 200, 200))
        self.screen.blit(resume_text, (self.width // 2 - resume_text.get_width() // 2, self.height // 2 + 50))
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
        
        pygame.quit()
