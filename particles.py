"""
Particle system for the Tag Game.
Provides visual effects for player movement, jumping, and other actions.
"""

import pygame
import random
import math
from constants import *

class Particle:
    def __init__(self, x, y, color, size=3, lifetime=1.0, velocity=(0, 0), 
                 gravity=0.1, fade=True, shape="circle"):
        """Initialize a particle.
        
        Args:
            x, y: Initial particle position
            color: RGB color tuple
            size: Radius or size in pixels
            lifetime: Time in seconds before the particle disappears
            velocity: Initial (vx, vy) velocity
            gravity: Gravitational acceleration
            fade: Whether the particle should fade out over time
            shape: "circle", "square", "trail", etc.
        """
        self.x = x
        self.y = y
        self.color = color
        self.start_color = color
        self.size = size
        self.start_size = size
        self.lifetime = lifetime
        self.start_lifetime = lifetime
        self.vx, self.vy = velocity
        self.gravity = gravity
        self.fade = fade
        self.shape = shape
        self.drag = random.uniform(0.92, 0.99)  # Air resistance
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-5, 5)
    
    def update(self, dt):
        """Update particle position and properties.
        
        Args:
            dt: Time delta in seconds
            
        Returns:
            False if the particle should be removed, True otherwise
        """
        # Update position
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        
        # Apply gravity
        self.vy += self.gravity * dt * 60
        
        # Apply drag
        self.vx *= self.drag
        self.vy *= self.drag
        
        # Update rotation for non-circular particles
        self.rotation += self.rotation_speed * dt * 60
        
        # Reduce lifetime
        self.lifetime -= dt
        
        # Fade out if needed
        if self.fade:
            fade_factor = max(0, self.lifetime / self.start_lifetime)
            # Interpolate color from start_color to black
            r = int(self.start_color[0] * fade_factor)
            g = int(self.start_color[1] * fade_factor)
            b = int(self.start_color[2] * fade_factor)
            self.color = (r, g, b)
            
            # Also shrink the particle
            self.size = self.start_size * fade_factor
        
        return self.lifetime > 0
    
    def draw(self, screen, camera=None):
        """Draw the particle on the screen.
        
        Args:
            screen: pygame surface to draw on
            camera: Optional camera to apply transformations
        """
        pos = (self.x, self.y)
        if camera:
            pos = camera.apply_pos(pos)
            draw_size = max(1, self.size * camera.zoom_level)
        else:
            draw_size = max(1, self.size)
        
        # Draw based on shape
        if self.shape == "circle":
            pygame.draw.circle(screen, self.color, (int(pos[0]), int(pos[1])), int(draw_size))
        elif self.shape == "square":
            rect = pygame.Rect(
                int(pos[0] - draw_size/2), 
                int(pos[1] - draw_size/2),
                int(draw_size), 
                int(draw_size)
            )
            pygame.draw.rect(screen, self.color, rect)
        elif self.shape == "star":
            points = []
            for i in range(5):
                angle = math.radians(self.rotation + i * 72)
                points.append((
                    pos[0] + math.cos(angle) * draw_size,
                    pos[1] + math.sin(angle) * draw_size
                ))
                angle = math.radians(self.rotation + i * 72 + 36)
                inner_radius = draw_size * 0.4
                points.append((
                    pos[0] + math.cos(angle) * inner_radius,
                    pos[1] + math.sin(angle) * inner_radius
                ))
            pygame.draw.polygon(screen, self.color, points)
        elif self.shape == "trail":
            # Trail particles use a line from previous position to current
            prev_x = self.x - self.vx
            prev_y = self.y - self.vy
            if camera:
                prev_pos = camera.apply_pos((prev_x, prev_y))
            else:
                prev_pos = (prev_x, prev_y)
            
            pygame.draw.line(
                screen, 
                self.color, 
                (int(prev_pos[0]), int(prev_pos[1])), 
                (int(pos[0]), int(pos[1])), 
                max(1, int(draw_size))
            )

