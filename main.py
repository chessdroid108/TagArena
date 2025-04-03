#!/usr/bin/env python3
"""
Tag Game - Main Entry Point
A two-player tag game with unique player properties and interactive platforms
built with Pygame and Pymunk physics engine.
"""

import pygame
import os
import sys
from game import Game

def main():
    """Main function to initialize and run the game."""
    # Configure for Replit environment 
    #os.environ["SDL_VIDEODRIVER"] = "x11"
    
    # Disable warnings
    #os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
        
    # Initialize pygame
    pygame.init()
    
    # Create and run the game
    try:
        # Create the game window
        game = Game()
        game.run()
    except KeyboardInterrupt:
        print("Game terminated by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        pygame.quit()

if __name__ == "__main__":
    main()
