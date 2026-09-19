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
    toggle_recording = pyqtSignal()

    def run(self):
        # Toggle UI using ctrl+space
        keyboard.add_hotkey("ctrl+space", self.toggle.emit)
        
        # Toggle recording using backtick key (`)
        self.key_pressed = False
        
        def on_press(e):
            if not self.key_pressed:
                self.key_pressed = True
                self.toggle_recording.emit()
                
        def on_release(e):
            self.key_pressed = False
                
        keyboard.on_press_key("`", on_press, suppress=True)
        keyboard.on_release_key("`", on_release, suppress=True)
        
        keyboard.wait()
