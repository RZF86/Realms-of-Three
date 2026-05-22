"""
Entry point for the Action Game
"""

import pygame
from game import Game


def main():
    """Initialize and run the game"""
    pygame.init()
    
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
