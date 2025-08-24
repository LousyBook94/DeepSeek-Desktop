import ctypes
import platform

try:
    import winreg
except ImportError:
    winreg = None # Graceful fallback on non-Windows

def show_error_popup(title, message):
    """
    Displays a native Windows error popup dialog.
    This is a no-op on non-Windows platforms.
    """
    if platform.system() != "Windows":
        print(f"ERROR (non-Windows): {title} - {message}")
        return

    # MessageBoxW constants
    MB_OK = 0x00000000
    MB_ICONERROR = 0x00000010

    try:
        # Ensure ctypes and user32 are available
        if not hasattr(ctypes, 'windll') or not hasattr(ctypes.windll, 'user32'):
            print("Error: ctypes.windll.user32 not available.")
            return

        ctypes.windll.user32.MessageBoxW(
            None,
            str(message),
            str(title),
            MB_OK | MB_ICONERROR
        )
    except Exception as e:
        # Fallback if the popup fails for some reason
        print(f"Error displaying popup: {e}")
        print(f"Original message: {title} - {message}")

# --- Windows Startup Registry Functions ---

REGISTRY_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"

def _open_startup_key(access):
    """Helper to open the startup registry key."""
    if not winreg:
        raise OSError("winreg module not available.")
    return winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY_PATH, 0, access)

def add_to_startup(app_name, exe_path):
    """Adds the application to the Windows startup registry."""
    if platform.system() != "Windows":
        print("Run-on-startup is only available on Windows.")
        return
    try:
        with _open_startup_key(winreg.KEY_WRITE) as key:
            # The value should be the full path to the executable, enclosed in quotes
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, f'"{exe_path}"')
        print(f"'{app_name}' has been added to startup.")
    except OSError as e:
        print(f"Error adding to startup: {e}")
        show_error_popup("Startup Error", f"Could not add the application to startup.\n\nDetails: {e}")

def remove_from_startup(app_name):
    """Removes the application from the Windows startup registry."""
    if platform.system() != "Windows":
        print("Run-on-startup is only available on Windows.")
        return
    try:
        with _open_startup_key(winreg.KEY_WRITE) as key:
            winreg.DeleteValue(key, app_name)
        print(f"'{app_name}' has been removed from startup.")
    except FileNotFoundError:
        print(f"'{app_name}' was not found in startup items.")
    except OSError as e:
        print(f"Error removing from startup: {e}")
        show_error_popup("Startup Error", f"Could not remove the application from startup.\n\nDetails: {e}")

def is_in_startup(app_name):
    """Checks if the application is in the Windows startup registry."""
    if platform.system() != "Windows":
        return False
    try:
        with _open_startup_key(winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, app_name)
        return True
    except (FileNotFoundError, OSError):
        return False
