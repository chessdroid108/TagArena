"""
Obstacle module for the Tag Game.
Defines different obstacle types with unique behaviors and effects.
"""

import pygame
import random
import math
from constants import *

class Obstacle:
    def __init__(self, game, position, obstacle_type="static", width=40, height=40, **kwargs):
        """
        Initialize an obstacle with position and type.
        
        Args:
            game: reference to the main game object
            position: (x, y) tuple for the center of the obstacle
            obstacle_type: type of obstacle (static, moving, rotating, damaging)
            width: width of the obstacle
            height: height of the obstacle
            **kwargs: additional parameters specific to obstacle type
        """
        self.game = game
        self.x, self.y = position
        self.obstacle_type = obstacle_type
        self.width = width
        self.height = height
        
        # Visuals
        self.color = OBSTACLE_COLOR
        self.outline_color = OBSTACLE_OUTLINE
        
        # For animated obstacles
        self.animation_time = 0
        self.animation_speed = 1.0
        
        # Moving obstacle properties
        self.original_pos = position
        self.vx = 0
        self.vy = 0
        self.movement_range = kwargs.get('movement_range', 100)
        self.movement_speed = kwargs.get('movement_speed', 1.0)
        self.movement_direction = kwargs.get('movement_direction', 'horizontal')
        
        # Initialize obstacle based on type
        if obstacle_type == "moving":
            self._init_moving_obstacle(**kwargs)
        elif obstacle_type == "rotating":
            self._init_rotating_obstacle(**kwargs)
        elif obstacle_type == "damaging":
            self._init_damaging_obstacle(**kwargs)
        elif obstacle_type == "bouncing":
            self._init_bouncing_obstacle(**kwargs)
    
    def _init_moving_obstacle(self, **kwargs):
        """Initialize a moving obstacle."""
        if self.movement_direction == 'horizontal':
            self.vx = self.movement_speed
            self.vy = 0
        elif self.movement_direction == 'vertical':
            self.vx = 0
            self.vy = self.movement_speed
        elif self.movement_direction == 'circular':
            self.angle = 0
            self.radius = self.movement_range
            self.angular_speed = self.movement_speed * 0.05
            self.center_x, self.center_y = self.original_pos
        
        # Customize appearance
        self.color = (100, 100, 150)
    
    def _init_rotating_obstacle(self, **kwargs):
        """Initialize a rotating obstacle."""
        self.rotation = 0
        self.rotation_speed = kwargs.get('rotation_speed', 2.0)
        self.points = []
        self.radius = max(self.width, self.height) / 2
        
        # Create points for the rotating shape (e.g. a spike bar)
        num_points = kwargs.get('num_points', 4)
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            px = self.radius * math.cos(angle)
            py = self.radius * math.sin(angle)
            self.points.append((px, py))
            
        # Add center point
        self.points.append((0, 0))
        
        # Customize appearance
        self.color = (150, 70, 70)
    
    def _init_damaging_obstacle(self, **kwargs):
        """Initialize a damaging obstacle."""
        self.damage = kwargs.get('damage', 1)
        self.damage_cooldown = 1.0  # seconds between damage
        self.current_cooldown = 0
        
        # Make it spiky
        self.is_spiky = True
        self.spike_length = kwargs.get('spike_length', 10)
        self.num_spikes = kwargs.get('num_spikes', 8)
        
        # Customize appearance
        self.color = (200, 50, 50)
    
    def _init_bouncing_obstacle(self, **kwargs):
        """Initialize a bouncing obstacle."""
        self.bounce_strength = kwargs.get('bounce_strength', 15)
        
        # Customize appearance
        self.color = (50, 200, 100)
    
    def update(self, dt):
        """Update obstacle state and animations.
        
        Args:
            dt: time delta in seconds
        """
        # Update animation time
        self.animation_time += dt
        
        # Type-specific updates
        if self.obstacle_type == "moving":
            self._update_moving(dt)
        elif self.obstacle_type == "rotating":
            self._update_rotating(dt)
        elif self.obstacle_type == "damaging":
            self._update_damaging(dt)
    
    def _update_moving(self, dt):
        """Update a moving obstacle."""
        if self.movement_direction == 'horizontal':
            self.x += self.vx * dt * 60
            
            # Reverse direction at bounds
            if abs(self.x - self.original_pos[0]) > self.movement_range:
                self.vx *= -1
                
        elif self.movement_direction == 'vertical':
            self.y += self.vy * dt * 60
            
            # Reverse direction at bounds
            if abs(self.y - self.original_pos[1]) > self.movement_range:
                self.vy *= -1
                
        elif self.movement_direction == 'circular':
            self.angle += self.angular_speed * dt * 60
            self.x = self.center_x + math.cos(self.angle) * self.radius
            self.y = self.center_y + math.sin(self.angle) * self.radius
    
    def _update_rotating(self, dt):
        """Update a rotating obstacle."""
        self.rotation += self.rotation_speed * dt * 60
        
        # Keep rotation in [0, 360) range
        self.rotation %= 360
    
    def _update_damaging(self, dt):
        """Update a damaging obstacle."""
        # Update cooldown
        if self.current_cooldown > 0:
            self.current_cooldown -= dt
    
    def get_rect(self):
        """Get the obstacle's collision rectangle."""
        return pygame.Rect(
            self.x - self.width/2,
            self.y - self.height/2,
            self.width,
            self.height
        )
    
    def get_collision_shape(self):
        """Get a more precise collision shape for complex obstacles."""
        if self.obstacle_type == "rotating":
            # Return list of transformed points for polygon collision
            transformed_points = []
            angle_rad = math.radians(self.rotation)
            for px, py in self.points:
                # Rotate point
                rx = px * math.cos(angle_rad) - py * math.sin(angle_rad)
                ry = px * math.sin(angle_rad) + py * math.cos(angle_rad)
                # Translate to obstacle position
                transformed_points.append((self.x + rx, self.y + ry))
            return transformed_points
        else:
            # Default to rectangle
            return self.get_rect()
    
    def check_collision(self, player_rect):
        """Check for collision with a player.
        
        Args:
            player_rect: pygame.Rect of the player
            
        Returns:
            True if collision occurred, False otherwise
        """
        # Basic rectangle collision
        if not player_rect.colliderect(self.get_rect()):
            return False
            
        # Additional collision logic for complex shapes
        if self.obstacle_type == "rotating":
            # For rotating obstacles, we need more precise collision
            # This is simplified - a more accurate version would use SAT
            # or per-pixel collision detection
            pass
            
        return True
    
    def apply_effect(self, player):
        """Apply obstacle effect to a player.
        
        Args:
            player: The player object to affect
            
        Returns:
            True if effect was applied, False otherwise
        """
        # Get obstacle rectangle
        obstacle_rect = self.get_rect()
        player_rect = player.get_rect()
        
        # Handle basic solid obstacle collision for all obstacle types except bouncing
        if self.obstacle_type != "bouncing":
            # Determine collision direction
            # Calculate overlap in each direction
            left_overlap = obstacle_rect.right - player_rect.left
            right_overlap = player_rect.right - obstacle_rect.left
            top_overlap = obstacle_rect.bottom - player_rect.top
            bottom_overlap = player_rect.bottom - obstacle_rect.top
            
            # Find the smallest overlap
            min_overlap = min(left_overlap, right_overlap, top_overlap, bottom_overlap)
            
            # Push the player outside the obstacle based on the smallest overlap
            if min_overlap == left_overlap:
                # Collision from the left
                player.x = obstacle_rect.right + player.radius
                player.vx = max(0, player.vx)  # Stop leftward movement
            elif min_overlap == right_overlap:
                # Collision from the right
                player.x = obstacle_rect.left - player.radius
                player.vx = min(0, player.vx)  # Stop rightward movement
            elif min_overlap == top_overlap:
                # Collision from above
                player.y = obstacle_rect.bottom + player.radius
                player.vy = max(0, player.vy)  # Stop upward movement
                player.is_grounded = False
            elif min_overlap == bottom_overlap:
                # Collision from below
                player.y = obstacle_rect.top - player.radius
                player.vy = min(0, player.vy)  # Stop downward movement
                player.is_grounded = True
                
            # Apply additional type-specific effects
            if self.obstacle_type == "damaging" and self.current_cooldown <= 0:
                # Apply damage effect
                player.take_damage(self.damage)
                self.current_cooldown = self.damage_cooldown
            
            # Play sound for collision
            from sounds import sound_manager
            sound_manager.play("obstacle_hit")
                
            return True
            
        elif self.obstacle_type == "bouncing":
            # Only apply bounce effect if player is above the obstacle
            # and moving downward (falling onto it)
            if player.vy > 0 and player_rect.bottom <= obstacle_rect.top + 10:
                # Top collision - bounce upward
                player.y = obstacle_rect.top - player.radius
                player.vy = -self.bounce_strength
                player.is_grounded = False
                
                # Play bounce sound
                from sounds import sound_manager
                sound_manager.play("bounce")
                
                return True
            else:
                # For side collisions with bounce obstacles, treat like regular obstacles
                # Determine collision direction
                left_overlap = obstacle_rect.right - player_rect.left
                right_overlap = player_rect.right - obstacle_rect.left
                top_overlap = obstacle_rect.bottom - player_rect.top
                bottom_overlap = player_rect.bottom - obstacle_rect.top
                
                # Find the smallest overlap
                min_overlap = min(left_overlap, right_overlap, top_overlap, bottom_overlap)
                
                # Push the player outside the obstacle based on the smallest overlap
                if min_overlap == left_overlap:
                    # Collision from the left
                    player.x = obstacle_rect.right + player.radius
                    player.vx = max(0, player.vx)  # Stop leftward movement
                elif min_overlap == right_overlap:
                    # Collision from the right
                    player.x = obstacle_rect.left - player.radius
                    player.vx = min(0, player.vx)  # Stop rightward movement
                elif min_overlap == bottom_overlap and player.vy < 0:
                    # Bottom collision when moving upward
                    player.y = obstacle_rect.bottom + player.radius
                    player.vy = 0  # Stop upward movement
                
                return True
                
        return False
    
    def draw(self, screen, camera=None):
        """Draw the obstacle on the screen.
        
        Args:
            screen: pygame surface to draw on
            camera: optional camera to apply transformations
        """
        # Get drawing position
        x, y = self.x, self.y
        width, height = self.width, self.height
        
        # Apply camera transformation if available
        if camera:
            rect = pygame.Rect(x - width/2, y - height/2, width, height)
            transformed_rect = camera.apply(rect)
            x, y = transformed_rect.centerx, transformed_rect.centery
            width, height = transformed_rect.width, transformed_rect.height
        
        # Draw based on obstacle type
        if self.obstacle_type == "static":
            self._draw_static(screen, x, y, width, height)
        elif self.obstacle_type == "moving":
            self._draw_moving(screen, x, y, width, height)
        elif self.obstacle_type == "rotating":
            self._draw_rotating(screen, x, y, camera)
        elif self.obstacle_type == "damaging":
            self._draw_damaging(screen, x, y, width, height)
        elif self.obstacle_type == "bouncing":
            self._draw_bouncing(screen, x, y, width, height)
    
    def _draw_static(self, screen, x, y, width, height):
        """Draw a static obstacle."""
        rect = pygame.Rect(x - width/2, y - height/2, width, height)
        pygame.draw.rect(screen, self.color, rect)
        pygame.draw.rect(screen, self.outline_color, rect, 2)
    
    def _draw_moving(self, screen, x, y, width, height):
        """Draw a moving obstacle."""
        rect = pygame.Rect(x - width/2, y - height/2, width, height)
        pygame.draw.rect(screen, self.color, rect)
        
        # Add motion indicators
        if self.movement_direction == 'horizontal':
            # Draw horizontal arrows
            arrow_length = min(width/4, 10)
            for offset in [-width/4, width/4]:
                pygame.draw.line(
                    screen, WHITE,
                    (x + offset - arrow_length, y),
                    (x + offset + arrow_length, y),
                    2
                )
                # Arrowhead
                pygame.draw.line(
                    screen, WHITE,
                    (x + offset + arrow_length, y),
                    (x + offset + arrow_length - 4, y - 4),
                    2
                )
                pygame.draw.line(
                    screen, WHITE,
                    (x + offset + arrow_length, y),
                    (x + offset + arrow_length - 4, y + 4),
                    2
                )
        elif self.movement_direction == 'vertical':
            # Draw vertical arrows
            arrow_length = min(height/4, 10)
            for offset in [-height/4, height/4]:
                pygame.draw.line(
                    screen, WHITE,
                    (x, y + offset - arrow_length),
                    (x, y + offset + arrow_length),
                    2
                )
                # Arrowhead
                pygame.draw.line(
                    screen, WHITE,
                    (x, y + offset + arrow_length),
                    (x - 4, y + offset + arrow_length - 4),
                    2
                )
                pygame.draw.line(
                    screen, WHITE,
                    (x, y + offset + arrow_length),
                    (x + 4, y + offset + arrow_length - 4),
                    2
                )
        
        # Outline
        pygame.draw.rect(screen, self.outline_color, rect, 2)
    
    def _draw_rotating(self, screen, x, y, camera):
        """Draw a rotating obstacle."""
        # Get scaled radius for camera
        radius = self.radius
        if camera:
            radius *= camera.zoom_level
        
        # Render the rotating shape
        angle_rad = math.radians(self.rotation)
        
        points = []
        for px, py in self.points[:-1]:  # Exclude center point for outlier
            # Rotate point
            rx = px * math.cos(angle_rad) - py * math.sin(angle_rad)
            ry = px * math.sin(angle_rad) + py * math.cos(angle_rad)
            # Scale for camera
            if camera:
                rx *= camera.zoom_level
                ry *= camera.zoom_level
            # Add obstacle position
            points.append((x + rx, y + ry))
        
        # Draw the shape
        if len(points) >= 3:
            # Draw filled shape
            pygame.draw.polygon(screen, self.color, points)
            
            # Draw outline
            pygame.draw.polygon(screen, self.outline_color, points, 2)
            
            # Draw center point
            pygame.draw.circle(screen, self.outline_color, (int(x), int(y)), 3)
            
            # Connect points to center
            for px, py in points:
                pygame.draw.line(screen, self.outline_color, (int(x), int(y)), (int(px), int(py)), 2)
    
    def _draw_damaging(self, screen, x, y, width, height):
        """Draw a damaging obstacle."""
        # Base rectangle
        rect = pygame.Rect(x - width/2, y - height/2, width, height)
        pygame.draw.rect(screen, self.color, rect)
        pygame.draw.rect(screen, self.outline_color, rect, 2)
        
        # Add spikes
        if self.is_spiky:
            spike_length = min(self.spike_length, width/4)
            if width > height:
                # Horizontal orientation - spikes on top and bottom
                for i in range(self.num_spikes):
                    # Top spikes
                    spike_x = x - width/2 + (i + 0.5) * width / self.num_spikes
                    pygame.draw.line(
                        screen, self.outline_color,
                        (spike_x, y - height/2),
                        (spike_x, y - height/2 - spike_length),
                        2
                    )
                    
                    # Bottom spikes
                    pygame.draw.line(
                        screen, self.outline_color,
                        (spike_x, y + height/2),
                        (spike_x, y + height/2 + spike_length),
                        2
                    )
            else:
                # Vertical orientation - spikes on left and right
                for i in range(self.num_spikes):
                    # Left spikes
                    spike_y = y - height/2 + (i + 0.5) * height / self.num_spikes
                    pygame.draw.line(
                        screen, self.outline_color,
                        (x - width/2, spike_y),
                        (x - width/2 - spike_length, spike_y),
                        2
                    )
                    
                    # Right spikes
                    pygame.draw.line(
                        screen, self.outline_color,
                        (x + width/2, spike_y),
                        (x + width/2 + spike_length, spike_y),
                        2
                    )
        
        # Add warning symbol
        warn_size = min(width, height) / 3
        pygame.draw.polygon(
            screen, YELLOW,
            [
                (x, y - warn_size),
                (x + warn_size * 0.866, y + warn_size/2),
                (x - warn_size * 0.866, y + warn_size/2)
            ]
        )
        pygame.draw.polygon(
            screen, BLACK,
            [
                (x, y - warn_size),
                (x + warn_size * 0.866, y + warn_size/2),
                (x - warn_size * 0.866, y + warn_size/2)
            ],
            2
        )
        pygame.draw.line(
            screen, BLACK,
            (x, y - warn_size/4),
            (x, y + warn_size/4),
            2
        )
        pygame.draw.circle(
            screen, BLACK,
            (int(x), int(y + warn_size/2.5)),
            2
        )
    
    def _draw_bouncing(self, screen, x, y, width, height):
        """Draw a bouncing obstacle."""
        # Base rectangle
        rect = pygame.Rect(x - width/2, y - height/2, width, height)
        pygame.draw.rect(screen, self.color, rect)
        
        # Add bounce indicators - springs or arrows
        indicator_width = width * 0.7
        indicator_height = height * 0.3
        
        # Draw springs
        spring_segments = 4
        segment_width = indicator_width / spring_segments
        
        for i in range(spring_segments):
            offset = i * segment_width
            y_offset = 0
            if i % 2 == 0:
                y_offset = indicator_height / 2
            
            spring_x = x - indicator_width/2 + offset
            pygame.draw.line(
                screen, WHITE,
                (spring_x, y),
                (spring_x + segment_width, y - y_offset),
                2
            )
        
        # Up arrows
        arrow_size = min(width/6, 8)
        pygame.draw.line(
            screen, WHITE,
            (x, y - indicator_height/2),
            (x, y - indicator_height),
            2
        )
        pygame.draw.line(
            screen, WHITE,
            (x, y - indicator_height),
            (x - arrow_size/2, y - indicator_height + arrow_size),
            2
        )
        pygame.draw.line(
            screen, WHITE,
            (x, y - indicator_height),
            (x + arrow_size/2, y - indicator_height + arrow_size),
            2
        )
        
        # Outline
        pygame.draw.rect(screen, self.outline_color, rect, 2)