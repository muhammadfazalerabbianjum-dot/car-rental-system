# =============================================================================
# # game.py - Broken Highway | Khel ka dil (The heart of the game)
# =============================================================================
#
# +-------------------------------------------------------------------------+
# |  KERNEL - Core Game Loop & State Machine                                |
# |                                                                         |
# |  The game runs as a single-threaded event-driven loop powered by        |
# |  tkinter's root.after(16, update) - this schedules update() to run      |
# |  approximately every 16 ms (~60 fps). Tkinter processes UI events       |
# |  between calls, keeping the window responsive.                          |
# |                                                                         |
# |  STATE MACHINE:                                                         |
# |                                                                         |
# |    START_SCREEN --SPACE--> COUNTDOWN --done--> PLAYING                  |
# |                                                   |  |                  |
# |                                          PAUSED <-P  P-> (resume)       |
# |                                                   |                     |
# |                                               collision                 |
# |                                                   |                     |
# |                                                DYING                    |
# |                                                   |                     |
# |                                               (fell off)                |
# |                                                   |                     |
# |                                             GAME_OVER                   |
# |                                              R |  | Q                   |
# |                                         COUNTDOWN  exit()               |
# |                                                                         |
# |  PHYSICS ORDER each frame:                                              |
# |    1. Apply gravity to car.vy                                           |
# |    2. Move car.y by car.vy                                              |
# |    3. Check landing (reset vy, on_ground, jumps_left)                   |
# |    4. Check collision with each gap                                     |
# |    5. Move all gaps left by speed                                       |
# |    6. Spawn new gap if timer expired                                    |
# |    7. Remove off-screen gaps; increment gap_bonus                       |
# |    8. Update score and speed                                            |
# |    9. Draw everything (background -> entities -> HUD)                   |
# |                                                                         |
# |  KISS PRINCIPLE: Each method does ONE thing. No nested 3-level ifs.     |
# +-------------------------------------------------------------------------+                 â”‚
# â”‚    8. Update score and speed                                            â”‚
# â”‚    9. Draw everything (background â†’ entities â†’ HUD)                    â”‚
# â”‚                                                                         â”‚
# â”‚  KISS PRINCIPLE: Each method does ONE thing. No nested 3-level ifs.    â”‚
# â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
#
# â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
# â”‚  TDD â€“ Test-Driven Development Steps (Azmayish ke 18 qadam)            â”‚
# â”‚                                                                         â”‚
# â”‚  TEST 01 â€“ Window created with correct title and dimensions             â”‚
# â”‚  TEST 02 â€“ Resolution picker returns valid (width, height) tuple        â”‚
# â”‚  TEST 03 â€“ car.png loads without error; PhotoImage is not None          â”‚
# â”‚  TEST 04 â€“ Fallback car drawn when car.png is missing                  â”‚
# â”‚  TEST 05 â€“ SPACE key transitions START_SCREEN â†’ COUNTDOWN              â”‚
# â”‚  TEST 06 â€“ Countdown fires 3â†’2â†’1â†’GO! in correct time sequence          â”‚
# â”‚  TEST 07 â€“ Car vy set to JUMP_VEL on first jump                        â”‚
# â”‚  TEST 08 â€“ Double jump allowed; third attempt rejected (jumps_left=0)  â”‚
# â”‚  TEST 09 â€“ Car lands at ground_y; on_ground=True; jumps_left reset=2   â”‚
# â”‚  TEST 10 â€“ Gap spawns at right edge with correct width and height       â”‚
# â”‚  TEST 11 â€“ Gap.x decreases by current speed every frame                â”‚
# â”‚  TEST 12 â€“ Gap removed when off-screen; gap_bonus_counter incremented  â”‚
# â”‚  TEST 13 â€“ aabb_overlap returns True when car rect intersects gap rect  â”‚
# â”‚  TEST 14 â€“ Collision sets car.dying=True and car.vy=DEATH_VEL          â”‚
# â”‚  TEST 15 â€“ Dying: car.y increases until > win_h â†’ GAME_OVER state      â”‚
# â”‚  TEST 16 â€“ Score increments per frame; gap clear adds 100; speed spikes â”‚
# â”‚  TEST 17 â€“ highscore.txt created if missing; updated when new best     â”‚
# â”‚  TEST 18 â€“ R key resets all variables and re-enters COUNTDOWN state    â”‚
# â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
#
# =============================================================================

import tkinter as tk
import random
import math
import time
import config as C
from assets  import load_car_image, read_highscore, write_highscore
from physics import apply_gravity, aabb_overlap, clamp
from entities import Car, Gap, Particle, Pillar, SpeedLine
from parallax import ParallaxBackground
from ui       import StartScreen, CountdownOverlay, HUD, PauseOverlay, GameOverScreen

# STRINGS â€“ game state labels
STATE_START    = "START_SCREEN"
STATE_COUNTDOWN= "COUNTDOWN"
STATE_PLAYING  = "PLAYING"
STATE_PAUSED   = "PAUSED"
STATE_DYING    = "DYING"
STATE_GAMEOVER = "GAMEOVER"


