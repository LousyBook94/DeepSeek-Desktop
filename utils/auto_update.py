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
from datetime import datetime
from tqdm import tqdm
import logging

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
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))
        
def setup_logging(script_dir):
    """Set up logging to file and console"""
    log_path = os.path.join(script_dir, "update.log")
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_path, mode='w'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger()

def get_current_version(script_dir):
    """Reads the current version from the VERSION_FILE."""
    version_path = os.path.join(script_dir, VERSION_FILE)
    if os.path.exists(version_path):
        with open(version_path, 'r') as f:
            return f.read().strip()
    return "0.0.0"

def fetch_latest_version_with_retry(logger):
    """Fetches the latest release info from GitHub with retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            logger.debug(f"[Attempt {attempt+1}/{MAX_RETRIES}] Fetching release info from GitHub...")
            response = requests.get(REPO_URL, timeout=60)
            response.raise_for_status()
            release_info = response.json()
            
            latest_version = release_info.get("tag_name", "")
            if not latest_version:
                logger.error("Version tag not found in release.")
                raise ValueError("Version tag not found in release.")
                
            latest_version = latest_version.lstrip('v')
            return latest_version, release_info
        except Exception as e:
            error_msg = f"[{attempt + 1}/{MAX_RETRIES}] Failed to fetch release info: {e}"
            if 'response' in locals():
                error_msg += f"\nResponse status: {response.status_code}"
            logger.error(error_msg)
            
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                logger.error("All attempts to fetch release info failed")
                return None, None

def compare_versions(current, latest):
    """Compares two version strings. Returns True if current >= latest."""
    def parse_version(v):
        if '-' in v:
            core, prerelease = v.split('-', 1)
            return [int(x) for x in core.split('.')], prerelease
        return [int(x) for x in v.split('.')], None
    
    try:
        current_parts, current_prerelease = parse_version(current)
        latest_parts, latest_prerelease = parse_version(latest)
        
        max_len = max(len(current_parts), len(latest_parts))
        current_parts.extend([0] * (max_len - len(current_parts)))
        latest_parts.extend([0] * (max_len - len(latest_parts)))
        
        for cur, lat in zip(current_parts, latest_parts):
            if cur > lat:
                return True
            elif cur < lat:
                return False
        
        if current_prerelease is None and latest_prerelease is None:
            return True
        elif current_prerelease is None:
            return True
        elif latest_prerelease is None:
            return False
        else:
            return current_prerelease >= latest_prerelease
            
    except ValueError as e:
        print(f"Warning: Version parsing error: {e}. Assuming update needed.")
        return False

def bring_console_to_front():
    """Brings the console window to the front (Windows only)."""
    try:
        # Простой вызов PowerShell для активации консоли
        subprocess.run(
            ['powershell', '-Command', 'Write-Host "Bringing console to front..."'],
            check=True,
            capture_output=True,
            text=True
        )
    except Exception as e:
        print(f"Could not bring console to front: {e}")

def download_release_with_retry(asset_url, asset_name, logger):
    """Downloads the release zip with retry logic and progress."""
    temp_zip_path = os.path.join(TEMP_DIR, "update.zip")
    
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Downloading {asset_name}...")
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
                        if chunk:
                            f.write(chunk)
                            progress_bar.update(len(chunk))
            
            if os.path.exists(temp_zip_path) and os.path.getsize(temp_zip_path) > 0:
                logger.info("Download complete!")
                return temp_zip_path
            else:
                raise IOError("Downloaded file is empty or not found.")

        except Exception as e:
            logger.error(f"[{attempt + 1}/{MAX_RETRIES}] Download failed: {e}")
            if attempt < MAX_RETRIES - 1:
                logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                raise
    return None

def create_backup(script_dir, app_name, version):
    """Creates a backup of the current application and related files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir_name = f"backup_{version}_{timestamp}"
    backup_dir = os.path.join(script_dir, backup_dir_name)
    
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [app_name, VERSION_FILE, "deepseek.ico"]
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
            shutil.copytree(dir_path, dest_path)
            print(f"[*] Backed up: {dir_name}/")
            
    return backup_dir

def extract_and_install_update(zip_path, script_dir, app_name, logger):
    """Extracts the update and installs new files."""
    logger.info("Extracting update...")
    extract_to_dir = os.path.join(TEMP_DIR, "extracted")
    
    if os.path.exists(extract_to_dir):
        shutil.rmtree(extract_to_dir)
    os.makedirs(extract_to_dir, exist_ok=True)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to_dir)
        logger.info("Extraction successful!")
    except zipfile.BadZipFile:
        logger.error("Failed to extract the zip file (it might be corrupted).")
        return False

    logger.info("Installing new files...")
    
    # Copy all files from extracted directory
    for item in os.listdir(extract_to_dir):
        src_path = os.path.join(extract_to_dir, item)
        dest_path = os.path.join(script_dir, item)
        
        try:
            if os.path.isdir(src_path):
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.copytree(src_path, dest_path)
            else:
                shutil.copy2(src_path, dest_path)
            logger.info(f"Updated: {item}")
        except Exception as e:
            logger.error(f"Failed to update {item}: {e}")
            return False

    return True

def restore_backup(backup_dir, script_dir, app_name):
    """Restores files from a backup."""
    print(f"[~] Restoring from backup: {os.path.basename(backup_dir)}...")
    
    for item in os.listdir(backup_dir):
        src_path = os.path.join(backup_dir, item)
        dest_path = os.path.join(script_dir, item)
        
        try:
            if os.path.exists(dest_path):
                if os.path.isdir(dest_path):
                    shutil.rmtree(dest_path)
                else:
                    os.remove(dest_path)
                    
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path)
            else:
                shutil.copy2(src_path, dest_path)
            print(f"[+] Restored: {item}")
        except Exception as e:
            print(f"[-] Failed to restore {item}: {e}")

