import os
import tempfile
import threading
import asyncio
import edge_tts
import pygame
import re

class VoiceSynthesizer:
    def __init__(self, voice="en-GB-RyanNeural"):
        self.voice = voice
        pygame.mixer.init()
        self.is_speaking = False
        self._playback_thread = None

    def speak(self, text: str):
        if not text:
            return
            
        # Clean text to sound more natural (remove markdown, code blocks, etc.)
        text = re.sub(r'```.*?```', ' ', text, flags=re.DOTALL)
        text = re.sub(r'`.*?`', ' ', text)
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        text = re.sub(r'[*_#~>]+', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        if not text:
            return
            
        self.stop() # stop any ongoing speech
        self.is_speaking = True
        self._playback_thread = threading.Thread(target=self._generate_and_play, args=(text,), daemon=True)
        self._playback_thread.start()

    def _generate_and_play(self, text: str):
        # We need a temp file to store the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            temp_path = f.name
        
        try:
            # Generate audio using edge-tts
            communicate = edge_tts.Communicate(text, self.voice)
            asyncio.run(communicate.save(temp_path))
            
            if not self.is_speaking:
                # Was stopped during generation
                return
                
            # Play the audio
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            
            # Wait until it finishes, while checking if we were stopped
            while pygame.mixer.music.get_busy() and self.is_speaking:
                pygame.time.Clock().tick(10)
                
        except Exception as e:
            print(f"Error playing TTS: {e}")
        finally:
            if os.path.exists(temp_path):
                try:
                    # Sometimes pygame keeps file handle open slightly longer,
                    # unloading the music frees it.
                    pygame.mixer.music.unload()
                    os.remove(temp_path)
                except Exception as e:
                    print(f"Failed to remove temp audio file: {e}")
            self.is_speaking = False

    def stop(self):
        self.is_speaking = False
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
