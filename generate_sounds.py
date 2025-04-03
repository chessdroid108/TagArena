"""
Sound generator for Tag Game.
Creates basic sound effects using PyGame's Sound module.
"""

import os
import numpy as np
import wave
import pygame

# Initialize pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2)

# Make sure directories exist
sounds_dir = os.path.join("assets", "sounds")
music_dir = os.path.join("assets", "music")
if not os.path.exists(sounds_dir):
    os.makedirs(sounds_dir)
if not os.path.exists(music_dir):
    os.makedirs(music_dir)

def create_sine_wave(freq, duration, volume=0.5, sample_rate=44100):
    """
    Create a sine wave array with the given frequency and duration.
    
    Args:
        freq: Frequency in Hz
        duration: Duration in seconds
        volume: Volume from 0.0 to 1.0
        sample_rate: Sample rate in Hz
        
    Returns:
        Numpy array with the generated sound data
    """
    # Generate time array
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    
    # Generate sine wave
    tone = np.sin(2 * np.pi * freq * t)
    
    # Apply volume
    tone = (tone * volume * 32767).astype(np.int16)
    
    # Make it stereo (2D array) - both channels have the same data
    stereo_tone = np.column_stack((tone, tone))
    
    return stereo_tone

def apply_envelope(data, attack=0.1, decay=0.1, sustain=0.8, release=0.2, sustain_level=0.7):
    """
    Apply an ADSR envelope to the sound data.
    
    Args:
        data: Numpy array with sound data
        attack: Attack time in percentage of total duration
        decay: Decay time in percentage of total duration
        sustain: Sustain time in percentage of total duration
        release: Release time in percentage of total duration
        sustain_level: Sustain level from 0.0 to 1.0
        
    Returns:
        Numpy array with the envelope applied
    """
    # Handle stereo data (shape should be (length, 2))
    if len(data.shape) == 2 and data.shape[1] == 2:
        length = data.shape[0]
        
        # Calculate segment lengths
        attack_end = int(length * attack)
        decay_end = attack_end + int(length * decay)
        sustain_end = decay_end + int(length * sustain)
        
        # Create envelope array (column vector for broadcasting)
        envelope = np.ones((length, 1))
        
        # Attack: 0 to 1
        if attack_end > 0:
            envelope[:attack_end] = np.linspace(0, 1, attack_end).reshape(-1, 1)
        
        # Decay: 1 to sustain_level
        if decay_end > attack_end:
            envelope[attack_end:decay_end] = np.linspace(1, sustain_level, decay_end - attack_end).reshape(-1, 1)
        
        # Sustain: sustain_level
        envelope[decay_end:sustain_end] = sustain_level
        
        # Release: sustain_level to 0
        if length > sustain_end:
            envelope[sustain_end:] = np.linspace(sustain_level, 0, length - sustain_end).reshape(-1, 1)
        
        # Apply envelope
        return (data * envelope).astype(np.int16)
    else:
        raise ValueError("Sound data must be stereo (2D array with shape (length, 2))")

def create_sound(filename, frequencies, duration, volume=0.5, envelope=True, **envelope_params):
    """
    Create a sound file with the given parameters.
    
    Args:
        filename: Output filename
        frequencies: List of frequencies to mix
        duration: Duration in seconds
        volume: Volume from 0.0 to 1.0
        envelope: Whether to apply an envelope
        **envelope_params: Parameters for the envelope
    """
    sample_rate = 44100
    
    # Generate the sound data - start with stereo silence
    num_samples = int(duration * sample_rate)
    sound_data = np.zeros((num_samples, 2), dtype=np.int16)
    
    # Mix all frequencies
    for freq in frequencies:
        sound_data += create_sine_wave(freq, duration, volume / len(frequencies), sample_rate)
    
    # Apply envelope if requested
    if envelope:
        sound_data = apply_envelope(sound_data, **envelope_params)
    
    # Save to file using wave module
    path = os.path.join(sounds_dir, filename)
    
    # Normalize the sound data to avoid clipping
    max_val = np.max(np.abs(sound_data))
    if max_val > 0:  # Avoid division by zero
        normalized_data = sound_data * (32767 / max_val)
        sound_data = normalized_data.astype(np.int16)
    
    # Open a wave file for writing
    with wave.open(path, 'wb') as wav_file:
        # Set parameters
        nchannels = 2  # Stereo
        sampwidth = 2  # 2 bytes (16 bits) per sample
        framerate = 44100  # CD quality
        nframes = sound_data.shape[0]
        
        # Set the parameters
        wav_file.setparams((nchannels, sampwidth, framerate, nframes, 'NONE', 'not compressed'))
        
        # Write the data
        wav_file.writeframes(sound_data.tobytes())
    
    print(f"Created sound: {path}")

