import sys
import keyboard
from PyQt6.QtCore import QThread, pyqtSignal

def _steal_windows_focus(hwnd):
    """On Windows, a background hotkey can't call SetForegroundWindow
    directly — it silently no-ops. Tapping Alt first resets that lock so
    the window actually takes keyboard focus instead of just flashing."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        user32 = ctypes.windll.user32
        user32.keybd_event(0x12, 0, 0, 0)      # Alt down
        user32.SetForegroundWindow(hwnd)
        user32.keybd_event(0x12, 0, 0x2, 0)    # Alt up
    except Exception:
        pass

class HotkeyThread(QThread):
    toggle = pyqtSignal()

    def run(self):
        keyboard.add_hotkey("ctrl+space", self.toggle.emit)
        keyboard.wait()
