import webview
import os
import argparse
import sys
import platform
import subprocess

# Add src to path for local imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from windows_helpers import apply_dark_titlebar_delayed
from api import Api

APP_TITLE = "DeepSeek - Into the Unknown"

# Global variable to store titlebar preference
titlebar_preference = 'auto'

# Verbose logging control (toggled in main based on release_mode)
VERBOSE_LOGS = True
def _log(msg: str):
    global VERBOSE_LOGS
    if VERBOSE_LOGS:
        print(msg)

def inject_js(window):
    """
    Inject all JavaScript modules from the injection/modules directory
    into the webview.
    """
    try:
        module_dir = os.path.join(os.path.dirname(__file__), 'injection', 'modules')
        js_files = sorted([f for f in os.listdir(module_dir) if f.endswith('.js')])
        
        all_js_code = []
        for js_file in js_files:
            with open(os.path.join(module_dir, js_file), 'r', encoding='utf-8') as f:
                all_js_code.append(f.read())
        
        # Combine all scripts into one
        combined_js = "\n\n".join(all_js_code)
        
        # Inject the combined JavaScript
        window.evaluate_js(combined_js)
        _log(f"Injected {len(js_files)} JS modules.")
        
    except FileNotFoundError:
        _log("Skipping JS injection: injection/modules directory not found.")
    except Exception as e:
        _log(f"Error injecting JavaScript: {e}")

def on_window_loaded(window):
    """Called when the window is loaded."""
    # Apply dark titlebar (if on Windows)
    if platform.system() == "Windows":
        apply_dark_titlebar_delayed(window, APP_TITLE, titlebar_preference, _log)
    # Inject custom JavaScript
    inject_js(window)

class Api:
    def __init__(self, window):
        self.window = window

    def toggle_always_on_top(self):
        self.window.on_top = not self.window.on_top
        _log(f"Always on top toggled {'on' if self.window.on_top else 'off'}")

    def open_new_window(self):
        # Relaunch the application in a new process, disabling the updater
        try:
            subprocess.Popen([sys.executable, sys.argv[0], '--no-updater'])
            _log("New window requested.")
        except Exception as e:
            _log(f"Failed to open new window: {e}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--release', action='store_true', help='Disable debug tools for release build')
    parser.add_argument('--no-updater', action='store_true', help='Disable auto-updater launch')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--dark-titlebar', action='store_true', help='Force dark titlebar')
    group.add_argument('--light-titlebar', action='store_true', help='Force light titlebar')
    args = parser.parse_args()
    
    # Store titlebar preference globally
    global titlebar_preference
    if args.dark_titlebar:
        titlebar_preference = 'dark'
    elif args.light_titlebar:
        titlebar_preference = 'light'
    
    # Determine if running in release mode
    is_frozen = getattr(sys, 'frozen', False)
    release_mode = args.release or is_frozen
    global VERBOSE_LOGS
    VERBOSE_LOGS = not release_mode
    
    # Launch auto-updater on Windows, unless disabled
    if platform.system() == "Windows" and not args.no_updater:
        try:
            updater_path = os.path.join(os.path.dirname(__file__), 'auto-update.bat')
            if os.path.exists(updater_path):
                subprocess.Popen([updater_path, '--auto'], creationflags=subprocess.CREATE_NEW_CONSOLE)
        except Exception as e:
            _log(f"Failed to launch auto-updater: {e}")

    # Create an API instance for the webview
    api = Api(None)
    
    # Create the webview window and link the API
    window = webview.create_window(
        APP_TITLE,
        "https://chat.deepseek.com",
        width=1200,
        height=800,
        text_select=True,
        js_api=api
    )
    api.window = window # Set the window instance for the API
    
    window.events.loaded += lambda: on_window_loaded(window)
    
    # Start the webview event loop
    webview.start(
        private_mode=False,
        storage_path="./data",
        debug=not release_mode
    )

if __name__ == "__main__":
    main()