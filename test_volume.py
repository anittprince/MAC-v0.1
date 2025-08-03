"""
MAC Assistant - Volume Control Test
Tests the Windows volume control functionality.
"""

from core.brain import MACBrain

def test_volume_control():
    """Test volume control commands."""
    print("MAC Assistant - Volume Control Test")
    print("=" * 50)
    
    brain = MACBrain()
    
    volume_commands = [
        ("Volume Status", "what is the volume"),
        ("Volume Up", "volume up"),
        ("Volume Down", "volume down"), 
        ("Increase Volume", "increase volume"),
        ("Decrease Volume", "decrease volume"),
        ("Sound Up", "sound up"),
        ("Mute", "mute"),
        ("Unmute", "unmute"),
        ("Volume Status Again", "current volume")
    ]
    
    for test_name, command in volume_commands:
        print(f"\n[{test_name}]")
        print(f"Command: '{command}'")
        
        result = brain.process_command(command)
        print(f"Status: {result['status']}")
        print(f"Response: {result['message']}")
        
        if result.get('data'):
            print(f"Data: {result['data']}")
        
        print("-" * 30)

def main():
    try:
        test_volume_control()
        print("\nVolume control test completed successfully!")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
