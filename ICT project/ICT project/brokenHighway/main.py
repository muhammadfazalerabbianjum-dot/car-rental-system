            # =============================================================================
# main.py - The adventures of AJX 704 | Darwaza (The front door)
# =============================================================================
# Entry point for the game.
# Responsibilities:
#   1. Show a resolution-picker dialog before the game window opens.
#   2. Create the main tkinter window at the chosen resolution.
#   3. Instantiate Game and start the main event loop.
#
# Run with:  py main.py   (from the brokenHighway\ directory)
# =============================================================================

import tkinter as tk
from tkinter import ttk
import sys
import os

# Ensure parent directory is on path so config etc. can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config as C
from game import Game


# =============================================================================
# RESOLUTION PICKER DIALOG
# =============================================================================

def pick_resolution() -> tuple[int, int] | None:
    """
    # FUNCTION: Show a small modal dialog that lets the player choose
    # the window resolution before the game starts.
    # Returns (width, height) tuple, or None if the user cancelled.
    #
    # Khelne se pehle resolution chunna - kitni bari khoob screen chahiye?
    """
    chosen = [None]   # mutable container so inner function can write to it

    dialog = tk.Tk()
    dialog.title("The adventures of AJX 704 - Select Resolution")
    dialog.resizable(False, False)
    dialog.configure(bg="#1a0533")

    # ---- Title label ----
    tk.Label(
        dialog,
        text="THE ADVENTURES OF",
        font=("Courier", 16, "bold"),
        fg="#f39c12", bg="#1a0533"
    ).pack(pady=(20, 2))

    tk.Label(
        dialog,
        text="AJX 704",
        font=("Courier", 24, "bold"),
        fg="#ffcc66", bg="#1a0533"
    ).pack(pady=(0, 16))

    tk.Label(
        dialog,
        text="Select Window Resolution:",
        font=("Courier", 11),
        fg="#ffffff", bg="#1a0533"
    ).pack(pady=(0, 8))

    # ---- Radio buttons for each resolution ----
    choice_var = tk.StringVar(value=C.DEFAULT_RES)

    for label, (w, h) in C.RESOLUTIONS.items():
        tk.Radiobutton(
            dialog,
            text=f"  {label}",
            variable=choice_var,
            value=label,
            font=("Courier", 11),
            fg="#dddddd", bg="#1a0533",
            selectcolor="#2c1654",
            activebackground="#1a0533",
            activeforeground="#f39c12",
        ).pack(anchor="w", padx=40, pady=2)

    # ---- Buttons row ----
    btn_frame = tk.Frame(dialog, bg="#1a0533")
    btn_frame.pack(pady=20)

    def on_start():
        key = choice_var.get()
        chosen[0] = C.RESOLUTIONS[key]
        dialog.destroy()

    def on_cancel():
        dialog.destroy()

    tk.Button(
        btn_frame,
        text="  >  Launch  ",
        font=("Courier", 12, "bold"),
        bg="#e67e22", fg="#ffffff",
        activebackground="#f39c12",
        relief="flat", cursor="hand2",
        command=on_start,
    ).pack(side="left", padx=10)

    tk.Button(
        btn_frame,
        text="  X  Exit  ",
        font=("Courier", 12),
        bg="#333333", fg="#aaaaaa",
        activebackground="#555555",
        relief="flat", cursor="hand2",
        command=on_cancel,
    ).pack(side="left", padx=10)

    # Centre dialog on screen
    dialog.update_idletasks()
    sw = dialog.winfo_screenwidth()
    sh = dialog.winfo_screenheight()
    dw = dialog.winfo_reqwidth()
    dh = dialog.winfo_reqheight()
    dialog.geometry(f"{dw}x{dh}+{(sw - dw) // 2}+{(sh - dh) // 2}")

    dialog.mainloop()
    return chosen[0]


# =============================================================================
# MAIN
# =============================================================================

def main():
    """
    # FUNCTION: Application entry point.
    # 1. Show resolution picker.
    # 2. Create game window.
    # 3. Start game.
    # Shuru karo - khel ka aghaz!
    """
    resolution = pick_resolution()

    # CONDITIONAL: user cancelled the dialog
    if resolution is None:
        print("[MAIN] Launch cancelled.")
        sys.exit(0)

    win_w, win_h = resolution

    # Create the main game window
    root = tk.Tk()
    root.title(C.TITLE)
    root.geometry(f"{win_w}x{win_h}")
    root.resizable(False, False)
    root.configure(bg="#000000")

    # Centre on screen
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"{win_w}x{win_h}+{(sw - win_w) // 2}+{(sh - win_h) // 2}")

    # Instantiate the game (also starts the update loop)
    game = Game(root, win_w, win_h)

    # Hand control to tkinter event loop
    root.mainloop()


if __name__ == "__main__":
    main()
