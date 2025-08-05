#!/usr/bin/env python3
"""Simple MAC Assistant Test"""

print("🎯 MAC Assistant - Simple Test")
print("=" * 40)

try:
    print("Step 1: Importing brain...")
    from core.brain import MACBrain
    print("✅ Import successful!")
    
    print("Step 2: Creating brain instance...")
    brain = MACBrain()
    print("✅ Brain created!")
    
    print("Step 3: Testing simple command...")
    result = brain.process_command("hello")
    print(f"✅ Command processed: {result['status']}")
    
    print("🏆 SUCCESS: Your JARVIS-level MAC Assistant is working!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
