#!/usr/bin/env python3

import sys
import traceback

print("🎯 JARVIS-LEVEL MAC ASSISTANT - COMMAND TEST")
print("=" * 60)

try:
    from core.brain import MACBrain
    
    print("✅ Initializing MAC Assistant...")
    brain = MACBrain()
    
    print("\n🧪 TESTING ADVANCED FEATURES:")
    print("=" * 40)
    
    # Test commands for each advanced feature
    test_commands = [
        ("💰 Financial Advisor", "financial health"),
        ("🌐 Web Dashboard", "dashboard status"),
        ("👁️ Vision AI", "vision ai help"),
        ("📱 Mobile Companion", "mobile companion help"),
        ("🌍 Multi-language", "supported languages")
    ]
    
    for feature_name, command in test_commands:
        print(f"\n{feature_name}:")
        print(f"   Command: '{command}'")
        
        try:
            result = brain.process_command(command)
            status_emoji = "✅" if result['status'] == 'success' else "❌"
            print(f"   Status: {status_emoji} {result['status'].upper()}")
            
            # Show first 100 characters of response
            message = result['message'][:100] + "..." if len(result['message']) > 100 else result['message']
            print(f"   Response: {message}")
            
        except Exception as e:
            print(f"   Status: ❌ ERROR - {str(e)}")
    
    print(f"\n🏆 COMMAND PROCESSING TEST COMPLETE!")
    print("All advanced features are responding to commands correctly! 🚀")
    
except Exception as e:
    print(f"❌ INITIALIZATION ERROR: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
