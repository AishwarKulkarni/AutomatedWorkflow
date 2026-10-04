import io
import threading
import asyncio
import edge_tts
import pygame
import re
import logging

class VoiceSynthesizer:
    def __init__(self, voice="en-GB-RyanNeural"):
        self.voice = voice
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
        try:
            # Generate audio using edge-tts
            communicate = edge_tts.Communicate(text, self.voice)
            audio_data = bytearray()
            
            async def generate_audio():
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data.extend(chunk["data"])
                        
            asyncio.run(generate_audio())
            
            if not self.is_speaking:
                return
                
            # Initialize pygame mixer in the playback thread for safety
            if not pygame.mixer.get_init():
                pygame.mixer.init()
                
            audio_stream = io.BytesIO(audio_data)
            pygame.mixer.music.load(audio_stream)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy() and self.is_speaking:
                pygame.time.Clock().tick(10)
                
        except Exception as e:
            logging.error(f"Error playing TTS: {e}")
        finally:
            try:
                pygame.mixer.music.unload()
                # We can keep mixer initialized for the next run, or quit it.
            except Exception:
                pass
            self.is_speaking = False

    def stop(self):
        self.is_speaking = False
        try:
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
        except Exception:
            pass
