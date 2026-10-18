# =============================================================================
# ui.py â€“ Broken Highway | Khel ka chehra (Game UI / Screens)
# =============================================================================
# Classes:
#   StartScreen       â€“ "Press SPACE to Begin" overlay
#   CountdownOverlay  â€“ 3 â†’ 2 â†’ 1 â†’ GO! sequence
#   HUD               â€“ score + high score display
#   PauseOverlay      â€“ "PAUSED" text overlay during pause
#   GameOverScreen    â€“ end screen with score, best, and instructions
#
# All classes draw directly onto the canvas using create_text / create_rectangle.
# Tags are used to batch-delete per class (e.g. "hud", "start", "gameover").
# =============================================================================

import config as C


# =============================================================================
# START SCREEN
# =============================================================================
class StartScreen:
    """
    # CLASS: Draws the start screen.
    # Shows game title, "Press SPACE to Begin", and current best score.
    # Shuru ki screen â€“ khel shuru karne se pehle ka nazara.
    """

    def draw(self, canvas, win_w: int, win_h: int, highscore: int):
        """
        # FUNCTION: Render start screen on canvas.
        # Called each frame while state == START_SCREEN.
        """
        canvas.delete("start")
        cx = win_w // 2
        cy = win_h // 2

        # Semi-transparent overlay (stipple trick)
        canvas.create_rectangle(
            0, 0, win_w, win_h,
            fill="#000000", stipple="gray50", outline="", tags="start"
        )

        # Title shadow (offset by 4px for depth effect)
        canvas.create_text(
            cx + 4, cy - 100 + 4,
            text="THE ADVENTURES OF",
            font=("Courier", int(win_h * 0.050), "bold"),
            fill="#000000", tags="start"
        )
        # Title primary
        canvas.create_text(
            cx, cy - 100,
            text="THE ADVENTURES OF",
            font=("Courier", int(win_h * 0.050), "bold"),
            fill=C.TITLE_COL, tags="start"
        )

        # Subtitle
        canvas.create_text(
            cx, cy - 45,
            text="AJX 704",
            font=("Courier", int(win_h * 0.075), "bold"),
            fill="#ffcc66", tags="start"
        )

        # Divider line
        canvas.create_line(
            cx - 200, cy - 18, cx + 200, cy - 18,
            fill=C.TITLE_COL, width=2, tags="start"
        )

        # Instructions
        canvas.create_text(
            cx, cy + 10,
            text="SPACE  -  Jump  (Double Jump supported)",
            font=("Courier", int(win_h * 0.022)),
            fill=C.SUBTITLE_COL, tags="start"
        )
        canvas.create_text(
            cx, cy + 40,
            text="P - Pause     R - Restart     Q - Quit",
            font=("Courier", int(win_h * 0.022)),
            fill="#cccccc", tags="start"
        )

        # Press SPACE prompt
        canvas.create_text(
            cx, cy + 90,
            text=">  Press SPACE to Begin  <",
            font=("Courier", int(win_h * 0.030), "bold"),
            fill="#ffffff", tags="start"
        )

        # High score
        canvas.create_text(
            cx, cy + 140,
            text=f"Best Score: {highscore}",
            font=("Courier", int(win_h * 0.025)),
            fill="#f0c040", tags="start"
        )


# =============================================================================
# COUNTDOWN OVERLAY
# =============================================================================
class CountdownOverlay:
    """
    # CLASS: Renders the countdown (3, 2, 1, GO!) over the game scene.
    # The Game class drives timing via root.after; this class only draws.
    # Ulti ginti â€“ 3, 2, 1, GO! dikhao.
    """

    def draw(self, canvas, win_w: int, win_h: int, text: str):
        """
        # FUNCTION: Draw a single countdown label centred on screen.
        # 'text' is one of: "3", "2", "1", "GO!"
        """
        canvas.delete("countdown")
        cx = win_w // 2
        cy = win_h // 2

        colour = "#ffffff" if text != "GO!" else "#00ff88"
        size   = int(win_h * 0.18)

        # Shadow
        canvas.create_text(
            cx + 5, cy + 5 - 60,
            text=text,
            font=("Courier", size, "bold"),
            fill="#000000", tags="countdown"
        )
        # Primary
        canvas.create_text(
            cx, cy - 60,
            text=text,
            font=("Courier", size, "bold"),
            fill=colour, tags="countdown"
        )

    def clear(self, canvas):
        canvas.delete("countdown")


