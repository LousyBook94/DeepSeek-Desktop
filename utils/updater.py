import os
import sys
import shutil
import tempfile
import zipfile
import requests
import json
import subprocess
import time
import logging
from datetime import datetime

# --- Configuration ---
APP_NAME = "DeepSeekChat.exe"
REPO_URL = "https://api.github.com/repos/LousyBook94/DeepSeek-Desktop/releases/latest"
VERSION_FILE = "version.txt"
TEMP_DIR = os.path.join(tempfile.gettempdir(), "DeepSeekUpdate")
MAX_RETRIES = 3
RETRY_DELAY = 5

def get_script_directory():
    """Returns the directory where the script is located."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        # In a non-frozen script, __file__ is utils/updater.py, so we need the parent directory
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Set up logging to file."""
    script_dir = get_script_directory()
    log_path = os.path.join(script_dir, "update.log")
    logger = logging.getLogger('updater')
    logger.setLevel(logging.DEBUG)

    # Avoid adding handlers multiple times
    if not logger.handlers:
        fh = logging.FileHandler(log_path, mode='w')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

logger = setup_logging()

def get_current_version():
    """Reads the current version from the VERSION_FILE."""
    script_dir = get_script_directory()
    version_path = os.path.join(script_dir, VERSION_FILE)
    if os.path.exists(version_path):
        with open(version_path, 'r') as f:
            return f.read().strip()
    return "0.0.0"

def compare_versions(current, latest):
    """Compares two version strings. Returns True if an update is needed."""
    def parse_version(v):
        if '-' in v:
            core, prerelease = v.split('-', 1)
            # a bit of a hack to handle pre-release tags
            return [int(x) for x in core.split('.')], prerelease
        return [int(x) for x in v.split('.')], "z" # 'z' is a placeholder for a stable release, which is > than any prerelease tag

    try:
        current_parts, current_prerelease = parse_version(current)
        latest_parts, latest_prerelease = parse_version(latest)

        if latest_parts > current_parts:
            return True
        elif latest_parts == current_parts:
            return latest_prerelease > current_prerelease
        else:
            return False

    except (ValueError, AttributeError) as e:
        logger.warning(f"Version parsing error: {e}. Assuming update needed.")
        return True

def check_for_updates():
    """Checks for the latest version and compares with the current one."""
    logger.info("Checking for updates...")
    current_version = get_current_version()
    logger.info(f"Current version: {current_version}")

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(REPO_URL, timeout=10)
            response.raise_for_status()
            release_info = response.json()

            latest_version_tag = release_info.get("tag_name", "").lstrip('v')
            if not latest_version_tag:
                raise ValueError("Version tag not found in release.")

            logger.info(f"Latest version found: {latest_version_tag}")

            update_needed = compare_versions(current_version, latest_version_tag)

            return {
                "update_needed": update_needed,
                "current_version": current_version,
                "latest_version": latest_version_tag,
                "release_info": release_info
            }

        except Exception as e:
            logger.error(f"Failed to fetch release info (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                return {"update_needed": False, "error": str(e)}

    return {"update_needed": False, "error": "Max retries reached"}


def download_update(release_info, progress_callback=None):
    """Downloads the release asset."""
    logger.info("Starting download...")

    asset_to_download = None
    if release_info and "assets" in release_info:
        for asset in release_info["assets"]:
            if "windows.zip" in asset["name"].lower():
                asset_to_download = asset
                break

    if not asset_to_download:
        logger.error("Windows release asset not found.")
        return None, "Windows release asset not found."

    asset_url = asset_to_download["browser_download_url"]
    asset_name = asset_to_download["name"]

    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    temp_zip_path = os.path.join(TEMP_DIR, "update.zip")

    try:
        with requests.get(asset_url, stream=True, timeout=60) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            downloaded = 0

            with open(temp_zip_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress)

        logger.info(f"Download complete: {asset_name}")
        return temp_zip_path, None

    except Exception as e:
        logger.error(f"Download failed: {e}")
        return None, str(e)


def install_update(zip_path, latest_version):
    """Installs the update and restarts the application."""
    script_dir = get_script_directory()
    logger.info(f"Starting installation from {zip_path} to {script_dir}")

    # 1. Close the running application
    try:
        subprocess.run(
            f'taskkill /F /IM "{APP_NAME}"',
            shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        logger.info(f"{APP_NAME} closed.")
        time.sleep(2) # Wait for the process to terminate
    except subprocess.CalledProcessError:
        logger.info(f"{APP_NAME} was not running.")
    except Exception as e:
        logger.error(f"Error closing {APP_NAME}: {e}")
        return False, f"Could not close the application: {e}"

    # 2. Create backup
    backup_dir = None
    try:
        current_version = get_current_version()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir_name = f"backup_{current_version}_{timestamp}"
        backup_dir = os.path.join(script_dir, backup_dir_name)
        os.makedirs(backup_dir, exist_ok=True)

        files_to_backup = [APP_NAME, VERSION_FILE, "deepseek.ico"]
        dirs_to_backup = ["injection", "utils"] # Also backup the utils dir

        for item in files_to_backup + dirs_to_backup:
            src_path = os.path.join(script_dir, item)
            if os.path.exists(src_path):
                dest_path = os.path.join(backup_dir, item)
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dest_path)
                else:
                    shutil.copy2(src_path, dest_path)
        logger.info(f"Backup created at {backup_dir}")
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return False, f"Backup failed: {e}"

    # 3. Extract and install
    extract_to_dir = os.path.join(TEMP_DIR, "extracted")
    try:
        if os.path.exists(extract_to_dir):
            shutil.rmtree(extract_to_dir)
        os.makedirs(extract_to_dir)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to_dir)

        for item in os.listdir(extract_to_dir):
            src_path = os.path.join(extract_to_dir, item)
            dest_path = os.path.join(script_dir, item)
            if os.path.isdir(src_path):
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.copytree(src_path, dest_path)
            else:
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                shutil.move(src_path, dest_path)
        logger.info("Update files installed.")

        # 4. Update version file
        with open(os.path.join(script_dir, VERSION_FILE), 'w') as f:
            f.write(latest_version)
        logger.info(f"Version updated to {latest_version}")

    except Exception as e:
        logger.error(f"Installation failed: {e}")
        # Restore backup
        if backup_dir:
            logger.info("Restoring backup...")
            try:
                for item in os.listdir(backup_dir):
                    src_path = os.path.join(backup_dir, item)
                    dest_path = os.path.join(script_dir, item)
                    if os.path.exists(dest_path):
                        if os.path.isdir(dest_path):
                            shutil.rmtree(dest_path)
                        else:
                            os.remove(dest_path)
                    if os.path.isdir(src_path):
                        shutil.copytree(src_path, dest_path)
                    else:
                        shutil.copy2(src_path, dest_path)
                logger.info("Backup restored.")
            except Exception as restore_e:
                logger.error(f"Backup restoration failed: {restore_e}")
        return False, f"Installation failed: {e}"

    # 5. Cleanup
    try:
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        logger.info("Temporary files cleaned up.")
    except Exception as e:
        logger.warning(f"Could not clean up temp files: {e}")

    # 6. Restart application
    try:
        app_path = os.path.join(script_dir, APP_NAME)
        if os.path.exists(app_path):
            logger.info(f"Restarting {APP_NAME}...")
            subprocess.Popen([app_path])
            # We need to exit the current process so the new one can run
            sys.exit(0)
        else:
            raise FileNotFoundError(f"{APP_NAME} not found after update.")
    except Exception as e:
        logger.error(f"Failed to restart application: {e}")
        return False, f"Failed to restart application: {e}"