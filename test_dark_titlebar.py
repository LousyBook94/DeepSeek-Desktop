#!/usr/bin/env python3
"""
Test script for dark titlebar functionality
"""

import sys
import platform
from main import is_dark_mode_enabled, should_use_dark_titlebar, titlebar_preference

def test_dark_mode_detection():
    """Test the dark mode detection functionality"""
    print("=== Dark Titlebar Test ===")
    print(f"Platform: {platform.system()}")
    print(f"Python version: {sys.version}")
    
    if platform.system() == "Windows":
        print("\n--- Windows Dark Mode Detection ---")
        try:
            dark_mode = is_dark_mode_enabled()
            print(f"System dark mode enabled: {dark_mode}")
        except Exception as e:
            print(f"Error detecting dark mode: {e}")
    else:
        print(f"Dark mode detection is Windows-only (current: {platform.system()})")
    
    print("\n--- Titlebar Preference Testing ---")
    
    # Test auto mode
    import main
    main.titlebar_preference = 'auto'
    print(f"Auto mode - should use dark titlebar: {should_use_dark_titlebar()}")
    
    # Test forced dark mode
    main.titlebar_preference = 'dark'
    print(f"Forced dark mode - should use dark titlebar: {should_use_dark_titlebar()}")
    
    # Test forced light mode
    main.titlebar_preference = 'light'
    print(f"Forced light mode - should use dark titlebar: {should_use_dark_titlebar()}")
    
    print("\n--- Test Complete ---")

if __name__ == "__main__":
    test_dark_mode_detection()