class Game:
    """
    # CLASS: Main game controller.
    # Owns the canvas, all entities, state machine, and game loop.
    # Owns the update() method scheduled by root.after every 16 ms.
    #
    # Yeh poora khel ka mukhiya hai â€“ sab kuch yahan chalta hai.
    """

    def __init__(self, root: tk.Tk, win_w: int, win_h: int):
        # VARIABLES â€“ window references
        self.root   = root
        self.win_w  = win_w
        self.win_h  = win_h

        # Canvas â€“ the single drawing surface
        self.canvas = tk.Canvas(
            root,
            width=win_w, height=win_h,
            bg=C.PALETTE_DAY[3],  # fallback bg colour
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        # Computed road geometry (scales with window)
        self.road_top = int(win_h * C.ROAD_TOP_FRAC)
        self.road_h   = win_h - self.road_top
        self.ground_y = self.road_top - C.CAR_DISPLAY_H  # car rests here

        # VARIABLES â€“ assets
        # Load car PNG; kept as instance attribute to prevent GC
        self.car_image = load_car_image(
            target_w=C.CAR_DISPLAY_W,
            target_h=C.CAR_DISPLAY_H
        )
        # True if car image loaded successfully, False = use fallback drawing
        self.has_image = (self.car_image is not None)

        # VARIABLES â€“ high score
        self.highscore  = read_highscore(C.HIGHSCORE_PATH)
        self.is_new_best = False

        # VARIABLES â€“ game state
        self.state = STATE_START

        # --- Game object instantiation ---
        self.car        = Car(self.ground_y)
        self.gaps:  list[Gap]    = []
        self.pillars: list[Pillar] = []

        # Background subsystem
        self.bg = ParallaxBackground(win_w, win_h)

        # UI subsystems
        self.start_screen    = StartScreen()
        self.countdown_ui    = CountdownOverlay()
        self.hud             = HUD()
        self.pause_overlay   = PauseOverlay()
        self.gameover_screen = GameOverScreen()

        # VARIABLES â€“ scoring and speed
        self.total_frames:     int   = 0
        self.gap_bonus_counter:int   = 0
        self.total_score:      int   = 0
        self.speed:            float = C.BASE_SPEED
        self.triggered_spikes: set   = set()

        # VARIABLES â€“ gap spawner
        self.gap_timer:    int = 0
        self.gap_threshold:int = random.randint(C.GAP_SPAWN_MIN_F, C.GAP_SPAWN_MAX_F)

        # VARIABLES â€“ road draw offset (for lane dash scrolling)
        self.road_offset: float = 0.0

        # VARIABLES â€“ pillar generation
        self._init_pillars()

        self.speed_lines = []

        # VARIABLES - easter eggs and fx
        self._shake_frames = 0
        self.afterimages = []
        self.key_buffer = []
        self.invincible = 0

        # VARIABLES - countdown control
        self._countdown_index = 0
        self._countdown_running = False

        # Phase 14 Variables 
        self.rain_drops = []
        self.skid_marks = []
        self.floating_texts = []
        self._flash_frames = 0
        self.last_score_milestone = 0

        # Phase 25 Juice Variables
        self.air_frames = 0        # Tracks how long car has been airborne per jump
        self._shake_x   = 0.0     # Current sub-pixel camera shake offset X
        self._shake_y   = 0.0     # Current sub-pixel camera shake offset Y
        self._shake_mag = 0.0     # Remaining shake energy (decays each frame)


        # Bind keyboard input
        self._bind_keys()

        # Kick off the game loop
        self.start_screen.draw(self.canvas, self.win_w, self.win_h, self.highscore)
        self.root.after(C.FRAME_MS, self._update)

    # ------------------------------------------------------------------
    # INITIALISATION HELPERS
    # ------------------------------------------------------------------

    def _init_pillars(self):
        """
        # FUNCTION: Pre-populate pillars spanning the full screen width.
        # Pillars are decorative and scroll with the road.
        # Bridge ke pillars shuru mein bharo.
        """
        pillar_h = int(self.win_h * C.PILLAR_HEIGHT_FRAC)
        x = 0
        # LOOP: create pillars across 3x window width for seamless scrolling
        while x < self.win_w * 3:
            self.pillars.append(Pillar(x, self.road_top, pillar_h))
            x += C.PILLAR_SPACING

    def _bind_keys(self):
        """
        # FUNCTION: Bind all keyboard controls.
        # SPACE=jump, P=pause, R=restart, Q=quit.
        # Keyboard input ko khel se jodo.
        """
        self.root.bind("<Key>", self._on_key)
        self.root.bind("<KeyPress-p>", self._on_pause)
        self.root.bind("<KeyPress-r>", self._on_restart)
        self.root.bind("<KeyPress-q>", self._on_quit)
        # Also bind uppercase variants
        self.root.bind("<KeyPress-P>", self._on_pause)
        self.root.bind("<KeyPress-R>", self._on_restart)
        self.root.bind("<KeyPress-Q>", self._on_quit)

    # ------------------------------------------------------------------
    # INPUT    # EVENTS  (Input handling)
    # ------------------------------------------------------------------

    def _on_key(self, event):
        """
        # FUNCTION: Handle keyboard events globally.
        """
        keysym = event.keysym.upper()
        
        # Buffer for Easter Eggs
        self.key_buffer.append(keysym)
        if len(self.key_buffer) > 10:
            self.key_buffer.pop(0)
            
        code = ",".join(self.key_buffer)
        
        # EASTER EGG 1: AJX Overdrive (A, J, X)
        if "A,J,X" in code:
            self.key_buffer.clear()
            self.invincible = 600  # 10 seconds (600 frames @ 60fps)
            self.speed = min(self.speed + 2.0, C.MAX_SPEED)
            import audio
            audio.play_jump()

        # EASTER EGG 2: Konami Code Gravity Flip (UP, UP, DOWN, DOWN)
        if "UP,UP,DOWN,DOWN" in code:
            self.key_buffer.clear()
            C.GRAVITY = -C.GRAVITY
            C.JUMP_VEL = -C.JUMP_VEL
            if C.GRAVITY < 0:
                self.road_top = int(self.win_h * 0.2)  # Road flips to the top
            else:
                self.road_top = int(self.win_h * C.ROAD_TOP_FRAC)
            self.road_h = self.win_h - self.road_top
            self.car.vy = 0 
            import audio
            audio.play_crash()

        if keysym == "SPACE":
            self._on_space()

    def _on_space(self, event=None):
        """
        # FUNCTION: Handle SPACE key press.
        # Behaviour depends on current state.
        # SPACE ka matlab: halat ke hisaab se action lo.
        """
        # CONDITIONALS: state-dependent behaviour
        if self.state == STATE_START:
            self._begin_countdown()
        elif self.state == STATE_PLAYING:
            self.car.jump()   # double-jump logic inside Car.jump()

    def _on_pause(self, event=None):
        """
        # FUNCTION: Toggle pause state.
        # P dabao â€“ ruk jao ya phir chaloo.
        """
        if self.state == STATE_PLAYING:
            self.state = STATE_PAUSED
        elif self.state == STATE_PAUSED:
            self.state = STATE_PLAYING
            self.pause_overlay.clear(self.canvas)

    def _on_restart(self, event=None):
        """
        # FUNCTION: Reset all game variables and start countdown again.
        # TEST 18: all variables reset, state â†’ COUNTDOWN.
        # R dabao â€“ phir se shuru karo.
        """
        # CONDITIONALS: only allow restart from PAUSED or GAMEOVER
        if self.state not in (STATE_PAUSED, STATE_GAMEOVER, STATE_PLAYING,
                               STATE_DYING, STATE_COUNTDOWN):
            return
        self._reset_game()

    def _on_quit(self, event=None):
        """
        # FUNCTION: Quit the game cleanly.
        # Q â€“ alvida! (Q â€“ goodbye!)
        """
        self.root.destroy()

    # ------------------------------------------------------------------
    # GAME RESET
    # ------------------------------------------------------------------

    def _reset_game(self):
        """
        # FUNCTION: Reset all mutable game state to initial values.
        # Called on R key or after Game Over â†’ Restart.
        # Sab kuch zero se shuru karo.
        """
        self.car.reset(self.ground_y)
        self.gaps.clear()
        self.pillars.clear()
        self._init_pillars()

        # VARIABLES reset
        self.total_frames      = 0
        self.gap_bonus_counter = 0
        self.total_score       = 0
        self.speed             = C.BASE_SPEED
        self.triggered_spikes  = set()
        self.gap_timer         = 0
        self.gap_threshold     = random.randint(C.GAP_SPAWN_MIN_F, C.GAP_SPAWN_MAX_F)
        self.road_offset       = 0.0
        self.is_new_best       = False

        # Clear all canvas overlays
        self.canvas.delete("gameover")
        self.canvas.delete("pause")
        self.canvas.delete("countdown")

        # Re-read highscore (in case it was updated externally)
        self.highscore = read_highscore(C.HIGHSCORE_PATH)

        self._begin_countdown()

    # ------------------------------------------------------------------
    # COUNTDOWN SEQUENCE
    # ------------------------------------------------------------------

    def _begin_countdown(self):
        """
        # FUNCTION: Start the countdown sequence (3 â†’ 2 â†’ 1 â†’ GO!).
        # Uses root.after chaining so game loop keeps running underneath.
        """
        # Clear the start screen overlay immediately
        self.canvas.delete("start")
        self.state = STATE_COUNTDOWN
        self._countdown_index = 0
        self._countdown_running = True
        self._tick_countdown()

    def _tick_countdown(self):
        """
        # FUNCTION: Display the next countdown label; schedule the next tick.
        # When all labels done â†’ transition to PLAYING.
        # Ek ek karke 3, 2, 1, GO! dikhao.
        """
        # CONDITIONAL: if restarted mid-countdown, abort old chain
        if not self._countdown_running:
            return

        labels = C.COUNTDOWN_STEPS   # ["3", "2", "1", "GO!"]
        idx    = self._countdown_index

        if idx < len(labels):
            label = labels[idx]
            self.countdown_ui.draw(self.canvas, self.win_w, self.win_h, label)

            # Delay for GO! is shorter than numbered labels
            delay = C.COUNTDOWN_GO_MS if label == "GO!" else C.COUNTDOWN_MS
            self._countdown_index += 1
            self.root.after(delay, self._tick_countdown)
        else:
            # Countdown finished â†’ start playing
            self.countdown_ui.clear(self.canvas)
            self._countdown_running = False
            self.state = STATE_PLAYING

    # ------------------------------------------------------------------
    # MAIN UPDATE LOOP  (Asli khel ka chakkar â€“ the core game loop)
    # ------------------------------------------------------------------

    def _update(self):
        """
        # FUNCTION: Called every FRAME_MS milliseconds via root.after.
        # This IS the game loop. Dispatches to state-specific updaters.
        # Har frame: update karo, draw karo, phir schedule karo.
        """
        # CONDITIONALS: route to the correct state handler
        if self.state == STATE_START:
            self._draw_start()
        elif self.state == STATE_COUNTDOWN:
            self._draw_game_scene()   # scene visible behind countdown
        elif self.state == STATE_PLAYING:
            self._update_playing()
        elif self.state == STATE_PAUSED:
            self._draw_game_scene()
            self.pause_overlay.draw(self.canvas, self.win_w, self.win_h)
            self._draw_hud()
        elif self.state == STATE_DYING:
            self._update_dying()
        elif self.state == STATE_GAMEOVER:
            pass   # static screen; no per-frame update needed

        # Schedule next frame (always, so window stays responsive)
        self.root.after(C.FRAME_MS, self._update)

    # ------------------------------------------------------------------
    # STATE: START SCREEN
    # ------------------------------------------------------------------

    def _draw_start(self):
        """Draw the start screen (background + overlay)."""
        self._draw_game_scene()
        self.start_screen.draw(self.canvas, self.win_w, self.win_h, self.highscore)
        # Raise the start overlay above the background
        self.canvas.tag_raise("start")

    # ------------------------------------------------------------------
    # STATE: PLAYING  (Khel jari hai)
    # ------------------------------------------------------------------

    def _update_playing(self):
        """
        # FUNCTION: One full physics + logic tick for the PLAYING state.
        # Order: physics -> entities -> gaps -> score -> draw.
        """
        # Store state before physics
        was_on_ground = self.car.on_ground

        # 1. Update car physics (gravity, movement, landing)
        self.car.update_physics(self.ground_y)

        # --- Air-time tracker ---
        if not self.car.on_ground:
            self.air_frames += 1
        else:
            self.air_frames = 0

        # --- Hard Landing Detection ---
        if not was_on_ground and self.car.on_ground:
            from entities import Particle
            landing_weight = min(1.0, self.air_frames / 45.0)  # 45 frames = "big" jump

            # SCREEN SHAKE: proportional to how long car was in the air
            self._shake_mag = landing_weight * 14.0

            # SPARKS: more sparks the harder the landing
            spark_count = int(8 + landing_weight * 24)  # 8 to 32 sparks
            for _ in range(spark_count):
                angle = random.uniform(math.pi * 0.9, math.pi * 1.8)  # Backwards arc
                vel   = random.uniform(2, 9) * (0.5 + landing_weight)
                col   = random.choice(["#ffcc00", "#ff8800", "#ffffff", "#ff4400"])
                p = Particle(
                    self.car.x + self.car.w * 0.2,
                    self.car.y + self.car.h - 4,
                    math.cos(angle) * vel, math.sin(angle) * vel - 1.0,
                    colour=col
                )
                self.car.particles.append(p)

            # SKID MARK: only on hard-enough landings
            if landing_weight > 0.3:
                self.skid_marks.append({
                    "x": self.car.x, "y": self.ground_y,
                    "w": int(self.car.w * (0.5 + landing_weight * 0.5)),
                    "life": int(40 + landing_weight * 80)
                })

            # Reset air_frames after sampling landing weight
            self.air_frames = 0

        # 2. Update wheel rotation
        self.car.update_wheels(self.speed)

        # 3. Update particles on car
        for p in self.car.particles:
            p.update()
        self.car.update_particles()

        # 4. Road offset (for lane dash scrolling)
        self.road_offset += self.speed

        # 5. Update and manage gaps
        self._update_gaps()

        # 6. Update pillars
        self._update_pillars()

        # 7. Update parallax background
        self.bg.update(self.speed)

        # 8. Collision detection
        if self._check_collision():
            if self.invincible > 0:
                self.car.vy = C.JUMP_VEL * 1.5
                self.car.on_ground = False
                self.car.y = self.road_top - self.car.h - 10
                self.car.jumps_left = self.car.MAX_JUMPS
                import audio
                audio.play_jump()
            else:
                self._trigger_death()
                return   # skip remaining updates for this frame

        # 9. Update score and speed
        self._update_score()

        if self.invincible > 0:
            self.invincible -= 1

        # 10. Process intense speed lines
        if self.speed > C.BASE_SPEED * 1.5:
            if random.random() < 0.2:
                self.speed_lines.append(SpeedLine(self.win_w, self.win_h))
            
            # GHOST TRAIL: Trigger when fast
            if self.speed >= 12.0 and random.random() > 0.5:
                self.afterimages.append({
                    "x": self.car.x, "y": self.car.y, "life": 12
                })

        surviving_lines = []
        for line in self.speed_lines:
            line.update(self.speed)
            if not line.is_off_screen():
                surviving_lines.append(line)
        self.speed_lines = surviving_lines

        # Update ghost trail logic
        surviving_ghosts = []
        for ghost in self.afterimages:
            ghost["x"] -= self.speed * 0.5
            ghost["life"] -= 1
            if ghost["life"] > 0:
                surviving_ghosts.append(ghost)
        self.afterimages = surviving_ghosts

        # 11. Draw everything
        self._draw_game_scene()
        self._draw_hud()

    # ------------------------------------------------------------------

    def _update_gaps(self):
        """
        # FUNCTION: Move all gaps left, remove off-screen ones, spawn new ones.
        # LOOP: iterate gaps list.
        # Gap ko baayi taraf chalao, pura gaya to hatao, naya banao.
        """
        surviving_gaps = []
        # LOOP: update each gap
        for gap in self.gaps:
            gap.update(self.speed)
            if gap.is_off_screen():
                # Gap cleared (car survived) â€“ award bonus
                if not gap.cleared:
                    self.gap_bonus_counter += 1
                    gap.cleared = True
                # Do NOT add to surviving â†’ will be dropped
            else:
                surviving_gaps.append(gap)
        self.gaps = surviving_gaps

        # Gap spawner timer
        self.gap_timer += 1
        if self.gap_timer >= self.gap_threshold:
            self._spawn_gap()
            self.gap_timer = 0
            self.gap_threshold = random.randint(C.GAP_SPAWN_MIN_F, C.GAP_SPAWN_MAX_F)

    def _spawn_gap(self):
        """
        # FUNCTION: Create a new gap at the right edge of the screen.
        # Dynamically calculates gap width so that jumping perfectly clears it 
        # (guaranteeing '1 jump' or '2 jump' scenarios).
        """
        # Single jump flight time approx = (-JUMP_VEL / GRAVITY) * 2
        sj_frames = (-C.JUMP_VEL / C.GRAVITY) * 2.0
        sj_dist   = sj_frames * self.speed
        
        # 70% chance for a gap clearable with 1 jump, 30% chance requiring 2 jumps
        if random.random() < 0.70:
            # 1-jump gap (60% to 85% of theoretical max distance so it feels fair)
            w = random.randint(int(sj_dist * 0.60), int(sj_dist * 0.85))
        else:
            # 2-jump gap (110% to 140% of single jump distance; demands a double jump)
            w = random.randint(int(sj_dist * 1.10), int(sj_dist * 1.40))
            
        gap = Gap(
            spawn_x   = self.win_w + 5,
            road_top  = self.road_top,
            road_h    = self.road_h,
            width     = int(w)
        )
        self.gaps.append(gap)

    # ------------------------------------------------------------------

    def _update_pillars(self):
        """
        # FUNCTION: Scroll pillars left; recycle off-screen pillars to right edge.
        # LOOP: reuse pillars rather than creating new ones (memory efficient).
        # Pillar ko baayi taraf chalao; screen se nikle to daayein lado.
        """
        rightmost = max((p.x for p in self.pillars), default=0)
        for pillar in self.pillars:
            pillar.update(self.speed)
        # If rightmost pillar is getting close to screen right, add another
        if rightmost < self.win_w + C.PILLAR_SPACING:
            self.pillars.append(Pillar(
                rightmost + C.PILLAR_SPACING,
                self.road_top,
                int(self.win_h * C.PILLAR_HEIGHT_FRAC)
            ))
        # Remove pillars far off-screen
        self.pillars = [p for p in self.pillars if p.x > -C.PILLAR_SPACING]

    # ------------------------------------------------------------------

    def _check_collision(self) -> bool:
        """
        # FUNCTION: Detect if car falls into a gap or hits a ledge.
        # TEST 13: falls cleanly if center is over the gap.
        """
        if self.car.dying:
            return False

        # Collision logic: does the car's center fall into the gap?
        car_center_x = self.car.x + (self.car.w / 2)
        car_bottom_y = self.car.y + self.car.h

        for gap in self.gaps:
             gx, gy, gw, gh = gap.get_rect()
             
             # If the car's horizontal center is within the gap width
             if gx + 5 < car_center_x < (gx + gw - 5):
                 # AND the car is essentially at road level
                 if car_bottom_y >= self.ground_y + self.car.h - 6:
                     return True

        return False

    # ------------------------------------------------------------------

    def _trigger_death(self):
        """
        # FUNCTION: Initiate death sequence.
        # TEST 14: sets car.dying=True.
        # Gir gaya! Maut ka sequence shuru karo.
        """
        import audio
        audio.play_crash()
        
        self._shake_frames = 20

        self.car.dying = True
        self.car.vy    = -6.0    # Pop up slightly for an arc
        self.state     = STATE_DYING

    # ------------------------------------------------------------------

    def _update_score(self):
        """
        # FUNCTION: Compute hybrid score and update speed.
        # Also checks if any gap has been cleared (car passed safely over it).
        """
        self.total_frames += 1

        # Check gap clearance (car has passed the gap while in the air)
        for gap in self.gaps:
            if not gap.cleared and (gap.x + gap.w) < self.car.x:
                gap.cleared = True
                self.gap_bonus_counter += 1
                # Trigger combo text!
                words = ["NICE!", "GREAT!", "FLAWLESS!", "SICK JUMP!", "AJX!"]
                chosen = random.choice(words)
                self.floating_texts.append({
                    "x": self.car.x, "y": self.car.y - 40,
                    "text": chosen, "life": 45, "max_life": 45, "dy": -2.0
                })

        # Hybrid score formula:
        distance_score  = self.total_frames * C.DIST_PER_FRAME
        self.total_score = int(distance_score) + (self.gap_bonus_counter * C.GAP_BONUS)
        
        # Score milestone flash
        if self.total_score >= self.last_score_milestone + 500:
            self.last_score_milestone = (self.total_score // 500) * 500
            if self.last_score_milestone > 0:
                self._flash_frames = 6
                self._shake_frames = 10

        # Gradual speed ramp
        ramp_speed = C.BASE_SPEED + (self.total_score / 100) * C.SPEED_RAMP_RATE
        self.speed = clamp(ramp_speed, self.speed, C.MAX_SPEED)

        # Sudden speed spikes at milestones
        for threshold, delta in C.SPEED_SPIKES.items():
            if self.total_score >= threshold and threshold not in self.triggered_spikes:
                self.speed = clamp(self.speed + delta, C.BASE_SPEED, C.MAX_SPEED)
                self.triggered_spikes.add(threshold)

    # ------------------------------------------------------------------
    # STATE: DYING
    # ------------------------------------------------------------------

    def _update_dying(self):
        """
        # FUNCTION: Animate the car falling through the gap.
        # TEST 15: car.y grows each frame; when > win_h â†’ GAME_OVER.
        # Gaadi neeche gir rahi hai â€“ animation.
        """
        # Override regular movement to perform a flying tumble
        self.car.vy += C.GRAVITY
        self.car.y += self.car.vy
        self.car.x += self.speed * 0.4  # Drift forward as it falls

        # Roll the broken wheel spokes rapidly
        self.car.left_angle -= 0.4
        self.car.right_angle -= 0.4

        self._draw_game_scene()
        self._draw_hud()

        # CONDITIONAL: when car has fully fallen off screen â†’ game over
        if self.car.y > self.win_h + C.CAR_DISPLAY_H:
            self._trigger_game_over()

    def _trigger_game_over(self):
        """
        # FUNCTION: Finalise game over state.
        # Update high score if beaten.
        # TEST 17: highscore.txt updated if new best.
        # Khel khatam â€“ score save karo.
        """
        self.state = STATE_GAMEOVER

        # CONDITIONAL: update high score if this run beat it
        if self.total_score > self.highscore:
            self.highscore  = self.total_score
            self.is_new_best = True
            write_highscore(C.HIGHSCORE_PATH, self.highscore)

        self.gameover_screen.draw(
            self.canvas, self.win_w, self.win_h,
            self.total_score, self.highscore, self.is_new_best
        )

    # ------------------------------------------------------------------
    # DRAWING  (Tasveerkashi â€“ painting the scene)
    # ------------------------------------------------------------------

    def _draw_game_scene(self):
        """
        # FUNCTION: Render background, road, entities in correct Z-order.
        """
        # Delete previous frame's background and road (redrawn fully)
        self.canvas.delete("bg")
        self.canvas.delete("road")

        # Dynamically fetch colors and time of day based on score
        palette, time_factor = C.get_current_palette(self.total_score)

        # Draw parallax background layers
        self.bg.draw(self.canvas, self.win_w, self.win_h, palette, time_factor, self.total_score)

        import random
        # RAIN + LIGHTNING (Night Time)
        if time_factor > 0.6:
            # Lightning flash
            if random.random() < (0.003 * (self.speed/10.0)):
                self._flash_frames = 3
            # Generate rain drops
            for _ in range(int(time_factor * 8)):
                self.rain_drops.append([random.randint(0, self.win_w+500), random.randint(-50, int(self.win_h*0.8)), random.randint(20, 50)])

        surv_rain = []
        for r in self.rain_drops:
            r[0] -= (self.speed * 1.5 + 8)
            r[1] += 20
            self.canvas.create_line(r[0], r[1], r[0]-r[2]*0.5, r[1]+r[2], fill="#88ccff", tags="bg")
            if r[1] < self.win_h: surv_rain.append(r)
        self.rain_drops = surv_rain

        # Draw speed lines
        for sl in self.speed_lines:
            w_anim = sl.w * random.uniform(1.2, 3.0)
            h_anim = random.randint(1, 3)
            self.canvas.create_rectangle(
                sl.x, sl.y, sl.x + w_anim, sl.y + h_anim,
                fill=random.choice(["#ffffff", "#e0eaff", "#c0d4ff"]), outline="", tags="bg"
            )

        # Draw Ghost Afterimages
        for ghost in self.afterimages:
            cw = self.car.w
            ch = self.car.h
            inset = (12 - ghost["life"]) * 2
            self.canvas.create_rectangle(
                ghost["x"] + inset, ghost["y"] + inset, 
                ghost["x"] + cw - inset, ghost["y"] + ch - inset,
                fill="#00ffff", outline="", stipple="gray25", tags="bg"
            )

        # Draw road and bridge (with gaps punched through)
        self.bg.draw_road(
            self.canvas, self.win_w, self.win_h,
            self.gaps, self.road_offset, palette, time_factor
        )

        # Draw Skid marks (on road)
        surv_skids = []
        for skid in self.skid_marks:
            skid["x"] -= self.speed
            skid["life"] -= 1
            if skid["life"] > 0 and skid["x"] > -100:
                alpha = int((skid["life"] / 120.0) * 50) + 10 # 10 to 60 dark grey
                ch_hex = f"#{alpha:02x}{alpha:02x}{alpha:02x}"
                self.canvas.create_rectangle(skid["x"], skid["y"]+2, skid["x"]+skid["w"], skid["y"]+5, fill=ch_hex, outline="", tags="road")
                surv_skids.append(skid)
        self.skid_marks = surv_skids

        # --- Camera Shake Decay ---
        if self._shake_mag > 0.3:
            self._shake_x  = random.uniform(-self._shake_mag, self._shake_mag)
            self._shake_y  = random.uniform(-self._shake_mag * 0.5, self._shake_mag * 0.5)
            self._shake_mag *= 0.72  # Exponential decay
        else:
            self._shake_x = 0.0
            self._shake_y = 0.0
            self._shake_mag = 0.0

        # Move canvas to apply shake
        self.canvas.place(x=int(self._shake_x), y=int(self._shake_y))

        # HEADLIGHTS at night (proper cone beam)
        if time_factor > 0.4:
            hx = int(self.car.x + self.car.w)
            hy = int(self.car.y + self.car.h * 0.5)
            cone_len = int(self.win_w * 0.22 * time_factor)
            cone_h   = int(50 * time_factor)
            # Outer glow cone (dimmer)
            self.canvas.create_polygon(
                hx, hy,
                hx + cone_len, hy - cone_h,
                hx + cone_len, hy + cone_h,
                fill="#ffff00", outline="", stipple="gray25", tags="car"
            )
            # Inner bright core
            self.canvas.create_polygon(
                hx, hy,
                hx + int(cone_len * 0.6), hy - cone_h // 3,
                hx + int(cone_len * 0.6), hy + cone_h // 3,
                fill="#fffff0", outline="", stipple="gray50", tags="car"
            )
            # Headlight dots
            self.canvas.create_oval(hx - 3, hy - 4, hx + 3, hy + 4, fill="#ffffff", outline="", tags="car")


        # Draw car (PNG or fallback rectangle)
        self._draw_car()

        # Draw particles
        self._draw_particles()

        # Floating score texts - scaled pulsing arcade-style popups
        surv_texts = []
        for ft in self.floating_texts:
            ft["x"] -= self.speed * 0.2
            ft["y"] += ft["dy"]
            ft["life"] -= 1
            if ft["life"] > 0:
                # Scale from large to normal as life ticks down
                max_life = ft.get("max_life", 45)
                scale_t  = ft["life"] / max_life
                # Pulsing size: starts HUGE, shrinks quickly, then holds
                fsize = int(10 + 20 * min(1.0, scale_t * 4))
                alpha_hex = int(255 * min(1.0, scale_t * 3))
                r = min(255, 255)
                g = int(max(0, 80 * scale_t))
                b = 0
                colour = f"#{r:02x}{g:02x}{b:02x}"
                # Shadow
                self.canvas.create_text(
                    ft["x"] + 3, ft["y"] + 3,
                    text=ft["text"],
                    font=("Courier", fsize, "bold"),
                    fill="#000000", tags="bg"
                )
                # Bright text
                self.canvas.create_text(
                    ft["x"], ft["y"],
                    text=ft["text"],
                    font=("Courier", fsize, "bold"),
                    fill=colour, tags="bg"
                )
                surv_texts.append(ft)
        self.floating_texts = surv_texts

        
        # Screen Flash (Lightning or Milestones)
        if self._flash_frames > 0:
            self.canvas.create_rectangle(0, 0, self.win_w, self.win_h, fill="#ffffff", outline="", tags="ui")
            self._flash_frames -= 1

    def _draw_car(self):
        """
        # FUNCTION: Draw the player car using PNG image or fallback shapes.
        # After drawing image, overlay rotating wheel spokes.
        # Gaadi draw karo â€“ tasveer ya backup shapes.
        """
        self.canvas.delete("car")

        cx = int(self.car.x)
        cy = int(self.car.y)
        cw = self.car.w
        ch = self.car.h

        if self.has_image and self.car_image:
            # Draw PNG image (shifted down slightly to compensate for transparent padding)
            self.canvas.create_image(
                cx, cy + 12,
                image=self.car_image,
                anchor="nw",
                tags="car"
            )
        else:
            # FALLBACK: draw green rectangle car
            self.canvas.create_rectangle(
                cx, cy, cx + cw, cy + ch,
                fill=C.CAR_BODY, outline="#1a5c3a", width=2, tags="car"
            )
            # Windscreen
            self.canvas.create_rectangle(
                cx + cw * 0.55, cy + ch * 0.15,
                cx + cw * 0.80, cy + ch * 0.65,
                fill="#88ccff", outline="", tags="car"
            )
            # Roof line
            self.canvas.create_line(
                cx + cw * 0.3, cy + ch * 0.15,
                cx + cw * 0.55, cy + ch * 0.15,
                fill="#1a5c3a", width=2, tags="car"
            )
            # Fallback wheels (circles)
            for wox, woy in [(C.WHEEL_LEFT_OFFSET_X, C.WHEEL_LEFT_OFFSET_Y),
                              (C.WHEEL_RIGHT_OFFSET_X, C.WHEEL_RIGHT_OFFSET_Y)]:
                wr = C.WHEEL_RADIUS
                self.canvas.create_oval(
                    cx + wox - wr, cy + woy - wr,
                    cx + wox + wr, cy + woy + wr,
                    fill=C.WHEEL_COL, outline="#555555", width=2, tags="car"
                )

        # Overlay wheel spokes (on top of image or fallback) to create optical illusion of rotation!
        if not self.has_image:
            self._draw_wheel_spokes(cx, cy)
            
        # Draw invincible shield aura
        if self.invincible > 0:
            import math
            import time
            ctx = cx + cw//2
            cty = cy + ch//2
            r = max(cw, ch) * 0.8
            pulse = math.sin(time.time() * 10) * 5
            # Clean concentric solid rings
            self.canvas.create_oval(ctx-r-pulse, cty-r-pulse, ctx+r+pulse, cty+r+pulse, outline="#00ffff", width=2, tags="car")
            self.canvas.create_oval(ctx-r+4, cty-r+4, ctx+r-4, cty+r-4, outline="#00ccaa", width=1, tags="car")
            # Timer Arc
            extent_deg = (self.invincible / 600.0) * 360
            self.canvas.create_arc(ctx-r-5, cty-r-5, ctx+r+5, cty+r+5, start=90, extent=extent_deg, style="arc", outline="#ffffff", width=4, tags="car")

        # Apply screen shake just before finishing the render frame
        if getattr(self, '_shake_frames', 0) > 0:
            intensity = min(15, self._shake_frames)
            import random
            dx = random.randint(-intensity, intensity)
            dy = random.randint(-intensity, intensity)
            self.canvas.move("all", dx, dy)
            self._shake_frames -= 1
            
        # Z-ORDER FIX: Guarantee UI never gets covered by the rapidly redrawn background layers
        for t in ["start", "countdown", "pause", "gameover", "hud"]:
            self.canvas.tag_raise(t)

    def _draw_wheel_spokes(self, car_x: int, car_y: int):
        """
        # FUNCTION: Draw rotating spoke lines over both wheels using trig.
        # This creates a brilliant optical illusion of spinning wheels, even on a static PNG!
        """
        import math as _math

        wheel_data = [
            (car_x + C.WHEEL_LEFT_OFFSET_X,  car_y + C.WHEEL_LEFT_OFFSET_Y,  self.car.left_angle),
            (car_x + C.WHEEL_RIGHT_OFFSET_X, car_y + C.WHEEL_RIGHT_OFFSET_Y, self.car.right_angle),
        ]

        # LOOP: draw each wheel
        for wx, wy, angle in wheel_data:
            r = C.WHEEL_RADIUS

            if not self.has_image:
                # Dark circle behind spokes (tyre)
                self.canvas.create_oval(
                    wx - r, wy - r, wx + r, wy + r,
                    fill="#1a1a1a", outline="#444444", width=1, tags="car"
                )

            # LOOP: draw each spoke
            for i in range(C.SPOKE_COUNT):
                spoke_angle = angle + (i * (_math.pi / C.SPOKE_COUNT))
                end_x = wx + r * _math.cos(spoke_angle)
                end_y = wy + r * _math.sin(spoke_angle)
                self.canvas.create_line(
                    wx, wy, end_x, end_y,
                    fill=C.SPOKE_COL, width=2, tags="car"
                )

            if not self.has_image:
                # Hub cap (small circle in centre)
                self.canvas.create_oval(
                    wx - 3, wy - 3, wx + 3, wy + 3,
                    fill="#888888", outline="", tags="car"
                )

    def _draw_particles(self):
        """
        # FUNCTION: Draw all active dust particles as shrinking circles.
        # LOOP: iterate car's particle list.
        # Dhool ke zarraat â€“ chhote gherte banao.
        """
        self.canvas.delete("particles")
        for p in self.car.particles:
            r = p.get_radius()
            if r < 0.5:
                continue
            self.canvas.create_oval(
                p.x - r, p.y - r,
                p.x + r, p.y + r,
                fill=p.colour, outline="", tags="particles"
            )

    def _draw_hud(self):
        """Draw the HUD score display."""
        self.hud.draw(
            self.canvas, self.win_w, self.win_h,
            self.total_score, self.highscore,
            self.speed, C.MAX_SPEED
        )
