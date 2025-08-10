import platform
import threading
import time

# Conditionally import Windows-specific libraries
if platform.system() == "Windows":
    try:
        import ctypes
        from ctypes import wintypes
        import winreg
    except ImportError:
        ctypes = None
        wintypes = None
        winreg = None
else:
    ctypes = None
    wintypes = None
    winreg = None

def is_dark_mode_enabled():
    """Check if Windows is using dark mode via the registry."""
    if not winreg:
        return False
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        value, _ = winreg.QueryValueEx(registry_key, "AppsUseLightTheme")
        winreg.CloseKey(registry_key)
        return value == 0
    except (FileNotFoundError, OSError):
        return False

def find_window_handle(window_title: str, _log):
    """Find a window handle by its title, with retry logic."""
    if not ctypes:
        return None
    try:
        user32 = ctypes.windll.user32
        hwnd = user32.FindWindowW(None, window_title)
        if hwnd:
            return hwnd

        # Fallback to enumerating windows if exact match fails
        EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, ctypes.py_object)

        def enum_windows_callback(hwnd, lst):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buffer = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buffer, length + 1)
                if window_title.lower() in buffer.value.lower():
                    lst.append(hwnd)
                    return wintypes.BOOL(False)  # Stop enumeration
            return wintypes.BOOL(True)

        callback = EnumWindowsProc(enum_windows_callback)
        found_windows = []
        user32.EnumWindows(callback, ctypes.py_object(found_windows))

        return found_windows[0] if found_windows else None
    except Exception as e:
        _log(f"Error finding window handle: {e}")
        return None

def should_use_dark_titlebar(titlebar_preference: str):
    """Determine if the dark titlebar should be used based on preference and system settings."""
    if titlebar_preference == 'dark':
        return True
    if titlebar_preference == 'light':
        return False
    return is_dark_mode_enabled()

def apply_dark_titlebar(window, APP_TITLE: str, titlebar_preference: str, _log):
    """Apply the dark titlebar to the window on Windows."""
    if platform.system() != "Windows" or not ctypes:
        return True  # No-op success on non-Windows platforms

    try:
        hwnd = window.hwnd if hasattr(window, 'hwnd') else find_window_handle(APP_TITLE, _log)
        if not hwnd:
            _log("Could not find window handle for titlebar theming.")
            return False

        dwmapi = ctypes.windll.dwmapi
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20  # Attribute for dark mode

        use_dark = should_use_dark_titlebar(titlebar_preference)
        dark_mode_val = ctypes.c_int(1 if use_dark else 0)

        result = dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(dark_mode_val),
            ctypes.sizeof(dark_mode_val)
        )

        if result == 0:
            mode_str = 'dark' if use_dark else 'light'
            source_str = f"({titlebar_preference} mode)" if titlebar_preference != 'auto' else "(system theme)"
            _log(f"Titlebar set to {mode_str} {source_str}")
            return True
        else:
            # Fallback for older Windows versions
            DWMWA_USE_IMMERSIVE_DARK_MODE_OLD = 19
            result = dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_USE_IMMERSIVE_DARK_MODE_OLD,
                ctypes.byref(dark_mode_val),
                ctypes.sizeof(dark_mode_val)
            )
            if result == 0:
                mode_str = 'dark' if use_dark else 'light'
                source_str = f"({titlebar_preference} mode)" if titlebar_preference != 'auto' else "(system theme)"
                _log(f"Titlebar set to {mode_str} {source_str} (using fallback)")
                return True

            _log(f"Failed to set titlebar theme: error code {result}")
            return False

    except Exception as e:
        _log(f"Error applying titlebar theme: {e}")
        return False

def apply_dark_titlebar_delayed(window, APP_TITLE: str, titlebar_preference: str, _log):
    """Apply dark titlebar with a delay to ensure the window is fully created."""
    if platform.system() != "Windows":
        return

    def delayed_apply():
        time.sleep(0.5)  # Initial delay
        for attempt in range(5):
            if apply_dark_titlebar(window, APP_TITLE, titlebar_preference, _log):
                return
            time.sleep(0.5 * (attempt + 1))  # Progressive backoff
        _log("Failed to apply dark titlebar after multiple attempts.")

    threading.Thread(target=delayed_apply, daemon=True).start()
