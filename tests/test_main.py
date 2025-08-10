import sys
import pytest
from unittest.mock import patch, MagicMock

import main

# Basic test to ensure the setup is working
def test_initialization():
    assert True

# --- Tests for should_use_dark_titlebar ---

def test_should_use_dark_titlebar_dark_preference():
    """Test with titlebar_preference set to 'dark'."""
    main.titlebar_preference = 'dark'
    assert main.should_use_dark_titlebar() is True

def test_should_use_dark_titlebar_light_preference():
    """Test with titlebar_preference set to 'light'."""
    main.titlebar_preference = 'light'
    assert main.should_use_dark_titlebar() is False

@patch('main.is_dark_mode_enabled', return_value=True)
def test_should_use_dark_titlebar_auto_with_dark_mode(mock_is_dark_mode_enabled):
    """Test 'auto' preference when system dark mode is ON."""
    main.titlebar_preference = 'auto'
    assert main.should_use_dark_titlebar() is True
    mock_is_dark_mode_enabled.assert_called_once()

@patch('main.is_dark_mode_enabled', return_value=False)
def test_should_use_dark_titlebar_auto_with_light_mode(mock_is_dark_mode_enabled):
    """Test 'auto' preference when system dark mode is OFF."""
    main.titlebar_preference = 'auto'
    assert main.should_use_dark_titlebar() is False
    mock_is_dark_mode_enabled.assert_called_once()

# --- Tests for is_dark_mode_enabled ---

@patch('platform.system', return_value='Linux')
def test_is_dark_mode_enabled_non_windows(mock_platform):
    """Test dark mode detection on non-Windows platforms."""
    assert main.is_dark_mode_enabled() is False

@patch('platform.system', return_value='Windows')
def test_is_dark_mode_enabled_windows_winreg_not_available(mock_platform):
    """Test dark mode detection on Windows when winreg is not available."""
    with patch('main.winreg', None, create=True):
        assert main.is_dark_mode_enabled() is False

@patch('platform.system', return_value='Windows')
@patch('main.winreg', create=True)
def test_is_dark_mode_enabled_windows_dark_mode(mock_winreg, mock_platform):
    """Test dark mode detection on Windows when dark mode is ON."""
    mock_winreg.QueryValueEx.return_value = (0, None)
    assert main.is_dark_mode_enabled() is True

@patch('platform.system', return_value='Windows')
@patch('main.winreg', create=True)
def test_is_dark_mode_enabled_windows_light_mode(mock_winreg, mock_platform):
    """Test dark mode detection on Windows when dark mode is OFF."""
    mock_winreg.QueryValueEx.return_value = (1, None)
    assert main.is_dark_mode_enabled() is False

@patch('platform.system', return_value='Windows')
@patch('main.winreg', create=True)
def test_is_dark_mode_enabled_windows_registry_file_not_found(mock_winreg, mock_platform):
    """Test dark mode detection on Windows when a registry key is not found."""
    mock_winreg.OpenKey.side_effect = FileNotFoundError
    assert main.is_dark_mode_enabled() is False

@patch('platform.system', return_value='Windows')
@patch('main.winreg', create=True)
def test_is_dark_mode_enabled_windows_registry_os_error(mock_winreg, mock_platform):
    """Test dark mode detection on Windows when an OS error occurs."""
    mock_winreg.OpenKey.side_effect = OSError
    assert main.is_dark_mode_enabled() is False

# --- Tests for command-line argument parsing in main() ---

@patch('subprocess.Popen')
@patch('webview.start')
@patch('webview.create_window')
@patch('sys.argv', ['main.py'])
def test_main_no_args(mock_create_window, mock_start, mock_popen):
    """Test main() with no command-line arguments."""
    main.main()
    assert main.titlebar_preference == 'auto'

