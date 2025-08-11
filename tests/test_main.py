import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

def test_should_use_dark_titlebar_auto_with_dark_mode(mocker):
    """Test 'auto' preference when system dark mode is ON."""
    mocker.patch('main.is_dark_mode_enabled', return_value=True)
    main.titlebar_preference = 'auto'
    assert main.should_use_dark_titlebar() is True

def test_should_use_dark_titlebar_auto_with_light_mode(mocker):
    """Test 'auto' preference when system dark mode is OFF."""
    mocker.patch('main.is_dark_mode_enabled', return_value=False)
    main.titlebar_preference = 'auto'
    assert main.should_use_dark_titlebar() is False

# --- Tests for is_dark_mode_enabled ---

def test_is_dark_mode_enabled_non_windows(mocker):
    """Test dark mode detection on non-Windows platforms."""
    mocker.patch('platform.system', return_value='Linux')
    assert main.is_dark_mode_enabled() is False

def test_is_dark_mode_enabled_windows_winreg_not_available(mocker):
    """Test dark mode detection on Windows when winreg is not available."""
    mocker.patch('platform.system', return_value='Windows')
    with patch('main.winreg', None, create=True): # Still need unittest patch for context manager
        assert main.is_dark_mode_enabled() is False

def test_is_dark_mode_enabled_windows_dark_mode(mocker):
    """Test dark mode detection on Windows when dark mode is ON."""
    mock_winreg = mocker.patch('main.winreg', create=True)
    mock_winreg.OpenKey.return_value = MagicMock() # Mock the opened key
    mock_winreg.QueryValueEx.return_value = (0, None) # 0 for dark mode
    mocker.patch('platform.system', return_value='Windows')
    assert main.is_dark_mode_enabled() is True

def test_is_dark_mode_enabled_windows_light_mode(mocker):
    """Test dark mode detection on Windows when dark mode is OFF."""
    mock_winreg = mocker.patch('main.winreg', create=True)
    mock_winreg.OpenKey.return_value = MagicMock()
    mock_winreg.QueryValueEx.return_value = (1, None) # 1 for light mode
    mocker.patch('platform.system', return_value='Windows')
    assert main.is_dark_mode_enabled() is False

def test_is_dark_mode_enabled_windows_registry_file_not_found(mocker):
    """Test dark mode detection on Windows when a registry key is not found."""
    mock_winreg = mocker.patch('main.winreg', create=True)
    mock_winreg.OpenKey.side_effect = FileNotFoundError
    mocker.patch('platform.system', return_value='Windows')
    assert main.is_dark_mode_enabled() is False

def test_is_dark_mode_enabled_windows_registry_os_error(mocker):
    """Test dark mode detection on Windows when an OS error occurs."""
    mock_winreg = mocker.patch('main.winreg', create=True)
    mock_winreg.OpenKey.side_effect = OSError
    mocker.patch('platform.system', return_value='Windows')
    assert main.is_dark_mode_enabled() is False

# --- Tests for command-line argument parsing in main() ---

def test_main_no_args(mocker):
    """Test main() with no command-line arguments."""
    mocker.patch('subprocess.Popen')
    mocker.patch('webview.start')
    mocker.patch('webview.create_window')
    mocker.patch('sys.argv', ['main.py'])
    
    # Need to reset global state for each test run
    main.titlebar_preference = 'auto' # Default from main()
    
    main.main()
    assert main.titlebar_preference == 'auto'

def test_main_dark_titlebar_arg(mocker):
    """Test main() with the --dark-titlebar argument."""
    mocker.patch('subprocess.Popen')
    mocker.patch('webview.start')
    mocker.patch('webview.create_window')
    mocker.patch('sys.argv', ['main.py', '--dark-titlebar'])
    
    main.main()
    assert main.titlebar_preference == 'dark'

def test_main_light_titlebar_arg(mocker):
    """Test main() with the --light-titlebar argument."""
    mocker.patch('subprocess.Popen')
    mocker.patch('webview.start')
    mocker.patch('webview.create_window')
    mocker.patch('sys.argv', ['main.py', '--light-titlebar'])
    
    main.main()
    assert main.titlebar_preference == 'light'

# --- Tests for apply_dark_titlebar ---

