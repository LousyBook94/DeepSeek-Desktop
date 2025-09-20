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
            # Define function signature: HRESULT DwmSetWindowAttribute(HWND, DWORD, LPCVOID, DWORD)
            try:
                dwmapi.DwmSetWindowAttribute.argtypes = [
                    ctypes.c_void_p,  # HWND
                    ctypes.c_int,     # DWORD attribute
                    ctypes.c_void_p,  # LPCVOID pvAttribute
                    ctypes.c_uint     # DWORD cbAttribute
                ]
                dwmapi.DwmSetWindowAttribute.restype = ctypes.c_int  # HRESULT
            except AttributeError:
                # Older systems may not expose the symbol; keep best-effort behavior
                pass
             
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
    # Start update check in a background thread
    update_check_thread = threading.Thread(target=check_for_updates_background, args=(window,), daemon=True)
    update_check_thread.start()

from utils import updater
import threading

# Global variable to store update info
update_info = {}

class Api:
    def __init__(self, window):
        self.window = window

    def start_update(self):
        _log("User requested to start update.")
        
        def update_progress(progress):
            self.window.evaluate_js(f"showUpdateProgress({progress})")

        def run_update():
            release_info = update_info.get("release_info")
            if not release_info:
                _log("Update failed: release_info not found.")
                self.window.evaluate_js("showUpdateError('Failed to get release information.')")
                return

            # Show progress popup
            self.window.evaluate_js("showUpdateProgress(0)")

            # Download
            zip_path, error = updater.download_update(release_info, progress_callback=update_progress)
            if error:
                _log(f"Update failed during download: {error}")
                self.window.evaluate_js(f"showUpdateError('Download failed: {error}')")
                return

            # Install
            self.window.evaluate_js("showUpdateProgress('installing')")
            success, message = updater.install_update(zip_path, update_info.get("latest_version"))
            if not success:
                _log(f"Update failed during installation: {message}")
                self.window.evaluate_js(f"showUpdateError('Installation failed: {message}')")

        # Run the update in a separate thread to avoid blocking the UI
        update_thread = threading.Thread(target=run_update, daemon=True)
        update_thread.start()


def check_for_updates_background(window):
    """Check for updates in a background thread."""
    _log("Checking for updates in the background...")
    global update_info
    update_info = updater.check_for_updates()
    _log(f"Update info: {update_info}")

    if update_info.get("update_needed"):
        _log(f"Update available: {update_info['current_version']} -> {update_info['latest_version']}")
        window.evaluate_js(f"showUpdatePopup('{update_info['current_version']}', '{update_info['latest_version']}')")
    elif update_info.get("error"):
        _log(f"Update check failed: {update_info['error']}")
    else:
        _log("No update needed.")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--release', action='store_true', help='Disable debug tools for release build')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--dark-titlebar', action='store_true', help='Force dark titlebar')
    group.add_argument('--light-titlebar', action='store_true', help='Force light titlebar')
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

    # Create window with persistent cookie storage
    api = Api(None) # Initialized with None, will be set later
    window = webview.create_window(
        APP_TITLE,
        "https://chat.deepseek.com",
        width=1200,
        height=800,
        text_select=True, # Enable selecting text (#2 vanja-san)
        js_api=api
    )
    api.window = window # Set the window object for the api

    # Add event listener for page load
    window.events.loaded += on_window_loaded

    # Create a local server to serve static files like version.txt
    import http.server
    import socketserver
    import os
    
    class FileHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=".", **kwargs)

        def end_headers(self):
            # Add CORS headers to allow access from the webview
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            return super().end_headers()

        def do_GET(self):
            if self.path == '/port':
                # Return the actual port number
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(str(self.server.server_address[1]).encode())
            else:
                # Handle other requests normally
                super().do_GET()

    def find_available_port(start_port=8080, max_attempts=100):
        """Find an available port starting from start_port"""
        import socket
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.bind(("", port))
                    return port
            except OSError:
                continue
        raise OSError(f"No available ports found in range {start_port}-{start_port + max_attempts - 1}")

    def start_http_server():
        # Find an available port starting from 8080
        try:
            port = find_available_port(8080)
            with socketserver.TCPServer(("", port), FileHandler) as httpd:
                print(f"HTTP server running on port {port}")
                httpd.serve_forever()
        except OSError as e:
            print(f"Failed to start HTTP server: {e}")

    # Start HTTP server in a separate thread
    server_thread = threading.Thread(target=start_http_server, daemon=True)
    server_thread.start()
    
    # Start webview with persistent storage
    webview.start(
        private_mode=False,  # Disable private mode for persistent cookies
        storage_path="./data",  # Storage directory
        debug=not release_mode  # Enable dev tools unless in release mode
    )

if __name__ == "__main__":
    main()