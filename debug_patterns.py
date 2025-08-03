#!/usr/bin/env python
"""
Debug pattern matching for YouTube command
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.brain import MACBrain
import re

def debug_patterns():
    """Debug pattern matching."""
    brain = MACBrain()
    test_text = "youtube machine learning tutorials"
    
    print(f"Testing: '{test_text}'")
    print("=" * 50)
    
    # Check each pattern type
    for command_type, patterns in brain.command_patterns.items():
        print(f"\n{command_type.upper()} patterns:")
        for pattern in patterns:
            if re.search(pattern, test_text, re.IGNORECASE):
                print(f"  ✓ MATCH: {pattern}")
            else:
                print(f"  ✗ No match: {pattern}")
    
    # Test the identification
    print(f"\nIdentified as: {brain._identify_command_type(test_text)}")
    
    # Test YouTube extraction
    if 'youtube' in test_text.lower():
        query = brain._extract_youtube_query(test_text)
        print(f"YouTube query extracted: '{query}'")

if __name__ == "__main__":
    debug_patterns()
