# Voice Processing Documentation

This document provides detailed information about the voice processing capabilities of the MAC Assistant, including speech recognition, text-to-speech synthesis, and audio handling.

## Overview

MAC Assistant uses a combination of offline and real-time voice processing technologies to provide responsive voice interaction without requiring internet connectivity for core functionality.

**Key Components:**
- **Speech Recognition**: Vosk (Kaldi-based) for offline speech-to-text
- **Text-to-Speech**: pyttsx3 for cross-platform voice synthesis
- **Audio Handling**: PyAudio for microphone input and speaker output
- **Voice Activity Detection**: Built-in silence detection and voice triggering

## Speech Recognition (Vosk)

### Technology Overview

**Vosk Speech Recognition:**
- **Based on**: Kaldi ASR (Automatic Speech Recognition) toolkit
- **Type**: Offline, local processing
- **Languages**: 20+ languages supported
- **Models**: Multiple sizes from 40MB to 1.8GB
- **Performance**: Real-time recognition on modern hardware

### Model Selection

#### Small Model (vosk-model-small-en-us-0.15)
```
Size: ~40MB
Accuracy: 85-90% for clear speech
Speed: Very fast, real-time
Use Case: Basic commands, resource-constrained systems
Download: https://alphacephei.com/vosk/models
```

#### Large Model (vosk-model-en-us-0.22)
```
Size: ~1.8GB
Accuracy: 95-98% for clear speech
Speed: Slower, but still real-time on modern hardware
Use Case: High accuracy requirements, complex commands
Download: https://alphacephei.com/vosk/models
```

#### Model Comparison

| Feature | Small Model | Large Model |
|---------|-------------|-------------|
| **Size** | 40MB | 1.8GB |
| **Accuracy** | 85-90% | 95-98% |
| **Speed** | Very Fast | Fast |
| **Memory Usage** | ~100MB | ~300MB |
| **CPU Usage** | Low | Medium |
| **Best For** | Basic commands | Complex speech |

### Implementation Details

#### Voice Input Module (`core/voice_input.py`)

```python
import vosk
import pyaudio
import json
import threading
from typing import Optional

class VoiceInput:
    def __init__(self, model_path: str = "models/vosk-model"):
        """
        Initialize voice input with Vosk model.
        
        Args:
            model_path: Path to Vosk model directory
        """
        self.model_path = model_path
        self.model = None
        self.recognizer = None
        self.audio = None
        self.stream = None
        self.is_listening = False
        
        self._initialize_model()
        self._initialize_audio()
    
    def _initialize_model(self):
        """Load Vosk model and create recognizer."""
        try:
            print(f"Loading Vosk model from {self.model_path}")
            self.model = vosk.Model(self.model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, 16000)
            print("Vosk model loaded successfully")
        except Exception as e:
            print(f"Error loading Vosk model: {e}")
            raise
    
    def _initialize_audio(self):
        """Initialize PyAudio for microphone input."""
        try:
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=4096
            )
            print("Audio input initialized")
        except Exception as e:
            print(f"Error initializing audio: {e}")
            raise
```

#### Audio Processing Pipeline

```python
def listen(self) -> Optional[str]:
    """
    Listen for voice input and return recognized text.
    
    Returns:
        Recognized text or None if no speech detected
    """
    if not self.stream:
        return None
    
    print("Listening for voice input...")
    self.is_listening = True
    
    try:
        while self.is_listening:
            # Read audio data
            data = self.stream.read(4096, exception_on_overflow=False)
            
            # Process audio with Vosk
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = result.get('text', '').strip()
                
                if text:
                    print(f"Recognized: {text}")
                    return text
            
            # Check for partial results
            partial = json.loads(self.recognizer.PartialResult())
            partial_text = partial.get('partial', '')
            
            if partial_text:
                print(f"Partial: {partial_text}", end='\r')
    
    except Exception as e:
        print(f"Error during voice recognition: {e}")
        return None
    
    return None
```

### Voice Activity Detection

#### Silence Detection

