#!/usr/bin/env python3
"""
Test script for the auto-updater functionality.
This script will test the main functions of the auto-updater without actually performing an update.
"""

import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Add the project root and utils directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "utils"))

import utils.auto_update as auto_update


def test_get_current_version():
    """Test reading the current version from version.py"""
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a version.py file
        version_file = os.path.join(temp_dir, "version.py")
        with open(version_file, "w") as f:
            f.write('__version__ = "1.2.3"\n')

        # Test reading the version
        version = auto_update.get_current_version(temp_dir)
        assert version == "1.2.3", f"Expected '1.2.3', got '{version}'"
        print("[PASS] get_current_version test passed")


def test_compare_versions():
    """Test version comparison logic"""
    # Test cases: (current, latest, expected_result)
    test_cases = [
        ("1.0.0", "1.0.0", True),  # Same versions
        ("1.0.1", "1.0.0", True),  # Current is newer
        ("1.0.0", "1.0.1", False),  # Latest is newer
        ("1.0.0.1", "1.0.0", True),  # Current has more parts
        ("1.0", "1.0.1", False),  # Latest has more parts
        ("1.0.1-beta", "1.0.1", False),  # Prerelease vs stable
        ("1.0.1", "1.0.1-beta", True),  # Stable vs prerelease
    ]

    for current, latest, expected in test_cases:
        result = auto_update.compare_versions(current, latest)
        assert (
            result == expected
        ), f"compare_versions('{current}', '{latest}') failed. Expected {expected}, got {result}"

    print("[PASS] compare_versions test passed")


def test_fetch_latest_version_with_retry():
    """Test fetching latest version with retry logic"""
    # This is a simplified test that mocks the requests
    with patch("utils.auto_update.requests.get") as mock_get:
        # Mock a successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {"tag_name": "v1.2.4"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Create a mock logger
        mock_logger = MagicMock()

        # Test the function
        version, info = auto_update.fetch_latest_version_with_retry(mock_logger)
        assert version == "1.2.4", f"Expected '1.2.4', got '{version}'"
        assert info["tag_name"] == "v1.2.4", "Info object doesn't match expected"

    print("[PASS] fetch_latest_version_with_retry test passed")


def test_get_script_directory():
    """Test getting the script directory"""
    script_dir = auto_update.get_script_directory()
    assert os.path.isdir(script_dir), f"Script directory '{script_dir}' does not exist"
    print("[PASS] get_script_directory test passed")


def main():
    """Run all tests"""
    print("Running auto-updater tests...")

    try:
        test_get_script_directory()
        test_get_current_version()
        test_compare_versions()
        test_fetch_latest_version_with_retry()

        print("\n[PASS] All tests passed!")
        return 0
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
