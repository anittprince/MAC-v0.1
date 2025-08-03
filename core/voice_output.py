"""
MAC Assistant - Voice Output Module
Handles text-to-speech using pyttsx3.
"""

import pyttsx3
import threading
import queue
from typing import Optional, List


class VoiceOutput:
    def __init__(self):
        self.engine = None
        self.is_speaking = False
        self.speech_queue = queue.Queue()
        self.speech_thread = None
        
        # Initialize TTS engine
        self._initialize_engine()
        
        # Start speech processing thread
        self._start_speech_thread()
    
    def _initialize_engine(self):
        """Initialize the text-to-speech engine."""
        try:
            self.engine = pyttsx3.init()
            
            # Configure voice properties
            self._configure_voice()
            
            print("Text-to-speech engine initialized successfully")
        except Exception as e:
            print(f"Failed to initialize TTS engine: {e}")
    
    def _configure_voice(self):
        """Configure voice properties like rate, volume, and voice."""
        if not self.engine:
            return
        
        try:
            # Set speech rate (words per minute)
            self.engine.setProperty('rate', 180)
            
            # Set volume (0.0 to 1.0)
            self.engine.setProperty('volume', 0.9)
            
            # Try to set a preferred voice
            voices = self.engine.getProperty('voices')
            if voices:
                # Prefer female voice if available, otherwise use first available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
                else:
                    # Use first available voice
                    self.engine.setProperty('voice', voices[0].id)
            
        except Exception as e:
            print(f"Error configuring voice: {e}")
    
    def speak(self, text: str, interrupt: bool = False):
        """
        Add text to speech queue.
        
        Args:
            text (str): Text to speak
            interrupt (bool): If True, clear queue and speak immediately
        """
        if not text or not text.strip():
            return
        
        if interrupt:
            # Clear the queue and stop current speech
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                except queue.Empty:
                    break
            self.stop_speaking()
        
        self.speech_queue.put(text.strip())
    
    def speak_immediately(self, text: str):
        """
        Speak text immediately, bypassing the queue.
        
        Args:
            text (str): Text to speak
        """
        if not self.engine or not text or not text.strip():
            return
        
        try:
            self.is_speaking = True
            self.engine.say(text.strip())
            self.engine.runAndWait()
            self.is_speaking = False
        except Exception as e:
            print(f"Error speaking immediately: {e}")
            self.is_speaking = False
    
    def _start_speech_thread(self):
        """Start the background thread for processing speech queue."""
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()
    
    def _speech_worker(self):
        """Worker thread that processes the speech queue."""
        while True:
            try:
                # Get text from queue (blocks until available)
                text = self.speech_queue.get(timeout=1.0)
                
                if text and self.engine:
                    self.is_speaking = True
                    self.engine.say(text)
                    self.engine.runAndWait()
                    self.is_speaking = False
                
                # Mark task as done
                self.speech_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in speech worker: {e}")
                self.is_speaking = False
    
    def stop_speaking(self):
        """Stop current speech."""
        if self.engine and self.is_speaking:
            try:
                self.engine.stop()
                self.is_speaking = False
            except Exception as e:
                print(f"Error stopping speech: {e}")
    
    def is_busy(self) -> bool:
        """Check if currently speaking or has items in queue."""
        return self.is_speaking or not self.speech_queue.empty()
    
    def wait_until_done(self, timeout: Optional[float] = None):
        """
        Wait until all queued speech is complete.
        
        Args:
            timeout (Optional[float]): Maximum time to wait
        """
        try:
            if timeout:
                self.speech_queue.join()  # Wait for all tasks to complete
            else:
                self.speech_queue.join()
        except Exception as e:
            print(f"Error waiting for speech completion: {e}")
    
    def clear_queue(self):
        """Clear all pending speech from queue."""
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
            except queue.Empty:
                break
    
    def get_available_voices(self) -> List[dict]:
        """Get list of available voices."""
        if not self.engine:
            return []
        
        try:
            voices = self.engine.getProperty('voices')
            voice_list = []
            
            for voice in voices:
                voice_info = {
                    'id': voice.id,
                    'name': voice.name,
                    'languages': getattr(voice, 'languages', []),
                    'gender': getattr(voice, 'gender', 'unknown'),
                    'age': getattr(voice, 'age', 'unknown')
                }
                voice_list.append(voice_info)
            
            return voice_list
        except Exception as e:
            print(f"Error getting available voices: {e}")
            return []
    
    def set_voice(self, voice_id: str) -> bool:
        """
        Set the voice to use for speech.
        
        Args:
            voice_id (str): Voice ID to use
            
        Returns:
            bool: True if voice was set successfully
        """
        if not self.engine:
            return False
        
        try:
            self.engine.setProperty('voice', voice_id)
            return True
        except Exception as e:
            print(f"Error setting voice: {e}")
            return False
    
    def set_rate(self, rate: int) -> bool:
        """
        Set the speech rate.
        
        Args:
            rate (int): Speech rate in words per minute
            
        Returns:
            bool: True if rate was set successfully
        """
        if not self.engine:
            return False
        
        try:
            self.engine.setProperty('rate', rate)
            return True
        except Exception as e:
            print(f"Error setting speech rate: {e}")
            return False
    
    def set_volume(self, volume: float) -> bool:
        """
        Set the speech volume.
        
        Args:
            volume (float): Volume level (0.0 to 1.0)
            
        Returns:
            bool: True if volume was set successfully
        """
        if not self.engine:
            return False
        
        try:
            volume = max(0.0, min(1.0, volume))  # Clamp between 0.0 and 1.0
            self.engine.setProperty('volume', volume)
            return True
        except Exception as e:
            print(f"Error setting volume: {e}")
            return False
