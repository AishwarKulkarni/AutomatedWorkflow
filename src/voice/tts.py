import os
import tempfile
import asyncio
import edge_tts
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
import re

def strip_html(text):
    # Quick and dirty way to strip html tags which sometimes might be present
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

class TTSWorker(QThread):
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, text: str, voice: str = "en-US-AriaNeural"):
        super().__init__()
        self.text = strip_html(text)
        self.voice = voice

    def run(self):
        try:
            fd, temp_file = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)
            
            communicate = edge_tts.Communicate(self.text, self.voice)
            
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(communicate.save(temp_file))
            loop.close()
            
            self.finished.emit(temp_file)
        except Exception as e:
            self.failed.emit(str(e))

class TTSManager(QObject):
    playback_started = pyqtSignal()
    playback_finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.mediaStatusChanged.connect(self._on_media_status)
        self._current_file = None

    def speak(self, text: str):
        if not text.strip():
            return
            
        # Stop current if playing
        self.player.stop()
        if self._current_file and os.path.exists(self._current_file):
            try:
                os.remove(self._current_file)
            except Exception:
                pass

        self.worker = TTSWorker(text)
        self.worker.finished.connect(self._on_synthesized)
        self.worker.failed.connect(lambda e: print(f"TTS Error: {e}"))
        self.worker.start()

    def _on_synthesized(self, file_path: str):
        self._current_file = file_path
        url = QUrl.fromLocalFile(file_path)
        self.player.setSource(url)
        self.player.play()
        self.playback_started.emit()

    def _on_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.playback_finished.emit()
            if self._current_file and os.path.exists(self._current_file):
                try:
                    os.remove(self._current_file)
                    self._current_file = None
                except Exception:
                    pass
