# =============================================================================
# entities.py â€“ Broken Highway | Khel ke kirdar (Game entities)
# =============================================================================
# Classes:
#   Car       â€“ player vehicle with jump, physics state, wheel spokes, particles
#   Gap       â€“ missing bridge section (hazard)
#   Particle  â€“ dust puff spawned on jump
#   Pillar    â€“ decorative structural element (scrolls with road)
#
# Each class owns its DATA only.
# DRAWING is done in game.py (separation of concerns).
# =============================================================================

import math
import random
from config import (
    CAR_FIXED_X, CAR_DISPLAY_W, CAR_DISPLAY_H,
    WHEEL_LEFT_OFFSET_X, WHEEL_LEFT_OFFSET_Y,
    WHEEL_RIGHT_OFFSET_X, WHEEL_RIGHT_OFFSET_Y,
    WHEEL_RADIUS, SPOKE_COUNT, SPOKE_INCR_GROUND,
    GRAVITY, MAX_FALL_VEL, JUMP_VEL, DEATH_VEL,
    GAP_MIN_WIDTH, GAP_MAX_WIDTH,
    PARTICLE_COUNT, PARTICLE_MAX_AGE, PARTICLE_MAX_R,
    PARTICLE_COLS,
    PILLAR_W, PILLAR_SPACING,
)


