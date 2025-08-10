import webview
import os
import argparse
import sys
import platform

APP_TITLE = "DeepSeek - Into the Unknown"

# Verbose logging control (toggled in main based on release_mode)
VERBOSE_LOGS = True
def _log(msg: str):
    global VERBOSE_LOGS
    if VERBOSE_LOGS:
        print(msg)

# Windows-specific imports for dark titlebar
if platform.system() == "Windows":
    try:
        import ctypes
        from ctypes import wintypes
        import winreg
    except ImportError:
        ctypes = None
        wintypes = None
        winreg = None

# Global variable to store titlebar preference
titlebar_preference = 'auto'

def is_dark_mode_enabled():
    """Check if Windows is using dark mode"""
    if platform.system() != "Windows" or not winreg:
        return False
    
    try:
        # Check the registry for dark mode setting
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        value, _ = winreg.QueryValueEx(registry_key, "AppsUseLightTheme")
        winreg.CloseKey(registry_key)
        # Value is 0 for dark mode, 1 for light mode
        return value == 0
    except (FileNotFoundError, OSError):
        # Default to light mode if we can't read the registry
        return False

def find_window_handle(window_title):
    """Find window handle by title with retry logic"""
    if platform.system() != "Windows" or not ctypes:
        return None
    
    try:
        user32 = ctypes.windll.user32
        
        # Try exact title match first
        hwnd = user32.FindWindowW(None, window_title)
        if hwnd:
            return hwnd
        
        # Try to enumerate all windows and find by partial title match
        # Define callback with proper WinAPI types
        EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, ctypes.py_object)
        def enum_windows_callback(hwnd, lst):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buffer = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buffer, length + 1)
                if window_title.lower() in buffer.value.lower():
                    lst.append(hwnd)
                    return wintypes.BOOL(False)  # Stop enumeration
            return wintypes.BOOL(True)  # Continue enumeration
        
        callback = EnumWindowsProc(enum_windows_callback)
        user32.EnumWindows.argtypes = [EnumWindowsProc, ctypes.py_object]
        user32.EnumWindows.restype = wintypes.BOOL
        
        # List to store found window handle
        found_windows = []
        user32.EnumWindows(callback, ctypes.py_object(found_windows))
        
        if found_windows:
            return found_windows[0]
        
        return None
    except Exception as e:
        print(f"Error finding window handle: {e}")
        return None

def should_use_dark_titlebar():
    """Determine if dark titlebar should be used based on preference and system settings"""
    global titlebar_preference
    
    if titlebar_preference == 'dark':
        return True
    elif titlebar_preference == 'light':
        return False
    else:  # auto
        return is_dark_mode_enabled()

def apply_dark_titlebar(window):
    """Apply dark titlebar to the window on Windows"""
    if platform.system() != "Windows" or not ctypes:
        return True  # Return True on non-Windows platforms (no-op success)
    
    try:
        # Get the window handle
        hwnd = None
        
        # Try to get the window handle from different possible attributes
        if hasattr(window, 'hwnd'):
            hwnd = window.hwnd
        elif hasattr(window, '_window') and hasattr(window._window, 'hwnd'):
            hwnd = window._window.hwnd
        elif hasattr(window, 'gui') and hasattr(window.gui, 'hwnd'):
            hwnd = window.gui.hwnd
        
        # If we couldn't get it from the window object, try to find it by title
        if not hwnd:
            hwnd = find_window_handle(APP_TITLE)
        
        if hwnd:
            # Constants for DwmSetWindowAttribute
            DWMWA_USE_IMMERSIVE_DARK_MODE_NEW = 20  # Win10 1903+
            DWMWA_USE_IMMERSIVE_DARK_MODE_OLD = 19  # Win10 1809 and earlier
            
            # Load dwmapi.dll
            dwmapi = ctypes.windll.dwmapi
            
            # Determine if we should use dark mode
            use_dark = should_use_dark_titlebar()
            dark_mode = ctypes.c_int(1 if use_dark else 0)
            
            # Try new attribute value first
            result = dwmapi.DwmSetWindowAttribute(
                ctypes.c_void_p(hwnd),
                ctypes.c_int(DWMWA_USE_IMMERSIVE_DARK_MODE_NEW),
                ctypes.byref(dark_mode),
                ctypes.sizeof(dark_mode)
            )
            
            # Fallback to old attribute value on failure
            if result != 0:
                result = dwmapi.DwmSetWindowAttribute(
                    ctypes.c_void_p(hwnd),
                    ctypes.c_int(DWMWA_USE_IMMERSIVE_DARK_MODE_OLD),
                    ctypes.byref(dark_mode),
                    ctypes.sizeof(dark_mode)
                )
            
            if result == 0:  # S_OK
                mode_str = 'dark' if use_dark else 'light'
                source_str = f"({titlebar_preference} mode)" if titlebar_preference != 'auto' else "(system theme)"
                _log(f"Titlebar set to {mode_str} {source_str}")
                return True
            else:
                _log(f"Failed to set titlebar theme: error code {result}")
                return False
        else:
            _log("Could not find window handle for titlebar theming")
            return False
            
    except Exception as e:
        print(f"Error applying titlebar theme: {e}")
        return False