```python
import numpy as np

def detect_voice_activity(self, audio_data: bytes, threshold: float = 0.01) -> bool:
    """
    Detect if audio contains speech.
    
    Args:
        audio_data: Raw audio bytes
        threshold: Energy threshold for voice detection
        
    Returns:
        True if voice activity detected
    """
    # Convert bytes to numpy array
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    
    # Calculate RMS energy
    rms = np.sqrt(np.mean(audio_array.astype(np.float32)**2))
    
    # Normalize to 0-1 range
    normalized_energy = rms / 32768.0
    
    return normalized_energy > threshold
```

#### Voice Triggering

```python
def wait_for_voice_trigger(self, timeout: float = 30.0) -> bool:
    """
    Wait for voice activity before starting recognition.
    
    Args:
        timeout: Maximum time to wait for voice
        
    Returns:
        True if voice detected within timeout
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        data = self.stream.read(1024, exception_on_overflow=False)
        
        if self.detect_voice_activity(data):
            print("Voice activity detected, starting recognition...")
            return True
        
        time.sleep(0.1)
    
    return False
```

## Text-to-Speech (pyttsx3)

### Technology Overview

**pyttsx3 Features:**
- **Cross-platform**: Works on Windows, macOS, Linux
- **Offline**: No internet required
- **Multiple engines**: SAPI5 (Windows), NSSpeechSynthesizer (macOS), espeak (Linux)
- **Voice selection**: Multiple voice options
- **Rate control**: Adjustable speech speed
- **Volume control**: Adjustable output volume

### Implementation Details

#### Voice Output Module (`core/voice_output.py`)

```python
import pyttsx3
import threading
from typing import Optional, List

class VoiceOutput:
    def __init__(self):
        """Initialize text-to-speech engine."""
        self.engine = None
        self.available_voices = []
        self.current_voice = None
        
        self._initialize_engine()
        self._configure_voice()
    
    def _initialize_engine(self):
        """Initialize pyttsx3 engine."""
        try:
            self.engine = pyttsx3.init()
            print("Text-to-speech engine initialized")
        except Exception as e:
            print(f"Error initializing TTS engine: {e}")
            raise
    
    def _configure_voice(self):
        """Configure voice settings."""
        if not self.engine:
            return
        
        # Get available voices
        self.available_voices = self.engine.getProperty('voices')
        
        # Set default voice (first available)
        if self.available_voices:
            self.current_voice = self.available_voices[0]
            self.engine.setProperty('voice', self.current_voice.id)
        
        # Configure speech rate (words per minute)
        self.engine.setProperty('rate', 200)
        
        # Configure volume (0.0 to 1.0)
        self.engine.setProperty('volume', 0.8)
        
        print(f"Voice configured: {self.current_voice.name if self.current_voice else 'Default'}")
```

#### Speech Synthesis

```python
def speak(self, text: str, blocking: bool = True) -> bool:
    """
    Convert text to speech and play audio.
    
    Args:
        text: Text to speak
        blocking: Whether to wait for speech to complete
        
    Returns:
        True if speech started successfully
    """
    if not self.engine or not text.strip():
        return False
    
    try:
        print(f"Speaking: {text}")
        
        if blocking:
            # Synchronous speech
            self.engine.say(text)
            self.engine.runAndWait()
        else:
            # Asynchronous speech
            thread = threading.Thread(target=self._speak_async, args=(text,))
            thread.daemon = True
            thread.start()
        
        return True
    
    except Exception as e:
        print(f"Error during speech synthesis: {e}")
        return False

def _speak_async(self, text: str):
    """Asynchronous speech synthesis."""
    self.engine.say(text)
    self.engine.runAndWait()
```

### Voice Customization

#### Voice Selection

```python
def list_available_voices(self) -> List[Dict[str, str]]:
    """
    Get list of available voices.
    
    Returns:
        List of voice information dictionaries
    """
    voices = []
    
    for voice in self.available_voices:
        voices.append({
            'id': voice.id,
            'name': voice.name,
            'languages': voice.languages,
            'gender': 'male' if 'male' in voice.name.lower() else 'female'
        })
    
    return voices

def set_voice(self, voice_id: str) -> bool:
    """
    Set active voice by ID.
    
    Args:
        voice_id: Voice identifier
        
    Returns:
        True if voice set successfully
    """
    try:
        self.engine.setProperty('voice', voice_id)
        # Update current voice reference
        for voice in self.available_voices:
            if voice.id == voice_id:
                self.current_voice = voice
                break
        return True
    except Exception as e:
        print(f"Error setting voice: {e}")
        return False
```

