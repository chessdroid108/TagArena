"""
Player module for the Tag Game.
Defines the Player class with custom physics properties and controls.
"""

import pygame
import math
import random
from constants import *

class Player:
    def __init__(self, game, position, controls, player_id, is_tagger=False, 
                color=None, accessory=None, expression=None):
        """
        Initialize a player with position and controls.
        
        Args:
            game: reference to the main game object
            position: (x, y) tuple for initial position
            controls: dict with 'left', 'right', 'jump', 'down' keys
            player_id: 1 to 4 to identify the player
            is_tagger: bool indicating if this player is the tagger
            color: RGB color tuple for the player blob (default based on player_id)
            accessory: String describing the accessory to use ('bow', 'hat', etc.)
            expression: String describing the facial expression to use 
        """
        self.game = game
        self.player_id = player_id
        self.is_tagger = is_tagger
        self.controls = controls
        
        # Physics properties
        self.x, self.y = position  # Position
        self.starting_x, self.starting_y = position  # Store starting position for tutorial tracking
        self.was_tagger_at_start = is_tagger  # Store initial tagger state for tutorial tracking
        self.vx, self.vy = 0, 0    # Velocity
        self.ax, self.ay = 0, 0    # Acceleration
        self.mass = PLAYER_MASS
        
        # Properties to match the property access pattern from our custom physics system
        self.position = (self.x, self.y)
        self.velocity = (self.vx, self.vy)
        
        # Movement states
        self.can_jump = False
        self.jump_pressed = False  # Track jump button state
        self.jump_released = True  # To prevent holding jump
        self.move_direction = 0    # -1=left, 0=none, 1=right
        
        # Double jump attributes
        self.jumps_left = 2  # Start with ability to double jump
        self.jump_key_was_pressed = False  # For tracking key press/release
        
        # Rectangle and radius for collision detection
        self.radius = PLAYER_RADIUS
        self.rect = pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )
        
        # Set default customization values if not provided
        if color is None:
            # Use default colors based on player_id
            if player_id == 1:
                self.color = (220, 60, 80)  # Red
            elif player_id == 2:
                self.color = (60, 140, 220)  # Blue
            elif player_id == 3:
                self.color = (60, 180, 80)  # Green
            elif player_id == 4:
                self.color = (200, 120, 220)  # Purple
        else:
            self.color = color
            
        if accessory is None:
            # Assign default accessories based on player ID
            accessories = ['bow', 'hat', 'glasses', 'crown']
            self.accessory = accessories[player_id - 1] if player_id <= len(accessories) else 'bow'
        else:
            self.accessory = accessory
        
        if expression is None:
            self.expression = 'happy'
        else:
            self.expression = expression
        
        # Movement properties
        self.speed = DEFAULT_SPEED
        self.jump_force = DEFAULT_JUMP_FORCE
        self.on_ground = False
        self.current_platform = None
        
        # Tag game properties
        self.tag_cooldown = 0
        self.score = 0
        
        # Apply tagger properties if this is the tagger
        self.update_tagger_status(is_tagger)
        
        # Track platform effects
        self.on_sticky_platform = False
        self.on_jump_platform = False
        self.on_speed_platform = False
        self.passing_through = False
        
        # Damage visualization
        self.damage_flash = 0  # Timer for red flash effect
        self.is_damaged = False  # Flag to track if player is damaged
        
        # Death and respawn
        self.death_timer = 0  # Timer for death on Sky Island floor
        self.is_dying = False  # Flag to track if player is dying
        
        # Add player to the game's player list
        if game.players is not None:
            game.players.append(self)
        
        # Blob character customization - different traits for each player
        self.blob_traits = {
            # Visual traits
            'wobble_speed': random.uniform(0.8, 1.2),
            'wobble_amount': random.uniform(0.08, 0.12),
            'eye_size': random.uniform(0.18, 0.22),
            'eye_spacing': random.uniform(0.35, 0.45),
            'eye_height': random.uniform(0.18, 0.25),
            # Animation traits
            'blink_interval': random.randint(150, 300),
            'blink_counter': 0,
            'is_blinking': False,
            'blink_duration': random.randint(5, 12),
            # Movement animation
            'squish_x': 1.0,  # Width multiplier when squishing
            'squish_y': 1.0,  # Height multiplier when squishing
            'rotation': 0,    # Rotation angle for movement
            'stretch_factor': 0.0,  # Amount of stretching during movement
            'stretch_direction': 0,  # Direction of stretching
            'running_cycle': 0.0,  # Phase of running animation
            'facing_direction': 1,  # 1 = right, -1 = left
            # Jump/fall animation
            'in_air_time': 0,  # Tracks time in air for animation
            'landing_impact': 0.0  # Landing impact effect intensity
        }
        
        # Animation timers
        self.animation_time = 0
        self.was_on_ground = False
        self.footstep_timer = 0
        self.footstep_interval = 0.3  # Time between footsteps
        
    def update_tagger_status(self, is_tagger):
        """Update player properties based on tagger status."""
        # Store the original color if we're not already a tagger
        if not self.is_tagger and not hasattr(self, 'original_color'):
            self.original_color = self.color
            
        self.is_tagger = is_tagger
        
        if is_tagger:
            # Default tagger is slightly slower
            self.base_speed = DEFAULT_SPEED * TAGGER_SPEED_MULTIPLIER
            self.color = TAGGER_COLOR
        else:
            self.base_speed = DEFAULT_SPEED
            # Restore player's original color if available
            if hasattr(self, 'original_color'):
                self.color = self.original_color
            else:
                self.color = RUNNER_COLOR
            
        # Reset speed (will be modified by platform effects)
        self.speed = self.base_speed
        
        # Initialize power-up states
        if not hasattr(self, 'active_powerups'):
            self.active_powerups = {}
            self.is_frozen = False
            self.has_shield = False
            self.is_invisible = False
            self.frozen_timer = 0
        
    def toggle_tagger_property(self):
        """Toggle between different tagger property sets."""
        # Only do something if this player is the tagger
        if not self.is_tagger:
            return
            
        # Randomly change tagger properties for variety
        property_set = random.randint(1, 3)
        
        if property_set == 1:
            # Fast but light tagger
            self.base_speed = DEFAULT_SPEED * 1.2
            self.mass = PLAYER_MASS * 0.8
            self.jump_force = DEFAULT_JUMP_FORCE * 0.9
        elif property_set == 2:
            # Heavy but strong jumper
            self.base_speed = DEFAULT_SPEED * 0.8
            self.mass = PLAYER_MASS * 1.5
            self.jump_force = DEFAULT_JUMP_FORCE * 1.3
        else:
            # Balanced tagger
            self.base_speed = DEFAULT_SPEED
            self.mass = PLAYER_MASS
            self.jump_force = DEFAULT_JUMP_FORCE
            
        # Apply current platform effects to the new base speed
        self.update_speed()
            
    def update_speed(self):
        """Update speed based on current platform effects."""
        self.speed = self.base_speed
        
        if self.on_sticky_platform:
            self.speed *= STICKY_SLOWDOWN
        elif self.on_speed_platform:
            self.speed *= SPEED_BOOST
            
    def handle_input(self, keys):
        """Handle keyboard input for player movement."""
        # Reset movement direction
        self.move_direction = 0
        
        # Handle horizontal movement
        if keys[self.controls['left']]:
            self.move_direction = -1
        if keys[self.controls['right']]:
            self.move_direction = 1
            
        # Double jump logic with key press/release tracking
        jump_key_pressed = keys[self.controls['jump']]
        
        # Track when key is pressed (rising edge detection)
        jump_key_just_pressed = jump_key_pressed and not self.jump_key_was_pressed
        
        # Reset jumps when touching ground
        if self.on_ground:
            self.jumps_left = 2
        
        # Jump when key is pressed AND we have jumps left
        if jump_key_just_pressed and self.jumps_left > 0:
            # Calculate jump strength based on platform type or air jump
            jump_strength = self.jump_force
            
            # First jump gets platform bonuses, second jump is always regular
            if self.jumps_left == 2 and self.on_jump_platform:
                jump_strength *= JUMP_BOOST
            
            # Second jump (air jump) has slightly reduced strength
            if self.jumps_left == 1:
                jump_strength *= 0.8
            
            # Apply jump velocity immediately
            self.vy = -jump_strength
            
            # Consume a jump
            self.jumps_left -= 1
            
            # No longer on ground
            self.on_ground = False
            
            # Play jump sound
            from sounds import sound_manager
            sound_manager.play("jump")
            
            # Add a small horizontal boost in the direction of movement
            # This makes running jumps feel more natural
            if self.move_direction != 0:
                self.vx += self.move_direction * self.speed * 0.1
                
            # Generate jump particles
            self.generate_jump_particles()
        
        # Update key press state for next frame
        self.jump_key_was_pressed = jump_key_pressed
        
        # Handle pass-through platforms
        self.passing_through = keys[self.controls['down']]
            
    def enforce_boundaries(self):
        """Enforce level boundaries to prevent players from escaping the game area."""
        # Define the safe area with a margin equal to player radius
        margin = PLAYER_RADIUS
        min_x = margin
        max_x = LEVEL_WIDTH - margin
        min_y = margin
        max_y = LEVEL_HEIGHT - margin
        
        # Check if player is outside boundaries
        if self.x < min_x:
            # Reposition to the boundary edge
            self.x = min_x
            # Stop horizontal movement
            if self.vx < 0:
                self.vx = 0
        elif self.x > max_x:
            self.x = max_x
            if self.vx > 0:
                self.vx = 0
                
        if self.y < min_y:
            self.y = min_y
            if self.vy < 0:
                self.vy = 0
        elif self.y > max_y:
            self.y = max_y
            if self.vy > 0:
                self.vy = 0
                
        # When a player is close to the edge, create a visual indicator
        edge_margin = 100
        if (self.x < edge_margin or self.x > LEVEL_WIDTH - edge_margin or
            self.y < edge_margin or self.y > LEVEL_HEIGHT - edge_margin):
            # Create a subtle particle effect to indicate proximity to edge
            if hasattr(self.game, 'particle_system') and random.random() < 0.02:
                edge_color = (200, 200, 255)  # Light blue
                self.game.particle_system.create_particles(
                    1, self.x, self.y, edge_color,
                    size_range=(1, 3),
                    lifetime_range=(0.3, 0.7),
                    speed_range=(10, 30),
                    direction_range=(0, 360),
                    gravity=0.01,
                    fade=True,
                    shape=random.choice(["circle", "square"])
                )
                
    def get_rect(self):
        """Get the player's collision rectangle."""
        # Update rectangle position to current player position
        self.rect.center = (int(self.x), int(self.y))
        return self.rect
        
    def take_damage(self):
        """Apply damage to the player with visual effect."""
        # Skip if player already has damage flash active or has shield
        if self.damage_flash > 0 or self.has_shield:
            return False
            
        # Set damage flash timer and flag
        self.damage_flash = 0.4  # Duration of flash in seconds
        self.is_damaged = True
        
        # Generate damage particles
        if hasattr(self.game, 'particle_system'):
            self.game.particle_system.create_particles(
                15,  # Number of particles
                self.x, self.y,
                (255, 30, 30),  # Red particles for damage
                size_range=(3, 6),
                lifetime_range=(0.3, 0.8),
                speed_range=(60, 120),
                direction_range=(0, 360),  # Radiate in all directions
                gravity=0.05,
                fade=True,
                shape="circle"
            )
            
        return True
        
    def start_dying(self):
        """Start the dying process for the player."""
        # Skip if already dying
        if self.is_dying:
            return
            
        # Set dying flag and timer
        self.is_dying = True
        self.death_timer = 3.0  # 3 seconds until death
        
        # Generate more intense damage particles
        if hasattr(self.game, 'particle_system'):
            self.game.particle_system.create_particles(
                25,  # More particles for death
                self.x, self.y,
                (255, 20, 20),  # Bright red particles
                size_range=(4, 8),
                lifetime_range=(0.5, 1.2),
                speed_range=(80, 150),
                direction_range=(0, 360),  # Radiate in all directions
                gravity=0.05,
                fade=True,
                shape="circle"
            )
        
    def respawn(self):
        """Respawn the player at the top of the map."""
        # Find a safe position near the top of the map
        # Try to find a platform near the top
        top_platforms = []
        for platform in self.game.platforms:
            if platform.get_rect().top < SCREEN_HEIGHT // 3:  # Top third of screen
                top_platforms.append(platform)
                
        if top_platforms:
            # Choose a random platform from the top ones
            platform = random.choice(top_platforms)
            platform_rect = platform.get_rect()
            # Position player on top of the platform
            self.x = platform_rect.centerx
            self.y = platform_rect.top - PLAYER_RADIUS
        else:
            # If no platforms found, just place at a safe position at the top
            self.x = random.randint(100, SCREEN_WIDTH - 100)
            self.y = 100
            
        # Reset velocity
        self.vx = 0
        self.vy = 0
        
        # Reset dying state
        self.is_dying = False
        self.death_timer = 0
        
        # Apply invulnerability briefly
        self.damage_flash = 1.0  # 1 second of invulnerability
        self.is_damaged = True
        
        # Create respawn effect
        if hasattr(self.game, 'particle_system'):
            self.game.particle_system.create_explosion(
                self.x, self.y,
                (255, 255, 255),  # White particles for respawn
                count=30,
                size_range=(3, 7),
                radius=50
            )
    
    def update(self, dt):
        """Update player physics and state."""
        # Convert dt to seconds if it's in milliseconds
        dt_seconds = dt if dt < 1 else dt / 1000
        
        # Handle freeze effect - frozen players can't move
        if self.is_frozen:
            self.frozen_timer -= dt_seconds
            if self.frozen_timer <= 0:
                self.is_frozen = False
            return  # Skip physics updates if frozen
        
        # Handle dying process
        if self.is_dying:
            self.death_timer -= dt_seconds
            if self.death_timer <= 0:
                self.respawn()
            
            # Create flashing effect and particles during death countdown
            if random.random() < 0.15:  # Occasional flash
                self.damage_flash = 0.1
                self.is_damaged = True
                
            # Create occasional particles
            if random.random() < 0.1 and hasattr(self.game, 'particle_system'):
                self.game.particle_system.create_particles(
                    5,  # Fewer particles per batch but more often
                    self.x, self.y,
                    (255, random.randint(0, 100), random.randint(0, 50)),  # Red-orange particles
                    size_range=(2, 5),
                    lifetime_range=(0.2, 0.5),
                    speed_range=(30, 70),
                    direction_range=(0, 360),
                    gravity=0.01,
                    fade=True,
                    shape="circle"
                )
            
            # Still allow some limited movement while dying
            self.vx *= 0.95  # Slow horizontal movement
            # Apply reduced gravity
            self.vy += GRAVITY * dt_seconds * 0.5
            # Apply velocity with reduced effect
            self.x += self.vx * dt_seconds * 0.5
            self.y += self.vy * dt_seconds * 0.5
            
            # Update collision rectangle
            self.rect.center = (int(self.x), int(self.y))
            
            # Skip further updates
            return
            
        # Update damage flash effect
        if self.damage_flash > 0:
            self.damage_flash -= dt_seconds
            if self.damage_flash <= 0:
                self.is_damaged = False
        
        # Store current ground status for this frame
        was_on_ground = self.on_ground
        
        # Apply gravity
        if not self.on_ground:
            self.vy += GRAVITY * dt_seconds
            # Apply air resistance to horizontal movement
            self.vx *= AIR_RESISTANCE
        else:
            # Apply ground friction to horizontal movement
            self.vx *= GROUND_FRICTION
            
        # Apply platform effects to movement
        if self.on_sticky_platform:
            # Extra friction on sticky platforms
            self.vx *= STICKY_SLOWDOWN
        elif self.on_speed_platform:
            # Less friction on speed platforms
            self.vx *= SPEED_BOOST
            
        # Handle player input - accelerate based on movement direction
        target_speed = self.move_direction * self.speed
        
        # Apply power-up effects
        if 'speed' in self.active_powerups:
            target_speed *= POWERUP_EFFECTS['speed']
            
        # Smoothly interpolate towards target speed
        # This makes movement more responsive while still feeling smooth
        self.vx = self.vx * 0.8 + target_speed * dt_seconds * 5.0
        
        # Enforce terminal velocity
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED
            
        # Apply velocity to position
        self.x += self.vx * dt_seconds
        self.y += self.vy * dt_seconds
        
        # Update collision rectangle
        self.rect.center = (int(self.x), int(self.y))
        
        # Enforce boundaries to prevent players from leaving the screen
        self.enforce_boundaries()
        
        # Update position and velocity tuples to match x,y variables
        self.position = (self.x, self.y)
        self.velocity = (self.vx, self.vy)
        
        # Update tag cooldown
        if self.tag_cooldown > 0:
            self.tag_cooldown -= dt * 1000  # Convert dt from seconds to milliseconds
            
        # Update power-up timers
        self.update_powerups(dt_seconds)
            
        # Check for collisions - this will be handled in the Game class
        # which will set on_ground and other platform effects
            
        # Reset platform effects for next collision detection cycle
        # This needs to happen after all physics is applied but before next update
        self.on_ground = False
        self.on_sticky_platform = False
        self.on_jump_platform = False
        self.on_speed_platform = False
        
        # Update blob animation state
        self.update_animation(dt)
        
    def update_powerups(self, dt_seconds):
        """Update power-up timers and remove expired power-ups."""
        # Make a copy of keys to avoid modifying during iteration
        powerup_keys = list(self.active_powerups.keys())
        
        for powerup in powerup_keys:
            self.active_powerups[powerup] -= dt_seconds
            if self.active_powerups[powerup] <= 0:
                # Power-up has expired
                del self.active_powerups[powerup]
                
                # Reset power-up specific states
                if powerup == 'shield':
                    self.has_shield = False
                elif powerup == 'invisible':
                    self.is_invisible = False
        
    def update_animation(self, dt):
        """Update blob animation state."""
        # Update animation timer
        self.animation_time += dt
        
        # Update blink counter
        self.blob_traits['blink_counter'] += 1
        
        # Handle blinking
        if self.blob_traits['is_blinking']:
            if self.blob_traits['blink_counter'] >= self.blob_traits['blink_duration']:
                self.blob_traits['is_blinking'] = False
                self.blob_traits['blink_counter'] = 0
        elif self.blob_traits['blink_counter'] >= self.blob_traits['blink_interval']:
            self.blob_traits['is_blinking'] = True
            self.blob_traits['blink_counter'] = 0
            
        # Update facing direction based on movement
        if abs(self.vx) > 1.0:
            self.blob_traits['facing_direction'] = 1 if self.vx > 0 else -1
            
        # Update running animation cycle when moving on ground
        if self.on_ground and abs(self.vx) > 10:
            # Progress running cycle based on speed and time
            cycle_speed = abs(self.vx) / 100.0  # Faster movement = faster animation
            self.blob_traits['running_cycle'] += dt * 10.0 * cycle_speed
            
            # Keep cycle in [0, 2π) range
            self.blob_traits['running_cycle'] %= (math.pi * 2)
            
            # Generate footstep particles at appropriate times in the running cycle
            self.footstep_timer -= dt
            if self.footstep_timer <= 0:
                self.generate_footstep_particles()
                self.footstep_timer = self.footstep_interval / max(1.0, abs(self.vx) / 100.0)
        else:
            # Slow down the cycle when not running
            self.blob_traits['running_cycle'] *= 0.9
            
        # Squish effect when landing
        just_landed = self.on_ground and not self.was_on_ground
        if just_landed:
            # Calculate landing impact based on falling speed
            impact = min(1.0, abs(self.vy) / 400.0)
            self.blob_traits['landing_impact'] = impact
            
            # Generate landing particles
            self.generate_landing_particles(impact)
            
            # Play landing sound if impact is significant
            if impact > 0.2:
                from sounds import sound_manager
                sound_manager.play("land")
            
        # Update landing impact recovery
        if self.blob_traits['landing_impact'] > 0:
            recovery_rate = PLAYER_SQUISH_RECOVERY * dt * 5.0
            self.blob_traits['landing_impact'] = max(0, self.blob_traits['landing_impact'] - recovery_rate)
            
        # Calculate squish factors based on landing and running
        if self.on_ground:
            # Running squish
            run_squish = 0.05 * min(1.0, abs(self.vx) / 200.0)
            run_squish *= math.sin(self.blob_traits['running_cycle'] * 2) * 0.5 + 0.5
            
            # Landing squish
            landing_squish = self.blob_traits['landing_impact'] * PLAYER_MAX_SQUISH
            
            # Combined squish effect
            total_squish = max(landing_squish, run_squish)
            self.blob_traits['squish_x'] = 1.0 + total_squish
            self.blob_traits['squish_y'] = 1.0 - total_squish
        else:
            # Air squish - elongate slightly when jumping/falling
            air_squish = 0.1 * min(1.0, abs(self.vy) / 200.0)
            self.blob_traits['squish_x'] = 1.0 - air_squish * 0.5
            self.blob_traits['squish_y'] = 1.0 + air_squish
            
        # Rotation based on movement
        if not self.on_ground:
            # Rotate slightly in air based on horizontal and vertical velocity
            target_rotation = self.vx * 0.1  # Rotate based on horizontal velocity
            rotation_speed = 5.0 * dt
            self.blob_traits['rotation'] += (target_rotation - self.blob_traits['rotation']) * rotation_speed
        else:
            # Slowly return to upright when on ground
            self.blob_traits['rotation'] *= 0.9
            
        # Track ground state for the next frame
        self.was_on_ground = self.on_ground
        
        # Update in_air_time for jump animations
        if not self.on_ground:
            self.blob_traits['in_air_time'] += dt
        else:
            self.blob_traits['in_air_time'] = 0
    
    def generate_footstep_particles(self):
        """Generate particles when the player is running."""
        if not hasattr(self.game, 'particle_system'):
            return
            
        # Only generate particles if we're moving and on the ground
        if abs(self.vx) < 50 or not self.on_ground:
            return
            
        # Create dust particles at the player's feet
        feet_y = self.y + PLAYER_RADIUS * 0.8
        
        # Determine player direction
        player_direction = 0
        if self.vx > 1:
            player_direction = 0  # Right
        elif self.vx < -1:
            player_direction = 180  # Left
            
        # Create footstep particles
        self.game.particle_system.create_footsteps(
            self.x, feet_y, self.color, player_direction, self.on_ground
        )
        
        # Play footstep sound
        from sounds import sound_manager
        sound_manager.play("footstep")
        
    def generate_landing_particles(self, impact):
        """Generate particles when the player lands."""
        if not hasattr(self.game, 'particle_system'):
            return
            
        # Only generate particles for significant impacts
        if impact < 0.2:
            return
            
        # Create dust particles radiating outward from the player's feet
        feet_y = self.y + PLAYER_RADIUS * 0.9
        
        # Number of particles based on impact
        count = int(LAND_PARTICLE_COUNT * impact)
        
        # Create landing dust cloud
        self.game.particle_system.create_particles(
            count, 
            self.x, feet_y, 
            (150, 150, 150),  # Dust color
            size_range=(2, 4),
            lifetime_range=(0.2, 0.8),
            speed_range=(50, 150),
            direction_range=(210, 330),  # Upward with spread
            gravity=0.1,
            fade=True,
            shape="circle"
        )
    
    def generate_jump_particles(self):
        """Generate particles when the player jumps."""
        if not hasattr(self.game, 'particle_system'):
            return
            
        # Create dust particles at the player's feet
        feet_y = self.y + PLAYER_RADIUS * 0.8
        
        # Create jump particles
        self.game.particle_system.create_particles(
            JUMP_PARTICLE_COUNT, 
            self.x, feet_y, 
            (150, 150, 150),  # Dust color
            size_range=(2, 4),
            lifetime_range=(0.2, 0.5),
            speed_range=(30, 80),
            direction_range=(30, 150),  # Downward with spread
            gravity=0.05,
            fade=True,
            shape="circle"
        )
    
    def draw(self, screen, camera=None):
        """Draw the player as a blob character with unique traits."""
        x, y = int(self.x), int(self.y)
        
        # Apply camera transformations if provided
        if camera:
            x, y = camera.apply_pos((x, y))
            draw_radius = PLAYER_RADIUS * camera.zoom_level
        else:
            draw_radius = PLAYER_RADIUS
        
        # Skip drawing if invisible power-up is active (make semi-transparent)
        alpha = 80 if self.is_invisible else 255
        
        # Calculate blob wobble effect based on time, velocity, and blob traits
        wobble_time = pygame.time.get_ticks() / 200.0 * self.blob_traits['wobble_speed']
        velocity_wobble = max(0.5, min(1.5, abs(self.vx) / 100))
        
        # Base radius with personalized wobble effect
        wobble_amount = self.blob_traits['wobble_amount']
        radius = draw_radius * (1 + wobble_amount * math.sin(wobble_time) * velocity_wobble)
        
        # Apply squish and stretch from animation
        squish_x = self.blob_traits['squish_x']
        squish_y = self.blob_traits['squish_y']
        
        # Adjust radius based on squish factors
        radius_x = radius * squish_x
        radius_y = radius * squish_y
        
        # Apply rotation for movement animation
        rotation = self.blob_traits['rotation']
        
        # Draw blob body (main circle)
        color = self.color
        if self.is_frozen:
            # Override color for frozen player
            color = (200, 220, 255)  # Light blue for frozen
        elif self.is_damaged:
            # Flash red when damaged
            flash_intensity = min(1.0, self.damage_flash * 5.0)  # More intense at start
            red = min(255, color[0] + int((255 - color[0]) * flash_intensity))
            green = max(0, color[1] - int(color[1] * flash_intensity * 0.8))
            blue = max(0, color[2] - int(color[2] * flash_intensity * 0.8))
            color = (red, green, blue)
            
        # Draw shield if active
        if self.has_shield:
            # Draw outer shield
            shield_radius = radius * 1.3
            pygame.draw.circle(screen, POWERUP_COLORS['shield'], (x, y), int(shield_radius), 3)
            
        # Draw the player blob
        pygame.draw.circle(screen, color, (x, y), int(radius))
        
        # Add highlight to make it look more blob-like
        highlight_radius = radius * 0.7
        highlight_offset = radius * 0.3
        highlight_color = self.get_highlight_color()
        pygame.draw.circle(
            screen, 
            highlight_color, 
            (int(x - highlight_offset), int(y - highlight_offset)), 
            int(highlight_radius * 0.5)
        )
        
        # Get personalized eye traits
        eye_size = self.blob_traits['eye_size']
        eye_spacing = self.blob_traits['eye_spacing']
        eye_height = self.blob_traits['eye_height']
        
        # Calculate eye positions
        eye_radius = radius * eye_size
        eye_distance = radius * eye_spacing
        eye_y_offset = radius * eye_height
        
        # Direction affects eye position
        eye_direction = 1 if self.move_direction >= 0 else -1
        
        # Draw eyes only if not blinking
        if not self.blob_traits['is_blinking']:
            # Left eye
            pygame.draw.circle(
                screen, 
                WHITE, 
                (int(x - eye_distance * eye_direction), int(y - eye_y_offset)), 
                int(eye_radius)
            )
            # Right eye
            pygame.draw.circle(
                screen, 
                WHITE, 
                (int(x + eye_distance * eye_direction), int(y - eye_y_offset)), 
                int(eye_radius)
            )
            
            # Draw pupils (follow movement direction)
            pupil_offset = eye_radius * 0.5 * eye_direction
            pygame.draw.circle(
                screen, 
                BLACK, 
                (int(x - eye_distance * eye_direction + pupil_offset), int(y - eye_y_offset)), 
                int(eye_radius * 0.5)
            )
            pygame.draw.circle(
                screen, 
                BLACK, 
                (int(x + eye_distance * eye_direction + pupil_offset), int(y - eye_y_offset)), 
                int(eye_radius * 0.5)
            )
        else:
            # Draw closed eyes (simple lines)
            eye_y = int(y - eye_y_offset)
            pygame.draw.line(
                screen, 
                BLACK,
                (int(x - eye_distance * eye_direction - eye_radius * 0.7), eye_y),
                (int(x - eye_distance * eye_direction + eye_radius * 0.7), eye_y),
                2
            )
            pygame.draw.line(
                screen, 
                BLACK,
                (int(x + eye_distance * eye_direction - eye_radius * 0.7), eye_y),
                (int(x + eye_distance * eye_direction + eye_radius * 0.7), eye_y),
                2
            )
        
        # Draw mouth based on expression and tagger status
        mouth_y = y + radius * 0.25
        if self.is_tagger:  # Tagger has a mischievous smile
            pygame.draw.arc(
                screen,
                BLACK,
                (x - radius * 0.5, mouth_y - radius * 0.3, radius, radius * 0.6),
                math.pi * 0.1, math.pi * 0.9, 
                2
            )
        else:  # Different expressions for runner
            if self.expression == 'happy':
                # Happy smile
                pygame.draw.arc(
                    screen,
                    BLACK,
                    (x - radius * 0.4, mouth_y - radius * 0.2, radius * 0.8, radius * 0.4),
                    0, math.pi,
                    2
                )
            elif self.expression == 'curious':
                # Smaller 'o' mouth
                pygame.draw.circle(
                    screen,
                    BLACK,
                    (x, int(mouth_y + radius * 0.1)),
                    int(radius * 0.15),
                    2
                )
            elif self.expression == 'excited':
                # Excited open smile
                pygame.draw.arc(
                    screen,
                    BLACK,
                    (int(x - radius * 0.4), int(mouth_y - radius * 0.2), 
                     int(radius * 0.8), int(radius * 0.4)),
                    0, 3.14,
                    3
                )
                # Add a small line in the middle for open mouth effect
                pygame.draw.line(
                    screen,
                    BLACK,
                    (int(x), int(mouth_y)),
                    (int(x), int(mouth_y + radius * 0.15)),
                    2
                )
            else:  # 'determined'
                # Straight line
                pygame.draw.line(
                    screen,
                    BLACK,
                    (int(x - radius * 0.3), int(mouth_y + radius * 0.1)),
                    (int(x + radius * 0.3), int(mouth_y + radius * 0.1)),
                    2
                )
        
        # Draw player accessories (only if not the tagger)
        if not self.is_tagger and self.accessory != 'none':
            if self.accessory == 'bow':
                # Draw a cute bow on top
                bow_y = y - radius - 6
                bow_width = radius * 0.5
                bow_height = radius * 0.3
                bow_color = (255, 100, 150)  # Pink bow
                
                # Bow center
                pygame.draw.circle(screen, bow_color, (x, int(bow_y)), int(bow_height * 0.4))
                
                # Left bow side
                pygame.draw.ellipse(
                    screen, 
                    bow_color,
                    (int(x - bow_width), int(bow_y - bow_height/2), 
                     int(bow_width * 0.8), int(bow_height))
                )
                
                # Right bow side
                pygame.draw.ellipse(
                    screen, 
                    bow_color,
                    (int(x + bow_width * 0.2), int(bow_y - bow_height/2), 
                     int(bow_width * 0.8), int(bow_height))
                )
                
            elif self.accessory == 'hat':
                # Draw a small hat
                hat_y = y - radius - 5
                hat_width = radius * 0.8
                hat_height = radius * 0.5
                hat_color = (60, 60, 180)  # Blue hat
                
                # Hat base
                pygame.draw.ellipse(
                    screen,
                    hat_color,
                    (int(x - hat_width/2), int(hat_y), 
                     int(hat_width), int(hat_height * 0.4))
                )
                
                # Hat top
                pygame.draw.rect(
                    screen,
                    hat_color,
                    (int(x - hat_width/4), int(hat_y - hat_height * 0.8),
                     int(hat_width/2), int(hat_height * 0.8))
                )
                
            elif self.accessory == 'glasses':
                # Draw glasses
                glasses_y = y - radius * 0.1
                glasses_width = radius * 0.4
                glasses_color = (30, 30, 30)
                
                # Left lens
                pygame.draw.circle(
                    screen,
                    glasses_color,
                    (int(x - glasses_width), int(glasses_y)),
                    int(radius * 0.25),
                    2
                )
                
                # Right lens
                pygame.draw.circle(
                    screen,
                    glasses_color,
                    (int(x + glasses_width), int(glasses_y)),
                    int(radius * 0.25),
                    2
                )
                
                # Bridge
                pygame.draw.line(
                    screen,
                    glasses_color,
                    (int(x - glasses_width * 0.5), int(glasses_y)),
                    (int(x + glasses_width * 0.5), int(glasses_y)),
                    2
                )
                
            elif self.accessory == 'bowtie':
                # Draw bowtie
                bowtie_y = y + radius * 0.7
                bowtie_width = radius * 0.6
                bowtie_height = radius * 0.3
                bowtie_color = (200, 0, 0)
                
                # Left side
                pygame.draw.polygon(
                    screen,
                    bowtie_color,
                    [
                        (x, bowtie_y),
                        (int(x - bowtie_width), int(bowtie_y - bowtie_height/2)),
                        (int(x - bowtie_width), int(bowtie_y + bowtie_height/2))
                    ]
                )
                
                # Right side
                pygame.draw.polygon(
                    screen,
                    bowtie_color,
                    [
                        (x, bowtie_y),
                        (int(x + bowtie_width), int(bowtie_y - bowtie_height/2)),
                        (int(x + bowtie_width), int(bowtie_y + bowtie_height/2))
                    ]
                )
                
                # Center knot
                pygame.draw.circle(screen, bowtie_color, (x, int(bowtie_y)), int(radius * 0.1))
                
            elif self.accessory == 'crown':
                # Draw a royal crown
                crown_y = y - radius - 10
                crown_width = radius * 0.7
                crown_height = radius * 0.4
                crown_color = (220, 180, 20)  # Gold color
                
                # Crown base
                pygame.draw.rect(
                    screen,
                    crown_color,
                    (int(x - crown_width/2), int(crown_y + crown_height * 0.6),
                     int(crown_width), int(crown_height * 0.4))
                )
                
                # Crown spikes
                spike_count = 5
                for i in range(spike_count):
                    spike_x = x - crown_width/2 + (crown_width * i / (spike_count - 1))
                    spike_height = crown_height * (0.8 if i % 2 == 0 else 1.0)  # Alternating heights
                    
                    pygame.draw.polygon(
                        screen,
                        crown_color,
                        [
                            (int(spike_x), int(crown_y + crown_height * 0.6)),
                            (int(spike_x - crown_width * 0.06), int(crown_y + crown_height - spike_height)),
                            (int(spike_x + crown_width * 0.06), int(crown_y + crown_height - spike_height))
                        ]
                    )
                
                # Add jewel to center spike
                pygame.draw.circle(
                    screen,
                    (200, 50, 50),  # Ruby red
                    (int(x), int(crown_y + crown_height * 0.3)),
                    int(crown_width * 0.06)
                )
        
        # Draw player ID
        font = pygame.font.Font(None, 18)
        text = font.render(str(self.player_id), True, WHITE)
        text_rect = text.get_rect(center=(x, y - int(radius) - 15))
        screen.blit(text, text_rect)
        
        # If tagger, draw a crown
        if self.is_tagger:
            crown_height = radius * 0.5
            crown_width = radius * 1.0
            crown_base_y = y - radius - 8
            
            # Crown base points
            crown_points = [
                (x - crown_width/2, crown_base_y),
                (x - crown_width/2, crown_base_y - crown_height/2),
                (x - crown_width/4, crown_base_y - crown_height/3),
                (x, crown_base_y - crown_height),
                (x + crown_width/4, crown_base_y - crown_height/3),
                (x + crown_width/2, crown_base_y - crown_height/2),
                (x + crown_width/2, crown_base_y),
            ]
            pygame.draw.polygon(screen, YELLOW, crown_points)
            
            # Add crown jewel
            pygame.draw.circle(screen, RED, 
                             (x, int(crown_base_y - crown_height/1.5)), 
                             int(crown_height/6))
    
    def get_highlight_color(self):
        """Generate a lighter version of the player's color for the blob highlight."""
        r = min(255, self.color[0] + 70)
        g = min(255, self.color[1] + 70)
        b = min(255, self.color[2] + 70)
        return (r, g, b)
            
    def can_tag(self):
        """Check if this player can tag another player."""
        return self.is_tagger and self.tag_cooldown <= 0
        
    def tag_player(self, other_player):
        """Tag another player and switch roles."""
        # Check if this player can tag and the other player doesn't have a shield
        if self.can_tag() and not other_player.has_shield:
            # Switch tagger status
            self.update_tagger_status(False)
            other_player.update_tagger_status(True)
            
            # Add point to the player who was the tagger
            self.score += 1
            
            # Set cooldown to prevent immediate tag-backs
            other_player.tag_cooldown = TAG_COOLDOWN
            
            # Play tag sound
            from sounds import sound_manager
            sound_manager.play("tag")
            # Play tagged sound for the player being tagged
            sound_manager.play("tagged")
            
            return True
        return False
        
    def apply_powerup(self, powerup_type):
        """Apply a power-up effect to this player."""
        # Set the power-up in the active power-ups dictionary with its duration
        self.active_powerups[powerup_type] = POWERUP_DURATION
        
        # Apply power-up specific effects
        if powerup_type == 'shield':
            self.has_shield = True
        elif powerup_type == 'super_jump':
            # Super jump affects the jump force - handled in update
            pass
        elif powerup_type == 'speed':
            # Speed affects the movement speed - handled in update
            pass
        elif powerup_type == 'invisible':
            self.is_invisible = True
        elif powerup_type == 'freeze':
            # Find the other player and freeze them
            for player in self.game.players:
                if player != self:
                    player.is_frozen = True
                    player.frozen_timer = POWERUP_EFFECTS['freeze']
                    break
        
    def get_position(self):
        """Get the current position of the player."""
        return (self.x, self.y)
