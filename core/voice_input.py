"""
MAC Assistant - Voice Input Module
Handles speech recognition using Vosk and SpeechRecognition.
"""

import json
import threading
import queue
import time
from typing import Optional, Callable
import speech_recognition as sr
import vosk
import pyaudio


class VoiceInput:
    def __init__(self, model_path: str = "models/vosk-model"):
        self.model_path = model_path
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.vosk_model = None
        self.vosk_rec = None
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.callback = None
        
        # Initialize Vosk model
        self._initialize_vosk()
        
        # Adjust for ambient noise
        self._calibrate_microphone()
    
    def _initialize_vosk(self):
        """Initialize Vosk speech recognition model."""
        try:
            self.vosk_model = vosk.Model(self.model_path)
            self.vosk_rec = vosk.KaldiRecognizer(self.vosk_model, 16000)
            print("Vosk model initialized successfully")
        except Exception as e:
            print(f"Failed to initialize Vosk model: {e}")
            print("Falling back to online speech recognition")
    
    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise."""
        try:
            with self.microphone as source:
                print("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Microphone calibrated")
        except Exception as e:
            print(f"Failed to calibrate microphone: {e}")
    
    def listen_once(self, timeout: float = 5.0) -> Optional[str]:
        """
        Listen for a single voice command.
        
        Args:
            timeout (float): Maximum time to wait for audio
            
        Returns:
            Optional[str]: Recognized text or None if failed
        """
        try:
            with self.microphone as source:
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=5)
                
            # Try Vosk first if available
            if self.vosk_rec:
                text = self._recognize_with_vosk(audio)
                if text:
                    return text
            
            # Fallback to Google Speech Recognition
            text = self.recognizer.recognize_google(audio)
            print(f"Recognized: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("Listening timeout")
            return None
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error during speech recognition: {e}")
            return None
    
    def _recognize_with_vosk(self, audio) -> Optional[str]:
        """Recognize speech using Vosk offline model."""
        try:
            # Convert audio to the format Vosk expects
            audio_data = audio.get_wav_data()
            
            # Vosk expects raw audio data
            if self.vosk_rec.AcceptWaveform(audio_data):
                result = json.loads(self.vosk_rec.Result())
                text = result.get('text', '').strip()
                if text:
                    print(f"Vosk recognized: {text}")
                    return text
            else:
                result = json.loads(self.vosk_rec.PartialResult())
                text = result.get('partial', '').strip()
                if text:
                    print(f"Vosk partial: {text}")
                    return text
                    
        except Exception as e:
            print(f"Vosk recognition error: {e}")
        
        return None
    
    def start_continuous_listening(self, callback: Callable[[str], None]):
        """
        Start continuous listening in background thread.
        
        Args:
            callback: Function to call with recognized text
        """
        if self.is_listening:
            print("Already listening")
            return
        
        self.callback = callback
        self.is_listening = True
        
        # Start background thread for continuous listening
        listening_thread = threading.Thread(target=self._continuous_listen_loop, daemon=True)
        listening_thread.start()
        print("Started continuous listening")
    
    def stop_continuous_listening(self):
        """Stop continuous listening."""
        self.is_listening = False
        print("Stopped continuous listening")
    
    def _continuous_listen_loop(self):
        """Main loop for continuous listening."""
        while self.is_listening:
            try:
                text = self.listen_once(timeout=1.0)
                if text and self.callback:
                    self.callback(text)
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
            except Exception as e:
                print(f"Error in continuous listening loop: {e}")
                time.sleep(1.0)  # Longer delay on error
    
    def is_microphone_available(self) -> bool:
        """Check if microphone is available."""
        try:
            with self.microphone as source:
                pass
            return True
        except Exception:
            return False
    
    def get_microphone_info(self) -> dict:
        """Get microphone device information."""
        try:
            p = pyaudio.PyAudio()
            info = {
                'default_input_device': p.get_default_input_device_info(),
                'device_count': p.get_device_count()
            }
            p.terminate()
            return info
        except Exception as e:
            return {'error': str(e)}
