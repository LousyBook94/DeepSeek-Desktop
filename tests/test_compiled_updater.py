#!/usr/bin/env python3
"""
Tests for the compiled auto-updater executable.
These tests require the executable to be built first.
"""

import os
import sys
import subprocess
import pytest

# Add the project root directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_executable_exists():
    """Test that the compiled executable exists"""
    exe_path = os.path.join(os.path.dirname(__file__), "..", "dist", "auto-updater.exe")
    # Skip this test if the executable doesn't exist (it may not be built yet)
    if not os.path.exists(exe_path):
        pytest.skip("Executable not found - may not be built yet")
    return exe_path


def test_executable_runs():
    """Test that the executable runs and shows help"""
    exe_path = os.path.join(os.path.dirname(__file__), "..", "dist", "auto-updater.exe")

    # Skip this test if the executable doesn't exist (it may not be built yet)
    if not os.path.exists(exe_path):
        pytest.skip("Executable not found - may not be built yet")

    # Run the executable with --help flag
    result = subprocess.run(
        [exe_path, "--help"], capture_output=True, text=True, timeout=10
    )

    # Check that it ran successfully
    assert (
        result.returncode == 0
    ), f"Executable failed with return code {result.returncode}"

    # Check that help text contains expected elements
    assert "--auto" in result.stdout, "Help text should contain --auto flag"
    assert "--debug" in result.stdout, "Help text should contain --debug flag"
    assert (
        "DeepSeek Desktop Auto-Updater" in result.stdout
    ), "Help text should contain description"
