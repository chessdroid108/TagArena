"""
Power-up module for the Tag Game.
Defines the Power-up class with custom behaviors and animations.
"""
import pygame
import random
import math
from constants import *

class PowerUp:
    def __init__(self, position, powerup_type):
        """
        Initialize a power-up with position and type.
        
        Args:
            position: (x, y) tuple for the center of the power-up
            powerup_type: type of power-up ('speed', 'shield', etc.)
        """
        self.x, self.y = position
        self.type = powerup_type
        self.radius = POWERUP_RADIUS
        self.color = POWERUP_COLORS[powerup_type]
        self.bob_offset = 0
        self.bob_speed = random.uniform(0.05, 0.1)
        self.bob_amount = random.uniform(5, 8)
        self.rotation = 0
        self.rotation_speed = random.uniform(0.5, 2.0)
        
        # Despawn timer - power-ups disappear after a while if not collected
        self.lifetime = POWERUP_DESPAWN_TIME
        self.flashing = False  # Will start flashing when about to disappear
        
        # Glow effects
        self.glow_intensity = random.uniform(0.7, 1.0)
        self.glow_direction = 0.02  # How fast the glow pulses
        
        # Collision rectangle for interaction detection
        self.rect = pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )
        
    def update(self, dt):
        """Update power-up animation and lifetime."""
        # Convert dt to seconds for animation and lifetime
        dt_seconds = dt if dt < 1 else dt / 1000
        
        # Update lifetime and check if should start flashing
        self.lifetime -= dt_seconds
        if self.lifetime <= 2.0 and not self.flashing:
            self.flashing = True
        
        # Bobbing effect - power-ups float up and down
        self.bob_offset = math.sin(pygame.time.get_ticks() * self.bob_speed) * self.bob_amount
        
        # Rotation for spin effect
        self.rotation += self.rotation_speed * dt_seconds * 60  # Scale by 60 for consistent rotation at different framerates
        
        # Update glow intensity (pulsing effect)
        self.glow_intensity += self.glow_direction
        if self.glow_intensity >= 1.0:
            self.glow_intensity = 1.0
            self.glow_direction = -abs(self.glow_direction)
        elif self.glow_intensity <= 0.6:
            self.glow_intensity = 0.6
            self.glow_direction = abs(self.glow_direction)
        
        # Update the collision rectangle
        self.rect.center = (int(self.x), int(self.y + self.bob_offset))
        
        # Return True if the powerup should be removed
        return self.lifetime <= 0
        
    def draw(self, screen, camera=None):
        """Draw the power-up on the screen."""
        # Base position with bob effect
        x, y = int(self.x), int(self.y + self.bob_offset)
        
        # Apply camera transformations if provided
        if camera:
            x, y = camera.apply_pos((x, y))
            draw_radius = self.radius * camera.zoom_level
        else:
            draw_radius = self.radius
        
        # Skip drawing every few frames if the powerup is about to expire (flashing effect)
        if self.flashing and pygame.time.get_ticks() % 300 < 150:
            # Just draw an outline when flashing
            pygame.draw.circle(screen, WHITE, (x, y), self.radius + 1, 2)
            return
        
        # Create a lighter color for the highlight/glow
        highlight_color = self.get_highlight_color()
        
        # Calculate rotation values for rotating elements
        sin_rot = math.sin(math.radians(self.rotation))
        cos_rot = math.cos(math.radians(self.rotation))
        
        # Draw enhanced outer glow
        for i in range(2):
            glow_radius = self.radius * (1.2 + i*0.15) * self.glow_intensity
            glow_alpha = 100 - (i * 40)  # Decreasing alpha for outer rings
            glow_surface = pygame.Surface((int(glow_radius*2), int(glow_radius*2)), pygame.SRCALPHA)
            
            # Create a gradient for the glow
            pygame.draw.circle(
                glow_surface, 
                (*self.color, glow_alpha), 
                (int(glow_radius), int(glow_radius)), 
                int(glow_radius)
            )
            screen.blit(
                glow_surface, 
                (x - int(glow_radius), y - int(glow_radius)), 
                special_flags=pygame.BLEND_ALPHA_SDL2
            )
        
        # Draw the base circle
        pygame.draw.circle(screen, self.color, (x, y), self.radius)
        
        # Draw a highlight on top for 3D effect
        highlight_pos = (x - int(self.radius*0.3), y - int(self.radius*0.3))
        small_highlight = pygame.Surface((int(self.radius*0.5), int(self.radius*0.5)), pygame.SRCALPHA)
        pygame.draw.circle(small_highlight, (255, 255, 255, 120), 
                          (int(self.radius*0.25), int(self.radius*0.25)), 
                          int(self.radius*0.25))
        screen.blit(small_highlight, highlight_pos)
        
        # Draw different visual effects based on power-up type
        if self.type == 'speed':
            # Speed power-up: draw lightning bolt
            bolt_points = [
                (x - self.radius * 0.4, y - self.radius * 0.5),
                (x, y - self.radius * 0.1),
                (x - self.radius * 0.2, y),
                (x + self.radius * 0.4, y + self.radius * 0.5),
                (x, y + self.radius * 0.1),
                (x + self.radius * 0.2, y)
            ]
            # Rotate the bolt points
            rotated_points = []
            for px, py in bolt_points:
                # Translate to origin
                tx, ty = px - x, py - y
                # Rotate
                rx = tx * cos_rot - ty * sin_rot
                ry = tx * sin_rot + ty * cos_rot
                # Translate back
                rotated_points.append((rx + x, ry + y))
            
            pygame.draw.polygon(screen, highlight_color, rotated_points)
            
        elif self.type == 'shield':
            # Shield power-up: draw circular shield with rotating arcs
            pygame.draw.circle(screen, highlight_color, (x, y), int(self.radius * 0.7), 2)
            
            # Add rotating arcs around the shield
            for i in range(3):
                angle_offset = self.rotation * 0.5 + (i * 120)
                start_angle = math.radians(angle_offset)
                end_angle = math.radians(angle_offset + 60)
                
                # Calculate arc points (approximating with lines)
                arc_radius = self.radius * 0.9
                arc_points = []
                num_points = 10
                for j in range(num_points):
                    angle = start_angle + (end_angle - start_angle) * j / (num_points - 1)
                    arc_x = x + arc_radius * math.cos(angle)
                    arc_y = y + arc_radius * math.sin(angle)
                    arc_points.append((arc_x, arc_y))
                
                if len(arc_points) >= 2:
                    pygame.draw.lines(screen, highlight_color, False, arc_points, 2)
            
        elif self.type == 'super_jump':
            # Super jump power-up: draw upward arrow with trail
            # Main arrow
            arrow_points = [
                (x - self.radius * 0.4, y + self.radius * 0.3),
                (x, y - self.radius * 0.5),
                (x + self.radius * 0.4, y + self.radius * 0.3)
            ]
            pygame.draw.polygon(screen, highlight_color, arrow_points)
            
            # Add some trailing particles below the arrow
            for i in range(3):
                trail_y_offset = 0.4 + (i * 0.2)
                particle_radius = self.radius * 0.15 * (3 - i) / 3
                trail_x = x + math.sin(pygame.time.get_ticks() * 0.01 + i) * self.radius * 0.2
                trail_y = y + self.radius * trail_y_offset
                pygame.draw.circle(screen, highlight_color, (int(trail_x), int(trail_y)), int(particle_radius))
            
        elif self.type == 'invisible':
            # Invisibility power-up: draw enhanced ghost-like shape
            ghost_y_offset = math.sin(pygame.time.get_ticks() * 0.003) * self.radius * 0.1
            ghost_points = [
                (x - self.radius * 0.4, y - self.radius * 0.3 + ghost_y_offset),
                (x - self.radius * 0.4, y + self.radius * 0.1 + ghost_y_offset),
                (x - self.radius * 0.2, y + self.radius * 0.3 + ghost_y_offset),
                (x, y + self.radius * 0.1 + ghost_y_offset),
                (x + self.radius * 0.2, y + self.radius * 0.3 + ghost_y_offset),
                (x + self.radius * 0.4, y + self.radius * 0.1 + ghost_y_offset),
                (x + self.radius * 0.4, y - self.radius * 0.3 + ghost_y_offset)
            ]
            pygame.draw.polygon(screen, highlight_color, ghost_points)
            
            # Add eyes
            eye_size = self.radius * 0.1
            pygame.draw.circle(screen, WHITE, 
                              (int(x - self.radius * 0.2), int(y - self.radius * 0.1 + ghost_y_offset)), 
                              int(eye_size))
            pygame.draw.circle(screen, WHITE, 
                              (int(x + self.radius * 0.2), int(y - self.radius * 0.1 + ghost_y_offset)), 
                              int(eye_size))
            
        elif self.type == 'freeze':
            # Freeze power-up: draw enhanced snowflake
            for i in range(6):
                angle = i * math.pi / 3 + math.radians(self.rotation * 0.5)
                # Main lines
                x1 = x + self.radius * 0.7 * math.cos(angle)
                y1 = y + self.radius * 0.7 * math.sin(angle)
                pygame.draw.line(screen, highlight_color, (int(x), int(y)), (int(x1), int(y1)), 2)
                
                # Add crystal branches to each line
                branch_angle1 = angle + math.pi / 6
                branch_angle2 = angle - math.pi / 6
                branch_length = self.radius * 0.3
                
                branch_x1 = x1 - branch_length * math.cos(branch_angle1)
                branch_y1 = y1 - branch_length * math.sin(branch_angle1)
                branch_x2 = x1 - branch_length * math.cos(branch_angle2)
                branch_y2 = y1 - branch_length * math.sin(branch_angle2)
                
                pygame.draw.line(screen, highlight_color, (int(x1), int(y1)), (int(branch_x1), int(branch_y1)), 1)
                pygame.draw.line(screen, highlight_color, (int(x1), int(y1)), (int(branch_x2), int(branch_y2)), 1)
        
        # Draw pulsing outline
        pulse = (math.sin(pygame.time.get_ticks() * 0.006) * 0.2) + 0.8  # Value between 0.6 and 1.0
        pygame.draw.circle(
            screen, 
            highlight_color, 
            (x, y), 
            int(self.radius * pulse), 
            2
        )
        
    def get_highlight_color(self):
        """Generate a lighter version of the power-up's color for highlights."""
        r = min(255, self.color[0] + 100)
        g = min(255, self.color[1] + 100)
        b = min(255, self.color[2] + 100)
        return (r, g, b)
        
    def get_rect(self):
        """Get the power-up's collision rectangle."""
        # Update rectangle position to current power-up position with bob offset
        self.rect.center = (int(self.x), int(self.y + self.bob_offset))
        return self.rect