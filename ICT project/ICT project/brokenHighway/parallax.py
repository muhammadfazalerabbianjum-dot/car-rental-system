# =============================================================================
# parallax.py â€“ Broken Highway | Parde dar parda manzar (Layered background)
# =============================================================================
# CLASS: ParallaxBackground
#
# Draws 7 layered background elements in back-to-front order.
# Each layer scrolls at a different fraction of game speed, creating
# the illusion of depth (parallax effect).
#
# Layer order (back â†’ front):
#   1. Sky gradient  â€“ static
#   2. Sun + glow    â€“ static
#   3. Distant city  â€“ very slow scroll
#   4. Peach clouds  â€“ slow scroll
#   5. Far hills     â€“ medium scroll
#   6. Near hills    â€“ faster scroll
#   7. Void depth    â€“ static (below bridge)
#   8. Bridge + pillars drawn in game.py (speed = 1.0)
#
# KERNEL NOTE: Parallax creates 2.5D depth without any 3D math.
# Each layer's offset = (game_speed * factor) accumulated each frame.
# =============================================================================

import math
import random
import config as C


class ParallaxBackground:
    """
    # CLASS: Manages and draws all background layers.
    # Call update(speed) every frame, then draw(canvas, win_w, win_h).
    # Parde: har frame mein update karo, phir draw karo.
    """

    def __init__(self, win_w: int, win_h: int):
        self.win_w = win_w
        self.win_h = win_h

        # Computed road geometry
        self.road_top = int(win_h * C.ROAD_TOP_FRAC)

        # VARIABLES – layer offsets (increase each frame)
        self.city_offset:     float = 0.0
        self.cloud_offset:    float = 0.0
        self.hill_far_offset: float = 0.0
        self.hill_near_offset:float = 0.0
        
        self.shooting_star = {"active": False, "x": 0, "y": 0, "life": 0}

        # Pre-generate stars
        self._stars        = self._gen_stars(win_w, win_h)
        # Pre-generate city skyline shapes and windows
        self._city_shapes  = self._gen_city(win_w)
        # Pre-generate cloud positions
        self._clouds       = self._gen_clouds(win_w)
        # Pre-generate far hills (Smooth Mountains)
        self._hills_far    = self._gen_hills(win_w, amplitude=0.25, base_frac=0.62, is_mountain=True)
        # Pre-generate near hills (Rolling Green Margallas)
        self._hills_near   = self._gen_hills(win_w, amplitude=0.06, base_frac=0.72, is_mountain=False)
        # Seed house lights on mountain slopes (deterministic, fixed positions)
        rng = random.Random(42)  # Fixed seed so lights are always same positions
        self._house_lights_far  = [(rng.randint(0, win_w*2), rng.uniform(0.4, 0.85), rng.uniform(0, math.pi*2)) for _ in range(80)]
        self._house_lights_near = [(rng.randint(0, win_w*2), rng.uniform(0.5, 0.90), rng.uniform(0, math.pi*2)) for _ in range(50)]
        # Pre-generate hyper-speed foreground pillars
        self._pillars = [(rng.randint(0, win_w*3), rng.randint(6, 18)) for _ in range(25)]
        
        # --- NEW 10/10 DYNAMIC PROPS ---
        # Wind Turbines on the hills
        self._turbines = [(rng.randint(0, win_w*2), rng.uniform(0.65, 0.95), rng.uniform(0, math.pi*2)) for _ in range(7)]
        # Flocks of birds
        self._birds = [(rng.randint(0, win_w*2), rng.randint(int(win_h*0.05), int(win_h*0.25)), rng.uniform(1.0, 3.0)) for _ in range(12)]
        
        self.boat = {"x": win_w * 0.8, "dx": -0.2}
        self.speedboat = {"x": win_w * 0.1, "dx": 4.5}
        self.heli = {"x": win_w * 1.5, "y": win_h * 0.15, "dx": -1.5}

        # Canvas item IDs (filled in during first draw)
        self._ids: list = []

    # ------------------------------------------------------------------
    # GENERATORS  (ek baar banao, baar baar use karo)
    # ------------------------------------------------------------------

    def _gen_stars(self, span: int, win_h: int) -> list:
        steps = []
        for _ in range(120):
            x = random.randint(0, span * 2)
            y = random.randint(0, int(win_h * 0.55))
            r = random.uniform(0.5, 1.5)
            p = random.uniform(0, math.pi * 2) # blink phase
            steps.append((x, y, r, p))
        return steps

    def _gen_city(self, span: int) -> list:
        """
        # FUNCTION: Generate random city building silhouettes and tiny windows.
        """
        buildings = []
        x = 0
        while x < span * 2:
            w = random.randint(25, 65)
            h = random.randint(int(self.win_h * 0.08), int(self.win_h * 0.22))
            
            # Generate windows
            windows = []
            if w > 30 and h > 40:
                cols = w // 10
                rows = h // 12
                for c in range(cols):
                    for r in range(rows):
                        if random.random() > 0.4:
                            # offset slightly to centre them
                            windows.append((c * 10 + 4, r * 12 + 4, 3, 5))
            
            buildings.append((x, w, h, windows))
            x += w + random.randint(2, 10)
        return buildings

    def _gen_clouds(self, span: int) -> list:
        """
        # FUNCTION: Generate random cloud positions.
        # Returns list of (x, y, rx, ry) ellipse parameters.
        # Baadal â€“ upar hi rehte hain.
        """
        clouds = []
        x = 0
        while x < span * 2:
            y  = random.randint(int(self.win_h * 0.05), int(self.win_h * 0.25))
            rx = random.randint(40, 90)
            ry = random.randint(15, 30)
            clouds.append((x, y, rx, ry))
            x += rx * 2 + random.randint(30, 120)
        return clouds

    def _gen_hills(self, span: int, amplitude: float,
                   base_frac: float, is_mountain: bool = False) -> dict:
        """
        # FUNCTION: Generate soft, rolling mountain and hill polygons.
        # is_mountain controls frequency and whether snow caps are drawn.
        """
        base_y = self.win_h * base_frac
        amp    = self.win_h * amplitude
        pts = []
        snow_caps = []
        
        step = 15
        L = float(span * 2)
        base_freq = (2.0 * math.pi) / L
        
        if is_mountain:
            # Massive wide curvy mountains (low frequency)
            f1, f2 = base_freq * 1.5, base_freq * 3.5
            for xi in range(0, int(L) + step, step):
                if xi > L: xi = L 
                val1 = math.sin(xi * f1) * amp * 0.7
                val2 = math.cos(xi * f2) * amp * 0.3
                yi = base_y - (val1 + val2) - amp * 0.2
                pts.append((xi, yi))
                
                # Snow caps on the high peaks
                if yi < base_y - amp * 0.8:
                    snow_caps.append([(xi, yi), (xi, yi+15)])
                if xi == L: break
        else:
            # Smooth rolling green tree-lines
            f1, f2, f3 = base_freq * 2.0, base_freq * 6.0, base_freq * 18.0
            for xi in range(0, int(L) + step, step):
                if xi > L: xi = L 
                val1 = math.sin(xi * f1) * amp * 0.4
                val2 = math.cos(xi * f2) * amp * 0.2
                val3 = math.sin(xi * f3) * amp * 0.1
                yi = base_y - (val1 + val2 + val3) - amp * 0.5
                pts.append((xi, yi))
                if xi == L: break

        # Close polygon at bottom
        pts.append((int(span) * 2, self.win_h))
        pts.append((0, self.win_h))
        
        return {"pts": pts, "snow": snow_caps}

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    def update(self, speed: float):
        """
        # FUNCTION: Advance each layer's scroll offset by speed * factor.
        # Called every frame before drawing.
        # Har frame mein offsets update karo.
        """
        self.city_offset      = (self.city_offset      + speed * C.PARALLAX["city"])      % self.win_w
        self.cloud_offset     = (self.cloud_offset     + speed * C.PARALLAX["clouds"])     % self.win_w
        self.hill_far_offset  = (self.hill_far_offset  + speed * C.PARALLAX["hill_far"])   % self.win_w
        self.hill_near_offset = (self.hill_near_offset + speed * C.PARALLAX["hill_near"])  % self.win_w
        
        # Ocean Boat Logic (Update X continuously)
        self.boat["x"] -= (self.boat["dx"] + speed * 0.1)
        # Wrap boat around gracefully
        if self.boat["x"] < -200:
            self.boat["x"] = self.win_w + 200
            
        # Speedboat physics
        self.speedboat["x"] += self.speedboat["dx"] - speed * 1.2
        if self.speedboat["x"] > self.win_w + 400:
            self.speedboat["x"] = -300
        elif self.speedboat["x"] < -400:
            self.speedboat["x"] = self.win_w + 300
            
        # Helicopter physics (slow hover)
        self.heli["x"] += self.heli["dx"] - speed * 0.3
        if self.heli["x"] < -300:
            self.heli["x"] = self.win_w + 300
            self.heli["y"] = random.randint(int(self.win_h * 0.05), int(self.win_h * 0.25))

    # ------------------------------------------------------------------
    # DRAW
    # ------------------------------------------------------------------

    def draw(self, canvas, win_w: int, win_h: int, palette: list, time_factor: float, score: int = 0):
        """
        # FUNCTION: Draw all background layers onto the canvas.
        """
        import time
        road_top = int(win_h * C.ROAD_TOP_FRAC)

        # Palette indices:
        # [0]=SKY_TOP, [1]=SKY_MID, [2]=SKY_LOWER, [3]=SKY_BOTTOM
        # [4]=SUN_COLOUR, [5]=SUN_GLOW, [6]=VOID_COL, [7]=CLOUD_COLOUR
        # [8]=CITY, [9]=HILL_FAR, [10]=HILL_NEAR

        # --- Layer 1: Sky gradient (static) ----------------------------
        # 16-band gradient interpolation mapping cleanly to the 4 sky colors
        num_bands = 16
        for i in range(num_bands):
            y_base = i / num_bands
            y_next = (i+1) / num_bands
            
            idx_float = y_base * 3
            idx = int(idx_float)
            rem = idx_float - idx
            if idx >= 3:
                c = palette[3]
            else:
                c = C.interpolate_color(palette[idx], palette[idx+1], rem)
                
            canvas.create_rectangle(
                0, win_h * y_base, win_w, win_h * y_next + 1,
                fill=c, outline="", tags="bg"
            )

        # --- Layer 1.5: Stars (fade in at night) -----------------------
        if time_factor > 0.3:
            star_col = C.interpolate_color(palette[0], "#ffffff", (time_factor - 0.3) / 0.7)
            sys_t = time.time() * 2.0
            for sx, sy, sr, sp in self._stars:
                # offset stars slowly
                dx = (sx - self.cloud_offset * 0.5) % (win_w * 2)
                for tile in [0, win_w]:
                    x0 = dx + tile - win_w
                    if x0 < win_w and x0 > -10:
                        # blink effect
                        r = sr * (0.6 + 0.4 * math.sin(sys_t + sp))
                        canvas.create_oval(x0-r, sy-r, x0+r, sy+r, fill=star_col, outline="", tags="bg")

        # --- Layer 2: Sun/Moon + glow rings ---------------------------------
        # Sun sets downwards and Moon rises upwards based on time_factor
        sun_x = win_w * 0.80
        sun_y_start = win_h * 0.18
        # Sun sinks off screen as time approaches 1.0
        sun_y = sun_y_start + (time_factor * win_h * 0.5)
        sun_r = win_h * 0.08

        # Draw sun if visible
        if time_factor < 1.0:
            for ring, alpha in [(2.2, palette[5]), (1.6, palette[5]), (1.0, palette[4])]:
                r = sun_r * ring
                if time_factor > 0.5:
                    # As sunset fades to night, sun outer rings shrink/dim
                    r *= (1.0 - (time_factor - 0.5)*2)
                canvas.create_oval(
                    sun_x - r, sun_y - r, sun_x + r, sun_y + r,
                    fill=alpha, outline="", tags="bg"
                )
                
        # Render multiple concentric soft glows for the moon using sunset/night palettes
        if time_factor > 0.5:
            moon_x = win_w * 0.20
            moon_y_start = win_h * 0.60
            moon_y = moon_y_start - ((time_factor - 0.5) * 2.0 * win_h * 0.42)
            moon_r = win_h * 0.05
            
            # Subtle glow 1
            canvas.create_oval(moon_x - moon_r*1.8, moon_y - moon_r*1.8, moon_x + moon_r*1.8, moon_y + moon_r*1.8, fill="#1c304d", outline="", tags="bg")
            # Subtle glow 2
            canvas.create_oval(moon_x - moon_r*1.3, moon_y - moon_r*1.3, moon_x + moon_r*1.3, moon_y + moon_r*1.3, fill="#2a4566", outline="", tags="bg")
            # Moon solid base
            canvas.create_oval(moon_x - moon_r, moon_y - moon_r, moon_x + moon_r, moon_y + moon_r, fill="#e1f0ff", outline="", tags="bg")
            # Moon craters
            canvas.create_oval(moon_x - moon_r*0.4, moon_y - moon_r*0.2, moon_x + moon_r*0.1, moon_y + moon_r*0.4, fill="#b5cde8", outline="", tags="bg")
            canvas.create_oval(moon_x + moon_r*0.3, moon_y - moon_r*0.5, moon_x + moon_r*0.6, moon_y - moon_r*0.2, fill="#c9e0f7", outline="", tags="bg")
            
        # --- Layer 2.6: Shooting Star ------------------------------------
        if time_factor > 0.8:
            if not self.shooting_star["active"]:
                if random.random() < 0.005: # rare occurrence
                    self.shooting_star = {
                        "active": True, 
                        "x": random.randint(int(win_w*0.3), win_w), 
                        "y": random.randint(0, int(win_h*0.2)), 
                        "life": 20
                    }
            if self.shooting_star["active"]:
                sx = self.shooting_star["x"]
                sy = self.shooting_star["y"]
                canvas.create_line(sx, sy, sx + 60, sy - 20, fill="#ffffff", width=2, tags="bg")
                self.shooting_star["x"] -= 25
                self.shooting_star["y"] += 8
                self.shooting_star["life"] -= 1
                if self.shooting_star["life"] <= 0:
                    self.shooting_star["active"] = False

        # --- Layer 2.8: Clouds (slow scroll) ------------------------------
        cloud_col = C.interpolate_color(palette[7], "#a0b8d6", 0.4) # Dim slightly for contrast against sky
        for (cx, cy, rx, ry) in self._clouds:
            dx = (cx - self.cloud_offset) % (win_w * 2)
            for tile in [0, win_w * 2]:
                x0 = dx + tile - win_w * 2
                if x0 > -rx*3 and x0 < win_w + rx*3:
                    # Fluffy 5-piece cloud construction using overlapping ovals for volume
                    base_w = rx * 1.5
                    canvas.create_rectangle(x0 - base_w, cy + ry*0.2, x0 + base_w, cy + ry*0.9, fill=cloud_col, outline="", tags="bg")
                    puffs = [
                        (-rx*0.8, ry*0.3, rx*0.6, ry*0.6),    # far left
                        (-rx*0.2, -ry*0.2, rx*0.8, ry*0.8),   # center main high
                        (rx*0.6, 0.0, rx*0.7, ry*0.7),        # right mid
                        (rx*0.9, ry*0.4, rx*0.4, ry*0.5)      # far right small
                    ]
                    for px, py, pw, ph in puffs:
                        canvas.create_oval(x0 + px - pw, cy + py - ph, x0 + px + pw, cy + py + ph, fill=cloud_col, outline="", tags="bg")

        # --- Layer 3: Far hills (Mountains) ---
        hill_far_col = palette[9]
        self._draw_hills(canvas, self._hills_far,  self.hill_far_offset,  win_w, hill_far_col)

        # --- Layer 3.5: City Landmarks ----------------
        # The city sits AT 0.72 (same as near hills base) so it is behind them!
        city_top = win_h * 0.72
        
        # Calculate glowing window color
        if time_factor > 0.0:
            window_col = C.interpolate_color(palette[8], "#ffda75", time_factor)
        else:
            window_col = palette[8]

        # --- Procedural Generic Skyline ----------------
        dx = -(self.city_offset % (self.win_w * 2))
        for (bx, bw, bh, windows) in self._city_shapes:
            # Deterministic tint per building
            b_rng = random.Random(bx)
            tint = b_rng.uniform(0.75, 1.25)
            if tint < 1.0:
                b_col = C.interpolate_color(palette[8], "#05070a", 1.0 - tint)
            else:
                b_col = C.interpolate_color(palette[8], palette[7], min(1.0, tint - 1.0))
            
            for tile in [0, self.win_w * 2]:
                cx = dx + bx + tile
                if cx > -bw and cx < win_w:
                    cy = city_top
                    # Building silhouette
                    canvas.create_rectangle(cx, cy - bh, cx + bw, cy, fill=b_col, outline="", tags="bg")
                    
                    # Golden lit windows at night
                    if time_factor > 0.3:
                        for (wx, wy, ww, wh) in windows:
                            canvas.create_rectangle(cx + wx, cy - bh + wy, cx + wx + ww, cy - bh + wy + wh, fill=window_col, outline="", tags="bg")


        # --- Layer 3.8: Near Hills (Tree Line) ---
        hill_near_col = palette[10]
        self._draw_hills(canvas, self._hills_near, self.hill_near_offset, win_w, hill_near_col)

        # --- Billboard: One-time event at score >= 500, scrolls past once ---
        if score >= 500:
            bill_dx = (win_w * 0.85 - self.city_offset * 1.1) % (self.win_w * 6) - win_w
            if -400 < bill_dx < win_w + 50:
                by = city_top - int(win_h * 0.15) 
                bill_w = 320 
                bill_h = 60
                canvas.create_rectangle(bill_dx + 80, by + bill_h, bill_dx + 90, city_top, fill="#111", tags="bg")
                canvas.create_rectangle(bill_dx + 230, by + bill_h, bill_dx + 240, city_top, fill="#111", tags="bg")
                canvas.create_rectangle(bill_dx, by, bill_dx + bill_w, by + bill_h, fill="#1a1a2e", outline="#00ffcc", width=2, tags="bg")
                canvas.create_rectangle(bill_dx + 3, by + 3, bill_dx + bill_w - 3, by + bill_h - 3, fill="", outline="#004444", width=2, tags="bg")
                canvas.create_text(
                    bill_dx + bill_w//2, by + bill_h//2,
                    text="DO DRIFTING, NOT DRUGS.\nIdhar zyada chass hai.",
                    font=("Courier", int(win_h * 0.016), "bold"),
                    fill="#f39c12", justify="center", tags="bg"
                )

    # ------------------------------------------------------------------

    def _draw_hills(self, canvas, hill_data: dict, offset: float, win_w: int, override_color: str):
        """
        # FUNCTION: Draw the full mountain span tiled cleanly to prevent polygon wrapping/morphing tears.
        """
        pts  = hill_data.get("pts", [])
        snow_caps = hill_data.get("snow", [])
        col  = override_color
        shift = offset % (win_w * 2)
        
        # Tile across the screen seamlessly
        for t in [0, win_w * 2]:
            flat2 = []
            for (px, py) in pts:
                flat2.extend([px - shift + t - win_w * 2, py])
            if len(flat2) >= 6:
                canvas.create_polygon(flat2, fill=col, outline="", tags="bg")
            
            # Draw snowcaps on top of the jagged peaks
            for cap_pts in snow_caps:
                flat_cap = []
                for (px, py) in cap_pts:
                    flat_cap.extend([px - shift + t - win_w * 2, py])
                if len(flat_cap) == 8:
                    # White/Blueish tint for snow depending on time
                    snow_color = C.interpolate_color("#ffffff", "#6e8cac", min(1.0, offset*0.0001)) # using offset as dummy time or just hardcode base white
                    canvas.create_polygon(flat_cap, fill="#f2f8ff", outline="", tags="bg")

    # ------------------------------------------------------------------

    def draw_road(self, canvas, win_w: int, win_h: int,
                  gaps: list, road_offset: float, palette: list, time_factor: float = 0.0):
        """
        # FUNCTION: Draw the bridge surface, pillars, lane markings, and gaps.
        # Called after draw() so road appears on top of background.
        # Bridge, pillars, dashes â€“ yeh sab road ke hisse hain.
        #
        # Gaps are drawn as HOLES (void colour rectangles) punched into
        # the otherwise continuous bridge surface.
        """
        road_top    = int(win_h * C.ROAD_TOP_FRAC)
        road_bottom = win_h
        road_h      = road_bottom - road_top

        # Road surface (cartoon asphalt / dirt mix)
        # Apply time-of-day tint to the road surface!
        road_col = "#a6a096"
        wood_col = "#6d4c41"
        shadow_col = "#4e342e"
        
        if time_factor > 0.0:
            road_col = C.interpolate_color(road_col, "#1c1e24", time_factor)
            wood_col = C.interpolate_color(wood_col, "#1a1310", time_factor)
            shadow_col = C.interpolate_color(shadow_col, "#0d0908", time_factor)
            
            # Sunset warm orange splash across the road
            if time_factor > 0.1 and time_factor < 0.6:
                sunset_str = math.sin((time_factor - 0.1) * (math.pi / 0.5))
                road_col = C.interpolate_color(road_col, "#c87842", sunset_str * 0.4)

        # Calculate continuous road segments by slicing the full width with gaps
        segments = []
        curr_x = 0
        sorted_gaps = sorted(gaps, key=lambda g: g.x)
        for gap in sorted_gaps:
            if curr_x < gap.x:
                segments.append((curr_x, gap.x))
            curr_x = max(curr_x, gap.x + gap.w)
        if curr_x < win_w:
            segments.append((curr_x, win_w))
            
        refl_col = "#1a3355"

        # 1. Draw Road Surface, Guardrail Beams & Wet Reflections PER SEGMENT
        for (x0, x1) in segments:
            if x1 <= 0 or x0 >= win_w or x0 >= x1: continue
            
            # Road surface
            canvas.create_rectangle(
                x0, road_top, x1, road_bottom,
                fill=road_col, outline="", tags="road" 
            )
            # Guardrail beams
            canvas.create_rectangle(x0, road_top - 10, x1, road_top - 4, fill="#f5f5f5", outline="", tags="road")
            canvas.create_rectangle(x0, road_top - 4, x1, road_top - 2, fill="#e0e0e0", outline="", tags="road")
            
            # Wet Road Reflections (static, no scrolling)
            if time_factor > 0.4:
                for ry in [road_top + 8, road_top + 22, road_top + 40]:
                    canvas.create_line(x0, ry, x1, ry, fill=refl_col, width=1, tags="road")

        # 2. Draw Guardrail posts (wooden sticks) ONLY if they land on a solid segment
        post_step = 60
        start_post_x = -(road_offset % post_step)
        x = start_post_x
        while x < win_w:
            # Check if this X falls onto any segment
            is_solid = False
            for (sx0, sx1) in segments:
                if sx0 <= x <= sx1:
                    is_solid = True
                    break
            
            if is_solid:
                canvas.create_rectangle(x, road_top - 12, x + 6, road_top, fill=wood_col, outline="", tags="road")
                canvas.create_rectangle(x+6, road_top - 12, x + 8, road_top, fill=shadow_col, outline="", tags="road")
            x += post_step

        # 3. Utility Poles (Renegade Racing Style)
        # Drooping wires will still span across gaps! Only the wooden pole requires solid ground.
        lamp_step = 500
        start_lamp_x = -(road_offset % lamp_step)
        x = start_lamp_x
        num_lamps = int(win_w / lamp_step) + 2
        for _ in range(num_lamps):
            rx = x
            
            # Draw wires connecting to the PREVIOUS pole
            prev_x = rx - lamp_step
            if rx > -200 and prev_x < win_w + 200:
                y1 = road_top - int(win_h * 0.35)
                y2 = y1
                mid_x = (rx + prev_x) / 2
                mid_y = y1 + 40 # The droop/sag
                canvas.create_line(prev_x + 10, y1, mid_x, mid_y, rx - 10, y2, smooth=True, fill="#1c1c1c", width=2, tags="road")
                canvas.create_line(prev_x - 10, y1 - 20, mid_x, mid_y - 15, rx + 10, y2 - 20, smooth=True, fill="#131313", width=1, tags="road")

            # Draw the wooden utility pole only if ground exists
            is_solid = False
            for (sx0, sx1) in segments:
                if sx0 <= rx <= sx1:
                    is_solid = True
                    break
                    
            if is_solid:
                px = rx
                py = road_top
                ph = int(win_h * 0.40) # Tall wooden poles
                # Main trunk
                canvas.create_rectangle(px - 6, py - ph, px + 4, py, fill="#5c4033", outline="", tags="road")
                canvas.create_rectangle(px - 6, py - ph, px - 2, py, fill="#745140", outline="", tags="road")
                # Cross beams
                canvas.create_rectangle(px - 30, py - ph + 10, px + 30, py - ph + 18, fill="#5c4033", outline="", tags="road")
                canvas.create_rectangle(px - 20, py - ph + 30, px + 20, py - ph + 36, fill="#5c4033", outline="", tags="road")
                # Insulators
                for ix in [px - 25, px - 15, px + 15, px + 25]:
                    canvas.create_oval(ix - 3, py - ph + 4, ix + 3, py - ph + 10, fill="#aaddff", tags="road")
                
            x += lamp_step

        # ── Gap Fillers (Water bottom + dirt cross-sections) ──────────────
        for gap in gaps:
            gx   = gap.x
            gw   = gap.w
            gy   = road_top   # top of the underground void
            gdep = road_bottom # bottom of screen
            depth = gdep - gy
            
            # Note: We NO LONGER mask the sky! The parallax background naturally shows through the gap!

            # Water at the bottom
            water_top = gdep - int(depth * 0.4)
            # Base water
            water_col = C.interpolate_color("#1ca3ec", "#002b59", time_factor)
            canvas.create_rectangle(gx, water_top, gx + gw, gdep, fill=water_col, outline="", tags="road")
            # Deeper water shadow
            dark_water_col = C.interpolate_color("#1682bd", "#001b38", time_factor)
            canvas.create_rectangle(gx, water_top + 30, gx + gw, gdep, fill=dark_water_col, outline="", tags="road")
            # Wave highlight lines
            wave_col = C.interpolate_color("#75cbf0", "#144882", time_factor)
            canvas.create_line(gx, water_top + 10, gx + gw, water_top + 10, fill=wave_col, tags="road")
            canvas.create_line(gx, water_top + 20, gx + gw, water_top + 20, fill=dark_water_col, tags="road")

            # Left concrete/dirt edge
            canvas.create_rectangle(gx - 14, gy, gx, gdep, fill=wood_col, outline="", tags="road")
            canvas.create_rectangle(gx - 14, gy, gx - 12, gdep, fill=shadow_col, outline="", tags="road")
            canvas.create_rectangle(gx - 14, gy, gx, gy + 6, fill="#7cb342", outline="", tags="road")  # Grass rim

            # Right concrete/dirt edge
            canvas.create_rectangle(gx + gw, gy, gx + gw + 14, gdep, fill=wood_col, outline="", tags="road")
            canvas.create_rectangle(gx + gw + 12, gy, gx + gw + 14, gdep, fill=shadow_col, outline="", tags="road")
            canvas.create_rectangle(gx + gw, gy, gx + gw + 14, gy + 6, fill="#689f38", outline="", tags="road")  # Grass rim


