# =============================================================================
# config.py - The adventures of AJX 704 | Tamam settings yahan hain (All settings here)
# =============================================================================
# KERNEL NOTE: Every magic number lives here. Change ONE value â†’ entire game
# updates consistently. This is the Single Source of Truth pattern.
# =============================================================================

import os

# ---------------------------------------------------------------------------
# WINDOW / RESOLUTION
# ---------------------------------------------------------------------------
# Available resolutions shown in the pre-launch picker dialog
RESOLUTIONS = {
    "800 x 600  (Windowed)":   (800,  600),
    "1280 x 720  (HD)":        (1280, 720),
    "1920 x 1080  (Full HD)":  (1920, 1080),
}
DEFAULT_RES = "800 x 600  (Windowed)"

TITLE = "The adventures of AJX 704"

# Frames per second â€“ target (root.after interval = 1000//FPS ms)
FPS = 60
FRAME_MS = 1000 // FPS  # 16 ms

# ---------------------------------------------------------------------------
# COLOURS  (Rango ka khazana â€“ treasure of colours)
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# COLOUR PALETTES (Din se raat tak)
# Order: [SKY_TOP, SKY_MID, SKY_LOWER, SKY_BOTTOM, SUN_COLOUR, SUN_GLOW, 
#         VOID_COL, CLOUD_COLOUR, CITY, HILL_FAR, HILL_NEAR]
# ---------------------------------------------------------------------------

PALETTE_DAY = [
    "#4a90e2", "#7abaff", "#a9d5ff", "#e4f1fe",   # SKY (Deep blue to soft white-blue)
    "#fff8c0", "#ffebb2", "#3498db", "#ffffff",   # SUN, GLOW, SEA/WATER Block (Bright blue), CLOUDS
    "#718fa8", "#78879e", "#5dae3d"               # CITY, HILL_FAR (Greyish rock mountains), HILL_NEAR (Vibrant green forest)
]

PALETTE_SUNSET = [
    "#1a0533", "#c0392b", "#e67e22", "#f39c12",
    "#fff176", "#ffcc02", "#1e0b3c", "#ffd9a0",
    "#2c1654", "#4a235a", "#1a0533"
]

PALETTE_NIGHT = [
    "#05051a", "#081b33", "#0e2645", "#14335c",
    "#f5f6fa", "#dcdde1", "#020914", "#718093",
    "#0b1221", "#060914", "#020308"
]

