#!/usr/bin/env python
"""
Test script for MAC Assistant AI integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.brain import MACBrain

def test_commands():
    """Test various commands with the brain."""
    brain = MACBrain()
    
    test_commands = [
        "whats the time",
        "what is 2 plus 2",
        "search for artificial intelligence",
        "youtube machine learning tutorials",
        "tell me about python programming",
        "hello",
        "weather forecast"
    ]
    
    print("Testing MAC Assistant AI Integration")
    print("=" * 50)
    
    for command in test_commands:
        print(f"\nUser: {command}")
        result = brain.process_command(command)
        print(f"MAC: {result['message']}")
        
        if result.get('data'):
            print(f"Data: {result['data']}")
        
        print(f"Status: {result['status']}")

if __name__ == "__main__":
    test_commands()