def apply_dark_titlebar_delayed(window):
    """Apply dark titlebar with a delay to ensure window is fully created"""
    import threading
    import time
    
    def delayed_apply():
        # Wait a bit for the window to be fully created
        time.sleep(0.5)
        
        # Try multiple times with progressive backoff
        for attempt in range(5):
            if apply_dark_titlebar(window):
                return  # Success, stop trying
            time.sleep(0.5 * (attempt + 1))  # Progressive backoff
        
        _log("Failed to apply dark titlebar after multiple attempts")
    
    # Run in a separate thread to avoid blocking
    thread = threading.Thread(target=delayed_apply, daemon=True)
    thread.start()

def inject_js(window):
    try:
        # Read injection script
        with open('injection/inject.js', 'r') as f:
            js_code = f.read()
        
        # Inject JavaScript
        window.evaluate_js(js_code)
    except Exception as e:
        print(f"Error injecting JavaScript: {e}")

def on_window_loaded(window):
    """Called when window is loaded"""
    # Apply dark titlebar with delay to ensure window is fully created
    apply_dark_titlebar_delayed(window)
    # Inject JavaScript
    inject_js(window)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--release', action='store_true', help='Disable debug tools for release build')
    parser.add_argument('--dark-titlebar', action='store_true', help='Force dark titlebar')
    parser.add_argument('--light-titlebar', action='store_true', help='Force light titlebar')
    args = parser.parse_args()
    
    # Store titlebar preference globally for access in other functions
    global titlebar_preference
    if args.dark_titlebar:
        titlebar_preference = 'dark'
    elif args.light_titlebar:
        titlebar_preference = 'light'
    else:
        titlebar_preference = 'auto'
    
    # Auto-enable release mode for frozen builds
    is_frozen = getattr(sys, 'frozen', False)
    release_mode = args.release or is_frozen
    # Gate verbose logs in release mode
    global VERBOSE_LOGS
    VERBOSE_LOGS = not release_mode
    
    # Launch auto-updater in background
    try:
        import subprocess
        import os
        updater_path = os.path.join(os.path.dirname(__file__), 'auto-update.bat')
        if os.path.exists(updater_path):
            subprocess.Popen([updater_path, '--auto'], creationflags=subprocess.CREATE_NEW_CONSOLE)
    except Exception as e:
        print("Failed to launch auto updater : ", e)
        pass  # Silently continue if updater fails to launch
    
    # Create window with persistent cookie storage
    window = webview.create_window(
        APP_TITLE,
        "https://chat.deepseek.com",
        width=1200,
        height=800,
        text_select=True # Enable selecting text (#2 vanja-san)
    )
    
    # Add event listener for page load
    window.events.loaded += on_window_loaded
    
    # Start webview with persistent storage
    webview.start(
        private_mode=False,  # Disable private mode for persistent cookies
        storage_path="./data",  # Storage directory
        debug=not release_mode  # Enable dev tools unless in release mode
    )

if __name__ == "__main__":
    main()