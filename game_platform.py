"""
Platform module for the Tag Game.
Defines different platform types with unique effects.
Uses custom collision detection instead of pymunk.
"""

import pygame
from constants import *

class Platform:
    def __init__(self, game, position, width, platform_type="regular"):
        """
        Initialize a platform with position and type.
        
        Args:
            game: reference to the main game object
            position: (x, y) tuple for the center of the platform
            width: width of the platform
            platform_type: type of platform affecting player behavior
        """
        self.game = game
        self.platform_type = platform_type
        self.width = width
        self.height = PLATFORM_HEIGHT
        
        # Position is center of platform
        self.x, self.y = position
        
        # Store the platform's rect for collision detection
        half_width = self.width / 2
        half_height = self.height / 2
        self.rect = pygame.Rect(
            self.x - half_width,
            self.y - half_height,
            self.width,
            self.height
        )
        
        # Add platform to game's platform list
        game.platforms.append(self)
            
    def get_color(self):
        """Get the color for this platform type."""
        if self.platform_type == "regular":
            return REGULAR_PLATFORM_COLOR
        elif self.platform_type == "sticky":
            return STICKY_PLATFORM_COLOR
        elif self.platform_type == "jump":
            return JUMP_PLATFORM_COLOR
        elif self.platform_type == "speed":
            return SPEED_PLATFORM_COLOR
        elif self.platform_type == "passthrough":
            return PASSTHROUGH_PLATFORM_COLOR
        else:
            return GRAY
    
    def get_rect(self):
        """Get the platform's collision rectangle."""
        return self.rect
            
    def apply_effect(self, player):
        """Apply platform effect to a player."""
        if self.platform_type == "sticky":
            player.on_sticky_platform = True
        elif self.platform_type == "jump":
            player.on_jump_platform = True
        elif self.platform_type == "speed":
            player.on_speed_platform = True
            
        # Update player speed based on platform effect
        player.update_speed()
            
    def draw(self, screen, camera=None):
        """Draw the platform on the screen."""
        if camera:
            # Transform the rect to screen coordinates
            draw_rect = camera.apply(self.rect)
            pygame.draw.rect(screen, self.get_color(), draw_rect)
        else:
            # No camera, draw as normal
            pygame.draw.rect(screen, self.get_color(), self.rect)
        
        # Add visual indicator based on platform type
        if self.platform_type != "regular":
            # Draw pattern or symbol depending on platform type
            
            # Calculate scale factor based on camera zoom
            scale = 1.0
            if camera:
                scale = camera.zoom_level
                
            spacing = 20 * scale
            
            for i in range(0, int(self.width), int(20)):
                # Calculate world coordinates
                world_x = self.rect.left + i + 10
                world_y = self.rect.centery
                
                # Apply camera transformation if available
                if camera:
                    x, y = camera.apply_pos((world_x, world_y))
                    size = 5 * scale  # Scale decorations by camera zoom
                else:
                    x, y = world_x, world_y
                    size = 5  # Default size
                
                if self.platform_type == "sticky":
                    # Draw zigzag pattern
                    points = [
                        (x - size, y - size),
                        (x, y + size),
                        (x + size, y - size)
                    ]
                    pygame.draw.lines(screen, BLACK, False, points, max(1, int(2 * scale)))
                    
                elif self.platform_type == "jump":
                    # Draw up arrow
                    pygame.draw.line(screen, BLACK, (x, y - size), (x, y + size), max(1, int(2 * scale)))
                    pygame.draw.line(screen, BLACK, (x - size, y), (x, y - size), max(1, int(2 * scale)))
                    pygame.draw.line(screen, BLACK, (x + size, y), (x, y - size), max(1, int(2 * scale)))
                    
                elif self.platform_type == "speed":
                    # Draw right arrow
                    pygame.draw.line(screen, BLACK, (x - size, y), (x + size, y), max(1, int(2 * scale)))
                    pygame.draw.line(screen, BLACK, (x, y - size), (x + size, y), max(1, int(2 * scale)))
                    pygame.draw.line(screen, BLACK, (x, y + size), (x + size, y), max(1, int(2 * scale)))
                    
                elif self.platform_type == "passthrough":
                    # Draw dashed line
                    pygame.draw.line(screen, BLACK, (x - size, y), (x + size, y), max(1, int(scale)))