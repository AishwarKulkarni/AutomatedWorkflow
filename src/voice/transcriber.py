import os
import threading
import numpy as np
import sounddevice as sd
from PyQt6.QtCore import QObject, pyqtSignal
from faster_whisper import WhisperModel

class VoiceTranscriber(QObject):
    transcription_ready = pyqtSignal(str)
    status_changed = pyqtSignal(str)

    def __init__(self, model_size="base"):
        super().__init__()
        self.model_size = model_size
        self.model = None
        self.is_recording = False
        self.audio_data = []
        self.stream = None
        self.sample_rate = 16000

        # Initialize model in background to avoid blocking UI on startup
        threading.Thread(target=self._init_model, daemon=True).start()

    def _init_model(self):
        try:
            self.status_changed.emit("Loading Voice Model...")
            # Using CPU for maximum compatibility out of the box on Windows. 
            # In a real app we'd try CUDA first.
            self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            self.status_changed.emit("Ready")
        except Exception as e:
            print(f"Error loading whisper model: {e}")
            self.status_changed.emit("Error loading model")

    def _audio_callback(self, indata, frames, time, status):
        if status:
            print(status, flush=True)
        if self.is_recording:
            # We need a copy of the numpy array
            self.audio_data.append(indata.copy())

    def start_recording(self):
        if self.is_recording or self.model is None:
            return
        
        self.is_recording = True
        self.audio_data = []
        
        try:
            # Whisper expects 16kHz audio, float32, mono
            self.stream = sd.InputStream(samplerate=self.sample_rate, channels=1, 
                                       dtype='float32', callback=self._audio_callback)
            self.stream.start()
            self.status_changed.emit("Recording...")
        except Exception as e:
            print(f"Error starting audio stream: {e}")
            self.is_recording = False
            self.status_changed.emit("Audio Error")

    def stop_recording(self):
        if not self.is_recording:
            return
        
        self.is_recording = False
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        if not self.audio_data:
            self.status_changed.emit("Ready")
            return

        self.status_changed.emit("Transcribing...")
        # Process transcription in a separate thread so UI doesn't freeze
        threading.Thread(target=self._transcribe_audio, daemon=True).start()

    def _transcribe_audio(self):
        try:
            audio_np = np.concatenate(self.audio_data, axis=0)
            audio_np = audio_np.flatten()
            
            # Simple VAD/silence removal by checking if audio is too short or quiet
            if len(audio_np) < self.sample_rate * 0.5: # less than 0.5 seconds
                self.status_changed.emit("Ready")
                return

            segments, info = self.model.transcribe(audio_np, beam_size=5)
            
            text = " ".join([segment.text for segment in segments]).strip()
            
            if text:
                self.transcription_ready.emit(text)
            self.status_changed.emit("Ready")
            
        except Exception as e:
            print(f"Transcription error: {e}")
            self.status_changed.emit("Error transcribing")
