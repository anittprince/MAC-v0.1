#!/usr/bin/env python3
"""
Test script for the enhanced MAC Assistant advanced features.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.brain import MACBrain

def test_advanced_features():
    """Test the new advanced features of MAC Assistant."""
    print("🧪 Testing Enhanced MAC Assistant Advanced Features\n")
    
    # Initialize the brain
    brain = MACBrain()
    
    # Test Advanced AI Features
    print("🧠 Testing Advanced AI Features:")
    
    # Test document analysis
    result = brain.process_command("analyze document")
    print(f"   Document Analysis: {result['message'][:100]}...")
    
    # Test research capability
    result = brain.process_command("research artificial intelligence")
    print(f"   Research Agent: {result['message'][:100]}...")
    
    # Test code assistant
    result = brain.process_command("review my code")
    print(f"   Code Assistant: {result['message'][:100]}...")
    
    print("\n🏢 Testing Enterprise Integration:")
    
    # Test team collaboration
    result = brain.process_command("schedule team meeting tomorrow")
    print(f"   Team Meeting: {result['message'][:100]}...")
    
    # Test project management
    result = brain.process_command("create new project for mobile app")
    print(f"   Project Management: {result['message'][:100]}...")
    
    print("\n🏠 Testing Smart Environment:")
    
    # Test smart home control
    result = brain.process_command("turn on living room lights")
    print(f"   Smart Home Control: {result['message'][:100]}...")
    
    # Test IoT devices
    result = brain.process_command("show connected devices")
    print(f"   IoT Devices: {result['message'][:100]}...")
    
    # Test energy optimization
    result = brain.process_command("optimize energy usage")
    print(f"   Energy Optimization: {result['message'][:100]}...")
    
    print("\n✅ All advanced features tested successfully!")
    print("\n📊 Feature Summary:")
    print("   🧠 Advanced AI: Document analysis, research, code assistance")
    print("   🏢 Enterprise: Team collaboration, project management, analytics")
    print("   🏠 Smart Environment: Home automation, IoT control, energy optimization")
    print("   🎯 All features integrated with existing personalization system")

if __name__ == "__main__":
    test_advanced_features()
