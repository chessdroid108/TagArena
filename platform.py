"""
Platform module for the Tag Game.
Defines the Platform class with different platform types and effects.
"""

import pygame
import random
import math
from constants import *

class Platform:
    def __init__(self, rect, platform_type="normal"):
        """
        Initialize a platform with a rectangle and type.
        
        Args:
            rect: pygame.Rect defining the platform dimensions and position
            platform_type: str indicating platform behavior 
                           ("normal", "sticky", "jump", "speed", "passthrough")
        """
        self.rect = rect
        self.type = platform_type
        
        # Set color based on platform type
        self.set_platform_color()
        
        # Visual effects
        self.wobble_offset = 0
        self.wobble_speed = random.uniform(0.002, 0.005)
        self.wobble_amount = random.uniform(2, 4) if platform_type == "passthrough" else 0
        self.pulse_amount = 0
        self.animation_timer = random.uniform(0, math.pi * 2)  # Random start phase
        
        # Platform-specific properties
        self.pass_through = platform_type == "passthrough"
        
    def set_platform_color(self):
        """Set the platform color based on its type."""
        if self.type == "normal":
            self.color = (150, 150, 150)  # Gray
            self.outline_color = (100, 100, 100)  # Darker gray
        elif self.type == "sticky":
            self.color = (200, 100, 50)  # Orange-brown
            self.outline_color = (150, 50, 25)  # Darker orange-brown
        elif self.type == "jump":
            self.color = (100, 200, 100)  # Green
            self.outline_color = (50, 150, 50)  # Darker green
        elif self.type == "speed":
            self.color = (100, 150, 255)  # Light blue
            self.outline_color = (50, 100, 200)  # Darker blue
        elif self.type == "passthrough":
            self.color = (170, 170, 200)  # Light purple
            self.outline_color = (120, 120, 150)  # Darker purple
            
    def update(self, dt):
        """Update platform animations."""
        # Update animation timer
        self.animation_timer += dt * 2
        
        # Update wobble for pass-through platforms
        if self.type == "passthrough":
            self.wobble_offset = math.sin(self.animation_timer * self.wobble_speed) * self.wobble_amount
        
        # Update pulse effect for jump platforms
        if self.type == "jump":
            self.pulse_amount = (math.sin(self.animation_timer * 2) * 0.1) + 0.9  # 0.8 to 1.0
            
        # Update ripple effect for speed platforms
        if self.type == "speed":
            # Speed platforms have a ripple effect which is handled in the draw method
            pass
            
    def draw(self, surface, camera=None):
        """Draw the platform to the surface."""
        # Get the platform's rectangle in screen coordinates
        if camera:
            rect = camera.apply_rect(self.rect)
        else:
            rect = self.rect
            
        # Skip drawing if off-screen
        if rect.right < 0 or rect.left > SCREEN_WIDTH or rect.bottom < 0 or rect.top > SCREEN_HEIGHT:
            return
            
        # Scale the rectangle if needed
        if self.type == "jump" and hasattr(self, 'pulse_amount'):
            # Expand the rectangle while keeping the top edge fixed
            orig_top = rect.top
            rect.height = int(rect.height * self.pulse_amount)
            rect.top = orig_top  # Keep top position fixed
            
        # Draw platform body
        pygame.draw.rect(surface, self.color, rect)
        
        # Draw platform outline
        pygame.draw.rect(surface, self.outline_color, rect, 2)
        
        # Draw type-specific decorations
        if self.type == "sticky":
            # Draw sticky texture (small dots)
            for i in range(3, rect.width - 3, 10):
                for j in range(3, rect.height - 3, 10):
                    dot_size = 2
                    pygame.draw.rect(surface, self.outline_color, 
                                    (rect.left + i, rect.top + j, dot_size, dot_size))
                    
        elif self.type == "jump":
            # Draw up arrows
            arrow_width = min(20, rect.width // 4)
            for i in range(rect.width // arrow_width):
                arrow_x = rect.left + (i * arrow_width) + (arrow_width // 2)
                arrow_points = [
                    (arrow_x, rect.top + 5),
                    (arrow_x - 5, rect.top + 15),
                    (arrow_x + 5, rect.top + 15)
                ]
                pygame.draw.polygon(surface, self.outline_color, arrow_points)
                
        elif self.type == "speed":
            # Draw speed lines
            for i in range(3, rect.width - 10, 15):
                line_x = rect.left + i
                pygame.draw.line(surface, self.outline_color, 
                                (line_x, rect.top + 5), 
                                (line_x + 10, rect.top + rect.height - 5), 2)
                
        elif self.type == "passthrough":
            # Draw dashed line on top
            dash_length = 5
            for i in range(0, rect.width, dash_length * 2):
                pygame.draw.line(surface, self.outline_color, 
                                (rect.left + i, rect.top), 
                                (rect.left + i + dash_length, rect.top), 2)
                                
    def check_collision(self, player):
        """
        Check if the player is colliding with this platform and handle the collision.
        
        Args:
            player: Player object to check collision with
        
        Returns:
            bool: True if collision occurred, False otherwise
        """
        # Skip collision if this is a passthrough platform and player is dropping through
        if self.pass_through and player.passing_through:
            return False
            
        # Get player's rectangle
        player_rect = player.get_rect()
        
        # Calculate the overlap between the player and platform
        if player_rect.colliderect(self.rect):
            # Calculate overlap amounts
            left_overlap = player_rect.right - self.rect.left
            right_overlap = self.rect.right - player_rect.left
            top_overlap = player_rect.bottom - self.rect.top
            bottom_overlap = self.rect.bottom - player_rect.top
            
            # Find the smallest overlap
            min_overlap = min(left_overlap, right_overlap, top_overlap, bottom_overlap)
            
            # Determine which side of the platform was hit
            if min_overlap == top_overlap and player.vy >= 0:
                # Player landed on top of platform
                player.y = self.rect.top - player.rect.height / 2
                player.vy = 0
                player.on_ground = True
                
                # Set player's current platform
                player.current_platform = self
                
                # Apply platform-specific effects
                if self.type == "sticky":
                    player.on_sticky_platform = True
                elif self.type == "jump":
                    player.on_jump_platform = True
                elif self.type == "speed":
                    player.on_speed_platform = True
                
                # Update player speed based on platform effects
                player.update_speed()
                
                return True
                
            elif min_overlap == bottom_overlap and player.vy <= 0:
                # Player hit bottom of platform (when jumping)
                player.y = self.rect.bottom + player.rect.height / 2
                player.vy = 0
                return True
                
            elif min_overlap == left_overlap and player.vx >= 0:
                # Player hit left side of platform
                player.x = self.rect.left - player.rect.width / 2
                player.vx = 0
                return True
                
            elif min_overlap == right_overlap and player.vx <= 0:
                # Player hit right side of platform
                player.x = self.rect.right + player.rect.width / 2
                player.vx = 0
                return True
                
        return False
