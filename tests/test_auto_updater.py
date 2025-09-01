import pytest
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock

# Add the project root to the Python path to import utils
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.auto_update import (
    get_current_version,
    compare_versions,
    get_script_directory,
    fetch_latest_version_with_retry,
    # We can't easily test the main() function without a complex setup
    # So we'll focus on the helper functions.
)


@pytest.fixture
def temp_test_dir():
    """Creates a temporary directory for test files and cleans up afterward."""
    test_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    os.chdir(test_dir)

    # Create a default version.py file
    version_file = "version.py"
    with open(version_file, "w") as f:
        f.write('__version__ = "1.0.0"\n')

    yield test_dir

    # Teardown
    os.chdir(original_cwd)
    shutil.rmtree(test_dir)


def test_get_script_directory_frozen(temp_test_dir):
    """Test get_script_directory when running as a frozen executable."""
    with patch("sys.frozen", True, create=True), patch(
        "sys.executable", "/path/to/executable"
    ):
        assert get_script_directory() == "/path/to"


def test_get_script_directory_script(temp_test_dir):
    """Test get_script_directory when running as a script."""
    script_path = os.path.join(temp_test_dir, "auto-update.py")
    with open(script_path, "w") as f:
        f.write("# dummy script")

    # Mock __file__ to return the path of the test script
    with patch("utils.auto_update.__file__", script_path):
        assert get_script_directory() == temp_test_dir


def test_get_current_version_exists(temp_test_dir):
    """Test get_current_version when version file exists."""
    script_dir = temp_test_dir
    version = get_current_version(script_dir)
    assert version == "1.0.0"


def test_get_current_version_not_exists(temp_test_dir):
    """Test get_current_version when version file does not exist."""
    os.remove("version.py")  # Remove the version file created by the fixture
    script_dir = temp_test_dir
    version = get_current_version(script_dir)
    assert version == "0.0.0"


@pytest.mark.parametrize(
    "current, latest, expected",
    [
        ("1.0.0", "1.0.0", True),
        ("1.1.0", "1.0.1", True),
        ("1.0.1", "1.0.1-beta", True),  # Assuming non-beta is newer
        ("1.0.0", "1.0.1", False),
        ("1.0.1-beta", "1.0.1", False),
        ("1.0.0.1", "1.0.0", True),
        ("1.0", "1.0.1", False),
        ("1.0.1", "1.0", True),
        ("invalid", "1.0.0", False),  # Invalid current
        ("1.0.0", "invalid", False),  # Invalid latest
    ],
)
def test_compare_versions(current, latest, expected):
    """Test compare_versions with various version strings."""
    assert compare_versions(current, latest) == expected


@patch("utils.auto_update.requests.get")
def test_fetch_latest_version_with_retry_success(mock_get, temp_test_dir):
    """Test fetch_latest_version_with_retry successful call."""
    mock_logger = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {"tag_name": "v1.0.1"}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    version, info = fetch_latest_version_with_retry(mock_logger)
    assert version == "1.0.1"
    assert info["tag_name"] == "v1.0.1"
    mock_get.assert_called_once()


@patch("utils.auto_update.requests.get")
@patch(
    "utils.auto_update.time.sleep", return_value=None
)  # Mock sleep to speed up tests
def test_fetch_latest_version_with_retry_failure(mock_sleep, mock_get, temp_test_dir):
    """Test fetch_latest_version_with_retry after max retries."""
    mock_logger = MagicMock()
    mock_get.side_effect = Exception("Network error")

    version, info = fetch_latest_version_with_retry(mock_logger)
    assert version is None
    assert info is None
    assert mock_get.call_count == 3  # MAX_RETRIES


# We can't easily test the main() function without a complex setup
# involving creating releases, downloading files, etc.
# For a real project, we might use more advanced mocking or integration tests.
# This would be a good candidate for a pytest.mark.integration test.