#### Speech Rate Control

```python
def set_speech_rate(self, rate: int) -> bool:
    """
    Set speech rate in words per minute.
    
    Args:
        rate: Words per minute (typically 150-250)
        
    Returns:
        True if rate set successfully
    """
    try:
        # Clamp rate to reasonable range
        rate = max(50, min(400, rate))
        self.engine.setProperty('rate', rate)
        print(f"Speech rate set to {rate} WPM")
        return True
    except Exception as e:
        print(f"Error setting speech rate: {e}")
        return False

def set_volume(self, volume: float) -> bool:
    """
    Set speech volume.
    
    Args:
        volume: Volume level (0.0 to 1.0)
        
    Returns:
        True if volume set successfully
    """
    try:
        # Clamp volume to valid range
        volume = max(0.0, min(1.0, volume))
        self.engine.setProperty('volume', volume)
        print(f"Speech volume set to {volume}")
        return True
    except Exception as e:
        print(f"Error setting volume: {e}")
        return False
```

## Audio Processing Pipeline

### Complete Voice Processing Flow

```python
class VoiceProcessor:
    def __init__(self, model_path: str = "models/vosk-model"):
        """Initialize complete voice processing pipeline."""
        self.voice_input = VoiceInput(model_path)
        self.voice_output = VoiceOutput()
        self.brain = MACBrain()
        self.is_processing = False
    
    def process_voice_command(self) -> Optional[Dict[str, Any]]:
        """
        Complete voice processing pipeline.
        
        Returns:
            Command response or None if no input
        """
        try:
            # 1. Voice Activity Detection
            if not self.voice_input.wait_for_voice_trigger(timeout=30):
                return None
            
            # 2. Speech Recognition
            recognized_text = self.voice_input.listen()
            if not recognized_text:
                return None
            
            # 3. Command Processing
            response = self.brain.process_command(recognized_text)
            
            # 4. Voice Response
            if response and response.get('message'):
                self.voice_output.speak(response['message'])
            
            return response
        
        except Exception as e:
            error_message = f"Error processing voice command: {e}"
            print(error_message)
            self.voice_output.speak("Sorry, I encountered an error processing your command.")
            return None
```

### Real-time Voice Processing

```python
def start_continuous_listening(self):
    """Start continuous voice processing loop."""
    print("Starting continuous voice processing...")
    self.is_processing = True
    
    while self.is_processing:
        try:
            # Process voice command
            response = self.process_voice_command()
            
            if response:
                print(f"Command processed: {response['message']}")
            
            # Brief pause before next iteration
            time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\nStopping voice processing...")
            self.stop_processing()
        except Exception as e:
            print(f"Error in continuous processing: {e}")
            time.sleep(1)  # Wait before retrying

def stop_processing(self):
    """Stop voice processing loop."""
    self.is_processing = False
    self.voice_input.stop_listening()
    print("Voice processing stopped")
```

## Performance Optimization

### Audio Buffer Management

```python
class OptimizedVoiceInput(VoiceInput):
    def __init__(self, model_path: str, buffer_size: int = 4096):
        super().__init__(model_path)
        self.buffer_size = buffer_size
        self.audio_buffer = collections.deque(maxlen=10)
    
    def _process_audio_buffer(self):
        """Process audio buffer for better performance."""
        while self.audio_buffer:
            audio_chunk = self.audio_buffer.popleft()
            
            if self.recognizer.AcceptWaveform(audio_chunk):
                result = json.loads(self.recognizer.Result())
                return result.get('text', '').strip()
        
        return None
```

### Memory Management

```python
def cleanup_resources(self):
    """Clean up audio and model resources."""
    try:
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.audio:
            self.audio.terminate()
        
        # Clear model from memory
        self.model = None
        self.recognizer = None
        
        print("Voice processing resources cleaned up")
    
    except Exception as e:
        print(f"Error during cleanup: {e}")
```

