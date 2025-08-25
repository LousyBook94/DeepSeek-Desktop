import os
import sys
import shutil
import tempfile
import zipfile
import requests
import json
import subprocess
import time
import re
import argparse
import platform
import ctypes
from datetime import datetime
from packaging import version
from tqdm import tqdm
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.windows import show_error_popup

# --- Configuration ---
APP_NAME = "DeepSeekChat.exe"
REPO_URL = "https://api.github.com/repos/LousyBook94/DeepSeek-Desktop/releases/latest"
VERSION_FILE = "version.txt"
TEMP_DIR = os.path.join(tempfile.gettempdir(), "DeepSeekUpdate")
MAX_RETRIES = 5
RETRY_DELAY = 5

def get_script_directory():
    """Returns the directory where the script is located."""
    if getattr(sys, 'frozen', False):
        # Running as a PyInstaller executable
        return os.path.dirname(sys.executable)
    else:
        # Running as a script
        return os.path.dirname(os.path.abspath(__file__))

def get_current_version(script_dir):
    """Reads the current version from the VERSION_FILE."""
    version_path = os.path.join(script_dir, VERSION_FILE)
    if os.path.exists(version_path):
        with open(version_path, 'r') as f:
            return f.read().strip()
    return "0.0.0"

def fetch_latest_version_with_retry():
    """Fetches the latest release info from GitHub with retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(REPO_URL, timeout=30)
            response.raise_for_status()
            release_info = response.json()
            latest_version = release_info.get("tag_name", "").lstrip('v')
            if not latest_version:
                raise ValueError("Version tag not found in release.")
            return latest_version, release_info
        except Exception as e:
            print(f"[{attempt + 1}/{MAX_RETRIES}] Failed to fetch release info: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                return None, None

def compare_versions(current, latest):
    """Compares two version strings using the 'packaging' library."""
    try:
        # Returns True if current version is same or newer than latest
        return version.parse(current) >= version.parse(latest)
    except version.InvalidVersion as e:
        print(f"Warning: Could not parse version string. Assuming update is needed. Error: {e}")
        return False

def bring_console_to_front():
    """Brings the console window to the front using ctypes (Windows only)."""
    if platform.system() != 'Windows':
        return

    try:
        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32

        # Get the handle to the console window
        console_hwnd = kernel32.GetConsoleWindow()
        if console_hwnd == 0:
            return # No console window found

        # Constants for ShowWindow
        SW_SHOWNORMAL = 1

        # Bring the window to the front
        user32.ShowWindow(console_hwnd, SW_SHOWNORMAL)
        user32.SetForegroundWindow(console_hwnd)

        # A small delay to ensure it comes to the front
        time.sleep(0.5)

    except Exception as e:
        print(f"Could not bring console to front: {e}")

def download_release_with_retry(asset_url, asset_name):
    """Downloads the release zip with retry logic and progress."""
    temp_zip_path = os.path.join(TEMP_DIR, "update.zip")
    
    for attempt in range(MAX_RETRIES):
        try:
            print(f"Downloading {asset_name}...")
            with requests.get(asset_url, stream=True, timeout=60) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                
                with open(temp_zip_path, 'wb') as f, tqdm(
                    total=total_size,
                    unit='iB',
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=asset_name,
                    ascii=True
                ) as progress_bar:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        progress_bar.update(len(chunk))
            
            if os.path.exists(temp_zip_path) and os.path.getsize(temp_zip_path) > 0:
                print("\nDownload complete!")
                return temp_zip_path
            else:
                raise IOError("Downloaded file is empty or not found.")

        except requests.exceptions.RequestException as e:
            print(f"\n[{attempt + 1}/{MAX_RETRIES}] Download failed: {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                raise
    return None

def create_backup(script_dir, app_name, version):
    """Creates a backup of the current application and related files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir_name = f"backup_{timestamp}"
    backup_dir = os.path.join(script_dir, backup_dir_name)
    
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [app_name, VERSION_FILE]
    dirs_to_backup = ["injection"]

    print(f"[*] Creating backup in {backup_dir_name}...")
    
    for item_name in files_to_backup:
        item_path = os.path.join(script_dir, item_name)
        if os.path.exists(item_path):
            shutil.copy2(item_path, os.path.join(backup_dir, item_name))
            print(f"[*] Backed up: {item_name}")

    for dir_name in dirs_to_backup:
        dir_path = os.path.join(script_dir, dir_name)
        if os.path.exists(dir_path):
            dest_path = os.path.join(backup_dir, dir_name)
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)
            shutil.copytree(dir_path, dest_path)
            print(f"[*] Backed up: {dir_name}/")
            
    return backup_dir