def generate_jump_sound():
    """Generate a jumping sound effect."""
    create_sound(
        "jump.wav",
        [200, 400, 600],
        0.3,
        volume=0.7,
        attack=0.05,
        decay=0.1,
        sustain=0.1,
        release=0.75,
        sustain_level=0.3
    )

def generate_land_sound():
    """Generate a landing sound effect."""
    create_sound(
        "land.wav",
        [150, 80, 30],
        0.2,
        volume=0.6,
        attack=0.01,
        decay=0.1,
        sustain=0.1,
        release=0.79,
        sustain_level=0.2
    )

def generate_footstep_sounds():
    """Generate footstep sound variations."""
    # Footstep 1
    create_sound(
        "footstep1.wav",
        [100, 50],
        0.15,
        volume=0.4,
        attack=0.01,
        decay=0.2,
        sustain=0.1,
        release=0.69,
        sustain_level=0.2
    )
    
    # Footstep 2
    create_sound(
        "footstep2.wav",
        [120, 60],
        0.15,
        volume=0.4,
        attack=0.01,
        decay=0.15,
        sustain=0.1,
        release=0.74,
        sustain_level=0.2
    )
    
    # Footstep 3
    create_sound(
        "footstep3.wav",
        [90, 45],
        0.15,
        volume=0.4,
        attack=0.01,
        decay=0.25,
        sustain=0.1,
        release=0.64,
        sustain_level=0.2
    )

def generate_tag_sound():
    """Generate a tag sound effect."""
    create_sound(
        "tag.wav",
        [600, 800, 1000],
        0.4,
        volume=0.7,
        attack=0.05,
        decay=0.1,
        sustain=0.3,
        release=0.55,
        sustain_level=0.5
    )

def generate_tagged_sound():
    """Generate a tagged (got caught) sound effect."""
    create_sound(
        "tagged.wav",
        [300, 200, 100],
        0.5,
        volume=0.7,
        attack=0.05,
        decay=0.3,
        sustain=0.3,
        release=0.35,
        sustain_level=0.3
    )

def generate_powerup_sounds():
    """Generate power-up related sound effects."""
    # Power-up pickup
    create_sound(
        "powerup_pickup.wav",
        [500, 800, 1200, 1500],
        0.5,
        volume=0.7,
        attack=0.05,
        decay=0.2,
        sustain=0.4,
        release=0.35,
        sustain_level=0.6
    )
    
    # Power-up activate
    create_sound(
        "powerup_activate.wav",
        [300, 600, 900, 1200],
        0.6,
        volume=0.7,
        attack=0.1,
        decay=0.2,
        sustain=0.4,
        release=0.3,
        sustain_level=0.7
    )
    
    # Power-up expire
    create_sound(
        "powerup_expire.wav",
        [1000, 800, 600, 400],
        0.5,
        volume=0.6,
        attack=0.1,
        decay=0.3,
        sustain=0.2,
        release=0.4,
        sustain_level=0.5
    )

def generate_platform_sounds():
    """Generate platform effect sounds."""
    # Speed platform
    create_sound(
        "speed_platform.wav",
        [400, 600, 800],
        0.3,
        volume=0.5,
        attack=0.05,
        decay=0.1,
        sustain=0.2,
        release=0.65,
        sustain_level=0.4
    )
    
    # Jump platform
    create_sound(
        "jump_platform.wav",
        [200, 400, 600, 800],
        0.4,
        volume=0.6,
        attack=0.05,
        decay=0.1,
        sustain=0.2,
        release=0.65,
        sustain_level=0.5
    )
    
    # Sticky platform
    create_sound(
        "sticky_platform.wav",
        [100, 150, 200],
        0.35,
        volume=0.5,
        attack=0.1,
        decay=0.2,
        sustain=0.4,
        release=0.3,
        sustain_level=0.3
    )

