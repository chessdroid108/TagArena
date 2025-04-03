"""
Constants and configuration settings for the Tag Game.
"""
import pygame

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Level dimensions (larger than screen for scrolling)
LEVEL_WIDTH = 1600  # Double the screen width for extended levels
LEVEL_HEIGHT = 1200  # Double the screen height for extended levels

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
GOLD = (255, 215, 0)
DARK_BLUE = (20, 40, 100)
LIGHT_BLUE = (80, 120, 220)

# Obstacle colors
OBSTACLE_COLOR = (90, 90, 120)
OBSTACLE_OUTLINE = (140, 140, 180)

# Player properties
PLAYER_RADIUS = 20
PLAYER_MASS = 1.0  # Mass for custom physics 
DEFAULT_SPEED = 380  # Base movement speed (increased)
DEFAULT_JUMP_FORCE = 400  # Jump force (reduced for better control)
TAGGER_SPEED_MULTIPLIER = 0.9  # Tagger is slightly slower by default
TAGGER_COLOR = (220, 60, 80)  # Vibrant reddish-pink for tagger
RUNNER_COLOR = (60, 140, 220)  # Vibrant blue for runner

# Power-up settings
POWERUP_SPAWN_INTERVAL = 12  # Seconds between power-up spawns
POWERUP_DURATION = 5         # How long power-ups last when collected
POWERUP_DESPAWN_TIME = 8     # How long power-ups remain on screen before disappearing
POWERUP_RADIUS = 15          # Size of power-up pickups
POWERUP_MAX_COUNT = 1        # Maximum number of power-ups on screen at one time

# Power-up types and effects
POWERUP_TYPES = [
    'speed',       # Increased movement speed
    'shield',      # Protection from being tagged
    'super_jump',  # Higher jumps
    'invisible',   # Partial invisibility (harder to see)
    'freeze'       # Freeze the other player briefly
]

# Power-up colors
POWERUP_COLORS = {
    'speed': ORANGE,
    'shield': BLUE,
    'super_jump': GREEN,
    'invisible': PURPLE,
    'freeze': CYAN
}

# Power-up effect multipliers
POWERUP_EFFECTS = {
    'speed': 1.8,        # Speed multiplier
    'super_jump': 1.5,   # Jump height multiplier
    'freeze': 1.5        # Seconds to freeze opponent
}

# Platform properties
PLATFORM_HEIGHT = 20
REGULAR_PLATFORM_COLOR = GRAY
STICKY_PLATFORM_COLOR = PURPLE
JUMP_PLATFORM_COLOR = GREEN
SPEED_PLATFORM_COLOR = YELLOW
PASSTHROUGH_PLATFORM_COLOR = CYAN

# Platform effects
STICKY_SLOWDOWN = 0.6  # Speed multiplier for sticky platforms
JUMP_BOOST = 1.4  # Jump force multiplier for jump platforms
SPEED_BOOST = 1.3  # Speed multiplier for speed platforms

# Custom Physics Constants
GRAVITY = 1200  # Gravity acceleration (pixels/second²) - reduced for better jumps
FRICTION = 0.8  # Friction coefficient (0 = no friction, 1 = full stop)
AIR_RESISTANCE = 0.98  # Air resistance (slows horizontal movement in air)
GROUND_FRICTION = 0.85  # Ground friction (slows horizontal movement on ground)
MAX_FALL_SPEED = 500  # Maximum falling speed - reduced for better control
TERMINAL_VELOCITY = 800  # Maximum velocity in any direction

# Collision Detection
COLLISION_TOLERANCE = 1.0  # Collision detection tolerance

# Game states
STATE_MENU = 0
STATE_PLAYING = 1
STATE_PAUSED = 2
STATE_GAME_OVER = 3
STATE_TUTORIAL = 4

# Game settings
TAG_COOLDOWN = 1000  # milliseconds before tagging again
ROUND_TIME = 60  # seconds
SCORE_TO_WIN = 5

# Controls (WASD for player 1, Arrow keys for player 2, IJKL for player 3, TFGH for player 4)
# Player 1
P1_LEFT = pygame.K_a
P1_RIGHT = pygame.K_d
P1_JUMP = pygame.K_w
P1_DOWN = pygame.K_s

# Player 2
P2_LEFT = pygame.K_LEFT
P2_RIGHT = pygame.K_RIGHT
P2_JUMP = pygame.K_UP
P2_DOWN = pygame.K_DOWN

# Player 3
P3_LEFT = pygame.K_j
P3_RIGHT = pygame.K_l
P3_JUMP = pygame.K_i
P3_DOWN = pygame.K_k

# Player 4
P4_LEFT = pygame.K_f
P4_RIGHT = pygame.K_h
P4_JUMP = pygame.K_t
P4_DOWN = pygame.K_g

# Menu
PAUSE_KEY = pygame.K_ESCAPE
TAGGER_PROPERTY_KEY = pygame.K_t

# Camera Settings
CAMERA_SMOOTH_FACTOR = 0.1  # Lower value = smoother camera movement
CAMERA_ZOOM_SMOOTH_FACTOR = 0.05  # Smoothing for zoom transitions
CAMERA_MIN_ZOOM = 0.5  # Maximum zoom out
CAMERA_MAX_ZOOM = 1.2  # Maximum zoom in
CAMERA_DEFAULT_ZOOM = 1.0  # Default zoom level

# Animation Settings
ANIMATION_FRAME_RATE = 10  # Frames per second for animations
PLAYER_MAX_SQUISH = 0.2  # Maximum squish factor for player when landing
PLAYER_SQUISH_RECOVERY = 0.2  # Recovery speed from squish

# Particle Settings
PARTICLE_LIFETIME = 1.0  # Default lifetime for particles
FOOTSTEP_PARTICLE_COUNT = 1  # Number of particles per footstep
JUMP_PARTICLE_COUNT = 8  # Number of particles when jumping
LAND_PARTICLE_COUNT = 12  # Number of particles when landing
TAG_PARTICLE_COUNT = 20  # Number of particles when one player tags another
PARTICLE_SIZE_RANGE = (2, 5)  # Min/max size for particles

# Obstacle Settings
OBSTACLE_DAMAGE = 1  # Damage done by damaging obstacles
OBSTACLE_BOUNCE_STRENGTH = 15  # Bounce height from bouncing obstacles
MAX_OBSTACLES_PER_LEVEL = 10  # Maximum number of obstacles per level
