"""
Utility functions for the Tag Game.
"""

import pygame
import random
from constants import *

def draw_text(surface, text, size, x, y, color):
    """
    Draw text on a surface with given parameters.
    
    Args:
        surface: pygame surface to draw on
        text: string to display
        size: font size
        x, y: position coordinates
        color: RGB color tuple
    """
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_surface, text_rect)
    
def random_color():
    """Generate a random RGB color."""
    return (
        random.randint(50, 255),
        random.randint(50, 255),
        random.randint(50, 255)
    )
    
def distance(point1, point2):
    """Calculate Euclidean distance between two points."""
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5
