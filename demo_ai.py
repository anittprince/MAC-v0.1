#!/usr/bin/env python
"""
Quick AI Demo - Test MAC Assistant AI features
This script demonstrates the AI integration without requiring full setup.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.brain import MACBrain

def demo_ai_features():
    """Demonstrate AI features with various commands."""
    print("🤖 MAC Assistant AI Integration Demo")
    print("=" * 50)
    
    brain = MACBrain()
    
    # Show AI services status
    ai_status = brain.get_ai_status()
    print("\n🔧 AI Services Status:")
    status_icons = {True: "✅", False: "❌"}
    for service, available in ai_status.items():
        print(f"  {status_icons[available]} {service.replace('_', ' ').title()}: {'Available' if available else 'Not configured'}")
    
    print("\n" + "="*50)
    print("📝 Testing Various Commands:")
    print("="*50)
    
    test_commands = [
        # Basic commands that should work without API keys
        ("Basic Time", "what time is it"),
        ("Greeting", "hello MAC"),
        ("System Info", "system info"),
        
        # AI-powered commands (may use fallback if no API keys)
        ("Search Query", "search for Python programming"),
        ("General Question", "what is artificial intelligence"),
        ("YouTube Search", "youtube machine learning tutorials"),
        ("Math Question", "what is 2 plus 2"),
        ("Definition", "define machine learning"),
        ("Weather Request", "weather forecast"),
        
        # Test fallback behavior
        ("Unknown Command", "play some music"),
        ("Random Question", "tell me a joke"),
    ]
    
    for category, command in test_commands:
        print(f"\n🎯 {category}")
        print(f"User: '{command}'")
        
        result = brain.process_command(command)
        
        # Format response based on status
        status_emoji = {
            'success': '✅',
            'error': '❌', 
            'unknown': '❓',
            'ai_fallback': '🤖'
        }
        
        emoji = status_emoji.get(result['status'], '⚪')
        print(f"{emoji} MAC: {result['message']}")
        
        if result.get('data'):
            print(f"📊 Data: {result['data']}")
        
        print(f"📋 Status: {result['status']}")
    
    print("\n" + "="*50)
    print("🎉 Demo Complete!")
    print("\n💡 To unlock full AI capabilities:")
    print("   1. Copy .env.template to .env")
    print("   2. Add your OpenAI API key")
    print("   3. Restart MAC Assistant")
    print("\n📚 See docs/AI_INTEGRATION.md for detailed setup guide")

if __name__ == "__main__":
    try:
        demo_ai_features()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("Please check your setup and try again.")
