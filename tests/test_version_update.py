#!/usr/bin/env python3
"""
Test script to reproduce the version.txt update issue.
"""

import os
import tempfile
import shutil


def test_version_update_issue():
    """Test to reproduce the version.txt update issue"""

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Testing in directory: {temp_dir}")

        # Create initial version.txt with version 0.1.0
        version_file = os.path.join(temp_dir, "version.txt")
        with open(version_file, "w") as f:
            f.write("0.1.0")

        print(f"Initial version in file: {open(version_file).read().strip()}")

        # Simulate what happens during update:
        # 1. The update archive contains version.txt with version 0.1.1
        # 2. During extraction, this file overwrites the existing one

        # Create a "new" version.txt as if it came from update archive
        new_version_file = os.path.join(temp_dir, "new_version.txt")
        with open(new_version_file, "w") as f:
            f.write("0.1.1")

        print("Simulating extraction of update archive...")

        # Move the new version.txt to overwrite the old one
        shutil.move(new_version_file, version_file)

        print(f"Version after extraction: {open(version_file).read().strip()}")

        # Now simulate the post-update version writing
        # This is what should happen but may not be working
        latest_version = "0.1.1"
        try:
            with open(version_file, "w", encoding="utf-8") as f:
                f.write(latest_version)
            print(
                f"Version after post-update writing: {open(version_file).read().strip()}"
            )
        except Exception as e:
            print(f"Error writing version: {e}")

        print("Test completed.")


if __name__ == "__main__":
    test_version_update_issue()
