"""
MAC Assistant - Quick Test Script
Test the core functionality without voice components.
"""

from core.brain import MACBrain

def test_brain():
    """Test the brain functionality."""
    print("Testing MAC Brain...")
    
    brain = MACBrain()
    
    # Test various commands
    test_commands = [
        "hello",
        "what time is it",
        "system info",
        "network status",
        "unknown command"
    ]
    
    for command in test_commands:
        print(f"\nCommand: {command}")
        result = brain.process_command(command)
        print(f"Status: {result['status']}")
        print(f"Response: {result['message']}")
        if result.get('data'):
            print(f"Data: {result['data']}")
        print("-" * 50)

def test_api_models():
    """Test API request/response models."""
    print("Testing API models...")
    
    # This would require FastAPI to be available
    try:
        from sync.api import CommandRequest, CommandResponse
        
        # Create test request
        request = CommandRequest(text="hello", client_id="test")
        print(f"Request created: {request}")
        
        # Create test response
        response = CommandResponse(
            status="success",
            message="Hello there!",
            processing_time=0.1,
            server_timestamp=1234567890.0
        )
        print(f"Response created: {response}")
        
    except ImportError as e:
        print(f"API models test skipped: {e}")

def main():
    """Run all tests."""
    print("MAC Assistant - Quick Test")
    print("=" * 50)
    
    try:
        test_brain()
        test_api_models()
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