def test_apply_dark_titlebar_non_windows(mocker):
    """Test that apply_dark_titlebar is a no-op on non-Windows systems."""
    mocker.patch('platform.system', return_value='Linux')
    window_mock = mocker.MagicMock()
    assert main.apply_dark_titlebar(window_mock) is True

def test_apply_dark_titlebar_windows_no_ctypes(mocker):
    """Test that apply_dark_titlebar is a no-op on Windows if ctypes is not available."""
    mocker.patch('platform.system', return_value='Windows')
    mocker.patch('main.ctypes', None, create=True)
    window_mock = mocker.MagicMock()
    assert main.apply_dark_titlebar(window_mock) is True

def test_apply_dark_titlebar_windows_no_hwnd(mocker):
    """Test apply_dark_titlebar on Windows when no window handle can be found."""
    mocker.patch('platform.system', return_value='Windows')
    mock_ctypes = mocker.patch('main.ctypes', create=True)
    mock_find_handle = mocker.patch('main.find_window_handle', return_value=None)
    
    window = mocker.MagicMock()
    # Ensure window has no hwnd attributes by deleting them if they exist
    # or by ensuring the mock doesn't auto-spec them
    del window.hwnd
    del window._window
    del window.gui
    
    assert main.apply_dark_titlebar(window) is False
    mock_find_handle.assert_called_once_with(main.APP_TITLE)

def test_apply_dark_titlebar_windows_success_new_attr(mocker):
    """Test successful application of dark titlebar using the new attribute."""
    mock_platform = mocker.patch('platform.system', return_value='Windows')
    mock_should_use = mocker.patch('main.should_use_dark_titlebar', return_value=True)
    mock_ctypes = mocker.patch('main.ctypes', create=True)
    
    mock_dwmapi = mock_ctypes.windll.dwmapi
    mock_dwmapi.DwmSetWindowAttribute.return_value = 0  # S_OK
    
    window = mocker.MagicMock(hwnd=123)
    assert main.apply_dark_titlebar(window) is True
    
    mock_dwmapi.DwmSetWindowAttribute.assert_called_once_with(
        mock_ctypes.c_void_p(123),
        mock_ctypes.c_int(20), # DWMWA_USE_IMMERSIVE_DARK_MODE_NEW
        mock_ctypes.byref(mock_ctypes.c_int(1)),
        mock_ctypes.sizeof(mock_ctypes.c_int(1))
    )
    mock_should_use.assert_called_once()

def test_apply_dark_titlebar_windows_success_old_attr(mocker):
    """Test successful application of dark titlebar using the old attribute as a fallback."""
    mock_platform = mocker.patch('platform.system', return_value='Windows')
    mock_should_use = mocker.patch('main.should_use_dark_titlebar', return_value=True)
    mock_ctypes = mocker.patch('main.ctypes', create=True)
    
    # Mock c_int to return a real int instead of a MagicMock
    def mock_c_int(value):
        return value
    
    mock_ctypes.c_int = mock_c_int
    
    mock_dwmapi = mock_ctypes.windll.dwmapi
    # Fail new attribute, succeed old attribute
    mock_dwmapi.DwmSetWindowAttribute.side_effect = [-1, 0]  # Fail, then S_OK
    
    window = mocker.MagicMock(hwnd=123)
    assert main.apply_dark_titlebar(window) is True
    assert mock_dwmapi.DwmSetWindowAttribute.call_count == 2
    
    # Check that the second call used the old attribute value (19)
    calls = mock_dwmapi.DwmSetWindowAttribute.call_args_list
    assert calls[1][0][1] == 19 # DWMWA_USE_IMMERSIVE_DARK_MODE_OLD
    mock_should_use.assert_called_once()

def test_apply_dark_titlebar_windows_failure(mocker):
    """Test failed application of dark titlebar for both attributes."""
    mock_platform = mocker.patch('platform.system', return_value='Windows')
    mock_should_use = mocker.patch('main.should_use_dark_titlebar', return_value=True)
    mock_ctypes = mocker.patch('main.ctypes', create=True)
    
    mock_dwmapi = mock_ctypes.windll.dwmapi
    mock_dwmapi.DwmSetWindowAttribute.return_value = -1  # Fail for both
    
    window = mocker.MagicMock(hwnd=123)
    assert main.apply_dark_titlebar(window) is False
    assert mock_dwmapi.DwmSetWindowAttribute.call_count == 2
    mock_should_use.assert_called_once()

