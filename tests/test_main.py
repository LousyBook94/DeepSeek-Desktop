import sys
import pytest
import platform
from unittest.mock import patch, MagicMock, ANY

# Add project root and src to path for imports
sys.path.insert(0, sys.path[0] + "/..")
from src import windows_helpers, api
import main

# --- Fixtures for Test Isolation ---

@pytest.fixture(autouse=True)
def isolated_globals(monkeypatch):
    """Fixture to isolate and reset module-level global variables for all tests."""
    original_titlebar_preference = main.titlebar_preference
    original_verbose_logs = main.VERBOSE_LOGS
    monkeypatch.setattr(main, 'titlebar_preference', 'auto')
    monkeypatch.setattr(main, 'VERBOSE_LOGS', False)
    yield
    main.titlebar_preference = original_titlebar_preference
    main.VERBOSE_LOGS = original_verbose_logs

@pytest.fixture
def mock_sys_argv(monkeypatch):
    """Fixture to mock and restore sys.argv."""
    original_argv = list(sys.argv)
    monkeypatch.setattr(sys, 'argv', ['main.py'])
    yield
    sys.argv = original_argv

@pytest.fixture
def mock_winreg(monkeypatch):
    """Fixture to create a complete mock for the winreg module."""
    mock = MagicMock()
    # Define constants expected by the code
    mock.HKEY_CURRENT_USER = "HKEY_CURRENT_USER"
    # Mock the context manager behavior of OpenKey
    key_handle = MagicMock()
    mock.OpenKey.return_value = key_handle
    # Mock QueryValueEx to return a default value
    mock.QueryValueEx.return_value = (1, None) # Default to light mode
    # Monkeypatch the module in the place where it's imported
    monkeypatch.setattr(windows_helpers, 'winreg', mock)
    return mock

@pytest.fixture
def mock_ctypes(monkeypatch):
    """Fixture to create a mock for the ctypes module."""
    mock = MagicMock()
    mock.windll.dwmapi.DwmSetWindowAttribute.return_value = 0
    monkeypatch.setattr(windows_helpers, 'ctypes', mock)
    return mock

# --- Tests for should_use_dark_titlebar (in windows_helpers) ---

def test_should_use_dark_titlebar_dark_preference():
    assert windows_helpers.should_use_dark_titlebar('dark') is True

def test_should_use_dark_titlebar_light_preference():
    assert windows_helpers.should_use_dark_titlebar('light') is False

def test_should_use_dark_titlebar_auto_with_dark_mode(monkeypatch):
    monkeypatch.setattr(windows_helpers, 'is_dark_mode_enabled', lambda: True)
    assert windows_helpers.should_use_dark_titlebar('auto') is True

# --- Tests for is_dark_mode_enabled (in windows_helpers) ---

def test_is_dark_mode_enabled_non_windows(monkeypatch):
    monkeypatch.setattr(platform, 'system', lambda: 'Linux')
    assert windows_helpers.is_dark_mode_enabled() is False

def test_is_dark_mode_enabled_windows_dark_mode(monkeypatch, mock_winreg):
    monkeypatch.setattr(platform, 'system', lambda: 'Windows')
    mock_winreg.QueryValueEx.return_value = (0, None)
    assert windows_helpers.is_dark_mode_enabled() is True
    # Verify that the correct registry key was opened and closed
    mock_winreg.OpenKey.assert_called_with("HKEY_CURRENT_USER", ANY)
    mock_winreg.CloseKey.assert_called_with(mock_winreg.OpenKey.return_value)

def test_is_dark_mode_enabled_windows_light_mode(monkeypatch, mock_winreg):
    monkeypatch.setattr(platform, 'system', lambda: 'Windows')
    mock_winreg.QueryValueEx.return_value = (1, None)
    assert windows_helpers.is_dark_mode_enabled() is False

def test_is_dark_mode_enabled_windows_registry_error(monkeypatch, mock_winreg):
    monkeypatch.setattr(platform, 'system', lambda: 'Windows')
    mock_winreg.OpenKey.side_effect = FileNotFoundError
    assert windows_helpers.is_dark_mode_enabled() is False

# --- Tests for command-line argument parsing in main() ---

@patch('main.webview')
@patch('main.subprocess.Popen')
def test_main_dark_titlebar_arg(mock_popen, mock_webview, mock_sys_argv):
    sys.argv.append('--dark-titlebar')
    main.main()
    assert main.titlebar_preference == 'dark'

@patch('main.webview')
@patch('main.subprocess.Popen')
def test_main_light_titlebar_arg(mock_popen, mock_webview, mock_sys_argv):
    sys.argv.append('--light-titlebar')
    main.main()
    assert main.titlebar_preference == 'light'

@pytest.mark.skipif(platform.system() != "Windows", reason="Auto-updater test is Windows-specific")
@patch('main.webview')
@patch('main.subprocess.Popen')
def test_main_no_args_on_windows(mock_popen, mock_webview, mock_sys_argv):
    main.main()
    assert main.titlebar_preference == 'auto'
    mock_popen.assert_called_once()

@pytest.mark.skipif(platform.system() == "Windows", reason="This test is for non-Windows platforms")
@patch('main.webview')
@patch('main.subprocess.Popen')
def test_main_no_args_on_non_windows(mock_popen, mock_webview, mock_sys_argv):
    main.main()
    assert main.titlebar_preference == 'auto'
    mock_popen.assert_not_called()

@patch('main.webview')
@patch('main.subprocess.Popen')
def test_main_with_no_updater_flag(mock_popen, mock_webview, mock_sys_argv):
    sys.argv.append('--no-updater')
    main.main()
    # Expect Popen NOT to be called for the auto-updater
    mock_popen.assert_not_called()

# --- Tests for Api class ---

def test_api_toggle_always_on_top():
    mock_window = MagicMock()
    mock_window.on_top = False
    api_instance = api.Api(mock_window)
    api_instance.toggle_always_on_top()
    assert mock_window.on_top is True
    api_instance.toggle_always_on_top()
    assert mock_window.on_top is False

@patch('src.api.subprocess.Popen')
def test_api_open_new_window(mock_popen, mock_sys_argv):
    api_instance = api.Api(None)
    api_instance.open_new_window()
    mock_popen.assert_called_once_with([sys.executable, 'main.py', '--no-updater'])

# --- Tests for apply_dark_titlebar (in windows_helpers) ---

def test_apply_dark_titlebar_windows_success(monkeypatch, mock_ctypes):
    monkeypatch.setattr(platform, 'system', lambda: 'Windows')
    monkeypatch.setattr(windows_helpers, 'should_use_dark_titlebar', lambda pref: True)
    window = MagicMock(hwnd=123)
    assert windows_helpers.apply_dark_titlebar(window, "Test App", "dark", main._log) is True
    mock_ctypes.windll.dwmapi.DwmSetWindowAttribute.assert_called()

def test_apply_dark_titlebar_non_windows(monkeypatch):
    monkeypatch.setattr(platform, 'system', lambda: 'Linux')
    # This test doesn't need ctypes, but we provide it to avoid potential issues
    # if other tests have side effects.
    assert windows_helpers.apply_dark_titlebar(MagicMock(), "Test", "auto", main._log) is True
