"""
UI module for the Tag Game.
Defines the UI class for handling game interface elements.
"""

import pygame
from constants import *
import time

class UI:
    def __init__(self, game):
        """
        Initialize the UI manager.
        
        Args:
            game: reference to the main game object
        """
        self.game = game
        
        # Load fonts
        pygame.font.init()
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.font_tiny = pygame.font.Font(None, 24)
        
        # UI state
        self.round_end_message = ""
        self.game_end_message = ""
        self.show_message_until = 0
        
        # UI elements
        self.create_ui_elements()
        
    def create_ui_elements(self):
        """Create UI elements like buttons, labels, etc."""
        # Start button
        button_width, button_height = 200, 50
        self.start_button_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - button_width // 2,
            SCREEN_HEIGHT // 2 + 100,
            button_width, button_height
        )
        
    def show_title_screen(self, screen):
        """
        Display the title screen until player starts the game.
        
        Args:
            screen: screen surface to draw on
        """
        waiting_for_start = True
        
        # Background colors
        bg_color = (30, 30, 50)
        header_color = (50, 50, 80)
        
        while waiting_for_start:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                    
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting_for_start = False
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.start_button_rect.collidepoint(event.pos):
                        waiting_for_start = False
                        
            # Fill background
            screen.fill(bg_color)
            
            # Draw title header
            pygame.draw.rect(screen, header_color, (0, 50, SCREEN_WIDTH, 150))
            
            # Draw title
            title_text = self.font_large.render("TAG ARENA", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 125))
            screen.blit(title_text, title_rect)
            
            # Draw game description
            desc_lines = [
                "A two-player tag game with custom physics and power-ups!",
                "",
                "Player 1 Controls: WASD",
                "Player 2 Controls: Arrow Keys",
                "",
                "Platform Types:",
                "- Gray: Normal platforms",
                "- Orange: Sticky platforms (slow movement)",
                "- Green: Jump platforms (higher jumps)",
                "- Blue: Speed platforms (faster movement)",
                "- Purple: Pass-through platforms (press DOWN to drop through)",
                "",
                "Power-ups:",
                "- Yellow: Speed Boost",
                "- Blue: Shield (temporary tag immunity)",
                "- Light Blue: Freeze (freeze opponent)",
                "- Green: Super Jump",
                "- Purple: Invisibility"
            ]
            
            y_pos = 220
            for line in desc_lines:
                text = self.font_tiny.render(line, True, (255, 255, 255))
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
                screen.blit(text, text_rect)
                y_pos += 25
                
            # Draw start button
            pygame.draw.rect(screen, (80, 180, 80), self.start_button_rect)
            pygame.draw.rect(screen, (50, 150, 50), self.start_button_rect, 3)
            
            start_text = self.font_medium.render("START GAME", True, (255, 255, 255))
            start_text_rect = start_text.get_rect(center=self.start_button_rect.center)
            screen.blit(start_text, start_text_rect)
            
            # Draw press space message
            space_text = self.font_small.render("or press SPACE to start", True, (200, 200, 200))
            space_rect = space_text.get_rect(center=(SCREEN_WIDTH // 2, self.start_button_rect.bottom + 40))
            screen.blit(space_text, space_rect)
            
            pygame.display.flip()
            pygame.time.wait(10)
            
    def set_round_end_message(self, message):
        """
        Set a message to display at the end of a round.
        
        Args:
            message: string message to display
        """
        self.round_end_message = message
        self.show_message_until = time.time() + 3.0  # Show for 3 seconds
        
    def set_game_end_message(self, message):
        """
        Set a message to display at the end of the game.
        
        Args:
            message: string message to display
        """
        self.game_end_message = message
        self.show_message_until = time.time() + 5.0  # Show for 5 seconds
        
    def draw_player_stats(self, screen):
        """
        Draw player stats (score, tagger status, active effects).
        
        Args:
            screen: screen surface to draw on
        """
        # Player 1 stats - left side
        player1 = self.game.player1
        
        # Background box
        p1_box = pygame.Rect(10, 10, 250, 80)
        pygame.draw.rect(screen, (20, 20, 30, 200), p1_box)
        pygame.draw.rect(screen, player1.color, p1_box, 3)
        
        # Name and score
        p1_name = self.font_small.render(f"Player 1: {player1.score}", True, WHITE)
        screen.blit(p1_name, (20, 15))
        
        # Status (tagger or runner)
        status_text = "TAGGER" if player1.is_tagger else "RUNNER"
        status_color = TAGGER_COLOR if player1.is_tagger else BLUE
        p1_status = self.font_small.render(status_text, True, status_color)
        screen.blit(p1_status, (20, 45))
        
        # Player 2 stats - right side
        player2 = self.game.player2
        
        # Background box
        p2_box = pygame.Rect(SCREEN_WIDTH - 260, 10, 250, 80)
        pygame.draw.rect(screen, (20, 20, 30, 200), p2_box)
        pygame.draw.rect(screen, player2.color, p2_box, 3)
        
        # Name and score
        p2_name = self.font_small.render(f"Player 2: {player2.score}", True, WHITE)
        p2_name_rect = p2_name.get_rect(topright=(SCREEN_WIDTH - 20, 15))
        screen.blit(p2_name, p2_name_rect)
        
        # Status (tagger or runner)
        status_text = "TAGGER" if player2.is_tagger else "RUNNER"
        status_color = TAGGER_COLOR if player2.is_tagger else BLUE
        p2_status = self.font_small.render(status_text, True, status_color)
        p2_status_rect = p2_status.get_rect(topright=(SCREEN_WIDTH - 20, 45))
        screen.blit(p2_status, p2_status_rect)
        
        # Draw active power-ups for each player
        self.draw_active_powerups(screen, player1, 20, 90)
        self.draw_active_powerups(screen, player2, SCREEN_WIDTH - 170, 90)
        
    def draw_active_powerups(self, screen, player, x, y):
        """
        Draw indicators for active power-ups.
        
        Args:
            screen: screen surface to draw on
            player: player object
            x, y: position to start drawing indicators
        """
        icon_size = 24
        spacing = 30
        
        # Create a semi-transparent background for the power-up icons
        icon_bg_width = len(POWERUP_TYPES) * spacing
        icon_bg = pygame.Rect(x - 5, y - 5, icon_bg_width, icon_size + 10)
        pygame.draw.rect(screen, (0, 0, 0, 128), icon_bg)
        
        # Draw powerup icons
        for i, powerup_type in enumerate(POWERUP_TYPES):
            icon_x = x + i * spacing
            icon_color = POWERUP_COLORS[powerup_type]
            
            # Draw icon background (gray if inactive, colored if active)
            if powerup_type in player.active_powerups:
                pygame.draw.circle(screen, icon_color, (icon_x, y + icon_size//2), icon_size//2)
                
                # Draw remaining time indicator
                remaining = player.active_powerups[powerup_type] / POWERUP_DURATION
                pygame.draw.rect(screen, WHITE, 
                                (icon_x - icon_size//2, y + icon_size + 2, 
                                icon_size * remaining, 3))
            else:
                # Draw inactive icon
                pygame.draw.circle(screen, (70, 70, 70), (icon_x, y + icon_size//2), icon_size//2)
                
            # Draw icon outline
            pygame.draw.circle(screen, WHITE, (icon_x, y + icon_size//2), icon_size//2, 1)
            
            # Draw icon symbol based on powerup type
            if powerup_type == "speed":
                # Lightning bolt
                pygame.draw.line(screen, BLACK, (icon_x - 3, y + 5), (icon_x + 3, y + icon_size - 5), 2)
            elif powerup_type == "shield":
                # Shield outline
                pygame.draw.circle(screen, BLACK, (icon_x, y + icon_size//2), icon_size//3, 2)
            elif powerup_type == "freeze":
                # Snowflake
                pygame.draw.line(screen, BLACK, (icon_x, y + 5), (icon_x, y + icon_size - 5), 2)
                pygame.draw.line(screen, BLACK, (icon_x - 6, y + icon_size//2), (icon_x + 6, y + icon_size//2), 2)
            elif powerup_type == "super_jump":
                # Up arrow
                points = [(icon_x, y + 5), (icon_x - 5, y + 15), (icon_x + 5, y + 15)]
                pygame.draw.polygon(screen, BLACK, points, 2)
            elif powerup_type == "invisible":
                # Eye with line through it
                pygame.draw.circle(screen, BLACK, (icon_x, y + icon_size//2), icon_size//4, 1)
                pygame.draw.line(screen, BLACK, (icon_x - 6, y + icon_size//2 - 6), 
                                (icon_x + 6, y + icon_size//2 + 6), 2)
        
    def draw_round_timer(self, screen):
        """
        Draw the round timer and round number.
        
        Args:
            screen: screen surface to draw on
        """
        # Draw round number
        round_text = self.font_small.render(f"Round {self.game.round_number}", True, WHITE)
        round_rect = round_text.get_rect(center=(SCREEN_WIDTH // 2, 20))
        screen.blit(round_text, round_rect)
        
        # Draw timer background
        timer_width = 200
        timer_height = 30
        timer_bg = pygame.Rect(
            SCREEN_WIDTH // 2 - timer_width // 2, 
            40, 
            timer_width, 
            timer_height
        )
        pygame.draw.rect(screen, (40, 40, 40), timer_bg)
        
        # Draw timer fill
        if self.game.round_time_left > 0 and self.game.round_in_progress:
            fill_width = (self.game.round_time_left / ROUND_TIME) * timer_width
            timer_fill = pygame.Rect(
                SCREEN_WIDTH // 2 - timer_width // 2, 
                40, 
                fill_width, 
                timer_height
            )
            
            # Change color based on time left
            if self.game.round_time_left < 10:
                fill_color = RED
            elif self.game.round_time_left < 20:
                fill_color = YELLOW
            else:
                fill_color = GREEN
                
            pygame.draw.rect(screen, fill_color, timer_fill)
            
        # Draw timer border
        pygame.draw.rect(screen, WHITE, timer_bg, 2)
        
        # Draw timer text
        minutes = int(self.game.round_time_left) // 60
        seconds = int(self.game.round_time_left) % 60
        timer_text = self.font_small.render(f"{minutes:01d}:{seconds:02d}", True, WHITE)
        timer_text_rect = timer_text.get_rect(center=timer_bg.center)
        screen.blit(timer_text, timer_text_rect)
        
    def draw_round_start_message(self, screen):
        """
        Draw the round start message.
        
        Args:
            screen: screen surface to draw on
        """
        if not self.game.round_in_progress and self.game.round_number == 0:
            # First round hasn't started yet
            message = "Press SPACE to start the game!"
            text = self.font_medium.render(message, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            
            # Draw background
            bg_rect = text_rect.inflate(40, 20)
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
            pygame.draw.rect(screen, WHITE, bg_rect, 2)
            
            screen.blit(text, text_rect)
            
    def draw_game_messages(self, screen):
        """
        Draw round end and game end messages.
        
        Args:
            screen: screen surface to draw on
        """
        current_time = time.time()
        
        # Show round end message if active
        if self.round_end_message and current_time < self.show_message_until:
            message_text = self.font_medium.render(self.round_end_message, True, WHITE)
            text_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
            
            # Draw background
            bg_rect = text_rect.inflate(40, 20)
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
            pygame.draw.rect(screen, WHITE, bg_rect, 2)
            
            screen.blit(message_text, text_rect)
            
            # Draw continue prompt
            prompt_text = self.font_small.render("Press SPACE to continue", True, WHITE)
            prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            screen.blit(prompt_text, prompt_rect)
            
        # Show game end message if active
        if self.game_end_message and current_time < self.show_message_until:
            message_text = self.font_large.render(self.game_end_message, True, WHITE)
            text_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
            
            # Draw background
            bg_rect = text_rect.inflate(40, 20)
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
            pygame.draw.rect(screen, (255, 215, 0), bg_rect, 3)  # Gold border
            
            screen.blit(message_text, text_rect)
            
            # Draw final scores
            p1_score_text = self.font_medium.render(
                f"Player 1: {self.game.player1.score}", True, self.game.player1.color)
            p1_rect = p1_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(p1_score_text, p1_rect)
            
            p2_score_text = self.font_medium.render(
                f"Player 2: {self.game.player2.score}", True, self.game.player2.color)
            p2_rect = p2_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            screen.blit(p2_score_text, p2_rect)
            
            # Draw restart prompt
            prompt_text = self.font_small.render("Press R to restart", True, WHITE)
            prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120))
            screen.blit(prompt_text, prompt_rect)
            
    def draw_pause_screen(self, screen):
        """
        Draw the pause screen overlay.
        
        Args:
            screen: screen surface to draw on
        """
        if self.game.paused:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
            
            # Pause text
            pause_text = self.font_large.render("PAUSED", True, WHITE)
            text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(pause_text, text_rect)
            
            # Instructions
            instructions = self.font_small.render("Press ESC to resume", True, WHITE)
            inst_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            screen.blit(instructions, inst_rect)
            
            restart_text = self.font_small.render("Press R to restart round", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            screen.blit(restart_text, restart_rect)
            
    def draw(self, screen):
        """
        Draw all UI elements.
        
        Args:
            screen: screen surface to draw on
        """
        # Draw player stats
        self.draw_player_stats(screen)
        
        # Draw round timer
        self.draw_round_timer(screen)
        
        # Draw round start message
        self.draw_round_start_message(screen)
        
        # Draw game messages (round end, game end)
        self.draw_game_messages(screen)
        
        # Draw pause screen if paused
        self.draw_pause_screen(screen)