def extract_and_install_update(zip_path, script_dir, app_name):
    """Extracts the update and installs new files."""
    print("[*] Extracting update...")
    extract_to_dir = os.path.join(TEMP_DIR, "extracted")
    os.makedirs(extract_to_dir, exist_ok=True)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to_dir)
        print("[+] Extraction successful!")
    except zipfile.BadZipFile:
        print("[-] Error: Failed to extract the zip file (it might be corrupted).")
        return False

    print("[*] Installing new files...")
    # Copy executable
    src_exe = os.path.join(extract_to_dir, app_name)
    dest_exe = os.path.join(script_dir, app_name)
    if os.path.exists(src_exe):
        shutil.move(src_exe, dest_exe)
        print(f"[+] Updated: {app_name}")
    else:
        print(f"[-] Warning: {app_name} not found in update package.")
        return False

    # Copy injection folder
    src_injection = os.path.join(extract_to_dir, "injection")
    dest_injection = os.path.join(script_dir, "injection")
    if os.path.exists(src_injection):
        if os.path.exists(dest_injection):
            shutil.rmtree(dest_injection)
        shutil.move(src_injection, dest_injection)
        print("[+] Updated: injection/")
    
    # Copy icon
    src_icon = os.path.join(extract_to_dir, "deepseek.ico")
    dest_icon = os.path.join(script_dir, "deepseek.ico")
    if os.path.exists(src_icon):
        shutil.move(src_icon, dest_icon)
        print("[+] Updated: deepseek.ico")

    return True

def restore_backup(backup_dir, script_dir, app_name):
    """Restores files from a backup."""
    print(f"[~] Restoring from backup: {os.path.basename(backup_dir)}...")
    
    # Restore executable
    src_exe = os.path.join(backup_dir, app_name)
    dest_exe = os.path.join(script_dir, app_name)
    if os.path.exists(src_exe):
        shutil.move(src_exe, dest_exe)
        print(f"[+] Restored: {app_name}")

    # Restore injection folder
    src_injection = os.path.join(backup_dir, "injection")
    dest_injection = os.path.join(script_dir, "injection")
    if os.path.exists(src_injection):
        if os.path.exists(dest_injection):
            shutil.rmtree(dest_injection)
        shutil.move(src_injection, dest_injection)
        print("[+] Restored: injection/")
        
    # Restore version file
    src_version = os.path.join(backup_dir, VERSION_FILE)
    dest_version = os.path.join(script_dir, VERSION_FILE)
    if os.path.exists(src_version):
        shutil.move(src_version, dest_version)
        print("[+] Restored: version.txt")

