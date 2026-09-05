import sys
import os
import json
import requests
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


class ChatWorker(QThread):
    """Streams a reply from OpenRouter, chunk by chunk."""
    chunk = pyqtSignal(str)
    finished_ok = pyqtSignal()
    failed = pyqtSignal(str)

    def __init__(self, history):
        super().__init__()
        self.history = history
        self.is_cancelled = False

    def run(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        model = os.getenv("OPENROUTER_MODEL", "")
        api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        if not api_key:
            if not self.is_cancelled:
                self.failed.emit("No OPENROUTER_API_KEY set in .env")
            return
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {"model": model, "messages": self.history, "stream": True}
        try:
            with requests.post(api_url, headers=headers, json=payload, stream=True, timeout=60) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if self.is_cancelled:
                        break
                    if not line:
                        continue
                    line = line.decode("utf-8")
                    if not line.startswith("data: "):
                        continue
                    payload_str = line[6:]
                    if payload_str == "[DONE]":
                        break
                    try:
                        delta = json.loads(payload_str)["choices"][0]["delta"]
                        if "content" in delta:
                            if not self.is_cancelled:
                                self.chunk.emit(delta["content"])
                    except (json.JSONDecodeError, KeyError, IndexError):
                        pass
            if not self.is_cancelled:
                self.finished_ok.emit()
        except Exception as e:
            if not self.is_cancelled:
                self.failed.emit(str(e))


class HotkeyThread(QThread):
    toggle = pyqtSignal()

    def run(self):
        keyboard.add_hotkey("ctrl+space", self.toggle.emit)
        keyboard.wait()
