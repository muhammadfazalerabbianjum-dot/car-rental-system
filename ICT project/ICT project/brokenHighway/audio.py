import sys
import threading

def _safe_play(freq, dur):
    """
    Safely plays a Windows beep tone in a separate thread.
    Cross-platform safe (fails silently on non-Windows).
    """
    if sys.platform != "win32":
        return
    try:
        import winsound
        winsound.Beep(freq, dur)
    except Exception:
        pass

def play_jump():
    threading.Thread(target=_safe_play, args=(600, 80), daemon=True).start()

def play_double_jump():
    threading.Thread(target=_safe_play, args=(900, 80), daemon=True).start()

def play_crash():
    threading.Thread(target=_safe_play, args=(150, 400), daemon=True).start()