@patch('subprocess.Popen')
@patch('webview.start')
@patch('webview.create_window')
@patch('sys.argv', ['main.py', '--dark-titlebar'])
def test_main_dark_titlebar_arg(mock_create_window, mock_start, mock_popen):
    """Test main() with the --dark-titlebar argument."""
    main.main()
    assert main.titlebar_preference == 'dark'

@patch('subprocess.Popen')
@patch('webview.start')
@patch('webview.create_window')
@patch('sys.argv', ['main.py', '--light-titlebar'])
def test_main_light_titlebar_arg(mock_create_window, mock_start, mock_popen):
    """Test main() with the --light-titlebar argument."""
    main.main()
    assert main.titlebar_preference == 'light'

# --- Tests for apply_dark_titlebar ---

@patch('platform.system', return_value='Linux')
def test_apply_dark_titlebar_non_windows(mock_platform):
    """Test that apply_dark_titlebar is a no-op on non-Windows systems."""
    assert main.apply_dark_titlebar(MagicMock()) is True

@patch('platform.system', return_value='Windows')
@patch('main.ctypes', None, create=True)
def test_apply_dark_titlebar_windows_no_ctypes(mock_platform):
    """Test that apply_dark_titlebar is a no-op on Windows if ctypes is not available."""
    assert main.apply_dark_titlebar(MagicMock()) is True

@patch('platform.system', return_value='Windows')
@patch('main.ctypes', create=True)
@patch('main.find_window_handle', return_value=None)
def test_apply_dark_titlebar_windows_no_hwnd(mock_find_handle, mock_ctypes, mock_platform):
    """Test apply_dark_titlebar on Windows when no window handle can be found."""
    window = MagicMock()
    # Ensure window has no hwnd attributes
    del window.hwnd
    del window._window
    del window.gui
    assert main.apply_dark_titlebar(window) is False
    mock_find_handle.assert_called_once_with(main.APP_TITLE)

@patch('platform.system', return_value='Windows')
@patch('main.should_use_dark_titlebar', return_value=True)
@patch('main.ctypes', create=True)
def test_apply_dark_titlebar_windows_success_new_attr(mock_ctypes, mock_should_use, mock_platform):
    """Test successful application of dark titlebar using the new attribute."""
    mock_ctypes.windll.dwmapi.DwmSetWindowAttribute.return_value = 0  # S_OK
    window = MagicMock(hwnd=123)
    assert main.apply_dark_titlebar(window) is True
    # Asserts that DwmSetWindowAttribute was called with the new attribute value (20)
    mock_ctypes.windll.dwmapi.DwmSetWindowAttribute.assert_called_with(
        mock_ctypes.c_void_p(123),
        mock_ctypes.c_int(20),
        mock_ctypes.byref(mock_ctypes.c_int(1)),
        mock_ctypes.sizeof(mock_ctypes.c_int(1))
    )

@patch('platform.system', return_value='Windows')
@patch('main.should_use_dark_titlebar', return_value=True)
@patch('main.ctypes', create=True)
def test_apply_dark_titlebar_windows_success_old_attr(mock_ctypes, mock_should_use, mock_platform):
    """Test successful application of dark titlebar using the old attribute as a fallback."""
    # Fail new attribute, succeed old attribute
    mock_ctypes.windll.dwmapi.DwmSetWindowAttribute.side_effect = [-1, 0]  # Fail, then S_OK
    window = MagicMock(hwnd=123)
    assert main.apply_dark_titlebar(window) is True
    assert mock_ctypes.windll.dwmapi.DwmSetWindowAttribute.call_count == 2
    # Asserts that the second call used the old attribute value (19)
    mock_ctypes.windll.dwmapi.DwmSetWindowAttribute.assert_called_with(
        mock_ctypes.c_void_p(123),
        mock_ctypes.c_int(19),
        mock_ctypes.byref(mock_ctypes.c_int(1)),
        mock_ctypes.sizeof(mock_ctypes.c_int(1))
    )

