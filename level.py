"""
Level module for the Tag Game.
Defines the Level class for managing platforms and layouts.
"""

import pygame
import random
from constants import *
from platform import Platform

class Level:
    def __init__(self, game):
        """
        Initialize the level manager.
        
        Args:
            game: reference to the main game object
        """
        self.game = game
        self.platforms = []
        self.layouts = self.create_level_layouts()
        
    def create_level_layouts(self):
        """
        Create multiple level layouts with platforms.
        
        Returns:
            list of layout functions
        """
        # Return list of layout-generating functions
        return [
            self.create_basic_layout,
            self.create_vertical_layout,
            self.create_scattered_layout,
            self.create_spiral_layout,
            self.create_corridors_layout
        ]
    
    def get_layout_count(self):
        """
        Get the number of available layouts.
        
        Returns:
            int: number of layouts
        """
        return len(self.layouts)
        
    def load_layout(self, index):
        """
        Load a specific level layout.
        
        Args:
            index: index of the layout to load
        """
        self.platforms.clear()
        
        # Call the appropriate layout function
        if 0 <= index < len(self.layouts):
            layout_func = self.layouts[index]
            layout_func()
        else:
            # Fallback to basic layout
            self.create_basic_layout()
            
    def create_basic_layout(self):
        """Create a basic platformer layout with horizontal platforms."""
        # Ground platform
        self.add_platform(0, LEVEL_HEIGHT - 50, LEVEL_WIDTH, 50, "normal")
        
        # Main platforms
        platform_width = 300
        
        # Left platforms
        self.add_platform(100, LEVEL_HEIGHT - 200, platform_width, PLATFORM_THICKNESS, "normal")
        self.add_platform(500, LEVEL_HEIGHT - 350, platform_width, PLATFORM_THICKNESS, "jump")
        self.add_platform(200, LEVEL_HEIGHT - 500, platform_width, PLATFORM_THICKNESS, "speed")
        
        # Middle platforms
        self.add_platform(LEVEL_WIDTH/2 - platform_width/2, LEVEL_HEIGHT - 250, 
                         platform_width, PLATFORM_THICKNESS, "passthrough")
        self.add_platform(LEVEL_WIDTH/2 - platform_width/2, LEVEL_HEIGHT - 450, 
                         platform_width, PLATFORM_THICKNESS, "sticky")
        
        # Right platforms
        self.add_platform(LEVEL_WIDTH - 400, LEVEL_HEIGHT - 200, platform_width, PLATFORM_THICKNESS, "normal")
        self.add_platform(LEVEL_WIDTH - 800, LEVEL_HEIGHT - 350, platform_width, PLATFORM_THICKNESS, "jump")
        self.add_platform(LEVEL_WIDTH - 500, LEVEL_HEIGHT - 500, platform_width, PLATFORM_THICKNESS, "speed")
        
        # Small floating platforms
        for i in range(5):
            x = random.randint(200, LEVEL_WIDTH - 200)
            y = random.randint(LEVEL_HEIGHT - 700, LEVEL_HEIGHT - 550)
            width = random.randint(100, 200)
            self.add_random_platform(x, y, width, PLATFORM_THICKNESS)
            
    def create_vertical_layout(self):
        """Create a vertically-oriented layout."""
        # Ground platform
        self.add_platform(0, LEVEL_HEIGHT - 50, LEVEL_WIDTH, 50, "normal")
        
        # Left side platforms
        self.add_platform(100, LEVEL_HEIGHT - 200, 250, PLATFORM_THICKNESS, "normal")
        self.add_platform(100, LEVEL_HEIGHT - 350, 250, PLATFORM_THICKNESS, "jump")
        self.add_platform(100, LEVEL_HEIGHT - 500, 250, PLATFORM_THICKNESS, "speed")
        self.add_platform(100, LEVEL_HEIGHT - 650, 250, PLATFORM_THICKNESS, "sticky")
        
        # Right side platforms
        self.add_platform(LEVEL_WIDTH - 350, LEVEL_HEIGHT - 200, 250, PLATFORM_THICKNESS, "normal")
        self.add_platform(LEVEL_WIDTH - 350, LEVEL_HEIGHT - 350, 250, PLATFORM_THICKNESS, "jump")
        self.add_platform(LEVEL_WIDTH - 350, LEVEL_HEIGHT - 500, 250, PLATFORM_THICKNESS, "speed")
        self.add_platform(LEVEL_WIDTH - 350, LEVEL_HEIGHT - 650, 250, PLATFORM_THICKNESS, "sticky")
        
        # Middle connecting platforms
        self.add_platform(LEVEL_WIDTH/2 - 125, LEVEL_HEIGHT - 275, 250, PLATFORM_THICKNESS, "passthrough")
        self.add_platform(LEVEL_WIDTH/2 - 125, LEVEL_HEIGHT - 425, 250, PLATFORM_THICKNESS, "passthrough")
        self.add_platform(LEVEL_WIDTH/2 - 125, LEVEL_HEIGHT - 575, 250, PLATFORM_THICKNESS, "passthrough")
        
    def create_scattered_layout(self):
        """Create a layout with randomly scattered platforms."""
        # Ground platform
        self.add_platform(0, LEVEL_HEIGHT - 50, LEVEL_WIDTH, 50, "normal")
        
        # Create random platforms
        platform_types = ["normal", "sticky", "jump", "speed", "passthrough"]
        
        for i in range(20):
            x = random.randint(100, LEVEL_WIDTH - 300)
            y = random.randint(LEVEL_HEIGHT - 700, LEVEL_HEIGHT - 100)
            width = random.randint(150, 350)
            platform_type = random.choice(platform_types)
            
            # Ensure platforms aren't too close to each other
            valid_position = True
            for platform in self.platforms:
                if (abs(platform.rect.centerx - (x + width/2)) < width and
                    abs(platform.rect.centery - y) < 100):
                    valid_position = False
                    break
                    
            if valid_position:
                self.add_platform(x, y, width, PLATFORM_THICKNESS, platform_type)
                
    def create_spiral_layout(self):
        """Create a spiral-shaped layout."""
        # Ground platform
        self.add_platform(0, LEVEL_HEIGHT - 50, LEVEL_WIDTH, 50, "normal")
        
        # Create spiral platforms
        platform_width = 300
        center_x = LEVEL_WIDTH // 2
        center_y = LEVEL_HEIGHT // 2
        
        # Start at outer edge and spiral inward
        radius = min(LEVEL_WIDTH, LEVEL_HEIGHT) * 0.4
        platform_types = ["normal", "sticky", "jump", "speed", "passthrough"]
        
        for i in range(8):
            angle = i * (2 * math.pi / 8)
            r = radius * (1 - i * 0.1)
            
            x = center_x + int(r * math.cos(angle)) - platform_width // 2
            y = center_y + int(r * math.sin(angle))
            
            # Constrain to level boundaries
            x = max(50, min(LEVEL_WIDTH - platform_width - 50, x))
            y = max(50, min(LEVEL_HEIGHT - 150, y))
            
            # Choose platform type
            platform_type = platform_types[i % len(platform_types)]
            
            self.add_platform(x, y, platform_width, PLATFORM_THICKNESS, platform_type)
            
    def create_corridors_layout(self):
        """Create a layout with corridors and multiple levels."""
        # Ground platform
        self.add_platform(0, LEVEL_HEIGHT - 50, LEVEL_WIDTH, 50, "normal")
        
        # First level
        self.add_platform(100, LEVEL_HEIGHT - 200, LEVEL_WIDTH - 200, PLATFORM_THICKNESS, "normal")
        # Add holes
        self.add_platform(100, LEVEL_HEIGHT - 200, 300, PLATFORM_THICKNESS, "normal")
        self.add_platform(600, LEVEL_HEIGHT - 200, 300, PLATFORM_THICKNESS, "normal")
        self.add_platform(1100, LEVEL_HEIGHT - 200, 300, PLATFORM_THICKNESS, "normal")
        self.add_platform(1600, LEVEL_HEIGHT - 200, 300, PLATFORM_THICKNESS, "normal")
        
        # Second level
        self.add_platform(300, LEVEL_HEIGHT - 350, LEVEL_WIDTH - 600, PLATFORM_THICKNESS, "sticky")
        
        # Third level with speed platforms
        self.add_platform(500, LEVEL_HEIGHT - 500, 300, PLATFORM_THICKNESS, "speed")
        self.add_platform(1000, LEVEL_HEIGHT - 500, 300, PLATFORM_THICKNESS, "speed")
        self.add_platform(1500, LEVEL_HEIGHT - 500, 300, PLATFORM_THICKNESS, "speed")
        
        # Top level with jump platforms
        self.add_platform(300, LEVEL_HEIGHT - 650, 300, PLATFORM_THICKNESS, "jump")
        self.add_platform(800, LEVEL_HEIGHT - 650, 300, PLATFORM_THICKNESS, "jump")
        self.add_platform(1300, LEVEL_HEIGHT - 650, 300, PLATFORM_THICKNESS, "jump")
        
        # Vertical platforms connecting levels
        self.add_platform(500, LEVEL_HEIGHT - 500, 50, 150, "normal")
        self.add_platform(1200, LEVEL_HEIGHT - 350, 50, 150, "normal")
        
        # Passthrough platforms
        self.add_platform(200, LEVEL_HEIGHT - 300, 200, PLATFORM_THICKNESS, "passthrough")
        self.add_platform(700, LEVEL_HEIGHT - 450, 200, PLATFORM_THICKNESS, "passthrough")
        self.add_platform(1200, LEVEL_HEIGHT - 600, 200, PLATFORM_THICKNESS, "passthrough")
        self.add_platform(1700, LEVEL_HEIGHT - 400, 200, PLATFORM_THICKNESS, "passthrough")
        
    def add_platform(self, x, y, width, height, platform_type):
        """
        Add a platform to the level.
        
        Args:
            x, y: position coordinates
            width, height: dimensions
            platform_type: type of platform
        """
        rect = pygame.Rect(x, y, width, height)
        platform = Platform(rect, platform_type)
        self.platforms.append(platform)
        
    def add_random_platform(self, x, y, width, height):
        """
        Add a platform with a random type.
        
        Args:
            x, y: position coordinates
            width, height: dimensions
        """
        platform_types = ["normal", "sticky", "jump", "speed", "passthrough"]
        platform_type = random.choice(platform_types)
        self.add_platform(x, y, width, height, platform_type)
        
    def get_valid_spawn_positions(self):
        """
        Get a list of valid positions on platforms where objects can spawn.
        
        Returns:
            list of (x, y) tuples
        """
        valid_positions = []
        
        for platform in self.platforms:
            # Skip small platforms or passthrough platforms for spawning
            if platform.rect.width < 100 or platform.type == "passthrough":
                continue
                
            # Add a few positions on this platform
            num_positions = max(1, platform.rect.width // 100)
            segment_width = platform.rect.width / num_positions
            
            for i in range(num_positions):
                x = platform.rect.left + (i + 0.5) * segment_width
                y = platform.rect.top  # Position is at top of platform
                valid_positions.append((x, y))
                
        return valid_positions
        
    def draw(self, surface):
        """
        Draw all platforms in the level.
        
        Args:
            surface: surface to draw on
        """
        for platform in self.platforms:
            platform.update(0.016)  # Default to ~60fps for animation
            platform.draw(surface)