# =============================================================================
# CAR  (Gaadi â€“ the player's vehicle)
# =============================================================================
class Car:
    """
    # CLASS: Represents the player's car.
    # Attributes track position, velocity, jump state, wheel rotation,
    # and dying animation.
    #
    # DOUBLE JUMP: jumps_left starts at 2 each time car lands.
    # Each SPACE press decrements jumps_left. When 0 â†’ no more jumps.
    # Gaadi do baar jump kar sakti hai â€“ upar se bhi!
    """

    MAX_JUMPS = 2   # CLASS VARIABLE: double-jump limit

    def __init__(self, ground_y: float):
        # VARIABLES â€“ position
        self.x: float = CAR_FIXED_X          # horizontal position (fixed)
        self.y: float = ground_y             # vertical position (top of car)
        self.w: int   = CAR_DISPLAY_W
        self.h: int   = CAR_DISPLAY_H

        # VARIABLES â€“ physics
        self.vy: float       = 0.0           # vertical velocity (+ve = down)
        self.on_ground: bool = True
        self.jumps_left: int = self.MAX_JUMPS  # reset on landing

        # VARIABLES â€“ wheel spoke angles (radians)
        self.left_angle:  float = 0.0
        self.right_angle: float = 0.0

        # VARIABLES â€“ state
        self.dying: bool = False

        # VARIABLES â€“ particles list (owned by car for proximity)
        self.particles: list = []

    # ------------------------------------------------------------------
    def jump(self) -> bool:
        """
        # FUNCTION: Attempt a jump. Returns True if jump was performed.
        # CONDITIONAL: only jump if jumps_left > 0.
        # Agar jumps bache hain to jump karo, warna nahi.
        """
        if self.jumps_left > 0:
            import audio
            if self.jumps_left == self.MAX_JUMPS:
                audio.play_jump()
            else:
                audio.play_double_jump()

            self.vy = JUMP_VEL          # apply upward velocity
            self.jumps_left -= 1
            self.on_ground = False
            self._spawn_particles()     # puff of dust
            return True
        return False

    # ------------------------------------------------------------------
    def _spawn_particles(self):
        """
        # FUNCTION: Generate PARTICLE_COUNT particles at rear wheel.
        # Called each time car jumps.
        # Jump ke waqt dhool ke zarraat paidaa karo.
        """
        # Rear wheel is on the LEFT side of the car (side view)
        px = self.x + WHEEL_LEFT_OFFSET_X
        py = self.y + WHEEL_LEFT_OFFSET_Y

        # LOOP: create each particle with random offsets
        for _ in range(PARTICLE_COUNT):
            dx = random.uniform(-8, 3)   # mostly trail behind car
            dy = random.uniform(-4, 2)
            col = random.choice(PARTICLE_COLS)
            self.particles.append(Particle(px, py, dx, dy, col))

    # ------------------------------------------------------------------
    def update_physics(self, ground_y: float):
        """
        # FUNCTION: Apply gravity and move car vertically each frame.
        # Check landing condition.
        # Har frame: gravity lagao, position update karo.
        """
        if self.dying:
            # CONDITIONAL: dying animation â€“ fall straight down, ignore normal physics
            self.vy = DEATH_VEL
            self.y += self.vy
            return   # skip normal physics during death

        # Apply gravity
        self.vy += GRAVITY
        if self.vy > MAX_FALL_VEL:
            self.vy = MAX_FALL_VEL

        self.y += self.vy

        # CONDITIONAL: landing check
        if self.y >= ground_y:
            self.y = ground_y
            self.vy = 0.0
            if not self.on_ground:
                # Gaadi zamin par aa gayi â€“ jumps reset karo
                self.on_ground = True
                self.jumps_left = self.MAX_JUMPS

    # ------------------------------------------------------------------
    def update_wheels(self, speed: float):
        """
        # FUNCTION: Rotate wheel spoke angles each frame when on ground.
        # In the air â†’ no rotation (wheels spin only when rolling).
        # Zameen par hone par pehiye ghoomte hain.
        """
        if self.on_ground and not self.dying and speed > 0:
            increment = SPOKE_INCR_GROUND * (speed / 4.0)  # scale with speed
            self.left_angle  += increment
            self.right_angle += increment

    # ------------------------------------------------------------------
    def update_particles(self):
        """
        # FUNCTION: Age particles by 1 frame; remove expired ones.
        # LOOP: iterate particles list and filter.
        # Zarraat burhapa â€“ ek frame umar badhao, expire hone par hatao.
        """
        surviving = []
        for p in self.particles:
            p.age += 1
            if p.age < p.max_age:
                surviving.append(p)
        self.particles = surviving

    # ------------------------------------------------------------------
    def get_collision_rect(self):
        """
        # FUNCTION: Return (x, y, w, h) of car's collision box.
        # Slightly inset to be fair to the player.
        # Collision box thoda chota rak ke player ko fair chance dena.
        """
        inset_x = self.w * 0.12
        inset_y = self.h * 0.08
        return (
            self.x  + inset_x,
            self.y  + inset_y,
            self.w  - inset_x * 2,
            self.h  - inset_y * 2,
        )

    # ------------------------------------------------------------------
    def get_wheel_centers(self):
        """
        # FUNCTION: Return (lx, ly), (rx, ry) for left and right wheel centres.
        # Used for drawing spokes.
        """
        lx = self.x + WHEEL_LEFT_OFFSET_X
        ly = self.y + WHEEL_LEFT_OFFSET_Y
        rx = self.x + WHEEL_RIGHT_OFFSET_X
        ry = self.y + WHEEL_RIGHT_OFFSET_Y
        return (lx, ly), (rx, ry)

    # ------------------------------------------------------------------
    def reset(self, ground_y: float):
        """
        # FUNCTION: Reset car to initial state for a new game.
        # Naya khel shuru karne ke liye gaadi reset karo.
        """
        self.y          = ground_y
        self.vy         = 0.0
        self.on_ground  = True
        self.jumps_left = self.MAX_JUMPS
        self.dying      = False
        self.particles  = []
        self.left_angle = 0.0
        self.right_angle= 0.0


