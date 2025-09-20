#!/usr/bin/env python3
"""
Simple test script to verify the AutoUpdater class functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from auto_update import AutoUpdater

def test_callback(event_type, data):
    """Simple test callback"""
    print(f"Callback: {event_type} - {data}")

def test_updater():
    """Test the AutoUpdater class"""
    print("Testing AutoUpdater class...")
    
    # Create AutoUpdater instance
    updater = AutoUpdater(callback=test_callback)
    
    # Test getting current version
    current_version = updater.get_current_version()
    print(f"Current version: {current_version}")
    
    # Test version comparison
    test_cases = [
        ("1.0.0", "1.0.1"),  # Should need update (current < latest)
        ("1.0.1", "1.0.0"),  # Should not need update (current > latest)
        ("1.0.0", "1.0.0"),  # Same version (should not need update)
        ("1.0.0", "1.0.0-beta"),  # Should not need update (current is stable, latest is beta)
        ("1.0.0-beta", "1.0.0"),  # Should need update (current is beta, latest is stable)
    ]
    
    print("\nTesting version comparison:")
    for current, latest in test_cases:
        needs_update = not updater.compare_versions(current, latest)  # Invert the result
        print(f"  {current} vs {latest}: {'Needs update' if needs_update else 'No update needed'}")
    
    print("\nAutoUpdater test completed successfully!")

if __name__ == "__main__":
    test_updater()