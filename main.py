import webview
import os
import argparse
import sys

def inject_js(window):
    try:
        # Read injection script
        with open('injection/inject.js', 'r') as f:
            js_code = f.read()
        
        # Inject JavaScript
        window.evaluate_js(js_code)
    except Exception as e:
        print(f"Error injecting JavaScript: {e}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--release', action='store_true', help='Disable debug tools for release build')
    args = parser.parse_args()
    
    # Auto-enable release mode for frozen builds
    is_frozen = getattr(sys, 'frozen', False)
    release_mode = args.release or is_frozen
    
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
        "DeepSeek - Into the Unknown",
        "https://chat.deepseek.com",
        width=1200,
        height=800,
        text_select=True # Enable selecting text (#2 vanja-san)
    )
    
    # Add event listener for page load
    window.events.loaded += inject_js
    
    # Start webview with persistent storage
    webview.start(
        private_mode=False,  # Disable private mode for persistent cookies
        storage_path="./data",  # Storage directory
        debug=not release_mode  # Enable dev tools unless in release mode
    )

if __name__ == "__main__":
    main()