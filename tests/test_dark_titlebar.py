#!/usr/bin/env python3
"""
Test script for dark titlebar functionality
"""

import platform
from main import is_dark_mode_enabled, should_use_dark_titlebar


def test_dark_mode_detection():
    """Basic assertions for titlebar preference logic; dark mode detection only on Windows."""
    import main

    # preference: auto -> echoes system value (don’t assert specific value cross-platform)
    main.titlebar_preference = "auto"
    _ = should_use_dark_titlebar()

    # preference: dark
    main.titlebar_preference = "dark"
    assert should_use_dark_titlebar() is True

    # preference: light
    main.titlebar_preference = "light"
    assert should_use_dark_titlebar() is False

    # Windows-only: ensure detector does not crash
    if platform.system() == "Windows":
        try:
            _ = is_dark_mode_enabled()
        except Exception as e:
            raise AssertionError(f"is_dark_mode_enabled raised unexpectedly: {e}")


if __name__ == "__main__":
    test_dark_mode_detection()
