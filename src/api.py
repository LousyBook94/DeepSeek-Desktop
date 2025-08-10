import sys
import subprocess

class Api:
    def __init__(self, window):
        self.window = window

    def toggle_always_on_top(self):
        if self.window:
            self.window.on_top = not self.window.on_top
            # The _log function is not available here, so we'll just print
            print(f"Always on top toggled {'on' if self.window.on_top else 'off'}")

    def open_new_window(self):
        # Relaunch the application in a new process, disabling the updater
        try:
            subprocess.Popen([sys.executable, sys.argv[0], '--no-updater'])
            print("New window requested.")
        except Exception as e:
            print(f"Failed to open new window: {e}")
