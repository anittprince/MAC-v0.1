"""
MAC Assistant - Demo Script
Demonstrates all key features of the MAC Assistant.
"""

import time
import threading
from core.brain import MACBrain

def demo_brain():
    """Demonstrate the brain functionality."""
    print("\n" + "="*60)
    print("MAC ASSISTANT - BRAIN DEMO")
    print("="*60)
    
    brain = MACBrain()
    
    print(f"Platform: {brain.get_platform_info()['platform']}")
    print(f"Available command types: {list(brain.get_available_commands().keys())}")
    
    print("\nTesting various commands:")
    print("-" * 40)
    
    demo_commands = [
        ("Greeting", "hello there"),
        ("Time Query", "what time is it"),
        ("System Information", "system info"),
        ("Network Status", "network status"),
        ("Application Control", "list running applications"),
        ("Unknown Command", "play music loudly"),
    ]
    
    for category, command in demo_commands:
        print(f"\n[{category}]")
        print(f"Command: '{command}'")
        
        result = brain.process_command(command)
        
        print(f"Status: {result['status']}")
        print(f"Response: {result['message']}")
        
        if result.get('data'):
            print(f"Additional data available: {type(result['data'])}")
        
        time.sleep(1)  # Pause between commands

def demo_api_server():
    """Demonstrate the API server functionality."""
    print("\n" + "="*60)
    print("MAC ASSISTANT - API SERVER DEMO")
    print("="*60)
    
    try:
        from sync.api import app
        print("✓ FastAPI server module loaded successfully")
        print("✓ Server endpoints available:")
        print("  - GET  /health")
        print("  - POST /command")
        print("  - GET  /info")
        print("  - GET  /commands")
        
        print("\nTo start the server, run:")
        print("python main.py --mode server")
        print("Server will be available at: http://localhost:8000")
        
    except ImportError as e:
        print(f"✗ API server dependencies missing: {e}")
        print("Install with: pip install fastapi uvicorn")

def demo_voice_components():
    """Demonstrate voice components (if available)."""
    print("\n" + "="*60)
    print("MAC ASSISTANT - VOICE COMPONENTS DEMO")
    print("="*60)
    
    # Test voice output
    try:
        from core.voice_output import VoiceOutput
        voice_out = VoiceOutput()
        print("✓ Voice output (TTS) initialized")
        
        # Test speaking (non-blocking)
        print("Testing text-to-speech...")
        voice_out.speak("Hello! This is MAC Assistant testing voice output.")
        time.sleep(3)
        
    except ImportError as e:
        print(f"✗ Voice output not available: {e}")
        print("Install with: pip install pyttsx3")
    
    # Test voice input
    try:
        from core.voice_input import VoiceInput
        print("✓ Voice input module loaded")
        print("Note: Voice input requires microphone and Vosk model")
        
    except ImportError as e:
        print(f"✗ Voice input not available: {e}")
        print("Install with: pip install vosk speechrecognition pyaudio")

def demo_android_integration():
    """Demonstrate Android integration concepts."""
    print("\n" + "="*60)
    print("MAC ASSISTANT - ANDROID INTEGRATION DEMO")
    print("="*60)
    
    print("Android App Features:")
    print("✓ Voice input using Android SpeechRecognizer")
    print("✓ Text-to-speech using Android TTS")
    print("✓ HTTP communication with Python server")
    print("✓ Material Design 3 UI")
    print("✓ Permission handling for microphone access")
    
    print("\nServer Communication:")
    print("• Android app sends voice commands as text to Python server")
    print("• Server processes commands and returns responses")
    print("• Android app speaks the response back to user")
    
    print("\nSetup Instructions:")
    print("1. Run Python server: python main.py --mode server")
    print("2. Open android/MACAssistant in Android Studio")
    print("3. Build and install on Android device")
    print("4. Enter server IP address in the app")
    print("5. Use voice commands through the app")

def main():
    """Run the complete demo."""
    print("MAC ASSISTANT - COMPLETE DEMONSTRATION")
    print("Cross-Platform Voice Assistant")
    print("Version 1.0.0")
    
    try:
        demo_brain()
        demo_api_server()
        demo_voice_components()
        demo_android_integration()
        
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)
        print("MAC Assistant is ready to use!")
        print("\nNext steps:")
        print("1. Run 'python main.py --mode text' for text-based interaction")
        print("2. Run 'python main.py --mode voice' for voice interaction")
        print("3. Run 'python main.py --mode server' for Android app backend")
        print("4. Build and install the Android app for mobile voice control")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nDemo error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