## Voice Quality Enhancement

### Noise Filtering

```python
import scipy.signal
import numpy as np

def apply_noise_filter(self, audio_data: np.ndarray, sample_rate: int = 16000) -> np.ndarray:
    """
    Apply basic noise filtering to audio data.
    
    Args:
        audio_data: Raw audio samples
        sample_rate: Audio sample rate
        
    Returns:
        Filtered audio data
    """
    # High-pass filter to remove low-frequency noise
    nyquist = sample_rate // 2
    low_cutoff = 300 / nyquist  # 300 Hz cutoff
    b, a = scipy.signal.butter(4, low_cutoff, btype='high')
    filtered_audio = scipy.signal.filtfilt(b, a, audio_data)
    
    # Normalize audio levels
    max_amplitude = np.max(np.abs(filtered_audio))
    if max_amplitude > 0:
        filtered_audio = filtered_audio / max_amplitude * 0.8
    
    return filtered_audio
```

### Voice Activity Detection Improvements

```python
def advanced_voice_detection(self, audio_data: bytes, 
                           energy_threshold: float = 0.01,
                           zero_crossing_threshold: int = 50) -> bool:
    """
    Advanced voice activity detection using multiple features.
    
    Args:
        audio_data: Raw audio bytes
        energy_threshold: Minimum energy level
        zero_crossing_threshold: Maximum zero crossings for voice
        
    Returns:
        True if voice activity detected
    """
    # Convert to numpy array
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    
    # Energy-based detection
    rms_energy = np.sqrt(np.mean(audio_array.astype(np.float32)**2))
    normalized_energy = rms_energy / 32768.0
    
    # Zero-crossing rate
    zero_crossings = np.sum(np.diff(np.signbit(audio_array)))
    
    # Spectral centroid (basic)
    fft = np.fft.fft(audio_array)
    magnitude = np.abs(fft)
    spectral_centroid = np.sum(magnitude * np.arange(len(magnitude))) / np.sum(magnitude)
    
    # Combine features for decision
    is_voice = (
        normalized_energy > energy_threshold and
        zero_crossings < zero_crossing_threshold and
        spectral_centroid > 1000  # Voice typically has higher spectral centroid
    )
    
    return is_voice
```

## Troubleshooting Voice Issues

### Common Problems and Solutions

#### No Audio Input Detected
```python
def diagnose_audio_input(self):
    """Diagnose audio input issues."""
    print("Diagnosing audio input...")
    
    # Check available input devices
    audio = pyaudio.PyAudio()
    input_devices = []
    
    for i in range(audio.get_device_count()):
        device_info = audio.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            input_devices.append({
                'index': i,
                'name': device_info['name'],
                'channels': device_info['maxInputChannels'],
                'sample_rate': device_info['defaultSampleRate']
            })
    
    if not input_devices:
        print("ERROR: No input devices found")
        return False
    
    print(f"Found {len(input_devices)} input devices:")
    for device in input_devices:
        print(f"  {device['index']}: {device['name']}")
    
    return True
```

#### Voice Recognition Not Working
```python
def test_voice_recognition(self):
    """Test voice recognition functionality."""
    print("Testing voice recognition...")
    
    try:
        # Test model loading
        test_model = vosk.Model(self.model_path)
        test_recognizer = vosk.KaldiRecognizer(test_model, 16000)
        print("✓ Model loaded successfully")
        
        # Test audio input
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=4096
        )
        print("✓ Audio stream opened")
        
        # Test recognition with sample audio
        print("Speak now for 3 seconds...")
        for _ in range(3 * 16000 // 4096):
            data = stream.read(4096)
            test_recognizer.AcceptWaveform(data)
        
        result = json.loads(test_recognizer.FinalResult())
        print(f"✓ Recognition result: {result.get('text', 'No speech detected')}")
        
        stream.close()
        audio.terminate()
        return True
        
    except Exception as e:
        print(f"✗ Voice recognition test failed: {e}")
        return False
```

This comprehensive voice processing documentation covers all aspects of speech recognition, text-to-speech synthesis, and audio handling in the MAC Assistant system.
