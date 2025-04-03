"""
Game module for the Tag Game.
Main game loop and physics management.
"""

import pygame
import random
import time
import os
import math
from constants import *
from player import Player
from game_platform import Platform
from menu import Menu
from utils import draw_text
from powerup import PowerUp
from particles import ParticleSystem
from camera import Camera
from tutorial import Tutorial
from obstacle import Obstacle
from sounds import sound_manager

class Game:
    def __init__(self):
        """Initialize the game, set up the screen, physics, and game objects."""
        # Initialize pygame display with the appropriate driver
        display_flags = 0
        
        # Set up the display regardless of environment
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), display_flags)
        pygame.display.set_caption("Tag Game")
        
        # Set up the clock
        self.clock = pygame.time.Clock()
        
        # Game state
        self.state = STATE_MENU
        self.running = True
        self.round_time = ROUND_TIME
        self.round_start_time = 0
        
        # Player customization preferences (will be set by the menu)
        self.player_preferences = None
        self.player_count = 2  # Default to 2 players
        
        # Current level (will be set by level selector)
        self.current_level = "Classic"
        
        # Create menu
        self.menu = Menu(self)
        
        # Initialize tutorial system
        self.tutorial = Tutorial(self)
        
        # Lists to store game objects
        self.players = []
        self.platforms = []
        self.powerups = []
        
        # Create game objects
        self.reset_game()
        
    def reset_game(self):
        """Reset the game state and create new game objects."""
        # Clear existing objects
        self.players = []
        self.platforms = []
        self.powerups = []
        self.obstacles = []  # Add obstacles list
        
        # Initialize particle system
        self.particle_system = ParticleSystem()
        
        # Initialize camera system
        self.camera = Camera(LEVEL_WIDTH, LEVEL_HEIGHT)
        
        # Reset power-up timer
        self.last_powerup_spawn_time = time.time()
        
        # Create platforms
        self.create_platforms()
        
        # Create obstacles
        self.create_obstacles()
        
        # Create players
        player1_controls = {
            'left': P1_LEFT,
            'right': P1_RIGHT,
            'jump': P1_JUMP,
            'down': P1_DOWN
        }
        
        player2_controls = {
            'left': P2_LEFT,
            'right': P2_RIGHT,
            'jump': P2_JUMP,
            'down': P2_DOWN
        }
        
        player3_controls = {
            'left': P3_LEFT,
            'right': P3_RIGHT,
            'jump': P3_JUMP,
            'down': P3_DOWN
        }
        
        player4_controls = {
            'left': P4_LEFT,
            'right': P4_RIGHT,
            'jump': P4_JUMP,
            'down': P4_DOWN
        }
        
        # Create players with random positions on top platforms
        p1_pos = (random.randint(100, SCREEN_WIDTH//4), SCREEN_HEIGHT//2)
        p2_pos = (random.randint(SCREEN_WIDTH//4 + 50, SCREEN_WIDTH//2), SCREEN_HEIGHT//2)
        p3_pos = (random.randint(SCREEN_WIDTH//2 + 50, 3*SCREEN_WIDTH//4), SCREEN_HEIGHT//2)
        p4_pos = (random.randint(3*SCREEN_WIDTH//4 + 50, SCREEN_WIDTH - 100), SCREEN_HEIGHT//2)
        
        # Apply customization preferences if available
        if self.player_preferences:
            # Get customization preferences
            p1_prefs = self.player_preferences[1]
            p2_prefs = self.player_preferences[2]
            
            # Create players with customizations
            self.player1 = Player(
                self, 
                p1_pos, 
                player1_controls, 
                1, 
                is_tagger=True,
                color=self.menu.color_options[p1_prefs['color_index']],
                accessory=p1_prefs['accessory'],
                expression=p1_prefs['expression']
            )
            
            self.player2 = Player(
                self, 
                p2_pos, 
                player2_controls, 
                2, 
                is_tagger=False,
                color=self.menu.color_options[p2_prefs['color_index']],
                accessory=p2_prefs['accessory'],
                expression=p2_prefs['expression']
            )
            
            # Create player 3 if player count >= 3
            if self.player_count >= 3:
                self.player3 = Player(
                    self, 
                    p3_pos, 
                    player3_controls, 
                    3, 
                    is_tagger=False,
                    color=self.menu.color_options[2],  # Green
                    accessory="glasses",
                    expression="curious"
                )
            
            # Create player 4 if player count == 4
            if self.player_count == 4:
                self.player4 = Player(
                    self, 
                    p4_pos, 
                    player4_controls, 
                    4, 
                    is_tagger=False,
                    color=self.menu.color_options[4],  # Purple
                    accessory="bowtie",
                    expression="surprised"
                )
        else:
            # Create players with default settings
            self.player1 = Player(self, p1_pos, player1_controls, 1, is_tagger=True)
            self.player2 = Player(self, p2_pos, player2_controls, 2, is_tagger=False)
            
            # Create player 3 if player count >= 3
            if self.player_count >= 3:
                self.player3 = Player(self, p3_pos, player3_controls, 3, is_tagger=False)
            
            # Create player 4 if player count == 4
            if self.player_count == 4:
                self.player4 = Player(self, p4_pos, player4_controls, 4, is_tagger=False)
        
        # Store references to all players (though they're already added in the Player constructor)
        if self.player1 not in self.players:
            self.players.append(self.player1)
        if self.player2 not in self.players:
            self.players.append(self.player2)
        
        # Add player 3 if player count >= 3
        if self.player_count >= 3 and hasattr(self, 'player3') and self.player3 not in self.players:
            self.players.append(self.player3)
        
        # Add player 4 if player count == 4
        if self.player_count == 4 and hasattr(self, 'player4') and self.player4 not in self.players:
            self.players.append(self.player4)
        
        # Reset game timing
        self.round_start_time = time.time()
        

        
    def create_platforms(self):
        """Create various platforms with different properties based on the selected level."""
        # Platform configurations for each level: (position, width, type)
        level_platforms = {
            "Classic": [
                # Bottom platforms
                ((200, 500), 250, "regular"),
                ((600, 500), 250, "sticky"),
                
                # Middle platforms
                ((150, 400), 200, "jump"),
                ((400, 350), 150, "passthrough"),
                ((650, 400), 200, "speed"),
                
                # Upper platforms
                ((300, 200), 150, "regular"),
                ((500, 250), 150, "jump"),
                
                # Small platforms
                ((100, 300), 80, "speed"),
                ((700, 300), 80, "sticky"),
                ((400, 150), 100, "passthrough")
            ],
            
            "Sky Islands": [
                # Bottom islands - floating platforms with gaps
                ((150, 520), 120, "regular"),
                ((400, 520), 120, "regular"),
                ((650, 520), 120, "regular"),
                
                # Middle islands
                ((250, 420), 120, "jump"),
                ((550, 420), 120, "speed"),
                
                # Upper islands
                ((150, 320), 120, "passthrough"),
                ((400, 320), 120, "passthrough"),
                ((650, 320), 120, "jump"),
                
                # Top islands
                ((250, 220), 100, "sticky"),
                ((550, 220), 100, "sticky"),
                
                # Highest platform
                ((400, 120), 120, "jump")
            ],
            
            "Urban Playground": [
                # Base floor - symmetrical design
                ((400, 550), 700, "regular"),
                
                # Middle section - left and right
                ((200, 450), 200, "speed"),
                ((600, 450), 200, "speed"),
                
                # Central platform
                ((400, 350), 350, "passthrough"),
                
                # Upper section
                ((150, 250), 150, "jump"),
                ((650, 250), 150, "jump"),
                
                # Top platform
                ((400, 150), 300, "sticky")
            ],
            
            "Maze Runner": [
                # Bottom floor
                ((400, 550), 700, "regular"),
                
                # Complex path structure
                ((150, 480), 200, "passthrough"),
                ((650, 480), 200, "regular"),
                ((400, 430), 200, "sticky"),
                ((200, 380), 200, "regular"),
                ((600, 380), 200, "speed"),
                ((150, 330), 200, "jump"),
                ((400, 280), 200, "passthrough"),
                ((650, 330), 200, "regular"),
                ((300, 230), 150, "speed"),
                ((500, 230), 150, "jump"),
                ((400, 170), 350, "regular"),
                # Maze walls
                ((50, 400), 80, "sticky"),
                ((750, 400), 80, "sticky"),
                ((300, 300), 60, "sticky"),
                ((500, 300), 60, "sticky")
            ],
            
            "Obstacle Course": [
                # Starting platform
                ((400, 550), 300, "regular"),
                
                # Obstacles - increasing difficulty
                ((150, 500), 100, "sticky"),
                ((250, 450), 80, "speed"),
                ((350, 400), 80, "jump"),
                ((450, 350), 70, "passthrough"),
                ((550, 300), 60, "sticky"),
                ((400, 250), 50, "speed"),
                ((300, 200), 50, "jump"),
                ((200, 150), 40, "passthrough"),
                ((100, 250), 80, "jump"),
                ((700, 500), 80, "passthrough")
            ]
        }
        
        # Get platform configurations for the current level
        platform_configs = level_platforms.get(self.current_level, level_platforms["Classic"])
        
        # Create each platform
        for position, width, platform_type in platform_configs:
            platform = Platform(self, position, width, platform_type)
            self.platforms.append(platform)
            
    def create_obstacles(self):
        """Create various obstacles based on the current level."""
        # Obstacle configurations for each level: (position, obstacle_type, width, height, **kwargs)
        level_obstacles = {
            "Classic": [
                # Simple static obstacles
                ((400, 450), "static", 30, 30),
                ((300, 300), "static", 40, 20),
                ((500, 200), "static", 20, 40)
            ],
            
            "Sky Islands": [
                # Bouncing obstacles for vertical movement
                ((220, 470), "bouncing", 50, 15, {"bounce_strength": 18}),
                ((580, 470), "bouncing", 50, 15, {"bounce_strength": 18}),
                ((400, 270), "bouncing", 50, 15, {"bounce_strength": 18}),
                
                # Moving obstacles for challenge
                ((300, 380), "moving", 30, 30, {"movement_direction": "horizontal", "movement_range": 120}),
                ((500, 380), "moving", 30, 30, {"movement_direction": "horizontal", "movement_range": 120})
            ],
            
            "Urban Playground": [
                # Rotating obstacles
                ((150, 350), "rotating", 60, 10, {"rotation_speed": 2.0, "num_points": 4}),
                ((650, 350), "rotating", 60, 10, {"rotation_speed": -2.0, "num_points": 4}),
                
                # Moving obstacles
                ((400, 250), "moving", 40, 20, {"movement_direction": "vertical", "movement_range": 80}),
                ((250, 350), "moving", 40, 20, {"movement_direction": "horizontal", "movement_range": 100}),
                ((550, 350), "moving", 40, 20, {"movement_direction": "horizontal", "movement_range": 100})
            ],
            
            "Maze Runner": [
                # Damaging obstacles in tight spots
                ((400, 350), "damaging", 25, 25, {"damage": 1, "spike_length": 8, "num_spikes": 6}),
                ((200, 265), "damaging", 25, 25, {"damage": 1, "spike_length": 8, "num_spikes": 6}),
                ((600, 265), "damaging", 25, 25, {"damage": 1, "spike_length": 8, "num_spikes": 6}),
                
                # Moving obstacles blocking passages
                ((400, 215), "moving", 30, 30, {"movement_direction": "horizontal", "movement_range": 150, "movement_speed": 2.0}),
                ((550, 400), "moving", 30, 30, {"movement_direction": "vertical", "movement_range": 60, "movement_speed": 1.5}),
                
                # Rotating obstacle in central area
                ((400, 400), "rotating", 50, 10, {"rotation_speed": 3.0, "num_points": 3})
            ],
            
            "Obstacle Course": [
                # Various obstacle types for an obstacle course
                ((150, 450), "bouncing", 40, 15, {"bounce_strength": 20}),
                ((250, 400), "static", 35, 35),
                ((350, 350), "damaging", 30, 30, {"damage": 1}),
                ((450, 300), "rotating", 45, 10, {"rotation_speed": 2.5, "num_points": 3}),
                ((550, 250), "moving", 30, 30, {"movement_direction": "circular", "movement_range": 40}),
                ((650, 450), "moving", 25, 25, {"movement_direction": "vertical", "movement_range": 80, "movement_speed": 2.0}),
                ((250, 200), "rotating", 60, 10, {"rotation_speed": -2.0, "num_points": 4}),
                ((450, 150), "damaging", 25, 25, {"damage": 1})
            ]
        }
        
        # Get obstacle configurations for the current level
        obstacle_configs = level_obstacles.get(self.current_level, [])
        
        # Create each obstacle
        for position, obstacle_type, width, height, *args in obstacle_configs:
            kwargs = args[0] if args else {}
            obstacle = Obstacle(self, position, obstacle_type, width, height, **kwargs)
            self.obstacles.append(obstacle)
            
    def check_collisions(self):
        """Check for collisions between players and platforms, and between players."""
        # First loop: reset player ground status
        for player in self.players:
            # Reset ground status before collision checks
            player.on_ground = False
            
        # Check player-platform collisions
        for player in self.players:
            player_rect = player.get_rect()
            
            # Check for floor detection - The bottom of the screen counts as ground
            if player.y >= SCREEN_HEIGHT - PLAYER_RADIUS:
                player.on_ground = True
                player.y = SCREEN_HEIGHT - PLAYER_RADIUS
                player.vy = 0
                
                # In Sky Islands map, falling off the map causes damage and starts the dying process
                if self.current_level == "Sky Islands":
                    # Apply damage effect with red flash when falling off the map
                    player.take_damage()
                    
                    # Start dying process if not already dying
                    if not player.is_dying:
                        player.start_dying()
                    
                    # Apply a bounce effect (upward velocity) after hitting the deadly floor
                    player.vy = -DEFAULT_JUMP_FORCE * 0.3  # Reduced bounce for dying players
                    
                    # Create effect particles to highlight the danger
                    if hasattr(self, 'particle_system'):
                        self.particle_system.create_particles(
                            20,  # Number of particles
                            player.x, player.y + PLAYER_RADIUS, 
                            (255, 50, 50),  # Red particles for danger
                            size_range=(3, 8),
                            lifetime_range=(0.5, 1.2),
                            speed_range=(80, 150)
                        )
            
            # Check collisions with each platform
            for platform in self.platforms:
                platform_rect = platform.get_rect()
                
                # If player is trying to pass through a passthrough platform, skip the collision check
                if (platform.platform_type == "passthrough" or platform.platform_type == "pass-through") and player.passing_through:
                    continue
                
                # Check if player is colliding with platform
                if player_rect.colliderect(platform_rect):
                    # Check if player is landing on top of platform
                    if (player.vy > 0 and 
                        player.y + PLAYER_RADIUS > platform_rect.top and
                        player.y < platform_rect.top + 10 and
                        (platform.platform_type != "passthrough" or not player.passing_through)):  # Small margin for better ground detection
                        
                        # Player is on top of platform
                        player.on_ground = True
                        player.y = platform_rect.top - PLAYER_RADIUS
                        player.vy = 0
                        player.current_platform = platform
                        
                        # Apply platform effects
                        platform.apply_effect(player)
                    
                    # Side collision handling
                    elif player.y > platform_rect.top + 10:
                        # Determine if collision is from left or right
                        if player.x < platform_rect.left:
                            player.x = platform_rect.left - PLAYER_RADIUS
                            player.vx = 0
                        elif player.x > platform_rect.right:
                            player.x = platform_rect.right + PLAYER_RADIUS
                            player.vx = 0
        
        # Check player-player collisions (for tagging)
        # Check all player combinations for tagging
        for i, player1 in enumerate(self.players):
            for player2 in self.players[i+1:]:  # Check against all players with higher index
                p1_rect = player1.get_rect()
                p2_rect = player2.get_rect()
                
                if p1_rect.colliderect(p2_rect):
                    # Check tagging logic
                    if player1.is_tagger and player1.can_tag():
                        player1.tag_player(player2)
                    elif player2.is_tagger and player2.can_tag():
                        player2.tag_player(player1)
        
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                # Menu navigation
                if self.state == STATE_MENU:
                    self.menu.handle_key(event.key)
                    
                # Game controls
                elif self.state == STATE_PLAYING:
                    # Pause game
                    if event.key == PAUSE_KEY:
                        self.state = STATE_PAUSED
                        # Play pause sound
                        from sounds import sound_manager
                        sound_manager.play("pause")
                        
                    # Toggle tagger properties
                    elif event.key == TAGGER_PROPERTY_KEY:
                        for player in self.players:
                            if player.is_tagger:
                                player.toggle_tagger_property()
                                
                    # Enter tutorial mode with T key + left shift
                    elif event.key == pygame.K_t and pygame.key.get_mods() & pygame.KMOD_LSHIFT:
                        self.state = STATE_TUTORIAL
                        self.tutorial.start()
                                
                # Tutorial controls
                elif self.state == STATE_TUTORIAL:
                    # First check if tutorial wants to handle the event
                    if not self.tutorial.handle_event(event):
                        # If tutorial didn't handle it, process common controls
                        if event.key == pygame.K_ESCAPE:
                            # Exit tutorial
                            self.state = STATE_PLAYING
                            self.tutorial.complete()
                        elif event.key == pygame.K_SPACE:
                            # Advance tutorial
                            self.tutorial.next_step()
                                
                # Pause menu options
                elif self.state == STATE_PAUSED:
                    if event.key == PAUSE_KEY:
                        self.state = STATE_PLAYING
                        # Play unpause sound
                        from sounds import sound_manager
                        sound_manager.play("unpause")
                    elif event.key == pygame.K_r:
                        # Restart round
                        self.reset_game()
                        self.state = STATE_PLAYING
                        # Play game restart sound
                        from sounds import sound_manager
                        sound_manager.play("game_start")
                    elif event.key == pygame.K_e:
                        # End game and go to game over screen
                        self.state = STATE_GAME_OVER
                        # Play game over sound
                        from sounds import sound_manager
                        sound_manager.play("game_over")
                        
                # Restart from game over
                elif self.state == STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        self.reset_game()
                        self.state = STATE_PLAYING
                        # Play game restart sound
                        from sounds import sound_manager
                        sound_manager.play("game_start")
                    elif event.key == pygame.K_m:
                        self.state = STATE_MENU
                        # Play menu transition sound
                        from sounds import sound_manager
                        sound_manager.play("menu_select")
                
    def check_player_boundaries(self):
        """Double-check that players stay within the level boundaries."""
        margin = PLAYER_RADIUS
        for player in self.players:
            # Create a safety margin around the screen boundaries
            min_x = margin
            max_x = SCREEN_WIDTH - margin
            min_y = margin
            max_y = SCREEN_HEIGHT - margin
            
            # Check and correct player position if outside boundaries
            corrected = False
            if player.x < min_x:
                player.x = min_x
                # Stop horizontal movement if moving outside boundary
                if player.vx < 0:
                    player.vx = 0
                corrected = True
                
            elif player.x > max_x:
                player.x = max_x
                # Stop horizontal movement if moving outside boundary
                if player.vx > 0:
                    player.vx = 0
                corrected = True
            
            if player.y < min_y:
                player.y = min_y
                # Stop vertical movement if moving outside boundary
                if player.vy < 0:
                    player.vy = 0
                corrected = True
                
            elif player.y > max_y:
                player.y = max_y
                # Stop vertical movement if moving outside boundary
                if player.vy > 0:
                    player.vy = 0
                corrected = True
    
    def update(self, dt):
        """Update game state."""
        if self.state == STATE_PLAYING or self.state == STATE_TUTORIAL:
            # Get keyboard state
            keys = pygame.key.get_pressed()
            
            # Handle player input and update physics
            for player in self.players:
                player.handle_input(keys)
                player.update(dt)
            
            # Update power-ups
            self.update_powerups(dt)
            
            # Check for power-up spawning
            self.spawn_powerups()
            
            # Update obstacles
            for obstacle in self.obstacles:
                obstacle.update(dt)
            
            # Custom collision detection
            self.check_collisions()
            
            # Check power-up collections
            self.check_powerup_collisions()
            
            # Check obstacle collisions
            self.check_obstacle_collisions()
            
            # Update tutorial if in tutorial mode
            if self.state == STATE_TUTORIAL:
                self.tutorial.update(dt)
            
            # Game-level boundary enforcement (as an extra safety measure)
            self.check_player_boundaries()
            
            # Update particle system
            self.particle_system.update(dt)
            
            # Update camera to follow both players
            self.camera.update(self.players, dt)
            
            # Check game over conditions
            self.check_game_over()
            
            # Update round timer
            self.update_round_timer()
            
    def update_round_timer(self):
        """Update the round timer and check for time-based events."""
        elapsed_time = time.time() - self.round_start_time
        remaining_time = max(0, self.round_time - elapsed_time)
        
        # If time runs out, end the round
        if remaining_time <= 0:
            self.state = STATE_GAME_OVER
            # Play game over sound
            from sounds import sound_manager
            sound_manager.play("game_over")
            
    def check_game_over(self):
        """Check if game is over based on score."""
        for player in self.players:
            if player.score >= SCORE_TO_WIN:
                self.state = STATE_GAME_OVER
                # Play game over sound
                from sounds import sound_manager
                sound_manager.play("game_over")
                
    def spawn_powerups(self):
        """Check if it's time to spawn a new power-up and spawn it."""
        # Only spawn if it's been more than POWERUP_SPAWN_INTERVAL seconds since the last spawn
        if time.time() - self.last_powerup_spawn_time > POWERUP_SPAWN_INTERVAL:
            # Don't spawn more than the maximum allowed number of powerups
            if len(self.powerups) < POWERUP_MAX_COUNT:
                # Pick a random position away from players
                valid_position = False
                attempts = 0
                x, y = 0, 0  # Initialize position variables
                
                while not valid_position and attempts < 20:
                    # Generate random position
                    x = random.randint(100, LEVEL_WIDTH - 100)
                    y = random.randint(100, LEVEL_HEIGHT - 100)
                    
                    # Check if it's far enough from players (min 150px distance)
                    min_distance = 150
                    valid_position = True
                    
                    # Check distance from each player
                    for player in self.players:
                        dist = math.hypot(x - player.x, y - player.y)
                        if dist < min_distance:
                            valid_position = False
                            break
                    
                    attempts += 1
                
                if valid_position:
                    # Pick a random power-up type
                    powerup_type = random.choice(POWERUP_TYPES)
                    
                    # Create and add the power-up
                    powerup = PowerUp((x, y), powerup_type)
                    self.powerups.append(powerup)
                    
                    # Reset the timer
                    self.last_powerup_spawn_time = time.time()
    
    def update_powerups(self, dt):
        """Update all power-ups on the screen and remove expired ones."""
        # Use a copy to allow removing items during iteration
        for i in range(len(self.powerups) - 1, -1, -1):
            powerup = self.powerups[i]
            # Update returns True if the powerup should be removed
            if powerup.update(dt):
                self.powerups.pop(i)
    
    def check_obstacle_collisions(self):
        """Check for collisions between players and obstacles."""
        for player in self.players:
            player_rect = player.get_rect()
            
            for obstacle in self.obstacles:
                # Check if player is colliding with obstacle
                if obstacle.check_collision(player_rect):
                    # Apply obstacle effect to player
                    obstacle.apply_effect(player)
                    
                    # Create visual particle effect for collision
                    if hasattr(self, 'particle_system'):
                        self.particle_system.create_particles(
                            10,  # Number of particles
                            player.x, player.y,
                            (255, 200, 100),  # Orange-yellow particles
                            size_range=(2, 5),
                            lifetime_range=(0.3, 0.8),
                            speed_range=(50, 120)
                        )

    def check_powerup_collisions(self):
        """Check for collisions between players and power-ups."""
        # Check each player against each power-up
        for player in self.players:
            player_rect = player.get_rect()
            
            # Use a copy to allow removing while iterating
            for i in range(len(self.powerups) - 1, -1, -1):
                powerup = self.powerups[i]
                
                # Check for collision
                if player_rect.colliderect(powerup.get_rect()):
                    # Apply the power-up to the player
                    player.apply_powerup(powerup.type)
                    
                    # Play powerup sound
                    from sounds import sound_manager
                    sound_manager.play(f"powerup_{powerup.type}" if sound_manager.sounds.get(f"powerup_{powerup.type}") else "powerup_collect")
                    
                    # Remove the power-up
                    self.powerups.pop(i)
    
    def draw(self):
        """Draw the game state."""
        # Clear the screen
        self.screen.fill(BLACK)
        
        if self.state == STATE_MENU:
            # Draw menu
            self.menu.draw(self.screen)
            
        elif self.state in [STATE_PLAYING, STATE_PAUSED, STATE_TUTORIAL]:
            # Draw background
            self.draw_background()
            
            # Draw platforms with camera transformation
            for platform in self.platforms:
                platform.draw(self.screen, self.camera)
            
            # Draw power-ups with camera transformation
            for powerup in self.powerups:
                powerup.draw(self.screen, self.camera)
                
            # Draw obstacles with camera transformation
            for obstacle in self.obstacles:
                obstacle.draw(self.screen, self.camera)
                
            # Draw particles
            self.particle_system.draw(self.screen, self.camera)
                
            # Draw players with camera transformation
            for player in self.players:
                player.draw(self.screen, self.camera)
                
            # Draw UI (without camera transformation)
            self.draw_ui()
            
            # Draw level boundary indicators
            self.draw_level_boundaries()
            
            # Draw tutorial overlay if in tutorial mode
            if self.state == STATE_TUTORIAL:
                self.tutorial.draw(self.screen, self.camera)
            
            # Draw pause overlay if paused
            if self.state == STATE_PAUSED:
                self.draw_pause_screen()
                
        elif self.state == STATE_GAME_OVER:
            # Draw game over screen
            self.draw_game_over_screen()
            
        # Update display
        pygame.display.flip()
        
    def draw_background(self):
        """Draw the game background."""
        # Select background based on current level
        if self.current_level == "Sky Islands":
            self.draw_sky_islands_background()
        elif self.current_level == "Urban Playground":
            self.draw_urban_background()
        elif self.current_level == "Maze Runner":
            self.draw_maze_background()
        elif self.current_level == "Obstacle Course":
            self.draw_obstacle_course_background()
        else:  # Classic or default
            self.draw_classic_background()
    
    def draw_classic_background(self):
        """Draw the classic level background with enhanced gradient and stars."""
        # Draw a deep blue to light blue gradient
        for y in range(0, SCREEN_HEIGHT, 1):
            # Smoother gradient formula
            ratio = y / SCREEN_HEIGHT
            r = int(20 + 30 * (1 - ratio))  # Dark blue-purple tint
            g = int(40 + 60 * (1 - ratio))  # Mid-range
            b = int(80 + 100 * (1 - ratio))  # Strong blue component
            color = (r, g, b)
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
            
        # Add decorative stars (small white dots at random positions)
        if not hasattr(self, 'stars'):
            # Generate stars once and reuse
            self.stars = []
            for _ in range(50):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT//2)  # More stars in upper half
                size = random.randint(1, 3)
                brightness = random.randint(150, 255)
                self.stars.append((x, y, size, brightness))
        
        # Draw the stars
        for x, y, size, brightness in self.stars:
            # Make stars twinkle by slightly varying brightness
            twinkle = random.randint(-20, 20)
            color = (min(255, brightness + twinkle),) * 3  # White with varying brightness
            pygame.draw.circle(self.screen, color, (x, y), size)
    
    def draw_sky_islands_background(self):
        """Draw a sky-themed background with clouds and sun."""
        # Sky gradient from light to dark blue
        for y in range(0, SCREEN_HEIGHT, 1):
            ratio = y / SCREEN_HEIGHT
            r = int(100 + 100 * (1 - ratio))  # Lighter blue at top
            g = int(150 + 100 * (1 - ratio))
            b = int(200 + 40 * (1 - ratio))
            color = (r, g, b)
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Draw a sun in the corner
        sun_color = (255, 240, 150)
        sun_pos = (50, 50)  # Upper left corner
        pygame.draw.circle(self.screen, sun_color, sun_pos, 40)
        
        # Draw subtle sun rays
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            start_x = sun_pos[0] + 35 * math.cos(rad)
            start_y = sun_pos[1] + 35 * math.sin(rad)
            end_x = sun_pos[0] + 60 * math.cos(rad)
            end_y = sun_pos[1] + 60 * math.sin(rad)
            pygame.draw.line(self.screen, sun_color, (start_x, start_y), (end_x, end_y), 3)
        
        # Draw distant clouds if not already generated
        if not hasattr(self, 'clouds'):
            self.clouds = []
            for _ in range(6):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(50, SCREEN_HEIGHT//3)
                width = random.randint(80, 200)
                self.clouds.append([x, y, width])
        
        # Draw and slowly move clouds
        for i, (x, y, width) in enumerate(self.clouds):
            # Cloud color with slight transparency
            cloud_color = (255, 255, 255, 200)
            
            # Draw cloud as group of circles
            cloud_surface = pygame.Surface((width, width//2), pygame.SRCALPHA)
            num_circles = width // 20
            for j in range(num_circles):
                circle_x = j * (width // num_circles) + random.randint(-5, 5)
                circle_y = random.randint(0, width//4)
                circle_radius = random.randint(width//8, width//4)
                pygame.draw.circle(cloud_surface, cloud_color, (circle_x, circle_y), circle_radius)
            
            # Blit the cloud onto the screen
            self.screen.blit(cloud_surface, (x, y))
            
            # Move clouds slowly
            self.clouds[i][0] = (x + 0.2) % (SCREEN_WIDTH + width)  # Wrap around when off-screen
    
    def draw_urban_background(self):
        """Draw an urban cityscape background."""
        # Draw gradient sky
        for y in range(0, SCREEN_HEIGHT, 1):
            ratio = y / SCREEN_HEIGHT
            # Urban sunset colors
            if ratio < 0.4:  # Upper sky - darker blue
                r = int(50 + 30 * ratio * 2.5)
                g = int(50 + 30 * ratio * 2.5)
                b = int(80 + 100 * (1 - ratio * 2.5))
            else:  # Lower sky - sunset orange-red
                r = int(100 + 155 * (ratio - 0.4) * 1.67)
                g = int(50 + 60 * (ratio - 0.4) * 1.67)
                b = int(80 - 30 * (ratio - 0.4) * 1.67)
            color = (r, g, b)
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Draw city silhouette at the bottom
        building_color = (20, 20, 40)  # Dark blue for buildings
        
        # Generate building skyline if not already done
        if not hasattr(self, 'buildings'):
            self.buildings = []
            x = 0
            while x < SCREEN_WIDTH:
                width = random.randint(40, 120)
                height = random.randint(100, 200)
                self.buildings.append((x, SCREEN_HEIGHT - height, width, height))
                x += width
        
        # Draw buildings
        for x, y, width, height in self.buildings:
            building_rect = pygame.Rect(x, y, width, height)
            pygame.draw.rect(self.screen, building_color, building_rect)
            
            # Add windows (small yellow squares in a grid pattern)
            window_size = 5
            window_spacing = 15
            window_color = (255, 255, 150)  # Yellowish for lit windows
            
            for wx in range(x + 10, x + width - 10, window_spacing):
                for wy in range(y + 10, y + height - 10, window_spacing):
                    # Randomly decide if window is lit
                    if random.random() < 0.7:  # 70% chance window is lit
                        pygame.draw.rect(self.screen, window_color, 
                                        (wx, wy, window_size, window_size))
    
    def draw_maze_background(self):
        """Draw a mysterious maze-appropriate background."""
        # Draw a darker gradient for maze atmosphere
        for y in range(0, SCREEN_HEIGHT, 1):
            ratio = y / SCREEN_HEIGHT
            # Dark purplish gradient
            r = int(20 + 40 * (1 - ratio))
            g = int(10 + 20 * (1 - ratio))
            b = int(40 + 50 * (1 - ratio))
            color = (r, g, b)
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Add mysterious fog effect
        if not hasattr(self, 'fog_particles'):
            # Generate fog particles
            self.fog_particles = []
            for _ in range(30):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                size = random.randint(50, 150)
                alpha = random.randint(5, 30)  # Transparency
                speed = random.uniform(0.1, 0.5)
                self.fog_particles.append([x, y, size, alpha, speed])
        
        # Draw and update fog
        for i, (x, y, size, alpha, speed) in enumerate(self.fog_particles):
            # Create a surface for the fog particle
            fog_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            
            # Draw a semi-transparent circle for fog
            fog_color = (200, 200, 220, alpha)
            pygame.draw.circle(fog_surface, fog_color, (size//2, size//2), size//2)
            
            # Draw the fog particle
            self.screen.blit(fog_surface, (x, y))
            
            # Move the fog particle
            self.fog_particles[i][0] = (x + speed) % (SCREEN_WIDTH + size)
    
    def draw_obstacle_course_background(self):
        """Draw a dynamic, energetic background for the obstacle course."""
        # Vibrant gradient background
        for y in range(0, SCREEN_HEIGHT, 1):
            ratio = y / SCREEN_HEIGHT
            # Red to orange gradient
            r = int(180 + 75 * (1 - ratio))
            g = int(50 + 120 * (1 - ratio))
            b = int(20 + 40 * (1 - ratio))
            color = (r, g, b)
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Add decorative geometric patterns
        if not hasattr(self, 'geometric_patterns'):
            self.geometric_patterns = []
            for _ in range(20):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                size = random.randint(10, 50)
                shape_type = random.choice(['triangle', 'rectangle', 'circle'])
                color_r = random.randint(100, 255)
                color_g = random.randint(100, 255)
                color_b = random.randint(100, 255)
                color = (color_r, color_g, color_b, 100)  # Semi-transparent
                self.geometric_patterns.append([x, y, size, shape_type, color])
        
        # Draw patterns
        for pattern in self.geometric_patterns:
            x, y, size, shape_type, color = pattern
            
            # Create surface for semi-transparent shape
            pattern_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            
            if shape_type == 'triangle':
                points = [(size, 0), (0, size*2), (size*2, size*2)]
                pygame.draw.polygon(pattern_surface, color, points)
            elif shape_type == 'rectangle':
                pygame.draw.rect(pattern_surface, color, (0, 0, size*2, size))
            else:  # circle
                pygame.draw.circle(pattern_surface, color, (size, size), size)
                
            # Draw pattern
            self.screen.blit(pattern_surface, (x, y))
            
    def draw_level_boundaries(self):
        """Draw visible level boundaries transformed by the camera."""
        # Boundary settings
        boundary_color = (120, 120, 255, 150)  # Light blue boundary
        boundary_thickness = 4
        
        # Get the transformed boundary corners
        top_left = self.camera.apply_pos((0, 0))
        top_right = self.camera.apply_pos((LEVEL_WIDTH, 0))
        bottom_left = self.camera.apply_pos((0, LEVEL_HEIGHT))
        bottom_right = self.camera.apply_pos((LEVEL_WIDTH, LEVEL_HEIGHT))
        
        # Draw the transformed boundary lines
        pygame.draw.line(self.screen, boundary_color, top_left, top_right, boundary_thickness)
        pygame.draw.line(self.screen, boundary_color, top_right, bottom_right, boundary_thickness)
        pygame.draw.line(self.screen, boundary_color, bottom_right, bottom_left, boundary_thickness)
        pygame.draw.line(self.screen, boundary_color, bottom_left, top_left, boundary_thickness)
            
    def draw_ui(self):
        """Draw the game UI (scores, timer, status)."""
        # Draw player scores with improved layout
        player_colors = [
            (220, 60, 80),    # Player 1 - Red
            (60, 140, 220),   # Player 2 - Blue
            (60, 180, 80),    # Player 3 - Green
            (200, 120, 220)   # Player 4 - Purple
        ]
        
        # Score layout positions
        score_positions = [
            (10, 30),           # Top left - P1
            (SCREEN_WIDTH-70, 30),  # Top right - P2
            (10, 60),           # Below P1 - P3
            (SCREEN_WIDTH-70, 60)   # Below P2 - P4
        ]
        
        # Draw all player scores
        for i, player in enumerate(self.players):
            if i < len(score_positions):
                x, y = score_positions[i]
                color = player_colors[i] if i < len(player_colors) else WHITE
                draw_text(self.screen, f"P{i+1}: {player.score}", 20, x, y, color)
        
        # Draw round time
        elapsed_time = time.time() - self.round_start_time
        remaining_time = max(0, self.round_time - elapsed_time)
        draw_text(self.screen, f"Time: {int(remaining_time)}", 24, SCREEN_WIDTH // 2, 30, WHITE)
        
        # Draw level name
        draw_text(self.screen, f"Level: {self.current_level}", 16, SCREEN_WIDTH // 2, 60, GREEN)
        
        # Draw tagger status - find which player is the tagger
        tagger_name = "None"
        for i, player in enumerate(self.players):
            if player.is_tagger:
                tagger_name = f"P{i+1}"
                break
                
        draw_text(self.screen, f"Tagger: {tagger_name}", 20, SCREEN_WIDTH // 2, 85, YELLOW)
        
        # Draw controls reminder - with improved UI
        draw_text(self.screen, "T: Change tagger properties | ESC: Pause", 16, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20, LIGHT_GRAY)
        # Show the controls for all 4 players
        controls_text = "P1: WASD | P2: Arrows | P3: IJKL | P4: TFGH"
        draw_text(self.screen, controls_text, 16, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40, LIGHT_GRAY)
        
    def draw_pause_screen(self):
        """Draw the pause screen overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Darker overlay for better readability
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        draw_text(self.screen, "GAME PAUSED", 48, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100, WHITE)
        
        # Menu options with a nicer layout
        options_y_start = SCREEN_HEIGHT // 2 - 10
        options_spacing = 40
        
        # Draw menu options with highlight for selected option
        draw_text(self.screen, "ESC - Resume Game", 30, SCREEN_WIDTH // 2, options_y_start, (220, 220, 220))
        draw_text(self.screen, "R - Restart Round", 30, SCREEN_WIDTH // 2, options_y_start + options_spacing, (220, 220, 220))
        draw_text(self.screen, "E - End Game", 30, SCREEN_WIDTH // 2, options_y_start + options_spacing * 2, (220, 220, 220))
        
        # Decorative elements
        pygame.draw.line(self.screen, GOLD, 
                         (SCREEN_WIDTH // 2 - 150, options_y_start - 30), 
                         (SCREEN_WIDTH // 2 + 150, options_y_start - 30), 3)
        pygame.draw.line(self.screen, GOLD, 
                         (SCREEN_WIDTH // 2 - 150, options_y_start + options_spacing * 3 - 10), 
                         (SCREEN_WIDTH // 2 + 150, options_y_start + options_spacing * 3 - 10), 3)
        
    def draw_game_over_screen(self):
        """Draw the game over screen."""
        # Background
        self.screen.fill(DARK_GRAY)
        
        # Game over text
        draw_text(self.screen, "GAME OVER", 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80, WHITE)
        
        # Determine winner - find player with highest score
        max_score = -1
        winner_id = -1
        is_tie = False
        
        for i, player in enumerate(self.players):
            if player.score > max_score:
                max_score = player.score
                winner_id = i + 1
                is_tie = False
            elif player.score == max_score:
                is_tie = True
        
        # Set winner text
        if is_tie:
            winner = "It's a tie!"
        else:
            winner = f"Player {winner_id}"
            
        # Show winner
        draw_text(self.screen, f"Winner: {winner}", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20, YELLOW)
        
        # Display all player scores with colors
        player_colors = [
            (220, 60, 80),    # Player 1 - Red
            (60, 140, 220),   # Player 2 - Blue
            (60, 180, 80),    # Player 3 - Green
            (200, 120, 220)   # Player 4 - Purple
        ]
        
        # First row: P1 and P2
        if len(self.players) >= 1:
            draw_text(self.screen, f"P1: {self.players[0].score}", 24, SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 20, player_colors[0])
        if len(self.players) >= 2:
            draw_text(self.screen, f"P2: {self.players[1].score}", 24, SCREEN_WIDTH // 2 + 80, SCREEN_HEIGHT // 2 + 20, player_colors[1])
        
        # Second row: P3 and P4
        if len(self.players) >= 3:
            draw_text(self.screen, f"P3: {self.players[2].score}", 24, SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 50, player_colors[2])
        if len(self.players) >= 4:
            draw_text(self.screen, f"P4: {self.players[3].score}", 24, SCREEN_WIDTH // 2 + 80, SCREEN_HEIGHT // 2 + 50, player_colors[3])
        
        # Restart instructions
        draw_text(self.screen, "Press R to restart or M for menu", 20, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90, LIGHT_GRAY)
        
    def run(self):
        """Run the main game loop."""
        while self.running:
            # Calculate time delta
            dt = self.clock.tick(FPS) / 1000.0  # Convert to seconds
            
            # Handle events
            self.handle_events()
            
            # Update game
            self.update(dt)
            
            # Draw everything
            self.draw()
            
            # In Replit, we need to display special information about how to view and play the game
            if "REPLIT_DB_URL" in os.environ and pygame.time.get_ticks() % 500 < 20:  # Show every ~500ms 
                print("\033[H\033[J")  # Clear the console
                print("==== Tag Game ====")
                print("Game is running in Replit! You should see the game display in the right panel.")
                print("\nControls:")
                print("Player 1: WASD to move, W to jump, S to drop through pass-through platforms")
                print("Player 2: Arrow keys to move, UP to jump, DOWN to drop through pass-through platforms")
                print("Player 3: IJKL to move, I to jump, K to drop through pass-through platforms")
                print("Player 4: TFGH to move, T to jump, G to drop through pass-through platforms")
                print("\nGame controls:")
                print("T to toggle tagger properties")
                print("ESC to pause/resume")
                print("R to restart (when in pause menu or game over screen)")
                print("E to end game (when in pause menu)")
                print("\nIf you don't see the game, try clicking on the VNC icon in the right panel.")