def generate_obstacle_sounds():
    """Generate obstacle interaction sounds."""
    # Obstacle hit
    create_sound(
        "obstacle_hit.wav",
        [200, 150, 100],
        0.3,
        volume=0.6,
        attack=0.01,
        decay=0.2,
        sustain=0.1,
        release=0.69,
        sustain_level=0.3
    )
    
    # Obstacle bounce
    create_sound(
        "obstacle_bounce.wav",
        [300, 500, 700],
        0.4,
        volume=0.6,
        attack=0.05,
        decay=0.1,
        sustain=0.2,
        release=0.65,
        sustain_level=0.5
    )
    
    # Damage sound
    create_sound(
        "damage.wav",
        [150, 100, 80],
        0.5,
        volume=0.7,
        attack=0.01,
        decay=0.3,
        sustain=0.2,
        release=0.49,
        sustain_level=0.4
    )

def generate_ui_sounds():
    """Generate UI and menu sounds."""
    # Menu select
    create_sound(
        "menu_select.wav",
        [400, 800],
        0.2,
        volume=0.5,
        attack=0.01,
        decay=0.1,
        sustain=0.1,
        release=0.79,
        sustain_level=0.6
    )
    
    # Menu change
    create_sound(
        "menu_change.wav",
        [300, 600],
        0.1,
        volume=0.4,
        attack=0.01,
        decay=0.1,
        sustain=0.0,
        release=0.89,
        sustain_level=0.5
    )
    
    # Game start
    create_sound(
        "game_start.wav",
        [300, 500, 700, 900],
        0.7,
        volume=0.7,
        attack=0.1,
        decay=0.2,
        sustain=0.5,
        release=0.2,
        sustain_level=0.7
    )
    
    # Game over
    create_sound(
        "game_over.wav",
        [500, 400, 300, 200],
        1.0,
        volume=0.7,
        attack=0.1,
        decay=0.3,
        sustain=0.4,
        release=0.2,
        sustain_level=0.6
    )
    
    # Round end
    create_sound(
        "round_end.wav",
        [600, 700, 800, 900],
        0.8,
        volume=0.6,
        attack=0.1,
        decay=0.2,
        sustain=0.4,
        release=0.3,
        sustain_level=0.6
    )
    
    # Count down
    create_sound(
        "count_down.wav",
        [400, 800],
        0.2,
        volume=0.6,
        attack=0.01,
        decay=0.1,
        sustain=0.1,
        release=0.79,
        sustain_level=0.6
    )

def generate_ambient_sounds():
    """Generate ambient sounds."""
    # Wind sound
    create_sound(
        "wind.wav",
        [100, 120, 140, 160],
        2.0,
        volume=0.4,
        attack=0.3,
        decay=0.3,
        sustain=1.0,
        release=0.4,
        sustain_level=0.5
    )

def generate_bounce_sound():
    """Generate bounce sound effect."""
    create_sound(
        "bounce.wav",
        [200, 400, 600, 800],
        0.3,
        volume=0.7,
        attack=0.05,
        decay=0.1,
        sustain=0.1,
        release=0.75,
        sustain_level=0.4
    )

def generate_cooldown_ready_sound():
    """Generate cooldown ready notification sound."""
    create_sound(
        "cooldown_ready.wav",
        [500, 700, 900],
        0.4,
        volume=0.5,
        attack=0.05,
        decay=0.2,
        sustain=0.3,
        release=0.45,
        sustain_level=0.6
    )

def generate_all_sounds():
    """Generate all sound effects."""
    print("Generating sound effects...")
    
    # Player movement sounds
    generate_jump_sound()
    generate_land_sound()
    generate_footstep_sounds()
    generate_bounce_sound()
    
    # Tag related sounds
    generate_tag_sound()
    generate_tagged_sound()
    generate_cooldown_ready_sound()
    
    # Power-up sounds
    generate_powerup_sounds()
    
    # Platform effect sounds
    generate_platform_sounds()
    
    # Obstacle interaction sounds
    generate_obstacle_sounds()
    
    # UI and menu sounds
    generate_ui_sounds()
    
    # Ambient sounds
    generate_ambient_sounds()
    
    print("All sound effects generated!")

if __name__ == "__main__":
    generate_all_sounds()
    pygame.quit()