# =============================================================================
# HUD â€“ Heads-Up Display
# =============================================================================
class HUD:
    """
    # CLASS: Draws score and high score during gameplay.
    # Also draws a small speed indicator bar in the top-right corner.
    # HUD â€“ khel ke dauran score dikhata hai.
    """

    def draw(self, canvas, win_w: int, win_h: int,
             score: int, highscore: int, speed: float, max_speed: float):
        """
        # FUNCTION: Render HUD elements.
        # Called every frame during PLAYING and PAUSED states.
        """
        canvas.delete("hud")
        pad  = 14
        fsz  = max(14, int(win_h * 0.030))

        # Score â€“ shadow then primary
        for dx, dy, col in [(2, 2, "#000000"), (0, 0, C.HUD_TEXT)]:
            canvas.create_text(
                pad + dx, pad + dy,
                anchor="nw",
                text=f"Score  {score:>6}",
                font=("Courier", fsz, "bold"),
                fill=col, tags="hud"
            )

        # High score
        for dx, dy, col in [(2, 2, "#000000"), (0, 0, "#f0c040")]:
            canvas.create_text(
                pad + dx, pad + fsz + 6 + dy,
                anchor="nw",
                text=f"Best   {highscore:>6}",
                font=("Courier", fsz),
                fill=col, tags="hud"
            )

        # Analog Speedometer (Exact X90 Mark II Grande style)
        import math
        gauge_r = int(win_h * 0.12)  # Much larger for detail
        # Add dynamic padding to X to prevent 1080p right-edge crop
        safe_pad = max(pad * 2, int(win_w * 0.06)) 
        gx = win_w - gauge_r - safe_pad 
        gy = pad + gauge_r + 20
        
        # Dial Outer Bezel
        canvas.create_oval(gx-gauge_r-4, gy-gauge_r-4, gx+gauge_r+4, gy+gauge_r+4, fill="#181818", outline="#555555", width=2, tags="hud")
        canvas.create_oval(gx-gauge_r, gy-gauge_r, gx+gauge_r, gy+gauge_r, fill="#2a2d34", outline="", tags="hud") # Matte gauge face
        
        # Tick marks and Numbers (0 to 180 km/h)
        # The sweep corresponds to approx 230 degrees. 
        # Leftmost (0 km/h) is at 225 deg (bottom left), Rightmost (180 km/h) is at -45 deg (bottom right).
        start_angle = 225
        sweep_range = 270 # Delta of 270 degrees
        
        for speed_val in range(0, 181, 10):
            ratio = speed_val / 180.0
            angle_deg = start_angle - (ratio * sweep_range)
            angle = math.radians(angle_deg)
            
            is_major = (speed_val % 20 == 0)
            r1 = gauge_r * (0.80 if is_major else 0.88)
            r2 = gauge_r * 0.95
            
            color = "#f2f2f2" if speed_val < 160 else "#cc3333" # 160/180 are redline/warn colors
            canvas.create_line(gx + r1*math.cos(angle), gy - r1*math.sin(angle), gx + r2*math.cos(angle), gy - r2*math.sin(angle), fill=color, width=2 if is_major else 1, tags="hud")
            
            # Print numbers 20, 40, ..., 180
            if speed_val % 20 == 0 and speed_val > 0:
                tr = gauge_r * 0.65
                canvas.create_text(gx + tr*math.cos(angle), gy - tr*math.sin(angle), text=str(speed_val), font=("Arial", max(8, int(win_h*0.018)), "bold"), fill="#f2f2f2", tags="hud")

        # Fake Odometer Box
        canvas.create_rectangle(gx-25, gy+15, gx+25, gy+30, fill="#111", outline="#000", tags="hud")
        canvas.create_text(gx, gy+22, text="49352", font=("Courier", 10), fill="#ccc", tags="hud")
        canvas.create_text(gx, gy+40, text="km/h", font=("Arial", 9, "bold"), fill="#999", tags="hud")
        
        # Calculate Current Needle Angle
        # Map game speed to an authentic 60kmh -> 180kmh visual sweep
        speed_ratio = speed / max_speed if max_speed > 0 else 0
        speed_ratio = min(1.0, max(0.0, speed_ratio))
        # Needle sweeps up from 60 (at zero) to 180 (at max speed)
        visual_kmh = 60.0 + (speed_ratio ** 1.3) * 120.0
        
        needle_deg = start_angle - ((visual_kmh / 180.0) * sweep_range)
        needle_rad = math.radians(needle_deg)
        nx = gx + (gauge_r * 0.85) * math.cos(needle_rad)
        ny = gy - (gauge_r * 0.85) * math.sin(needle_rad)
        
        # Needle Shadow (For depth)
        canvas.create_line(gx+2, gy+2, nx+2, ny+2, fill="#000000", width=4, tags="hud")
        # Orange Needle
        canvas.create_line(gx, gy, nx, ny, fill="#ff7700", width=3, tags="hud")
        
        # Center Pin (Black cap)
        canvas.create_oval(gx-10, gy-10, gx+10, gy+10, fill="#111", outline="#333", width=2, tags="hud")


