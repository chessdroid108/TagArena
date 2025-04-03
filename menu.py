"""
Menu module for the Tag Game.
Provides a main menu and settings interface.
"""

import pygame
import random
import math
from constants import *
from utils import draw_text

class Menu:
    def __init__(self, game):
        """
        Initialize the game menu.
        
        Args:
            game: Reference to the main game object
        """
        self.game = game
        self.selected_option = 0
        self.options = ["Start Game", "Tutorial", "Select Level", "Player Count", "Customize Characters", "How to Play", "Quit"]
        
        # State for screens
        self.showing_help = False
        self.showing_customization = False
        self.showing_level_selection = False
        self.showing_player_count = False
        
        # Player count selection
        self.player_count = 2  # Default to 2 players
        
        # Level selection state
        self.selected_level = 0  # Default level
        self.level_options = [
            "Classic",
            "Sky Islands", 
            "Urban Playground",
            "Maze Runner",
            "Obstacle Course"
        ]
        
        # Level descriptions
        self.level_descriptions = {
            "Classic": "The original level layout with a good mix of all platform types.",
            "Sky Islands": "Platforms floating in the sky with large gaps - challenge your jumping skills!",
            "Urban Playground": "A symmetrical layout with interconnected platforms for strategic play.",
            "Maze Runner": "Complex maze-like structure with multiple paths and hiding spots.",
            "Obstacle Course": "A challenging sequence of increasingly difficult platforms to traverse."
        }
        
        # Customization state
        self.customizing_player = 1  # Which player we're customizing (1 or 2)
        self.customization_option = 0  # Currently selected option in customization
        self.customization_options = [
            "Color", "Accessory", "Expression", "Done"
        ]
        
        # Available customization choices
        self.color_options = [
            (220, 60, 80),   # Reddish-pink
            (60, 140, 220),  # Blue
            (60, 220, 100),  # Green
            (220, 180, 60),  # Yellow
            (180, 100, 220), # Purple
            (100, 220, 220), # Cyan
            (220, 120, 50),  # Orange
        ]
        self.accessory_options = ["none", "bow", "hat", "glasses", "bowtie", "crown"]
        self.expression_options = ["happy", "curious", "determined", "surprised", "excited"]
        
        # Default preferences for both players
        # These will be applied to players when the game starts
        self.player_preferences = {
            1: {
                'color_index': 0,  # Index in the color_options list
                'accessory': 'bow',
                'expression': 'happy'
            },
            2: {
                'color_index': 1,
                'accessory': 'hat',
                'expression': 'determined'
            },
            3: {
                'color_index': 2,  # Green 
                'accessory': 'glasses',
                'expression': 'curious'
            },
            4: {
                'color_index': 4,  # Purple
                'accessory': 'crown',
                'expression': 'excited'
            }
        }
        
    def handle_key(self, key):
        """Handle keyboard input for menu navigation."""
        if self.showing_help:
            # Any key returns from help screen
            if key in [pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_SPACE]:
                self.showing_help = False
            return
            
        if self.showing_customization:
            self.handle_customization_keys(key)
            return
            
        if self.showing_level_selection:
            self.handle_level_selection_keys(key)
            return
            
        if self.showing_player_count:
            self.handle_player_count_keys(key)
            return
            
        # Main menu navigation
        if key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.options)
        elif key == pygame.K_RETURN:
            self.select_option()
            
    def handle_player_count_keys(self, key):
        """Handle keys in the player count selection screen."""
        if key == pygame.K_ESCAPE:
            # Exit player count selection mode
            self.showing_player_count = False
            return
            
        if key == pygame.K_LEFT:
            # Decrease player count (minimum 2)
            self.player_count = max(2, self.player_count - 1)
        elif key == pygame.K_RIGHT:
            # Increase player count (maximum 4)
            self.player_count = min(4, self.player_count + 1)
        elif key == pygame.K_RETURN:
            # Apply player count selection and return to main menu
            self.game.player_count = self.player_count
            self.showing_player_count = False
            
    def handle_level_selection_keys(self, key):
        """Handle keys in the level selection screen."""
        if key == pygame.K_ESCAPE:
            # Exit level selection mode
            self.showing_level_selection = False
            return
            
        if key == pygame.K_UP:
            # Navigate options
            self.selected_level = (self.selected_level - 1) % len(self.level_options)
        elif key == pygame.K_DOWN:
            self.selected_level = (self.selected_level + 1) % len(self.level_options)
        elif key == pygame.K_RETURN:
            # Select level and start game
            self.game.current_level = self.level_options[self.selected_level]
            self.apply_customizations()
            self.game.reset_game()
            self.game.state = STATE_PLAYING
            self.showing_level_selection = False
            
    def handle_customization_keys(self, key):
        """Handle keys in the character customization screen."""
        if key == pygame.K_ESCAPE:
            # Exit customization mode
            self.showing_customization = False
            return
            
        if key == pygame.K_UP:
            # Navigate options
            self.customization_option = (self.customization_option - 1) % len(self.customization_options)
        elif key == pygame.K_DOWN:
            self.customization_option = (self.customization_option + 1) % len(self.customization_options)
        elif key == pygame.K_LEFT:
            # Change values
            self.change_customization(-1)
        elif key == pygame.K_RIGHT:
            # Change values
            self.change_customization(1)
        elif key == pygame.K_TAB:
            # Switch between players based on player count
            # Cycle through all available players: 1 -> 2 -> 3 -> 4 -> 1 (if player_count is 4)
            self.customizing_player = (self.customizing_player % self.player_count) + 1
        elif key == pygame.K_RETURN:
            # Select option
            if self.customization_options[self.customization_option] == "Done":
                self.showing_customization = False
    
    def change_customization(self, direction):
        """Change the value of the current customization option."""
        current_option = self.customization_options[self.customization_option]
        player_prefs = self.player_preferences[self.customizing_player]
        
        if current_option == "Color":
            # Cycle through color options
            color_index = player_prefs['color_index']
            color_index = (color_index + direction) % len(self.color_options)
            player_prefs['color_index'] = color_index
            
        elif current_option == "Accessory":
            # Cycle through accessory options
            current_accessory = player_prefs['accessory']
            current_index = self.accessory_options.index(current_accessory)
            new_index = (current_index + direction) % len(self.accessory_options)
            player_prefs['accessory'] = self.accessory_options[new_index]
            
        elif current_option == "Expression":
            # Cycle through expression options
            current_expression = player_prefs['expression']
            current_index = self.expression_options.index(current_expression)
            new_index = (current_index + direction) % len(self.expression_options)
            player_prefs['expression'] = self.expression_options[new_index]
            
    def select_option(self):
        """Handle menu option selection."""
        if self.selected_option == 0:  # Start Game
            self.apply_customizations()
            self.game.reset_game()
            self.game.state = STATE_PLAYING
        elif self.selected_option == 1:  # Tutorial
            self.apply_customizations()
            self.game.reset_game()
            self.game.state = STATE_TUTORIAL
            self.game.tutorial.start()
        elif self.selected_option == 2:  # Select Level
            self.showing_level_selection = True
        elif self.selected_option == 3:  # Player Count
            self.showing_player_count = True
        elif self.selected_option == 4:  # Customize Characters
            self.showing_customization = True
        elif self.selected_option == 5:  # How to Play
            self.showing_help = True
        elif self.selected_option == 6:  # Quit
            self.game.running = False
            
    def apply_customizations(self):
        """Apply the player preferences to the game."""
        # Store the preferences so they can be used when creating players
        self.game.player_preferences = self.player_preferences
            
    def draw(self, screen):
        """Draw the menu on the screen."""
        # Draw a more appealing background with animated particles
        self.draw_menu_background(screen)
        
        if self.showing_help:
            self.draw_help_screen(screen)
        elif self.showing_customization:
            self.draw_customization_screen(screen)
        elif self.showing_level_selection:
            self.draw_level_selection_screen(screen)
        elif self.showing_player_count:
            self.draw_player_count_screen(screen)
        else:
            self.draw_main_menu(screen)
            
    def draw_menu_background(self, screen):
        """Draw an attractive animated background for all menu screens."""
        # Create a gradient background
        for y in range(0, SCREEN_HEIGHT, 1):
            ratio = y / SCREEN_HEIGHT
            # Deep blue to lighter blue gradient
            r = int(20 + 10 * (1 - ratio))
            g = int(30 + 20 * (1 - ratio))
            b = int(50 + 70 * (1 - ratio))
            color = (r, g, b)
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
            
        # Initialize animated particles if not already done
        if not hasattr(self, 'menu_particles'):
            self.menu_particles = []
            for _ in range(40):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                size = random.randint(1, 4)
                speed = random.uniform(0.5, 1.5)
                color_value = random.randint(150, 255)
                color = (color_value // 3, color_value // 2, color_value)
                self.menu_particles.append([x, y, size, speed, color])
                
        # Update and draw particles
        for i, (x, y, size, speed, color) in enumerate(self.menu_particles):
            # Draw particle
            pygame.draw.circle(screen, color, (int(x), int(y)), size)
            
            # Move particle upward with slight horizontal drift
            self.menu_particles[i][1] = (y - speed) % SCREEN_HEIGHT
            self.menu_particles[i][0] = (x + math.sin(y/30) * 0.5) % SCREEN_WIDTH
            
        # Draw decorative elements based on current menu
        if self.showing_help:
            self.draw_menu_decoration(screen, "help")
        elif self.showing_customization:
            self.draw_menu_decoration(screen, "custom")
        elif self.showing_level_selection:
            self.draw_menu_decoration(screen, "level")
        elif self.showing_player_count:
            self.draw_menu_decoration(screen, "players")
        else:
            self.draw_menu_decoration(screen, "main")
    
    def draw_menu_decoration(self, screen, menu_type):
        """Draw decorative elements specific to each menu type."""
        # Add a subtle frame around the menu area
        frame_rect = pygame.Rect(SCREEN_WIDTH//2 - 250, 50, 500, SCREEN_HEIGHT - 100)
        pygame.draw.rect(screen, (60, 80, 120, 50), frame_rect, 3, border_radius=15)
        
        # Add decoration corners
        corner_size = 20
        corner_color = (180, 200, 255)
        
        # Top left corner
        pygame.draw.line(screen, corner_color, 
                        (frame_rect.left, frame_rect.top + corner_size), 
                        (frame_rect.left, frame_rect.top), 2)
        pygame.draw.line(screen, corner_color, 
                        (frame_rect.left, frame_rect.top), 
                        (frame_rect.left + corner_size, frame_rect.top), 2)
        
        # Top right corner
        pygame.draw.line(screen, corner_color, 
                        (frame_rect.right - corner_size, frame_rect.top), 
                        (frame_rect.right, frame_rect.top), 2)
        pygame.draw.line(screen, corner_color, 
                        (frame_rect.right, frame_rect.top), 
                        (frame_rect.right, frame_rect.top + corner_size), 2)
        
        # Bottom left corner
        pygame.draw.line(screen, corner_color, 
                        (frame_rect.left, frame_rect.bottom - corner_size), 
                        (frame_rect.left, frame_rect.bottom), 2)
        pygame.draw.line(screen, corner_color, 
                        (frame_rect.left, frame_rect.bottom), 
                        (frame_rect.left + corner_size, frame_rect.bottom), 2)
        
        # Bottom right corner
        pygame.draw.line(screen, corner_color, 
                        (frame_rect.right - corner_size, frame_rect.bottom), 
                        (frame_rect.right, frame_rect.bottom), 2)
        pygame.draw.line(screen, corner_color, 
                        (frame_rect.right, frame_rect.bottom), 
                        (frame_rect.right, frame_rect.bottom - corner_size), 2)
                        
        # Add specific decoration based on menu type
        if menu_type == "main":
            # Add player silhouettes chasing each other
            player_colors = [(220, 60, 80), (60, 140, 220), (60, 180, 80), (200, 120, 220)]
            
            # Determine current animation state based on time
            animation_time = pygame.time.get_ticks() / 1000
            circle_center = (SCREEN_WIDTH // 2, 450)
            circle_radius = 80
            
            for i in range(4):
                angle = animation_time * 1.5 + i * (math.pi / 2)
                player_x = circle_center[0] + math.cos(angle) * circle_radius
                player_y = circle_center[1] + math.sin(angle) * circle_radius
                pygame.draw.circle(screen, player_colors[i], (int(player_x), int(player_y)), 15)
                
                # Add simple face
                eye_offset = 5
                pygame.draw.circle(screen, WHITE, (int(player_x - eye_offset), int(player_y - 3)), 3)
                pygame.draw.circle(screen, WHITE, (int(player_x + eye_offset), int(player_y - 3)), 3)
                
                # Add simple smile
                smile_rect = pygame.Rect(int(player_x) - 6, int(player_y) + 2, 12, 6)
                pygame.draw.arc(screen, WHITE, smile_rect, 0, math.pi, 2)
            
    def draw_player_count_screen(self, screen):
        """Draw the player count selection screen."""
        # Draw title
        draw_text(screen, "PLAYER COUNT", 40, SCREEN_WIDTH // 2, 80, YELLOW)
        
        # Draw selection
        draw_text(screen, "Select number of players:", 28, SCREEN_WIDTH // 2, 160, WHITE)
        
        # Player count selector with visual indicator
        count_y = 240
        
        # Draw selector background
        selector_width = 350
        selector_height = 60
        selector_x = SCREEN_WIDTH // 2 - selector_width // 2
        selector_rect = pygame.Rect(selector_x, count_y - selector_height // 2, selector_width, selector_height)
        pygame.draw.rect(screen, DARK_BLUE, selector_rect, border_radius=10)
        pygame.draw.rect(screen, LIGHT_BLUE, selector_rect, 2, border_radius=10)
        
        # Draw selector buttons
        for i in range(2, 5):  # For players 2, 3, 4
            button_width = selector_width // 3
            button_x = selector_x + (i-2) * button_width
            button_rect = pygame.Rect(button_x, count_y - selector_height // 2, button_width, selector_height)
            
            # Highlight selected count
            if i == self.player_count:
                pygame.draw.rect(screen, GREEN, button_rect, border_radius=10)
                text_color = WHITE
            else:
                text_color = LIGHT_GRAY
            
            # Draw player number
            draw_text(screen, str(i), 32, button_x + button_width // 2, count_y, text_color)
        
        # Draw player avatars
        avatar_y = 320
        avatar_spacing = 100
        avatar_size = 40
        
        # Calculate start position based on player count
        total_width = (self.player_count - 1) * avatar_spacing
        start_x = SCREEN_WIDTH // 2 - total_width // 2
        
        # Player colors
        player_colors = [
            (220, 60, 80),    # Player 1 - Red
            (60, 140, 220),   # Player 2 - Blue
            (60, 180, 80),    # Player 3 - Green
            (200, 120, 220)   # Player 4 - Purple
        ]
        
        # Draw player avatars
        for i in range(self.player_count):
            avatar_x = start_x + i * avatar_spacing
            color = player_colors[i]
            
            # Draw circular avatar
            pygame.draw.circle(screen, color, (avatar_x, avatar_y), avatar_size)
            pygame.draw.circle(screen, self.get_highlight_color(color), 
                              (int(avatar_x - avatar_size * 0.3), int(avatar_y - avatar_size * 0.3)), 
                              int(avatar_size * 0.3))
            
            # Draw player number
            draw_text(screen, f"P{i+1}", 24, avatar_x, avatar_y + avatar_size + 20, color)
            
            # Draw controls info
            if i == 0:
                controls = "WASD"
            elif i == 1:
                controls = "Arrows"
            elif i == 2:
                controls = "IJKL"
            elif i == 3:
                controls = "TFGH"
                
            draw_text(screen, controls, 16, avatar_x, avatar_y + avatar_size + 45, LIGHT_GRAY)
        
        # Instructions
        instructions = [
            "Left/Right Arrow: Change player count",
            "ENTER: Confirm selection", 
            "ESC: Return to menu"
        ]
        
        footer_y = SCREEN_HEIGHT - (len(instructions) + 1) * 25
        for instruction in instructions:
            draw_text(screen, instruction, 16, SCREEN_WIDTH // 2, footer_y, LIGHT_GRAY)
            footer_y += 25
            
    def draw_customization_screen(self, screen):
        """Draw the character customization screen."""
        # Draw title
        draw_text(screen, "CHARACTER CUSTOMIZATION", 40, SCREEN_WIDTH // 2, 80, YELLOW)
        
        # Draw which player is being customized
        player_text = f"Player {self.customizing_player}"
        draw_text(screen, player_text, 30, SCREEN_WIDTH // 2, 130, self.get_player_color())
        
        # Draw customization options
        option_y = 180
        for i, option in enumerate(self.customization_options):
            selected = (i == self.customization_option)
            option_color = GREEN if selected else WHITE
            prefix = "> " if selected else "  "
            suffix = " <" if selected else "  "
            
            # Get the current value for this option
            value = self.get_customization_value(option)
            
            # Draw the option and its current value
            draw_text(screen, f"{prefix}{option}: {value}{suffix}", 25, 
                     SCREEN_WIDTH // 2, option_y, option_color)
            option_y += 40
        
        # Preview the character
        self.draw_character_preview(screen)
        
        # Instructions footer
        instructions = [
            "Arrow keys: Navigate and change options",
            "TAB: Switch between players",
            "ENTER: Select option",
            "ESC: Return to menu"
        ]
        
        footer_y = SCREEN_HEIGHT - (len(instructions) + 1) * 25
        for instruction in instructions:
            draw_text(screen, instruction, 16, SCREEN_WIDTH // 2, footer_y, LIGHT_GRAY)
            footer_y += 25
    
    def get_customization_value(self, option):
        """Get the display value for a customization option."""
        player_prefs = self.player_preferences[self.customizing_player]
        
        if option == "Color":
            color_index = player_prefs['color_index']
            color_names = ["Red", "Blue", "Green", "Yellow", "Purple", "Cyan", "Orange"]
            return color_names[color_index]
            
        elif option == "Accessory":
            return player_prefs['accessory'].capitalize()
            
        elif option == "Expression":
            return player_prefs['expression'].capitalize()
            
        return ""
    
    def get_player_color(self):
        """Get the current color for the player being customized."""
        color_index = self.player_preferences[self.customizing_player]['color_index']
        return self.color_options[color_index]
        
    def draw_character_preview(self, screen):
        """Draw a preview of the character with current customizations."""
        # Preview area
        preview_x = SCREEN_WIDTH // 2
        preview_y = 390
        preview_size = 80
        
        # Get player preferences
        player_prefs = self.player_preferences[self.customizing_player]
        color = self.color_options[player_prefs['color_index']]
        expression = player_prefs['expression']
        accessory = player_prefs['accessory']
        
        # Draw blob body
        pygame.draw.circle(screen, color, (preview_x, preview_y), preview_size)
        
        # Draw highlight
        highlight_color = self.get_highlight_color(color)
        pygame.draw.circle(
            screen, 
            highlight_color, 
            (int(preview_x - preview_size * 0.3), int(preview_y - preview_size * 0.3)), 
            int(preview_size * 0.3)
        )
        
        # Draw eyes
        eye_size = preview_size * 0.2
        eye_spacing = preview_size * 0.4
        
        # Left eye
        pygame.draw.circle(
            screen, 
            WHITE, 
            (int(preview_x - eye_spacing), int(preview_y - preview_size * 0.1)), 
            int(eye_size)
        )
        
        # Right eye
        pygame.draw.circle(
            screen, 
            WHITE, 
            (int(preview_x + eye_spacing), int(preview_y - preview_size * 0.1)), 
            int(eye_size)
        )
        
        # Draw pupils
        pygame.draw.circle(
            screen, 
            BLACK, 
            (int(preview_x - eye_spacing), int(preview_y - preview_size * 0.1)), 
            int(eye_size * 0.5)
        )
        pygame.draw.circle(
            screen, 
            BLACK, 
            (int(preview_x + eye_spacing), int(preview_y - preview_size * 0.1)), 
            int(eye_size * 0.5)
        )
        
        # Draw expression-based mouth
        mouth_y = preview_y + preview_size * 0.2
        if expression == "happy":
            # Happy smile
            pygame.draw.arc(
                screen,
                BLACK,
                (int(preview_x - preview_size * 0.4), int(mouth_y - preview_size * 0.2), 
                 int(preview_size * 0.8), int(preview_size * 0.4)),
                0, 3.14,
                3
            )
        elif expression == "curious":
            # 'O' mouth
            pygame.draw.circle(
                screen,
                BLACK,
                (preview_x, int(mouth_y)),
                int(preview_size * 0.15),
                3
            )
        elif expression == "determined":
            # Straight line
            pygame.draw.line(
                screen,
                BLACK,
                (int(preview_x - preview_size * 0.3), int(mouth_y)),
                (int(preview_x + preview_size * 0.3), int(mouth_y)),
                3
            )
        elif expression == "surprised":
            # Surprised mouth
            pygame.draw.ellipse(
                screen,
                BLACK,
                (int(preview_x - preview_size * 0.25), int(mouth_y - preview_size * 0.15),
                 int(preview_size * 0.5), int(preview_size * 0.3)),
                3
            )
        elif expression == "excited":
            # Excited open smile
            pygame.draw.arc(
                screen,
                BLACK,
                (int(preview_x - preview_size * 0.4), int(mouth_y - preview_size * 0.2), 
                 int(preview_size * 0.8), int(preview_size * 0.4)),
                0, 3.14,
                3
            )
            # Add a small line in the middle for open mouth effect
            pygame.draw.line(
                screen,
                BLACK,
                (int(preview_x), int(mouth_y)),
                (int(preview_x), int(mouth_y + preview_size * 0.15)),
                2
            )
        
        # Draw accessory
        if accessory == "bow":
            # Draw a bow on top
            bow_y = preview_y - preview_size - 5
            bow_width = preview_size * 0.5
            bow_height = preview_size * 0.3
            bow_color = (255, 100, 150)
            
            # Bow center
            pygame.draw.circle(screen, bow_color, (preview_x, int(bow_y)), int(bow_height * 0.4))
            
            # Left bow
            pygame.draw.ellipse(
                screen, 
                bow_color,
                (int(preview_x - bow_width), int(bow_y - bow_height/2), 
                 int(bow_width * 0.8), int(bow_height))
            )
            
            # Right bow
            pygame.draw.ellipse(
                screen, 
                bow_color,
                (int(preview_x + bow_width * 0.2), int(bow_y - bow_height/2), 
                 int(bow_width * 0.8), int(bow_height))
            )
            
        elif accessory == "hat":
            # Draw a hat
            hat_y = preview_y - preview_size - 5
            hat_width = preview_size * 0.8
            hat_height = preview_size * 0.5
            hat_color = (60, 60, 180)
            
            # Hat base
            pygame.draw.ellipse(
                screen,
                hat_color,
                (int(preview_x - hat_width/2), int(hat_y), 
                 int(hat_width), int(hat_height * 0.4))
            )
            
            # Hat top
            pygame.draw.rect(
                screen,
                hat_color,
                (int(preview_x - hat_width/4), int(hat_y - hat_height * 0.8),
                 int(hat_width/2), int(hat_height * 0.8))
            )
            
        elif accessory == "glasses":
            # Draw glasses
            glasses_y = preview_y - preview_size * 0.1
            glasses_width = preview_size * 0.4
            glasses_color = (30, 30, 30)
            
            # Left lens
            pygame.draw.circle(
                screen,
                glasses_color,
                (int(preview_x - glasses_width), int(glasses_y)),
                int(preview_size * 0.25),
                2
            )
            
            # Right lens
            pygame.draw.circle(
                screen,
                glasses_color,
                (int(preview_x + glasses_width), int(glasses_y)),
                int(preview_size * 0.25),
                2
            )
            
            # Bridge
            pygame.draw.line(
                screen,
                glasses_color,
                (int(preview_x - glasses_width * 0.5), int(glasses_y)),
                (int(preview_x + glasses_width * 0.5), int(glasses_y)),
                2
            )
            
        elif accessory == "bowtie":
            # Draw bowtie
            bowtie_y = preview_y + preview_size * 0.7
            bowtie_width = preview_size * 0.6
            bowtie_height = preview_size * 0.3
            bowtie_color = (200, 0, 0)
            
            # Left side
            pygame.draw.polygon(
                screen,
                bowtie_color,
                [
                    (preview_x, bowtie_y),
                    (int(preview_x - bowtie_width), int(bowtie_y - bowtie_height/2)),
                    (int(preview_x - bowtie_width), int(bowtie_y + bowtie_height/2))
                ]
            )
            
            # Right side
            pygame.draw.polygon(
                screen,
                bowtie_color,
                [
                    (preview_x, bowtie_y),
                    (int(preview_x + bowtie_width), int(bowtie_y - bowtie_height/2)),
                    (int(preview_x + bowtie_width), int(bowtie_y + bowtie_height/2))
                ]
            )
            
            # Center knot
            pygame.draw.circle(screen, bowtie_color, (preview_x, int(bowtie_y)), int(preview_size * 0.1))
            
        elif accessory == "crown":
            # Draw a royal crown
            crown_y = preview_y - preview_size - 10
            crown_width = preview_size * 0.7
            crown_height = preview_size * 0.4
            crown_color = (220, 180, 20)  # Gold color
            
            # Crown base
            pygame.draw.rect(
                screen,
                crown_color,
                (int(preview_x - crown_width/2), int(crown_y + crown_height * 0.6),
                 int(crown_width), int(crown_height * 0.4))
            )
            
            # Crown spikes
            spike_count = 5
            for i in range(spike_count):
                spike_x = preview_x - crown_width/2 + (crown_width * i / (spike_count - 1))
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
                (int(preview_x), int(crown_y + crown_height * 0.3)),
                int(crown_width * 0.06)
            )
    
    def get_highlight_color(self, color):
        """Generate a lighter version of a color for highlights."""
        r = min(255, color[0] + 70)
        g = min(255, color[1] + 70)
        b = min(255, color[2] + 70)
        return (r, g, b)
            
    def draw_main_menu(self, screen):
        """Draw the main menu options with enhanced visuals."""
        # Draw title with a glow effect
        title_color = YELLOW
        title_text = "TAG GAME"
        title_y = 100
        title_x = SCREEN_WIDTH // 2
        title_size = 60
        
        # Draw glow (larger size, semi-transparent)
        for offset in range(5, 0, -1):
            alpha = 150 - offset * 25  # Fade out
            glow_color = (*title_color, alpha)
            glow_size = title_size + offset * 2
            glow_surf = pygame.Surface((SCREEN_WIDTH, 100), pygame.SRCALPHA)
            draw_text(glow_surf, title_text, glow_size, SCREEN_WIDTH // 2, 50, glow_color)
            screen.blit(glow_surf, (0, title_y - 50))
        
        # Draw actual title
        draw_text(screen, title_text, title_size, title_x, title_y, title_color)
        
        # Draw subtitle
        draw_text(screen, "A Fast-Paced Multiplayer Chase", 24, title_x, title_y + 50, (220, 220, 220))
        
        # Draw menu options with better styling
        options_start_y = 220
        for i, option in enumerate(self.options):
            option_y = options_start_y + i * 50
            is_selected = (i == self.selected_option)
            
            # Create button-like appearance for options
            option_width = 250
            option_height = 40
            option_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - option_width // 2, 
                option_y - option_height // 2,
                option_width, 
                option_height
            )
            
            if is_selected:
                # Selected option has a filled background with animation
                pulse = (math.sin(pygame.time.get_ticks() / 200) + 1) * 0.5  # Value oscillates between 0 and 1
                highlight_color = (
                    min(255, int(30 + 40 * pulse)),
                    min(255, int(100 + 40 * pulse)),
                    min(255, int(50 + 40 * pulse))
                )
                pygame.draw.rect(screen, highlight_color, option_rect, border_radius=10)
                pygame.draw.rect(screen, GREEN, option_rect, 2, border_radius=10)
                text_color = WHITE
                
                # Draw animated arrow indicators
                arrow_offset = 10 + int(pulse * 5)  # Animate the arrows
                arrow_x1 = option_rect.left - arrow_offset
                arrow_x2 = option_rect.right + arrow_offset
                pygame.draw.polygon(screen, WHITE, [
                    (arrow_x1, option_y),
                    (arrow_x1 - 10, option_y - 10),
                    (arrow_x1 - 10, option_y + 10)
                ])
                pygame.draw.polygon(screen, WHITE, [
                    (arrow_x2, option_y),
                    (arrow_x2 + 10, option_y - 10),
                    (arrow_x2 + 10, option_y + 10)
                ])
            else:
                # Unselected options have a subtle background
                pygame.draw.rect(screen, (40, 50, 70, 180), option_rect, border_radius=10)
                pygame.draw.rect(screen, (100, 120, 150), option_rect, 1, border_radius=10)
                text_color = LIGHT_GRAY
                
            # Draw the option text
            draw_text(screen, option, 28, SCREEN_WIDTH // 2, option_y, text_color)
            
        # Draw version and credits with a nicer format
        footer_rect = pygame.Rect(0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 60)
        pygame.draw.rect(screen, (0, 0, 30, 150), footer_rect)
        pygame.draw.line(screen, (100, 100, 150, 200), 
                        (0, SCREEN_HEIGHT - 60), 
                        (SCREEN_WIDTH, SCREEN_HEIGHT - 60), 1)
        
        draw_text(screen, "Created with Pygame & Pymunk", 16, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40, LIGHT_BLUE)
        draw_text(screen, "v1.0.0", 14, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20, LIGHT_GRAY)
        
        # Draw controls hint
        controls_text = "Arrow Keys: Navigate | Enter: Select"
        draw_text(screen, controls_text, 16, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 75, LIGHT_GRAY)
        
    def draw_level_selection_screen(self, screen):
        """Draw the level selection screen."""
        # Draw title
        draw_text(screen, "SELECT LEVEL", 40, SCREEN_WIDTH // 2, 80, YELLOW)
        
        # Draw level options
        option_y = 140
        for i, level in enumerate(self.level_options):
            selected = (i == self.selected_level)
            option_color = GREEN if selected else WHITE
            prefix = "> " if selected else "  "
            suffix = " <" if selected else "  "
            
            # Draw the level name
            draw_text(screen, f"{prefix}{level}{suffix}", 28, SCREEN_WIDTH // 2, option_y, option_color)
            option_y += 40
            
            # If this level is selected, show its description
            if selected:
                description = self.level_descriptions[level]
                # Draw description with word wrapping
                if len(description) > 50:  # Simple word wrap
                    first_half = description[:50].rsplit(' ', 1)[0]
                    second_half = description[len(first_half):].strip()
                    draw_text(screen, first_half, 16, SCREEN_WIDTH // 2, option_y, LIGHT_GRAY)
                    option_y += 25
                    draw_text(screen, second_half, 16, SCREEN_WIDTH // 2, option_y, LIGHT_GRAY)
                else:
                    draw_text(screen, description, 16, SCREEN_WIDTH // 2, option_y, LIGHT_GRAY)
                option_y += 30
        
        # Draw level preview
        self.draw_level_preview(screen, self.level_options[self.selected_level])
        
        # Back instruction
        draw_text(screen, "Press ENTER to select, ESC to return", 20, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40, GREEN)
        
    def draw_level_preview(self, screen, level_name):
        """Draw a preview of the selected level."""
        # Preview area
        preview_x = SCREEN_WIDTH // 2
        preview_y = 350
        preview_width = 300
        preview_height = 150
        
        # Draw preview background
        preview_rect = pygame.Rect(
            preview_x - preview_width // 2,
            preview_y - preview_height // 2,
            preview_width,
            preview_height
        )
        pygame.draw.rect(screen, DARK_GRAY, preview_rect)
        pygame.draw.rect(screen, LIGHT_GRAY, preview_rect, 2)
        
        # Draw level-specific preview
        if level_name == "Classic":
            # Classic layout
            self.draw_platform_preview(screen, preview_rect, [
                ((0.2, 0.8), 0.4, GRAY),       # Bottom platforms
                ((0.7, 0.8), 0.4, PURPLE),
                ((0.15, 0.6), 0.3, GREEN),    # Middle platforms
                ((0.5, 0.5), 0.2, CYAN),
                ((0.8, 0.6), 0.3, YELLOW),
                ((0.3, 0.3), 0.25, GRAY),     # Upper platforms
                ((0.65, 0.4), 0.25, GREEN)
            ])
        elif level_name == "Sky Islands":
            # Sky Islands layout - floating platforms with gaps
            self.draw_platform_preview(screen, preview_rect, [
                ((0.2, 0.8), 0.2, GRAY),      # Bottom islands
                ((0.5, 0.8), 0.2, GRAY),
                ((0.8, 0.8), 0.2, GRAY),
                ((0.35, 0.6), 0.2, GREEN),    # Middle islands
                ((0.65, 0.6), 0.2, YELLOW),
                ((0.2, 0.4), 0.2, CYAN),      # Upper islands
                ((0.5, 0.4), 0.2, CYAN),
                ((0.8, 0.4), 0.2, GREEN),
                ((0.35, 0.2), 0.2, PURPLE),   # Top islands
                ((0.65, 0.2), 0.2, PURPLE)
            ])
        elif level_name == "Urban Playground":
            # Urban Playground - symmetrical with many connections
            self.draw_platform_preview(screen, preview_rect, [
                ((0.5, 0.9), 0.9, GRAY),      # Base floor
                ((0.3, 0.7), 0.3, YELLOW),    # Left mid platform
                ((0.7, 0.7), 0.3, YELLOW),    # Right mid platform
                ((0.5, 0.5), 0.5, CYAN),      # Central platform
                ((0.2, 0.3), 0.25, GREEN),    # Upper left
                ((0.8, 0.3), 0.25, GREEN),    # Upper right
                ((0.5, 0.2), 0.4, PURPLE)     # Top platform
            ])
        elif level_name == "Maze Runner":
            # Maze Runner - complex layout with many paths
            self.draw_platform_preview(screen, preview_rect, [
                ((0.5, 0.9), 0.9, GRAY),      # Bottom floor
                ((0.2, 0.7), 0.3, CYAN),     
                ((0.8, 0.7), 0.3, GRAY),     
                ((0.5, 0.6), 0.3, PURPLE),    
                ((0.3, 0.5), 0.3, GRAY),     
                ((0.7, 0.5), 0.3, YELLOW),   
                ((0.2, 0.4), 0.3, GREEN),    
                ((0.5, 0.3), 0.3, CYAN),      
                ((0.8, 0.4), 0.3, GRAY),     
                ((0.5, 0.15), 0.5, GRAY)      # Top platform
            ])
        elif level_name == "Obstacle Course":
            # Obstacle Course - challenging layout
            self.draw_platform_preview(screen, preview_rect, [
                ((0.5, 0.9), 0.4, GRAY),      # Start platform
                ((0.2, 0.75), 0.15, PURPLE),  # Obstacles
                ((0.4, 0.65), 0.15, YELLOW),
                ((0.6, 0.55), 0.15, GREEN),
                ((0.8, 0.45), 0.15, CYAN),
                ((0.7, 0.35), 0.15, PURPLE),
                ((0.5, 0.25), 0.15, GREEN),
                ((0.3, 0.15), 0.15, YELLOW),
                ((0.1, 0.35), 0.15, GREEN),
                ((0.9, 0.8), 0.15, CYAN)
            ])
        
        # Draw player indicators based on player count
        p_y = int(preview_rect.top + 20)
        player_colors = []
        
        # Get colors for all active players
        for i in range(1, self.player_count + 1):
            player_colors.append(self.color_options[self.player_preferences[i]['color_index']])
        
        # Calculate spacing based on player count
        spacing = preview_width / (self.player_count + 1)
        
        # Draw each player blob
        for i in range(self.player_count):
            p_x = int(preview_rect.left + spacing * (i + 1))
            # Draw player blob
            pygame.draw.circle(screen, player_colors[i], (p_x, p_y), 10)
        
    def draw_platform_preview(self, screen, preview_rect, platforms):
        """Helper to draw a list of platforms within the preview area."""
        x_offset = preview_rect.left
        y_offset = preview_rect.top
        width = preview_rect.width
        height = preview_rect.height
        
        for (rel_x, rel_y), rel_width, color in platforms:
            platform_x = x_offset + int(width * rel_x)
            platform_y = y_offset + int(height * rel_y)
            platform_width = int(width * rel_width)
            platform_height = 8  # Fixed platform height for preview
            
            platform_rect = pygame.Rect(
                platform_x - platform_width // 2,
                platform_y - platform_height // 2,
                platform_width,
                platform_height
            )
            pygame.draw.rect(screen, color, platform_rect)
            
    def draw_help_screen(self, screen):
        """Draw the help/instructions screen."""
        # Draw title
        draw_text(screen, "HOW TO PLAY", 40, SCREEN_WIDTH // 2, 80, YELLOW)
        
        # Draw instructions - now split into two columns
        left_column = [
            "Tag Game is a multiplayer game where one player is the tagger",
            "and tries to tag the other players.",
            "",
            "Controls:",
            "Player 1: WASD to move and jump",
            "Player 2: Arrow keys to move and jump",
            "Player 3: IJKL to move and jump",
            "Player 4: TFGH to move and jump",
            "",
            "Press DOWN to pass through certain platforms",
            "Press T to change tagger properties",
            "Press ESC to pause the game",
            "",
            "Platform Types:",
            "Gray - Regular platform",
            "Purple - Sticky platform (slows you down)",
            "Green - Jump platform (higher jumps)",
            "Yellow - Speed platform (move faster)",
            "Cyan - Pass-through platform (press DOWN)",
            "",
            "First player to score 5 tags wins!"
        ]
        
        right_column = [
            "Power-Ups:",
            "",
            "Speed (Lightning) - Move faster",
            "Shield (Circle) - Block one tag attempt",
            "Super Jump (Arrow) - Higher jumps",
            "Invisibility (Ghost) - Become harder to see",
            "Freeze (Snowflake) - Freeze the other player",
            "",
            "Power-up effects last for a limited time.",
            "Only one power-up can be active at a time.",
            "Flashing power-ups will despawn soon!",
            "",
            "Collect power-ups by running over them.",
            "Use power-ups strategically to win!"
        ]
        
        # Draw left column
        left_x = SCREEN_WIDTH // 3
        y_pos = 140
        for line in left_column:
            if line:
                draw_text(screen, line, 18, left_x, y_pos, WHITE)
            y_pos += 25
        
        # Draw right column
        right_x = (SCREEN_WIDTH // 3) * 2
        y_pos = 140
        for line in right_column:
            if line:
                draw_text(screen, line, 18, right_x, y_pos, WHITE)
            y_pos += 25
            
        # Back instruction
        draw_text(screen, "Press ENTER to return to menu", 20, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40, GREEN)
