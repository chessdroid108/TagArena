"""
Sound module for the Tag Game.
Handles loading and playing sound effects for various game events.
"""

import pygame
import os
import random

class SoundManager:
    def __init__(self):
        """Initialize the sound manager, loading all sounds and setting volumes."""
        # Initialize sound mixer
        pygame.mixer.init()
        
        # Set default volumes
        self.sfx_volume = 0.7  # 70%
        self.music_volume = 0.5  # 50%
        
        # Create sound dictionaries
        self.sounds = {}
        self.music = {}
        
        # Load sound effects
        self._load_sounds()
        
        # Settings
        self.enabled = True
        self.music_enabled = True
        
    def _load_sounds(self):
        """Load all sound effects from the sounds directory."""
        # Create assets/sounds directory if it doesn't exist
        sounds_dir = os.path.join("assets", "sounds")
        if not os.path.exists(sounds_dir):
            os.makedirs(sounds_dir)
            
        # Define sounds to load with filenames and categories
        sound_files = {
            # Player movement sounds
            "jump": "jump.wav",
            "land": "land.wav",
            "footstep": ["footstep1.wav", "footstep2.wav", "footstep3.wav"],
            "bounce": "bounce.wav",
            
            # Tag related sounds
            "tag": "tag.wav",
            "tagged": "tagged.wav",
            "cooldown_ready": "cooldown_ready.wav",
            
            # Power-up sounds
            "powerup_pickup": "powerup_pickup.wav",
            "powerup_activate": "powerup_activate.wav",
            "powerup_expire": "powerup_expire.wav",
            
            # Platform effect sounds
            "speed_platform": "speed_platform.wav",
            "jump_platform": "jump_platform.wav",
            "sticky_platform": "sticky_platform.wav",
            
            # Obstacle interaction sounds
            "obstacle_hit": "obstacle_hit.wav",
            "obstacle_bounce": "obstacle_bounce.wav",
            "damage": "damage.wav",
            
            # UI and menu sounds
            "menu_select": "menu_select.wav",
            "menu_change": "menu_change.wav",
            "game_start": "game_start.wav",
            "game_over": "game_over.wav",
            "round_end": "round_end.wav",
            "count_down": "count_down.wav",
            
            # Ambient sounds
            "wind": "wind.wav"
        }
        
        # Load all sound effects
        for sound_name, filenames in sound_files.items():
            if isinstance(filenames, list):
                # For sound variations (like footsteps), load all and store in a list
                self.sounds[sound_name] = []
                for filename in filenames:
                    path = os.path.join(sounds_dir, filename)
                    # Only try to load if the file exists
                    if os.path.exists(path):
                        sound = pygame.mixer.Sound(path)
                        sound.set_volume(self.sfx_volume)
                        self.sounds[sound_name].append(sound)
            else:
                # Regular single sound
                path = os.path.join(sounds_dir, filenames)
                # Only try to load if the file exists
                if os.path.exists(path):
                    self.sounds[sound_name] = pygame.mixer.Sound(path)
                    self.sounds[sound_name].set_volume(self.sfx_volume)
                else:
                    # Create a placeholder if sound doesn't exist yet
                    self.sounds[sound_name] = None
        
        # Load background music tracks
        music_dir = os.path.join("assets", "music")
        if not os.path.exists(music_dir):
            os.makedirs(music_dir)
            
        music_files = {
            "menu": "menu_music.mp3",
            "game": ["game_music1.mp3", "game_music2.mp3"],
            "victory": "victory_music.mp3"
        }
        
        # Store music file paths
        for music_name, filenames in music_files.items():
            if isinstance(filenames, list):
                self.music[music_name] = []
                for filename in filenames:
                    path = os.path.join(music_dir, filename)
                    if os.path.exists(path):
                        self.music[music_name].append(path)
            else:
                path = os.path.join(music_dir, filenames)
                if os.path.exists(path):
                    self.music[music_name] = path
                else:
                    self.music[music_name] = None
    
    def play(self, sound_name, force=False):
        """
        Play a sound effect by name.
        
        Args:
            sound_name: The name of the sound to play
            force: If True, play even if sound effects are disabled
        """
        if not self.enabled and not force:
            return
            
        sound = self.sounds.get(sound_name)
        if sound is None:
            # Sound doesn't exist or hasn't been loaded
            return
            
        # Handle sound variations (list of sounds)
        if isinstance(sound, list):
            if len(sound) > 0:
                # Play a random variation
                random.choice(sound).play()
        else:
            # Play the single sound
            sound.play()
    
    def play_music(self, music_name, loop=True, force=False):
        """
        Play a music track by name.
        
        Args:
            music_name: The name of the music track to play
            loop: Whether to loop the music
            force: If True, play even if music is disabled
        """
        if not self.music_enabled and not force:
            return
            
        path = self.music.get(music_name)
        if path is None:
            # Music doesn't exist or hasn't been loaded
            return
            
        # Handle music variations (list of tracks)
        if isinstance(path, list):
            if len(path) > 0:
                # Pick a random track
                path = random.choice(path)
            else:
                return
                
        # Stop any currently playing music
        pygame.mixer.music.stop()
        
        # Load and play the new track
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1 if loop else 0)
        except pygame.error:
            # File might not exist or be in the wrong format
            print(f"Error loading music: {path}")
    
    def stop_music(self):
        """Stop any currently playing music."""
        pygame.mixer.music.stop()
    
    def set_sfx_volume(self, volume):
        """
        Set the volume for sound effects.
        
        Args:
            volume: Volume level from 0.0 to 1.0
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
        
        # Update volumes for all loaded sounds
        for sound_name, sound in self.sounds.items():
            if sound is not None:
                if isinstance(sound, list):
                    for s in sound:
                        s.set_volume(self.sfx_volume)
                else:
                    sound.set_volume(self.sfx_volume)
    
    def set_music_volume(self, volume):
        """
        Set the volume for music.
        
        Args:
            volume: Volume level from 0.0 to 1.0
        """
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def toggle_sounds(self):
        """Toggle sound effects on/off."""
        self.enabled = not self.enabled
        return self.enabled
    
    def toggle_music(self):
        """Toggle music on/off."""
        self.music_enabled = not self.music_enabled
        
        if self.music_enabled:
            # Resume music at current volume
            pygame.mixer.music.set_volume(self.music_volume)
        else:
            # Mute music but don't stop it
            pygame.mixer.music.set_volume(0.0)
            
        return self.music_enabled


# Create a global sound manager instance for easy importing
sound_manager = SoundManager()