# =============================================================================
# PAUSE OVERLAY
# =============================================================================
class PauseOverlay:
    """
    # CLASS: Semi-transparent overlay shown while game is paused.
    # Rok â€“ ruka hua khel.
    """

    def draw(self, canvas, win_w: int, win_h: int):
        canvas.delete("pause")
        cx = win_w // 2
        cy = win_h // 2

        canvas.create_rectangle(
            0, 0, win_w, win_h,
            fill="#000000", stipple="gray25", outline="", tags="pause"
        )
        canvas.create_text(
            cx + 4, cy + 4,
            text="PAUSED",
            font=("Courier", int(win_h * 0.10), "bold"),
            fill="#000000", tags="pause"
        )
        canvas.create_text(
            cx, cy,
            text="PAUSED",
            font=("Courier", int(win_h * 0.10), "bold"),
            fill="#ffffff", tags="pause"
        )
        canvas.create_text(
            cx, cy + int(win_h * 0.12),
            text="Press P to Resume  |  R to Restart  |  Q to Quit",
            font=("Courier", int(win_h * 0.022)),
            fill="#cccccc", tags="pause"
        )

    def clear(self, canvas):
        canvas.delete("pause")


# =============================================================================
# GAME OVER SCREEN
# =============================================================================
class GameOverScreen:
    """
    # CLASS: End screen showing score, high score, and restart options.
    # Khel khatam â€“ Game Over screen.
    """

    def draw(self, canvas, win_w: int, win_h: int,
             score: int, highscore: int, is_new_best: bool):
        """
        # FUNCTION: Render game over screen.
        # is_new_best â€“ shows "New Best!" banner if True.
        # Agar naya record ban gaya to khushi ka paigham dikhao!
        """
        canvas.delete("gameover")
        cx = win_w // 2
        cy = win_h // 2

        # Overlay
        canvas.create_rectangle(
            0, 0, win_w, win_h,
            fill="#000000", stipple="gray50", outline="", tags="gameover"
        )

        # GAME OVER title
        fsz = int(win_h * 0.095)
        for dx, dy, col in [(4, 4, "#000000"), (0, 0, "#e74c3c")]:
            canvas.create_text(
                cx + dx, cy - int(win_h * 0.22) + dy,
                text="GAME  OVER",
                font=("Courier", fsz, "bold"),
                fill=col, tags="gameover"
            )

        # New best banner
        if is_new_best:
            canvas.create_text(
                cx, cy - int(win_h * 0.10),
                text="â˜…  NEW BEST!  â˜…",
                font=("Courier", int(win_h * 0.040), "bold"),
                fill="#f1c40f", tags="gameover"
            )

        # Score display
        canvas.create_text(
            cx, cy,
            text=f"Your Score : {score}",
            font=("Courier", int(win_h * 0.038), "bold"),
            fill="#ffffff", tags="gameover"
        )
        canvas.create_text(
            cx, cy + int(win_h * 0.065),
            text=f"Best Score : {highscore}",
            font=("Courier", int(win_h * 0.030)),
            fill="#f0c040", tags="gameover"
        )

        # Instructions
        canvas.create_text(
            cx, cy + int(win_h * 0.16),
            text="R - Play Again     Q - Quit",
            font=("Courier", int(win_h * 0.027), "bold"),
            fill="#aaaaaa", tags="gameover"
        )
