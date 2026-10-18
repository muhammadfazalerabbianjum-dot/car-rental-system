# =============================================================================
# assets.py â€“ Broken Highway | Asset loading aur fallback
# =============================================================================
# FUNCTIONS:
#   load_car_image(path, target_w, target_h) â†’ PhotoImage or None
#   get_subsample_factor(orig_w, orig_h, target_w, target_h) â†’ int
# =============================================================================

import tkinter as tk
import os
from config import CAR_IMG_PATH, CAR_DISPLAY_W, CAR_DISPLAY_H


def get_subsample_factor(orig_w: int, orig_h: int,
                          target_w: int, target_h: int) -> int:
    """
    # FUNCTION: calculate the subsample integer divisor so the image fits
    # within (target_w, target_h) without going below 1.
    # tkinter PhotoImage.subsample(n) shrinks both dimensions by factor n.
    # We choose the factor that ensures BOTH dimensions fit the target.
    # Yeh function image ko sahi size mein karta hai.
    """
    # Since a car PNG with huge padding might be practically square,
    # we just base the subsample off width to avoid squishing the car too small.
    factor_w = max(1, orig_w // target_w)
    return factor_w


def load_car_image(target_w: int = CAR_DISPLAY_W,
                   target_h: int = CAR_DISPLAY_H,
                   path: str = CAR_IMG_PATH):
    """
    # FUNCTION: Load car.png and scale it to (target_w, target_h).
    # Returns a tk.PhotoImage object, or None if loading fails.
    # Caller MUST keep a reference to the returned object to prevent
    # Python's garbage collector from destroying it (tkinter quirk).
    #
    # Agar file nahi mili, to None return karo â€“ fallback use hogi.
    """
    # CONDITIONAL: check file exists before attempting load
    if not os.path.isfile(path):
        print(f"[ASSETS] car.png not found at: {path} â€” fallback will be used.")
        return None

    try:
        # Load the raw image
        raw = tk.PhotoImage(file=path)
        orig_w, orig_h = raw.width(), raw.height()

        # Calculate subsample factor
        factor = get_subsample_factor(orig_w, orig_h, target_w, target_h)

        # Apply subsampling (only shrink; tkinter cannot enlarge PNGs)
        scaled = raw.subsample(factor, factor)
        print(f"[ASSETS] car.png loaded: {orig_w}Ã—{orig_h} â†’ subsampled Ã—{factor} "
              f"â†’ ~{orig_w//factor}Ã—{orig_h//factor}")
        return scaled

    except Exception as exc:
        print(f"[ASSETS] Failed to load car.png: {exc} â€” fallback will be used.")
        return None


def read_highscore(path: str) -> int:
    """
    # FUNCTION: Read integer from highscore.txt.
    # If file missing or corrupt â†’ return 0 and create the file.
    # Highscore file se score paro, nahi hai to zero.
    """
    try:
        with open(path, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        write_highscore(path, 0)
        return 0


def write_highscore(path: str, score: int) -> None:
    """
    # FUNCTION: Write integer score to highscore.txt.
    # Naya highscore file mein likhna.
    """
    try:
        with open(path, "w") as f:
            f.write(str(score))
    except OSError as exc:
        print(f"[ASSETS] Could not write highscore: {exc}")
