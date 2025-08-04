#!/usr/bin/env python3

import sys
import traceback

print("🔍 Testing MAC Assistant Import...")
print(f"Python version: {sys.version}")
print(f"Current working directory: {sys.path[0]}")

try:
    print("1. Testing basic imports...")
    import os
    import platform
    print("✅ Basic imports successful")
    
    print("2. Testing core module import...")
    import core
    print("✅ Core module imported")
    
    print("3. Testing financial advisor import...")
    from core.financial_advisor import FinancialAdvisorAgent
    print("✅ Financial advisor imported")
    
    print("4. Testing web dashboard import...")
    from core.web_dashboard import WebDashboardManager
    print("✅ Web dashboard imported")
    
    print("5. Testing brain import...")
    from core.brain import MACBrain
    print("✅ Brain imported successfully!")
    
    print("6. Creating brain instance...")
    brain = MACBrain()
    print("✅ Brain instance created!")
    
    print("\n🎯 JARVIS-LEVEL MAC ASSISTANT TEST COMPLETE!")
    print("All modules loaded successfully!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
