#!/usr/bin/env python
"""
Test Text-to-Speech in Text Mode
Demonstrates the enhanced text mode with TTS functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import MACAssistant

def test_text_mode_with_tts():
    """Test text mode with TTS functionality."""
    print("🔊 Testing MAC Assistant Text Mode with Text-to-Speech")
    print("=" * 60)
    
    # Initialize assistant
    assistant = MACAssistant()
    
    # Test commands
    test_commands = [
        "hello",
        "what time is it", 
        "search for artificial intelligence",
        "tell me about machine learning"
    ]
    
    print("\n🎯 Testing Text Mode Commands with TTS:")
    print("-" * 40)
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n[{i}] Testing: '{command}'")
        print("=" * 30)
        
        # Process command
        result = assistant.process_single_command(command)
        
        # Print result
        print(f"Response: {result['message']}")
        print(f"Status: {result['status']}")
        
        if result.get('data'):
            print(f"Data: {result['data']}")
        
        # Speak the response
        print("🔊 Speaking response...")
        assistant.voice_output.speak(result['message'])
        
        # Small delay between commands
        import time
        time.sleep(1)
    
    print("\n✅ Text Mode TTS Test Complete!")
    print("\n💡 Usage Tips:")
    print("  • Run: python main.py --mode text")
    print("  • Type 'mute' to disable TTS")
    print("  • Type 'unmute' to enable TTS") 
    print("  • Run: python main.py --mode text --no-speech (to start without TTS)")

if __name__ == "__main__":
    try:
        test_text_mode_with_tts()
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        print("Please check your setup and try again.")
