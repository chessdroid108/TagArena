"""
Tutorial module for the Tag Game.
Provides step-by-step interactive instructions with animations.
"""

import pygame
import random
import math
import time
from constants import *
from utils import draw_text

class Tutorial:
    def __init__(self, game):
        """
        Initialize the tutorial system.
        
        Args:
            game: Reference to the main game object
        """
        self.game = game
        self.current_step = 0
        self.steps = []
        self.particles = []
        self.timer = 0
        self.active = False
        self.target_reached = False
        self.highlight_targets = []
        self.arrow_targets = []
        self.messages = []
        self.arrow_bounce = 0
        
        # Create tutorial sequence
        self.create_tutorial_steps()
    
    def create_tutorial_steps(self):
        """Create the sequence of tutorial steps."""
        self.steps = [
            {
                'title': "Welcome to Tag Game!",
                'message': "Let's learn how to play. Press SPACE to continue.",
                'highlight': None,
                'arrow': None,
                'action': None,
                'auto_advance': False
            },
            {
                'title': "Player Controls",
                'message': "Use your movement keys to move your character.",
                'highlight': 'player1',
                'arrow': ('player1', 50),
                'action': None,
                'auto_advance': False
            },
            {
                'title': "Moving Around",
                'message': "Player 1: Use WASD keys to move. Try moving left and right.",
                'highlight': 'player1',
                'arrow': ('player1', 50),
                'action': 'move_p1',
                'auto_advance': True
            },
            {
                'title': "Jumping",
                'message': "Press W to jump. Try jumping up to the platforms.",
                'highlight': 'platform',
                'arrow': ('platform', 80),
                'action': 'jump_p1',
                'auto_advance': True
            },
            {
                'title': "Special Platforms",
                'message': "Different platforms have special effects. Try the green one for higher jumps!",
                'highlight': 'jump_platform',
                'arrow': ('jump_platform', 50),
                'action': 'use_special_platform',
                'auto_advance': True
            },
            {
                'title': "Pass-Through Platforms",
                'message': "Press S while on a cyan platform to drop through it.",
                'highlight': 'passthrough_platform',
                'arrow': ('passthrough_platform', 50),
                'action': 'use_passthrough',
                'auto_advance': True
            },
            {
                'title': "Tagging",
                'message': "The tagger (red outline) tries to catch other players. Collide with them to tag!",
                'highlight': 'player2',
                'arrow': ('player2', 50),
                'action': 'tag_player',
                'auto_advance': True
            },
            {
                'title': "Power-ups",
                'message': "Power-ups give special abilities. Collect them when they appear!",
                'highlight': 'powerup',
                'arrow': ('powerup', 40),
                'action': 'collect_powerup',
                'auto_advance': True
            },
            {
                'title': "Winning the Game",
                'message': "First player to score 5 points wins! Score by tagging others.",
                'highlight': 'score',
                'arrow': ('score', 30),
                'action': None,
                'auto_advance': False
            },
            {
                'title': "Now You're Ready!",
                'message': "Press SPACE to start playing the real game, or ESC to quit the tutorial.",
                'highlight': None,
                'arrow': None,
                'action': None,
                'auto_advance': False
            }
        ]
    
    def start(self):
        """Start the tutorial from the beginning."""
        self.current_step = 0
        self.active = True
        self.target_reached = False
        self.timer = 0
        self.particles = []
        
        # Spawn a powerup for the powerup collection step
        if not self.game.powerups:
            self.game.spawn_powerups()
    
    def next_step(self):
        """Advance to the next step of the tutorial."""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.target_reached = False
            self.timer = 0
            
            # Create success particles for transition
            self.create_success_particles()
            
            # Final step - return to game
            if self.current_step == len(self.steps) - 1:
                # Prepare to end tutorial on next space
                pass
        else:
            # Tutorial complete
            self.complete()
    
    def complete(self):
        """Complete the tutorial and return to regular gameplay."""
        self.active = False
        self.game.state = STATE_PLAYING
    
    def update(self, dt):
        """
        Update the tutorial state and animations.
        
        Args:
            dt: Time delta in seconds
        """
        if not self.active:
            return
        
        # Update timer
        self.timer += dt
        
        # Update arrow bounce animation
        self.arrow_bounce = math.sin(self.timer * 5) * 5
        
        # Check for auto-advance conditions
        current_step = self.steps[self.current_step]
        
        if current_step['auto_advance'] and self.target_reached:
            # Auto-advance after a short delay
            if self.timer > 1.0:  # 1 second delay after completing action
                self.next_step()
        
        # Check for specific actions that mark step completion
        action = current_step.get('action')
        if action and not self.target_reached:
            self.check_target_reached(action)
        
        # Update particles
        self.update_particles(dt)
    
    def check_target_reached(self, target_type):
        """
        Check if the player has reached the specified target.
        
        Args:
            target_type: Type of target to check for
            
        Returns:
            bool: True if target reached, False otherwise
        """
        # Basic movement check
        if target_type == 'move_p1':
            # Check if player has moved left or right
            player = self.game.player1
            if abs(player.x - player.starting_x) > 50:
                self.target_reached = True
                return True
        
        # Jump check
        elif target_type == 'jump_p1':
            # Check if player has jumped
            player = self.game.player1
            if player.y < player.starting_y - 50:
                self.target_reached = True
                return True
        
        # Special platform check
        elif target_type == 'use_special_platform':
            # Check if player is on a jump platform
            player = self.game.player1
            if hasattr(player, 'current_platform') and player.current_platform:
                if player.current_platform.platform_type == 'jump':
                    self.target_reached = True
                    return True
        
        # Passthrough platform check
        elif target_type == 'use_passthrough':
            # Check if player is passing through a platform
            player = self.game.player1
            if player.passing_through:
                self.target_reached = True
                return True
        
        # Tag player check
        elif target_type == 'tag_player':
            # Check if a tag has occurred
            if self.game.player1.is_tagger != self.game.player1.was_tagger_at_start:
                self.target_reached = True
                return True
        
        # Powerup collection check
        elif target_type == 'collect_powerup':
            # Check if a powerup has been collected
            player = self.game.player1
            if player.active_powerups:
                self.target_reached = True
                return True
        
        return False
    
    def handle_event(self, event):
        """
        Handle pygame events for tutorial interaction.
        
        Args:
            event: pygame event to process
            
        Returns:
            bool: True if event was handled by tutorial, False otherwise
        """
        if not self.active:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # If step doesn't require specific action, advance on space
                current_step = self.steps[self.current_step]
                if not current_step['action'] or self.target_reached:
                    self.next_step()
                    return True
        
        return False
    
    def create_success_particles(self):
        """Create particles for successful action completion."""
        # Generate particles around the center of the screen
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        num_particles = 40
        
        for _ in range(num_particles):
            # Random position around center
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(50, 150)
            x = center_x + math.cos(angle) * distance
            y = center_y + math.sin(angle) * distance
            
            # Random particle properties
            size = random.uniform(2, 8)
            lifetime = random.uniform(0.5, 1.5)
            speed = random.uniform(50, 150)
            
            # Random color (bright colors)
            colors = [
                (255, 220, 100),  # Yellow
                (100, 255, 100),  # Green
                (100, 200, 255),  # Blue
                (255, 150, 100),  # Orange
                (200, 100, 255)   # Purple
            ]
            color = random.choice(colors)
            
            # Add particle
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'lifetime': lifetime,
                'max_lifetime': lifetime,
                'color': color
            })
    
    def update_particles(self, dt):
        """Update particle effects."""
        # Update and remove expired particles
        for i in range(len(self.particles) - 1, -1, -1):
            particle = self.particles[i]
            
            # Update position
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            
            # Update lifetime
            particle['lifetime'] -= dt
            
            # Remove expired particles
            if particle['lifetime'] <= 0:
                self.particles.pop(i)
    
    def find_highlight_target(self, target_type):
        """
        Find the rectangle to highlight based on target type.
        
        Args:
            target_type: Type of object to highlight
            
        Returns:
            pygame.Rect or None: Rectangle to highlight
        """
        if not target_type:
            return None
        
        if target_type == 'player1':
            return self.game.player1.get_rect()
        
        elif target_type == 'player2':
            return self.game.player2.get_rect()
        
        elif target_type == 'platform':
            # Find the closest platform above the player
            player = self.game.player1
            closest_platform = None
            min_distance = float('inf')
            
            for platform in self.game.platforms:
                platform_rect = platform.get_rect()
                if platform_rect.bottom < player.y:  # Platform is above player
                    distance = player.y - platform_rect.bottom
                    if distance < min_distance:
                        min_distance = distance
                        closest_platform = platform
            
            if closest_platform:
                return closest_platform.get_rect()
        
        elif target_type == 'jump_platform':
            # Find the closest jump platform
            for platform in self.game.platforms:
                if platform.platform_type == 'jump':
                    return platform.get_rect()
        
        elif target_type == 'passthrough_platform':
            # Find the closest passthrough platform
            for platform in self.game.platforms:
                if platform.platform_type == 'passthrough':
                    return platform.get_rect()
        
        elif target_type == 'powerup':
            # Find the first powerup
            if self.game.powerups:
                return self.game.powerups[0].get_rect()
        
        elif target_type == 'score':
            # Create a rect around the score display area
            return pygame.Rect(10, 10, 120, 40)
        
        return None
    
    def find_arrow_position(self, target_type, offset):
        """
        Calculate the position for a pointing arrow.
        
        Args:
            target_type: Type of object to point at
            offset: Distance offset from the target
            
        Returns:
            tuple or None: (x, y, angle) for the arrow
        """
        if not target_type:
            return None
        
        target_rect = self.find_highlight_target(target_type)
        if not target_rect:
            return None
        
        # Calculate center of target
        target_x = target_rect.centerx
        target_y = target_rect.centery
        
        # Position arrow above target
        arrow_x = target_x
        arrow_y = target_y - offset - self.arrow_bounce  # Add bounce animation
        angle = 90  # Pointing downward
        
        return (arrow_x, arrow_y, angle)
    
    def draw(self, screen, camera=None):
        """
        Draw the tutorial overlay.
        
        Args:
            screen: Screen surface to draw on
            camera: Optional camera to transform positions
        """
        if not self.active:
            return
        
        # Get current step
        current_step = self.steps[self.current_step]
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))  # Semi-transparent dark overlay
        screen.blit(overlay, (0, 0))
        
        # Draw highlighted area if specified
        highlight_target = current_step.get('highlight')
        if highlight_target:
            target_rect = self.find_highlight_target(highlight_target)
            if target_rect and camera:
                # Transform rect with camera
                target_rect = camera.apply(target_rect)
                
                # Draw highlight around target
                pygame.draw.rect(screen, (255, 255, 100, 180), target_rect.inflate(20, 20), 3, border_radius=5)
        
        # Draw instruction arrow
        arrow_target = current_step.get('arrow')
        if arrow_target:
            target_type, offset = arrow_target
            arrow_pos = self.find_arrow_position(target_type, offset)
            
            if arrow_pos and camera:
                arrow_x, arrow_y, angle = arrow_pos
                transformed_pos = camera.apply_pos((arrow_x, arrow_y))
                
                # Draw a bouncing arrow
                arrow_size = 20
                arrow_color = (255, 255, 100)
                
                # Draw triangle arrow
                arrow_points = [
                    (transformed_pos[0], transformed_pos[1] + arrow_size),
                    (transformed_pos[0] - arrow_size/2, transformed_pos[1]),
                    (transformed_pos[0] + arrow_size/2, transformed_pos[1])
                ]
                pygame.draw.polygon(screen, arrow_color, arrow_points)
        
        # Draw info panel
        panel_width = 600
        panel_height = 150
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = SCREEN_HEIGHT - panel_height - 20
        
        # Draw panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, (40, 40, 60, 220), panel_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 100, 200), panel_rect, 3, border_radius=10)
        
        # Draw title
        title_y = panel_y + 30
        draw_text(screen, current_step['title'], 30, SCREEN_WIDTH // 2, title_y, YELLOW)
        
        # Draw message
        message_y = panel_y + 80
        draw_text(screen, current_step['message'], 20, SCREEN_WIDTH // 2, message_y, WHITE)
        
        # Draw "press space" indicator if not auto-advancing
        if not current_step['auto_advance']:
            prompt_y = panel_y + panel_height - 25
            draw_text(screen, "Press SPACE to continue...", 16, SCREEN_WIDTH // 2, prompt_y, LIGHT_GRAY)
        
        # Draw particles
        for particle in self.particles:
            # Calculate particle opacity based on remaining lifetime
            alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
            size = particle['size']
            color = particle['color']
            
            # Create surface for particle
            particle_surf = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
            particle_color_with_alpha = (*color, alpha)
            pygame.draw.circle(particle_surf, particle_color_with_alpha, (int(size), int(size)), int(size))
            
            # Blit particle to screen
            screen.blit(particle_surf, (int(particle['x'] - size), int(particle['y'] - size)))