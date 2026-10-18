# =============================================================================
# physics.py â€“ Broken Highway | Tabeeyat ke qawaneen (Laws of physics)
# =============================================================================
# Pure stateless functions â€“ no side effects, easy to test in isolation.
# These functions are called by the Game loop every frame.
#
# KERNEL NOTE: Physics is separated so the game loop stays readable.
# Each function does ONE thing. KISS principle (Keep It Simple, Stupid).
# =============================================================================

from config import GRAVITY, MAX_FALL_VEL


def apply_gravity(vy: float) -> float:
    """
    # FUNCTION: Increase downward velocity by GRAVITY each frame.
    # Returns the new vy value.
    # Gravity har frame mein vy ko badhata hai â€“ upar se neeche.
    #
    # Physics: F = ma â†’ simplified to constant acceleration per frame.
    # Capped at MAX_FALL_VEL so car cannot warp through thin geometry.
    """
    vy += GRAVITY
    # CONDITIONAL: clamp to terminal velocity
    if vy > MAX_FALL_VEL:
        vy = MAX_FALL_VEL
    return vy


def aabb_overlap(ax: float, ay: float, aw: float, ah: float,
                 bx: float, by: float, bw: float, bh: float) -> bool:
    """
    # FUNCTION: Axis-Aligned Bounding Box (AABB) collision detection.
    # Returns True if rectangles A and B overlap.
    # Do rectangles overlap? Agar haan to True.
    #
    # Uses the Separating Axis Theorem simplified for axis-aligned boxes:
    # Two boxes DO NOT overlap if there is a gap on ANY axis.
    # If no such gap exists â†’ they overlap.
    #
    # Parameters:
    #   ax, ay â€“ top-left of rect A; aw, ah â€“ width/height of A
    #   bx, by â€“ top-left of rect B; bw, bh â€“ width/height of B
    """
    # CONDITIONAL: Check for separation on X axis
    if ax + aw <= bx or bx + bw <= ax:
        return False
    # CONDITIONAL: Check for separation on Y axis
    if ay + ah <= by or by + bh <= ay:
        return False
    return True


def clamp(value: float, lo: float, hi: float) -> float:
    """
    # FUNCTION: Limit value to [lo, hi] range.
    # Qemat ko hadood mein rakhna (keep value within bounds).
    """
    return max(lo, min(hi, value))


def apply_speed_ramp(current_speed: float, total_score: int,
                     triggered_spikes: set, speed_spikes: dict,
                     ramp_rate: float, max_speed: float) -> tuple:
    """
    # FUNCTION: Calculate new scroll speed based on score.
    # Handles both gradual ramp and sudden spikes at milestones.
    # Returns (new_speed, updated_triggered_spikes).
    #
    # Speed spikes: Ek jagah par achanak raftar badh jaati hai!
    # Gradual ramp: Dheere dheere raftar badhti hai.
    """
    speed = current_speed

    # LOOP: check each spike threshold
    for threshold, delta in speed_spikes.items():
        # CONDITIONAL: spike triggers when score crosses threshold
        if total_score >= threshold and threshold not in triggered_spikes:
            speed += delta
            triggered_spikes.add(threshold)

    # Gradual ramp: percentage of score contributes small increment
    ramp = (total_score / 100) * ramp_rate
    speed = clamp(current_speed + ramp * 0.016, current_speed, max_speed)

    # Apply spikes on top
    speed = clamp(speed, 0, max_speed)
    return speed, triggered_spikes


def get_ground_y(win_h: int, road_top_frac: float, car_h: float) -> float:
    """
    # FUNCTION: Compute the Y coordinate where car rests on the road.
    # Win_h * road_top_frac gives road surface top; subtract car height.
    # Gaadi zameen par kahan rukti hai? Yahan calculate karo.
    """
    road_top = win_h * road_top_frac
    return road_top - car_h