class ParticleSystem:
    def __init__(self):
        """Initialize the particle system."""
        self.particles = []
    
    def update(self, dt):
        """Update all particles in the system.
        
        Args:
            dt: Time delta in seconds
        """
        # Use a reversed loop to safely remove items during iteration
        for i in range(len(self.particles) - 1, -1, -1):
            if not self.particles[i].update(dt):
                self.particles.pop(i)
    
    def draw(self, screen, camera=None):
        """Draw all particles in the system.
        
        Args:
            screen: pygame surface to draw on
            camera: Optional camera to apply transformations
        """
        for particle in self.particles:
            particle.draw(screen, camera)
    
    def add_particle(self, particle):
        """Add a particle to the system.
        
        Args:
            particle: The particle to add
        """
        self.particles.append(particle)
    
    def create_particles(self, count, x, y, color, size_range=(2, 4), 
                         lifetime_range=(0.5, 1.5), speed_range=(1, 3), 
                         direction_range=(0, 360), gravity=0.1, fade=True, 
                         shape="circle"):
        """Create multiple particles at once.
        
        Args:
            count: Number of particles to create
            x, y: Position to create particles at
            color: Base color (will be varied slightly)
            size_range: (min, max) size in pixels
            lifetime_range: (min, max) lifetime in seconds
            speed_range: (min, max) initial speed
            direction_range: (min, max) direction in degrees
            gravity: Gravitational acceleration
            fade: Whether particles should fade out
            shape: Particle shape
        """
        for _ in range(count):
            # Vary color slightly
            r = min(255, max(0, color[0] + random.randint(-20, 20)))
            g = min(255, max(0, color[1] + random.randint(-20, 20)))
            b = min(255, max(0, color[2] + random.randint(-20, 20)))
            varied_color = (r, g, b)
            
            # Random size and lifetime
            size = random.uniform(size_range[0], size_range[1])
            lifetime = random.uniform(lifetime_range[0], lifetime_range[1])
            
            # Random velocity based on direction and speed
            speed = random.uniform(speed_range[0], speed_range[1])
            direction = math.radians(random.uniform(direction_range[0], direction_range[1]))
            vx = math.cos(direction) * speed
            vy = math.sin(direction) * speed
            
            # Create and add the particle
            particle = Particle(
                x, y, varied_color, size, lifetime, 
                (vx, vy), gravity, fade, shape
            )
            self.add_particle(particle)
    
    def create_explosion(self, x, y, color, count=20, size_range=(2, 5), radius=30):
        """Create an explosion effect with particles radiating outward.
        
        Args:
            x, y: Center of explosion
            color: Base color
            count: Number of particles
            size_range: (min, max) size of particles
            radius: Distance particles travel
        """
        for _ in range(count):
            # Random direction (full 360 degrees)
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(0, radius)
            speed = distance / 10
            
            # Velocity based on angle
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Vary color slightly
            r = min(255, max(0, color[0] + random.randint(-20, 20)))
            g = min(255, max(0, color[1] + random.randint(-20, 20)))
            b = min(255, max(0, color[2] + random.randint(-20, 20)))
            varied_color = (r, g, b)
            
            # Random size and lifetime
            size = random.uniform(size_range[0], size_range[1])
            lifetime = random.uniform(0.5, 1.5)
            
            # Create particle with random shape
            shape = random.choice(["circle", "square", "star"])
            particle = Particle(
                x, y, varied_color, size, lifetime, 
                (vx, vy), 0.05, True, shape
            )
            self.add_particle(particle)
    
    def create_trail(self, x, y, color, count=3, direction=None, speed_factor=1.0):
        """Create a trail effect behind a moving object.
        
        Args:
            x, y: Current position
            color: Base color
            count: Number of trail particles
            direction: Optional direction of movement (degrees)
            speed_factor: Multiplier for particle speed
        """
        # Use trail particles for a smoother motion blur effect
        for _ in range(count):
            # Random offset
            offset_x = random.uniform(-3, 3)
            offset_y = random.uniform(-3, 3)
            
            # Base velocity (opposite of movement direction)
            vx, vy = 0, 0
            if direction is not None:
                angle = math.radians(direction + 180)  # Opposite direction
                speed = random.uniform(1, 3) * speed_factor
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
            
            # Slightly transparent color
            alpha = random.uniform(0.3, 0.7)
            r = int(color[0] * alpha)
            g = int(color[1] * alpha)
            b = int(color[2] * alpha)
            trail_color = (r, g, b)
            
            # Create and add the trail particle
            size = random.uniform(1, 3)
            lifetime = random.uniform(0.1, 0.3)
            particle = Particle(
                x + offset_x, y + offset_y, 
                trail_color, size, lifetime, 
                (vx, vy), 0, True, "trail"
            )
            self.add_particle(particle)
            
    def create_footsteps(self, x, y, color, player_direction, is_on_ground=True):
        """Create footstep particles when a player is running.
        
        Args:
            x, y: Player position (feet)
            color: Base color
            player_direction: Direction player is facing (degrees)
            is_on_ground: Whether player is on the ground
        """
        if not is_on_ground:
            return
            
        # Create dust particles around the feet
        count = random.randint(1, 3)
        dust_color = (150, 150, 150)  # Gray dust
        
        # Spread more behind the player
        offset_angle = (player_direction + 180) % 360
        
        for _ in range(count):
            # Random position around feet with bias behind player
            angle = math.radians(random.uniform(offset_angle - 90, offset_angle + 90))
            distance = random.uniform(2, 8)
            pos_x = x + math.cos(angle) * distance
            pos_y = y + 2  # Slightly above ground
            
            # Small dust particle with upward motion
            self.create_particles(
                1, pos_x, pos_y, dust_color,
                size_range=(1, 3),
                lifetime_range=(0.2, 0.5),
                speed_range=(0.5, 1.5),
                direction_range=(240, 300),  # Upward with spread
                gravity=0.01
            )