#!/usr/bin/env python3
"""
Test script to simulate update without file locking issues.
"""

import os
import tempfile
import shutil


def test_update_logic():
    """Test the update logic without file locking issues"""

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Testing in directory: {temp_dir}")

        # Create initial files
        script_dir = os.path.join(temp_dir, "app")
        os.makedirs(script_dir, exist_ok=True)

        # Create initial version.txt with version 0.1.0
        version_file = os.path.join(script_dir, "version.txt")
        with open(version_file, "w") as f:
            f.write("0.1.0")

        print(f"Initial version in file: {open(version_file).read().strip()}")

        # Create a "new" version.txt as if it came from update archive with version 0.1.61
        new_version_file = os.path.join(temp_dir, "new_version.txt")
        with open(new_version_file, "w") as f:
            f.write("0.1.61")

        print("Simulating extraction of update archive...")

        # Move the new version.txt to overwrite the old one (simulating archive extraction)
        shutil.copy2(new_version_file, version_file)

        print(f"Version after extraction: {open(version_file).read().strip()}")

        # Now simulate the post-update version writing logic
        latest_version = "0.1.61"
        current_version = "0.1.0"

        # Read the version that was installed
        installed_version = None
        if os.path.exists(version_file):
            with open(version_file, "r", encoding="utf-8") as f:
                installed_version = f.read().strip()

        print(f"Installed version from file: {installed_version}")

        # If the installed version is different from what we expect, update it
        if installed_version != latest_version:
            with open(version_file, "w", encoding="utf-8") as f:
                f.write(latest_version)
            print(f"Updated version file to: {latest_version}")
        else:
            print(f"Version file already contains correct version: {latest_version}")

        print(f"Final version in file: {open(version_file).read().strip()}")
        print("Test completed.")


if __name__ == "__main__":
    test_update_logic()
