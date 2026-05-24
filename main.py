"""
Entry point for the Action Game with shops and autosave
"""

import pygame
from game import Game
from saves import SaveManager

def main():
    """Initialize and run the game"""
    pygame.init()
    
    # Initialize save manager
    save_manager = SaveManager()
    
    game = Game(save_manager)
    game.run()


if __name__ == "__main__":
    main()