@patch('platform.system', return_value='Windows')
@patch('main.should_use_dark_titlebar', return_value=True)
@patch('main.ctypes', create=True)
def test_apply_dark_titlebar_windows_failure(mock_ctypes, mock_should_use, mock_platform):
    """Test failed application of dark titlebar for both attributes."""
    mock_ctypes.windll.dwmapi.DwmSetWindowAttribute.return_value = -1  # Fail
    window = MagicMock(hwnd=123)
    assert main.apply_dark_titlebar(window) is False
    assert mock_ctypes.windll.dwmapi.DwmSetWindowAttribute.call_count == 2

@patch('platform.system', return_value='Windows')
@patch('main.ctypes', create=True)
def test_apply_dark_titlebar_windows_exception(mock_ctypes, mock_platform):
    """Test that an exception during titlebar application is caught."""
    mock_ctypes.windll.dwmapi.DwmSetWindowAttribute.side_effect = Exception("Test Exception")
    window = MagicMock(hwnd=123)
    assert main.apply_dark_titlebar(window) is False

# --- Tests for find_window_handle ---

@patch('platform.system', return_value='Linux')
def test_find_window_handle_non_windows(mock_platform):
    """Test that find_window_handle is a no-op on non-Windows systems."""
    assert main.find_window_handle("some_title") is None

@patch('platform.system', return_value='Windows')
@patch('main.ctypes', None, create=True)
def test_find_window_handle_windows_no_ctypes(mock_platform):
    """Test that find_window_handle is a no-op on Windows if ctypes is not available."""
    assert main.find_window_handle("some_title") is None

@patch('platform.system', return_value='Windows')
@patch('main.ctypes', create=True)
def test_find_window_handle_success_with_findwindoww(mock_ctypes, mock_platform):
    """Test finding a window successfully with FindWindowW."""
    mock_ctypes.windll.user32.FindWindowW.return_value = 12345  # Mock HWND
    assert main.find_window_handle("some_title") == 12345
    mock_ctypes.windll.user32.FindWindowW.assert_called_once_with(None, "some_title")

@patch('platform.system', return_value='Windows')
@patch('main.ctypes', create=True)
@patch('main.wintypes', create=True)
def test_find_window_handle_success_with_enumwindows(mock_wintypes, mock_ctypes, mock_platform):
    """Test finding a window successfully with EnumWindows."""
    mock_user32 = mock_ctypes.windll.user32
    mock_user32.FindWindowW.return_value = None  # Fail FindWindowW

    # Simulate the side effect of EnumWindows: populating the list of found windows.
    def enum_windows_side_effect(callback, found_windows_py_object):
        # The second argument to EnumWindows is a py_object, whose `value`
        # is the actual list we want to populate.
        found_windows_py_object.value.append(54321)

    mock_user32.EnumWindows.side_effect = enum_windows_side_effect

    # We also need to mock py_object to have a `value` attribute.
    # The actual list is created inside find_window_handle.
    mock_ctypes.py_object.side_effect = lambda obj: type('MockPyObject', (), {'value': obj})()

    assert main.find_window_handle("some_title") == 54321
    assert mock_user32.EnumWindows.call_count == 1


@patch('platform.system', return_value='Windows')
@patch('main.ctypes', create=True)
def test_find_window_handle_not_found(mock_ctypes, mock_platform):
    """Test when no window is found by either method."""
    mock_user32 = mock_ctypes.windll.user32
    mock_user32.FindWindowW.return_value = None
    mock_user32.EnumWindows.return_value = None # Simulate no windows found
    assert main.find_window_handle("some_title") is None

@patch('platform.system', return_value='Windows')
@patch('main.ctypes', create=True)
def test_find_window_handle_exception(mock_ctypes, mock_platform):
    """Test that an exception during window finding is caught."""
    mock_ctypes.windll.user32.FindWindowW.side_effect = Exception("Test Exception")
    assert main.find_window_handle("some_title") is None