def main():
    parser = argparse.ArgumentParser(description="DeepSeek Desktop Auto-Updater")
    parser.add_argument("--auto", action="store_true", help="Run in auto mode (non-interactive).")
    parser.add_argument("--debug", action="store_true", help="Keep console open after update for debugging.")
    args = parser.parse_args()

    auto_mode = args.auto
    debug_mode = args.debug
    script_dir = get_script_directory()
    
    logger = setup_logging(script_dir)
    logger.info(f"Script directory: {script_dir}")
    
    os.makedirs(TEMP_DIR, exist_ok=True)
    logger.info(f"Temp directory: {TEMP_DIR}")

    # Check if application is running
    try:
        subprocess.check_output(
            f'tasklist /FI "IMAGENAME eq {APP_NAME}" /FO CSV | find "{APP_NAME}"', 
            shell=True, 
            stderr=subprocess.DEVNULL
        )
        logger.info(f"{APP_NAME} is running. Attempting to close...")
        subprocess.run(
            f'taskkill /F /IM "{APP_NAME}"', 
            shell=True, 
            check=True, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        time.sleep(3)
        logger.info(f"{APP_NAME} closed.")
    except subprocess.CalledProcessError:
        logger.info(f"{APP_NAME} is not running.")

    # Get current version
    current_version = get_current_version(script_dir)
    logger.info(f"Current version: {current_version}")

    # Fetch latest version
    latest_version, release_info = fetch_latest_version_with_retry(logger)
    if not latest_version:
        if auto_mode:
            sys.exit(0)
        else:
            print("[-] Could not fetch latest version. Exiting.")
            return
            
    logger.info(f"Latest version: {latest_version}")

    # Compare versions
    update_needed = not compare_versions(current_version, latest_version)
    logger.info(f"Update needed: {update_needed}")
    
    if not update_needed:
        print(f"[+] You already have the latest version ({current_version})!")
        app_path = os.path.join(script_dir, APP_NAME)
        if os.path.exists(app_path):
            logger.info(f"Starting {APP_NAME}...")
            subprocess.Popen([app_path])
        return

    print(f"[!] Update available: {current_version} -> {latest_version}")

    # Find Windows asset
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

    # Download asset
    try:
        zip_path = download_release_with_retry(
            asset_to_download["browser_download_url"], 
            asset_to_download["name"],
            logger
        )
        if not zip_path:
            print("[-] Failed to download the update.")
            if auto_mode:
                sys.exit(1)
            return
    except Exception as e:
        logger.error(f"Download error: {e}")
        if auto_mode:
            sys.exit(1)
        return

    # Auto mode confirmation
    user_input = None
    if auto_mode:
        bring_console_to_front()
        print("\n[!] NEW VERSION AVAILABLE!")
        print(f"     Current: {current_version}")
        print(f"     Latest:  {latest_version}")
        print("\nYou have 30 seconds to respond...")
        print("If no response, update will proceed automatically.")
        print()

        start_time = time.time()
        while time.time() - start_time < 30:
            try:
                if msvcrt.kbhit():
                    user_input = msvcrt.getch().decode('utf-8').lower()
                    if user_input in ['y', 'n']:
                        break
                    else:
                        print("\nInvalid input. Please press Y or N.", end="", flush=True)
            except:
                pass
            time.sleep(0.1)

        if user_input == 'n':
            print("[*] Update cancelled by user.")
            sys.exit(0)
        elif user_input != 'y':
            print("[*] No response received. Auto-proceeding with update...")

    # Create backup
    backup_dir = create_backup(script_dir, APP_NAME, current_version)
    
    # Install update
    try:
        if extract_and_install_update(zip_path, script_dir, APP_NAME, logger):
            with open(os.path.join(script_dir, VERSION_FILE), 'w') as f:
                f.write(latest_version)
            logger.info(f"Updated version to: {latest_version}")
            print("\n[+] Update installed successfully!")
        else:
            print("[-] Update failed. Restoring backup...")
            restore_backup(backup_dir, script_dir, APP_NAME)
            if auto_mode:
                sys.exit(1)
            return
    except Exception as e:
        logger.error(f"Critical error during update: {e}")
        print("[-] Restoring backup...")
        restore_backup(backup_dir, script_dir, APP_NAME)
        if auto_mode:
            sys.exit(1)
        return

    # Start application
    app_path = os.path.join(script_dir, APP_NAME)
    if os.path.exists(app_path):
        logger.info(f"Starting {APP_NAME}...")
        subprocess.Popen([app_path])
        print("\n*** UPDATE COMPLETED SUCCESSFULLY! ***")
        print(f"*** Version: {current_version} -> {latest_version} ***")
    else:
        logger.error("Application executable not found after update.")
        restore_backup(backup_dir, script_dir, APP_NAME)
        if auto_mode:
            sys.exit(1)

    # Cleanup
    logger.info("Cleaning up temporary files...")
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    logger.info("Cleanup complete. Exiting.")

if __name__ == "__main__":
    try:
        import msvcrt
        main()
    except ImportError:
        print("msvcrt module not found. Auto mode interactive prompt may not work correctly.")
        main()
    except KeyboardInterrupt:
        print("\n[-] Update cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[-] An unexpected error occurred: {e}")
        sys.exit(1)