def main():
    parser = argparse.ArgumentParser(description="DeepSeek Desktop Auto-Updater")
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Run in auto mode (non-interactive)."
    )
    args = parser.parse_args()

    auto_mode = args.auto
    script_dir = get_script_directory()
    print(f"Script directory: {script_dir}")
    
    # Ensure TEMP_DIR exists
    os.makedirs(TEMP_DIR, exist_ok=True)

    # Step 1: Check if application is running
    if not auto_mode:
        print("[1/6] >> Checking if application is running...")
    try:
        # Check if the process is running
        subprocess.check_output(f'tasklist /FI "IMAGENAME eq {APP_NAME}" /FO CSV | find "{APP_NAME}"', shell=True, stderr=subprocess.DEVNULL)
        if not auto_mode:
            print(f"[*] {APP_NAME} is running. Attempting to close...")
        subprocess.run(f'taskkill /F /IM "{APP_NAME}"', shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3) # Wait for process to terminate
        if not auto_mode:
            print(f"[+] {APP_NAME} closed.")
    except subprocess.CalledProcessError:
        if not auto_mode:
            print(f"[+] {APP_NAME} is not running.")

    # Step 2: Get current version
    if not auto_mode:
        print("\n[2/6] >> Checking current version...")
    current_version = get_current_version(script_dir)
    if not auto_mode:
        print(f"[*] Current version: {current_version}")

    # Step 3: Fetch latest version
    if not auto_mode:
        print("\n[3/6] >> Fetching latest release information...")
    try:
        latest_version, release_info = fetch_latest_version_with_retry()
        if not latest_version:
            if auto_mode:
                sys.exit(0) # Silently exit if no version found in auto mode
            else:
                print("[-] Could not fetch latest version. Exiting.")
                return
        if not auto_mode:
            print(f"[*] Latest version: {latest_version}")
    except Exception as e:
        print(f"[-] Error fetching release info: {e}")
        if auto_mode:
            sys.exit(1)
        return

    # Step 4: Compare versions
    if not auto_mode:
        print("\n[4/6] >> Comparing versions...")
    if compare_versions(current_version, latest_version):
        if not auto_mode:
            print(f"[+] You already have the latest version ({current_version})!")
        # In auto mode, if no update, just exit
        if auto_mode:
            sys.exit(0)
        else:
            # Still open the app if it was running or closed by us
            app_path = os.path.join(script_dir, APP_NAME)
            if os.path.exists(app_path):
                print(f"[+] Starting {APP_NAME}...")
                subprocess.Popen([app_path])
            return

    if not auto_mode:
        print(f"[!] Update available: {current_version} -> {latest_version}")

    # Step 5: Download and install update
    if not auto_mode:
        print("\n[5/6] >> Downloading and installing update...")
    elif auto_mode:
        # In auto mode, bring console to front only if an update is found
        bring_console_to_front()
        print("\n[!] NEW VERSION AVAILABLE!")
        print(f"     Current: {current_version}")
        print(f"     Latest:  {latest_version}")
        print("\nYou have 30 seconds to respond...")
        print("If no response, update will proceed automatically.")
        print()

    asset_to_download = None
    if release_info and "assets" in release_info:
        for asset in release_info["assets"]:
            if "windows.zip" in asset["name"].lower():
                asset_to_download = asset
                break
    
    if not asset_to_download:
        print("[-] Error: Windows release asset not found.")
        if auto_mode:
            sys.exit(1)
        return

    try:
        zip_path = download_release_with_retry(asset_to_download["browser_download_url"], asset_to_download["name"])
        if not zip_path:
            print("[-] Failed to download the update.")
            if auto_mode:
                sys.exit(1)
            return
    except Exception as e:
        print(f"[-] Download error: {e}")
        if auto_mode:
            sys.exit(1)
        return

    if auto_mode:
        print("[*] Auto-proceeding with update...")

    # Create backup before installing
    backup_dir = create_backup(script_dir, APP_NAME, current_version)
    
    # Extract and install
    if extract_and_install_update(zip_path, script_dir, APP_NAME):
        # Update version file
        version_file_path = os.path.join(script_dir, VERSION_FILE)
        with open(version_file_path, 'w') as f:
            f.write(latest_version)
        print(f"[+] Updated version to: {latest_version}")
        print("\n[+] Update installed successfully!")
    else:
        print("[-] Update failed. Restoring backup...")
        restore_backup(backup_dir, script_dir, APP_NAME)
        if auto_mode:
            sys.exit(1)
        return

    # Step 6: Start application
    if not auto_mode:
        print("\n[6/6] >> Starting application...")
        app_path = os.path.join(script_dir, APP_NAME)
        if os.path.exists(app_path):
            print(f"[+] Starting {APP_NAME}...")
            subprocess.Popen([app_path])
            print("\n*** UPDATE COMPLETED SUCCESSFULLY! ***")
            print(f"*** Version: {current_version} -> {latest_version} ***")
            print("*** Enjoy your updated DeepSeek Desktop! ***")
        else:
            print("[-] Error: Application executable not found after update.")
            restore_backup(backup_dir, script_dir, APP_NAME)
    else: # auto_mode
        app_path = os.path.join(script_dir, APP_NAME)
        if os.path.exists(app_path):
            print(f"[+] Starting {APP_NAME} automatically...")
            subprocess.Popen([app_path])
            print("\n*** UPDATE COMPLETED SUCCESSFULLY! ***")
            print(f"*** Version: {current_version} -> {latest_version} ***")
        else:
            print("[-] Error: Application executable not found after update.")
            restore_backup(backup_dir, script_dir, APP_NAME)
            sys.exit(1)

    # Cleanup
    print("\n[*] Cleaning up temporary files...")
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    print("[+] Cleanup complete. Exiting.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[-] Update cancelled by user.")
        sys.exit(1)
    except Exception as e:
        error_message = f"An unexpected error occurred during the update process.\n\nDetails: {e}"
        print(f"\n[-] {error_message}")
        show_error_popup("Auto-Update Failed", error_message)
        sys.exit(1)