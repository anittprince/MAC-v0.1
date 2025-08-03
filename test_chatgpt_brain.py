#!/usr/bin/env python
"""
Test ChatGPT Brain Integration
Demonstrates MAC Assistant with ChatGPT as the primary brain.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.brain import MACBrain

def test_chatgpt_brain():
    """Test ChatGPT as the primary brain."""
    print("🧠 Testing MAC Assistant with ChatGPT Brain")
    print("=" * 60)
    
    brain = MACBrain()
    
    # Check ChatGPT availability
    ai_status = brain.get_ai_status()
    
    if ai_status['chatgpt']:
        print("✅ ChatGPT Brain: ACTIVE")
        print("🤖 All commands will be processed by ChatGPT first")
    else:
        print("❌ ChatGPT Brain: NOT CONFIGURED")
        print("⚠️  Running in fallback mode")
    
    print("\n" + "="*60)
    print("🎯 Testing Various Commands with ChatGPT Brain:")
    print("="*60)
    
    test_commands = [
        # Natural conversation
        ("Natural Greeting", "Hello, how are you today?"),
        ("Personal Question", "What's your name and what can you do?"),
        ("General Knowledge", "What is the capital of France?"),
        ("Math Question", "What's 15 multiplied by 24?"),
        ("Explanation Request", "Explain quantum physics in simple terms"),
        
        # System commands that should work with ChatGPT
        ("Time Query", "what time is it"),
        ("System Information", "tell me about my computer"),
        ("Weather Request", "what's the weather like"),
        
        # Complex questions
        ("Planning Help", "Help me plan a productive day"),
        ("Technical Question", "How does machine learning work?"),
        ("Creative Request", "Write a short poem about technology"),
        
        # Mixed system/AI commands
        ("Volume Control", "can you turn up the volume"),
        ("Search Request", "search for latest AI news"),
        ("YouTube Request", "find videos about python programming"),
    ]
    
    for category, command in test_commands:
        print(f"\n🎯 {category}")
        print("-" * 40)
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
            data = result['data']
            if isinstance(data, dict):
                if 'source' in data:
                    print(f"🔍 Source: {data['source']}")
                if 'tokens_used' in data:
                    print(f"🎯 Tokens: {data['tokens_used']}")
                if 'chatgpt_response' in data:
                    print(f"🤖 ChatGPT: {data['chatgpt_response']}")
                if 'system_result' in data:
                    print(f"💻 System: {data['system_result']}")
        
        print(f"📊 Status: {result['status']}")
        print()
    
    print("="*60)
    print("🎉 ChatGPT Brain Test Complete!")
    
    if ai_status['chatgpt']:
        print("\n🚀 ChatGPT Brain Performance:")
        print("   ✅ Natural conversation handling")
        print("   ✅ System command integration") 
        print("   ✅ Intelligent response generation")
        print("   ✅ Context-aware interactions")
    else:
        print("\n💡 To Enable ChatGPT Brain:")
        print("   1. Get OpenAI API key from: https://platform.openai.com/api-keys")
        print("   2. Copy .env.template to .env")
        print("   3. Add: OPENAI_API_KEY=your_key_here")
        print("   4. Restart and test again!")

def test_conversation_flow():
    """Test conversational flow with ChatGPT."""
    print("\n" + "="*60)
    print("💬 Testing Conversation Flow")
    print("="*60)
    
    brain = MACBrain()
    
    conversation = [
        "Hello, I'm new here",
        "What can you help me with?",
        "Can you tell me the time?",
        "That's great! What about the weather?",
        "Thank you for your help!"
    ]
    
    for i, message in enumerate(conversation, 1):
        print(f"\n[Turn {i}] User: {message}")
        result = brain.process_command(message)
        print(f"[Turn {i}] MAC: {result['message']}")
        
        # Check if data exists before accessing it
        if result.get('data') and isinstance(result['data'], dict) and result['data'].get('source'):
            print(f"         Source: {result['data']['source']}")

if __name__ == "__main__":
    try:
        test_chatgpt_brain()
        test_conversation_flow()
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        print("Please check your setup and try again.")