# =============================================================================
# GAP  (Raaste mein toota hua hissa â€“ missing bridge section)
# =============================================================================
class Gap:
    """
    # CLASS: A gap (missing section) in the bridge.
    # Spawns at the right edge of the screen and scrolls left.
    # Toota hua bridge â€“ gaadi yahan se gir sakti hai!
    """

    def __init__(self, spawn_x: float, road_top: float, road_h: float, width: float = None):
        if width is None:
            self.w: float = random.uniform(GAP_MIN_WIDTH, GAP_MAX_WIDTH)
        else:
            self.w: float = width
        self.x: float = spawn_x          # start at right edge
        self.y: float = road_top         # top of gap = top of road
        self.h: float = road_h           # full road thickness
        self.cleared: bool = False       # True once car has passed safely

    # ------------------------------------------------------------------
    def update(self, speed: float):
        """
        # FUNCTION: Move gap left by current scroll speed.
        # Yeh gap baayi taraf chalta rahega.
        """
        self.x -= speed

    # ------------------------------------------------------------------
    def is_off_screen(self) -> bool:
        """
        # FUNCTION: True when gap has fully passed the left edge.
        # Agar screen se nikal gaya to True.
        """
        return self.x + self.w < 0

    # ------------------------------------------------------------------
    def get_rect(self):
        """Return (x, y, w, h) collision rectangle."""
        return self.x, self.y, self.w, self.h


# =============================================================================
# PARTICLE  (Dhool ka zarra â€“ a dust particle)
# =============================================================================
class Particle:
    """
    # CLASS: A single dust/exhaust particle spawned on jump.
    # Has position, velocity, age, colour.
    # Ek zarraa â€“ chhota, jaldi marta hai.
    """

    def __init__(self, x: float, y: float, dx: float, dy: float, colour: str):
        self.x:       float = x
        self.y:       float = y
        self.dx:      float = dx        # per-frame horizontal drift
        self.dy:      float = dy        # per-frame vertical drift
        self.age:     int   = 0
        self.max_age: int   = PARTICLE_MAX_AGE
        self.colour:  str   = colour

    # ------------------------------------------------------------------
    def get_radius(self) -> float:
        """
        # FUNCTION: Radius shrinks linearly as particle ages.
        # Umar ke saath zarra chota hota jaata hai.
        """
        progress = self.age / self.max_age   # 0.0 â†’ 1.0
        return PARTICLE_MAX_R * (1.0 - progress)

    # ------------------------------------------------------------------
    def update(self):
        """Move particle by its velocity each frame."""
        self.x += self.dx
        self.y += self.dy
        self.dy += 0.3      # slight gravity drag on particles
        self.age += 1


# =============================================================================
# PILLAR  (Deewar â€“ bridge support pillar)
# =============================================================================
class Pillar:
    """
    # CLASS: Decorative bridge support pillar.
    # Draws a vertical column hanging below the road surface.
    # Bridge ke neeche ki deewaar â€“ sirf dikhne ke liye.
    """

    def __init__(self, x: float, road_top: float, pillar_h: float):
        self.x:       float = x
        self.road_top: float = road_top
        self.h:       float = pillar_h

    # ------------------------------------------------------------------
    def update(self, speed: float):
        """Scroll left with road."""
        self.x -= speed

    # ------------------------------------------------------------------
    def is_off_screen(self) -> bool:
        return self.x + PILLAR_W < 0

# =============================================================================
# SPEEDLINE  (Raftar ki lakeerein â€“ motion blur streaks)
# =============================================================================
class SpeedLine:
    """
    # CLASS: A horizontal streak that simulates high speed (anime speed lines).
    # Spawns far right, moves left very fast.
    """
    def __init__(self, win_w: int, win_h: int):
        self.x: float = float(win_w + random.randint(0, 200))
        self.y: float = random.uniform(win_h * 0.05, win_h * 0.95)
        self.w: float = random.uniform(40, 250)
        self.speed_offset: float = random.uniform(5.0, 15.0)

    def update(self, base_speed: float):
        self.x -= (base_speed + self.speed_offset)

    def is_off_screen(self) -> bool:
        return self.x + self.w < 0