def interpolate_color(c1: str, c2: str, factor: float) -> str:
    c1 = c1.lstrip('#')
    c2 = c2.lstrip('#')
    r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
    r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
    r = int(r1 + (r2 - r1) * factor)
    g = int(g1 + (g2 - g1) * factor)
    b = int(b1 + (b2 - b1) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"

def get_current_palette(score: int):
    # Day (0-50), Sunset fade (50-100), Sunset (100-150), Night fade (150-250), Night (250+)
    # time_factor: 0.0 (Day) -> 1.0 (Night)
    if score <= 50:
        return PALETTE_DAY, 0.0
    elif score <= 100:
        f = (score - 50) / 50.0
        return [interpolate_color(c1, c2, f) for c1, c2 in zip(PALETTE_DAY, PALETTE_SUNSET)], f * 0.5
    elif score <= 150:
        return PALETTE_SUNSET, 0.5
    elif score <= 250:
        f = (score - 150) / 100.0
        return [interpolate_color(c1, c2, f) for c1, c2 in zip(PALETTE_SUNSET, PALETTE_NIGHT)], 0.5 + f * 0.5
    else:
        return PALETTE_NIGHT, 1.0

# Road / bridge
BRIDGE_TOP    = "#686a6c"   # grey concrete
BRIDGE_SIDE   = "#56585b"   # bridge side wall
PILLAR_COL    = "#808285"   # concrete support pillars

LANE_DASH     = "#ffffff"   # lane marking dashes

# Car fallback colours (when car.png not found)
CAR_BODY      = "#cccccc"   # grey fallback
WHEEL_COL     = "#0f0f0f"   # TE37 black wheels
SPOKE_COL     = "#222222"   # dark spokes

# HUD
HUD_TEXT      = "#ffffff"
HUD_SHADOW    = "#000000"

# UI overlays
OVERLAY_BG    = "#000000"   # semi-transparent overlay (drawn with stipple)
TITLE_COL     = "#f39c12"   # golden title
SUBTITLE_COL  = "#ffffff"

# Particles
PARTICLE_COLS = ["#ffffff", "#ffd700", "#ff8c00", "#ff4500"]

# Speed bar
SPEED_BAR_BG  = "#333333"
SPEED_BAR_FG  = "#e74c3c"

# ---------------------------------------------------------------------------
# PHYSICS  (Tabeeyat â€“ physics)
# ---------------------------------------------------------------------------
GRAVITY       = 0.7    # pixels per frameÂ² downward acceleration
MAX_FALL_VEL  = 20     # terminal velocity (cap so car doesn't warp through gaps)
JUMP_VEL      = -15    # initial upward velocity on jump (negative = up)
DEATH_VEL     = 7      # downward velocity when dying (falls through gap)

# ---------------------------------------------------------------------------
# CAR DIMENSIONS  (target display size â€“ PNG will be scaled)
# ---------------------------------------------------------------------------
# The actual car.png is 1024Ã—1054 â€“ we scale to these display dimensions.
# These are LOGICAL dimensions used for collision and drawing offsets.
CAR_DISPLAY_W = 110    # pixels wide on screen
CAR_DISPLAY_H = 65     # pixels tall on screen
CAR_FIXED_X   = 180   # horizontal position (fixed â€“ road scrolls, car stays)

# Wheel centres relative to car top-left
# (tuned for a side-view car with wheels at bottom)
WHEEL_LEFT_OFFSET_X  = 18   # adjusted for real car png
WHEEL_LEFT_OFFSET_Y  = 54   
WHEEL_RIGHT_OFFSET_X = 82   # adjusted for real car png
WHEEL_RIGHT_OFFSET_Y = 54
WHEEL_RADIUS         = 12   # slightly larger for aggressive look
SPOKE_COUNT          = 5    # TE37 style 5-spoke wheels
SPOKE_INCR_GROUND    = 0.25 # radians added per frame when on ground

# ---------------------------------------------------------------------------
# ROAD / BRIDGE GEOMETRY  (scaled per resolution at runtime in game.py)
# ---------------------------------------------------------------------------
# All road geometry is expressed as fractions of WIN_H so it scales cleanly.
ROAD_TOP_FRAC      = 0.78   # road surface top  = WIN_H * 0.78
BRIDGE_HEIGHT_FRAC = 0.22   # road thickness    = WIN_H * 0.22
VOID_DEPTH_FRAC    = 0.40   # dark void height below road

# Pillar geometry
PILLAR_W           = 18     # width of each bridge pillar
PILLAR_SPACING     = 200    # horizontal distance between pillars
PILLAR_HEIGHT_FRAC = 0.18   # pillar hangs this far below road surface

# Lane dashes
LANE_DASH_LENGTH   = 30
LANE_DASH_GAP      = 20

# ---------------------------------------------------------------------------
# GAP SETTINGS  (Toota hua bridge â€“ broken bridge sections)
# ---------------------------------------------------------------------------
GAP_MIN_WIDTH      = 140    # narrowest gap (pixels) - car is ~110px
GAP_MAX_WIDTH      = 240    # widest gap
GAP_SPAWN_MIN_F    = 80     # minimum frames between gap spawns
GAP_SPAWN_MAX_F    = 180    # maximum frames between gap spawns

# ---------------------------------------------------------------------------
# SPEED & DIFFICULTY  (Raftar aur mushkil â€“ speed and difficulty)
# ---------------------------------------------------------------------------
BASE_SPEED         = 4.0    # starting scroll speed (px/frame)
MAX_SPEED          = 14.0   # absolute maximum scroll speed

# Speed spikes at score thresholds: {score: delta_speed}
# Sudden jump in speed to increase difficulty dramatically
SPEED_SPIKES = {
    300:  1.5,
    700:  2.0,
    1200: 2.5,
    2000: 3.0,
    3000: 2.0,
}

# Gradual ramp between spikes (px/frame per 100 score points)
SPEED_RAMP_RATE    = 0.05

# ---------------------------------------------------------------------------
# SCORING  (Score â€“ points system)
# ---------------------------------------------------------------------------
DIST_PER_FRAME     = 0.5    # distance score added each frame
GAP_BONUS          = 100    # bonus for clearing a gap

# ---------------------------------------------------------------------------
# PARALLAX SCROLL FACTORS  (har layer ka scroll factor)
# Each layer scrolls at BASE_SPEED * factor pixels per frame
# ---------------------------------------------------------------------------
PARALLAX = {
    "city":       0.04,
    "clouds":     0.08,
    "hill_far":   0.15,
    "hill_near":  0.30,
}

# ---------------------------------------------------------------------------
# COUNTDOWN  (Ulti ginti â€“ countdown)
# ---------------------------------------------------------------------------
COUNTDOWN_STEPS = ["3", "2", "1", "GO!"]
COUNTDOWN_MS    = 900    # ms per number
COUNTDOWN_GO_MS = 450    # ms for "GO!"

# ---------------------------------------------------------------------------
# PARTICLES  (Zarraat â€“ particles)
# ---------------------------------------------------------------------------
PARTICLE_COUNT    = 6     # spawned per jump
PARTICLE_MAX_AGE  = 14
PARTICLE_MAX_R    = 5     # starting radius

# ---------------------------------------------------------------------------
# FILE PATHS
# ---------------------------------------------------------------------------
# Absolute path to project root (one level up from this file)
PROJECT_ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAR_IMG_PATH   = os.path.join(PROJECT_ROOT, "carwithoutbackground.png")
HIGHSCORE_PATH = os.path.join(PROJECT_ROOT, "highscore.txt")