def test_apply_dark_titlebar_windows_exception(mocker):
    """Test that an exception during titlebar application is caught."""
    mock_platform = mocker.patch('platform.system', return_value='Windows')
    mock_ctypes = mocker.patch('main.ctypes', create=True)
    
    mock_dwmapi = mock_ctypes.windll.dwmapi
    mock_dwmapi.DwmSetWindowAttribute.side_effect = Exception("Test Exception")
    
    window = mocker.MagicMock(hwnd=123)
    assert main.apply_dark_titlebar(window) is False

# --- Tests for find_window_handle ---

def test_find_window_handle_non_windows(mocker):
    """Test that find_window_handle is a no-op on non-Windows systems."""
    mocker.patch('platform.system', return_value='Linux')
    assert main.find_window_handle("some_title") is None

def test_find_window_handle_windows_no_ctypes(mocker):
    """Test that find_window_handle is a no-op on Windows if ctypes is not available."""
    mocker.patch('platform.system', return_value='Windows')
    mocker.patch('main.ctypes', None, create=True)
    assert main.find_window_handle("some_title") is None

def test_find_window_handle_success_with_findwindoww(mocker):
    """Test finding a window successfully with FindWindowW."""
    mock_ctypes = mocker.patch('main.ctypes', create=True)
    mock_user32 = mock_ctypes.windll.user32
    mock_user32.FindWindowW.return_value = 12345  # Mock HWND
    
    assert main.find_window_handle("some_title") == 12345
    mock_user32.FindWindowW.assert_called_once_with(None, "some_title")

def test_find_window_handle_success_with_enumwindows(mocker):
    """Test finding a window successfully with EnumWindows."""
    mocker.patch('platform.system', return_value='Windows')
    mock_ctypes = mocker.patch('main.ctypes', create=True)
    mock_wintypes = mocker.patch('main.wintypes', create=True)
    mock_user32 = mock_ctypes.windll.user32
    mock_user32.FindWindowW.return_value = None  # Fail FindWindowW

    # Mock GetWindowTextLengthW and GetWindowTextW
    mock_user32.GetWindowTextLengthW.return_value = 10  # Some length > 0
    
    # Mock create_unicode_buffer to return a buffer with our test title
    mock_buffer = mocker.MagicMock()
    mock_buffer.value = "some_title test window"
    mock_ctypes.create_unicode_buffer.return_value = mock_buffer
    
    # Mock GetWindowTextW to succeed
    mock_user32.GetWindowTextW.return_value = True
    
    # Mock WINFUNCTYPE to create a proper callback type
    def mock_winfunctype(*args):
        def wrapper(func):
            return func
        return wrapper
    
    mock_ctypes.WINFUNCTYPE = mock_winfunctype
    
    # Mock py_object to return the actual list passed to it
    def mock_py_object(obj):
        return obj
    mock_ctypes.py_object = mock_py_object
    
    # Mock EnumWindows to simulate finding a window
    def enum_windows_side_effect(callback, lst_param):
        # Simulate the callback being called with a window handle
        # The callback will check the window title and add to list if it matches
        callback(54321, lst_param)
        return True  # Success
    
    mock_user32.EnumWindows.side_effect = enum_windows_side_effect
    
    result = main.find_window_handle("some_title")
    assert result == 54321
    assert mock_user32.EnumWindows.call_count == 1


def test_find_window_handle_not_found(mocker):
    """Test when no window is found by either method."""
    mock_ctypes = mocker.patch('main.ctypes', create=True)
    mock_user32 = mock_ctypes.windll.user32
    mock_user32.FindWindowW.return_value = None
    mock_user32.EnumWindows.return_value = None # Simulate no windows found
    assert main.find_window_handle("some_title") is None

def test_find_window_handle_exception(mocker):
    """Test that an exception during window finding is caught."""
    mock_ctypes = mocker.patch('main.ctypes', create=True)
    mock_ctypes.windll.user32.FindWindowW.side_effect = Exception("Test Exception")
    assert main.find_window_handle("some_title") is None
