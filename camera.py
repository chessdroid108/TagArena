"""
Camera module for the Tag Game.
Provides a camera system that follows the players, with zoom functionality.
"""

import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Camera:
    def __init__(self, width, height):
        """Initialize the camera.
        
        Args:
            width: The width of the level
            height: The height of the level
        """
        self.width = width
        self.height = height
        self.state = pygame.Rect(0, 0, width, height)
        
        # Camera properties
        self.target_x = 0
        self.target_y = 0
        self.zoom_level = 1.0
        self.target_zoom = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 1.5
        
        # Smoothing factors (0 = no smoothing, 1 = no movement)
        self.position_smooth = 0.1
        self.zoom_smooth = 0.05
    
    def update(self, players, dt):
        """Update the camera position to focus on both players.
        
        Args:
            players: List of player objects with x, y attributes
            dt: Time delta since last frame
        """
        if not players:
            return
            
        # Find average position of both players
        total_x = sum(player.x for player in players)
        total_y = sum(player.y for player in players)
        avg_x = total_x / len(players)
        avg_y = total_y / len(players)
        
        # Set target to average position
        self.target_x = avg_x
        self.target_y = avg_y
        
        # Calculate distance between players
        if len(players) >= 2:
            max_distance = 0
            for i in range(len(players)):
                for j in range(i+1, len(players)):
                    dx = players[i].x - players[j].x
                    dy = players[i].y - players[j].y
                    distance = (dx**2 + dy**2)**0.5
                    max_distance = max(max_distance, distance)
            
            # Adjust zoom based on distance
            # Further apart = zoom out (smaller value)
            base_zoom = 1.0
            distance_factor = max(100, min(max_distance, 700))
            self.target_zoom = base_zoom * (400 / distance_factor)
            
            # Clamp zoom to reasonable limits
            self.target_zoom = max(self.min_zoom, min(self.max_zoom, self.target_zoom))
        
        # Smooth camera movement
        self.state.centerx += (self.target_x - self.state.centerx) * self.position_smooth * (60 * dt)
        self.state.centery += (self.target_y - self.state.centery) * self.position_smooth * (60 * dt)
        self.zoom_level += (self.target_zoom - self.zoom_level) * self.zoom_smooth * (60 * dt)
        
        # Ensure camera stays within level bounds after applying zoom
        view_w = SCREEN_WIDTH / self.zoom_level
        view_h = SCREEN_HEIGHT / self.zoom_level
        
        self.state.width = view_w
        self.state.height = view_h
        
        # Prevent camera from showing areas outside the level
        self.state.left = max(0, min(self.state.left, self.width - view_w))
        self.state.top = max(0, min(self.state.top, self.height - view_h))
    
    def apply(self, entity_rect):
        """Transform entity rect to screen coordinates.
        
        Args:
            entity_rect: pygame.Rect of the entity to transform
            
        Returns:
            pygame.Rect in screen coordinates with zoom applied
        """
        # Calculate zoom-adjusted rect
        screen_rect = pygame.Rect(
            (entity_rect.x - self.state.left) * self.zoom_level,
            (entity_rect.y - self.state.top) * self.zoom_level,
            entity_rect.width * self.zoom_level,
            entity_rect.height * self.zoom_level
        )
        return screen_rect
    
    def apply_pos(self, pos):
        """Transform a position to screen coordinates.
        
        Args:
            pos: (x, y) tuple of the position to transform
            
        Returns:
            (x, y) tuple in screen coordinates with zoom applied
        """
        x, y = pos
        screen_x = (x - self.state.left) * self.zoom_level
        screen_y = (y - self.state.top) * self.zoom_level
        return (screen_x, screen_y)
    
    def reverse_apply(self, screen_pos):
        """Transform a screen position to world coordinates.
        
        Args:
            screen_pos: (x, y) tuple of screen position
            
        Returns:
            (x, y) tuple in world coordinates
        """
        screen_x, screen_y = screen_pos
        world_x = (screen_x / self.zoom_level) + self.state.left
        world_y = (screen_y / self.zoom_level) + self.state.top
        return (world_x, world_y)