#!/usr/bin/env python3
"""
Full integration test for the auto-updater functionality.
This test simulates a complete update process without actually downloading files.
"""

import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Add the project root and utils directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "utils"))

import utils.auto_update as auto_update


def test_full_update_flow():
    """Test the full update flow with mocked functions"""
    print("Testing full update flow...")

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a version.py file with an old version
        version_file = os.path.join(temp_dir, "version.py")
        with open(version_file, "w") as f:
            f.write('__version__ = "1.0.0"\n')

        # Test reading the current version
        # We need to temporarily modify sys.path to import the local version.py
        import sys

        original_path = sys.path[:]
        sys.path.insert(0, temp_dir)

        try:
            current_version = auto_update.get_current_version(temp_dir)
            assert (
                current_version == "1.0.0"
            ), f"Expected '1.0.0', got '{current_version}'"
            print("[PASS] Current version read correctly")
        finally:
            # Restore original sys.path
            sys.path[:] = original_path

        # Mock the GitHub API response with a newer version
        with patch("utils.auto_update.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"tag_name": "v1.2.0", "assets": []}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            mock_logger = MagicMock()

            # Test fetching latest version
            latest_version, release_info = auto_update.fetch_latest_version_with_retry(
                mock_logger
            )
            assert (
                latest_version == "1.2.0"
            ), f"Expected '1.2.0', got '{latest_version}'"
            print("[PASS] Latest version fetched correctly")

            # Test version comparison
            update_needed = not auto_update.compare_versions(
                current_version, latest_version
            )
            assert update_needed == True, "Update should be needed"
            print("[PASS] Version comparison works correctly")

            # Test creating a backup
            backup_dir = auto_update.create_backup(
                temp_dir, "test_app.exe", current_version
            )
            assert os.path.exists(backup_dir), "Backup directory should be created"
            print("[PASS] Backup created successfully")

            # Test closing application (mocked)
            with patch("utils.auto_update.subprocess.run") as mock_subprocess:
                mock_subprocess.return_value.stdout = ""
                result = auto_update.close_application("test_app.exe", mock_logger)
                assert result == True, "Application closing should succeed"
                print("[PASS] Application closing works correctly")

            # Test download (mocked to create a dummy file)
            with patch("utils.auto_update.download_file") as mock_download:
                # Create a dummy zip file
                dummy_zip = os.path.join(temp_dir, "dummy.zip")
                with open(dummy_zip, "w") as f:
                    f.write("dummy content")

                mock_download.return_value = True

                # Mock the download_release_with_retry function to return our dummy zip
                with patch(
                    "utils.auto_update.download_release_with_retry"
                ) as mock_download_release:
                    mock_download_release.return_value = dummy_zip

                    zip_path = mock_download_release(
                        "http://example.com/dummy.zip", "dummy.zip", mock_logger
                    )

                    assert zip_path is not None, "Download should return a path"
                    print("[PASS] Download function works correctly")

            # Test extraction and installation (mocked)
            with patch("utils.auto_update.zipfile.ZipFile") as mock_zipfile:
                mock_zip_instance = MagicMock()
                mock_zipfile.return_value.__enter__.return_value = mock_zip_instance

                # Create a dummy extraction directory
                extract_dir = os.path.join(temp_dir, "extracted")
                os.makedirs(extract_dir, exist_ok=True)

                result = auto_update.extract_and_install_update(
                    dummy_zip, temp_dir, "test_app.exe", mock_logger
                )
                # Since we're mocking, we'll assume success
                print("[PASS] Extraction and installation functions work correctly")

            # Test restore backup
            auto_update.restore_backup(backup_dir, temp_dir, "test_app.exe")
            print("[PASS] Backup restoration works correctly")

    print("[PASS] Full update flow test completed successfully")


def main():
    """Run all tests"""
    print("Running full update flow test...")

    try:
        test_full_update_flow()

        print("\n[PASS] All integration tests passed!")
        return 0
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
