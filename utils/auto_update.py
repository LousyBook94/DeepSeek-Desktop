import os
import sys
import shutil
import tempfile
import zipfile
import requests
import subprocess
import time
import argparse
from datetime import datetime
import logging
from typing import Optional, Tuple, Dict, Any

# Try to import Rich for enhanced UI, but provide fallbacks
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.table import Table
    from rich.text import Text
    from rich import box

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# --- Configuration ---
APP_NAME = "DeepSeekChat.exe"
REPO_URL = "https://api.github.com/repos/LousyBook94/DeepSeek-Desktop/releases/latest"
VERSION_FILE = "version.py"
TEMP_DIR = os.path.join(tempfile.gettempdir(), "DeepSeekUpdate")
MAX_RETRIES = 3
RETRY_DELAY = 2

# Initialize console (Rich or fallback)
if RICH_AVAILABLE:
    # Handle Windows encoding issues
    try:
        console = Console()
    except Exception:
        # Fallback to simple console if Rich fails
        RICH_AVAILABLE = False

        class Console:
            def print(self, *args, **kwargs):
                # Remove Rich markup for fallback
                text = str(args[0]) if args else ""
                # Simple replacements for common Rich markup
                text = text.replace("[green]", "").replace("[/green]", "")
                text = text.replace("[red]", "").replace("[/red]", "")
                text = text.replace("[yellow]", "").replace("[/yellow]", "")
                text = text.replace("[blue]", "").replace("[/blue]", "")
                text = text.replace("[bold]", "").replace("[/bold]", "")
                print(text)

        console = Console()
else:

    class Console:
        def print(self, *args, **kwargs):
            # Remove Rich markup for fallback
            text = str(args[0]) if args else ""
            # Simple replacements for common Rich markup
            text = text.replace("[green]", "").replace("[/green]", "")
            text = text.replace("[red]", "").replace("[/red]", "")
            text = text.replace("[yellow]", "").replace("[/yellow]", "")
            text = text.replace("[blue]", "").replace("[/blue]", "")
            text = text.replace("[bold]", "").replace("[/bold]", "")
            print(text)

    console = Console()


def get_script_directory() -> str:
    """Returns the directory where the script is located."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


def setup_logging(script_dir: str) -> logging.Logger:
    """Set up logging to file and console"""
    log_path = os.path.join(script_dir, "update.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_path, mode="w", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return logging.getLogger()


def get_current_version(script_dir: str) -> str:
    """Reads the current version from the version.py file bundled with the application."""
    try:
        # Try to import version module directly
        # This works for both script and frozen executables
        import version
        return version.__version__
    except ImportError as e:
        console.print(f"[red]Error importing version module: {e}[/red]")
        # Fallback: try to read version.py as file
        try:
            # For PyInstaller bundled app, files are in _MEIPASS
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
                version_path = os.path.join(bundle_dir, "version.py")
            else:
                # Running as script
                version_path = os.path.join(script_dir, "version.py")
                if not os.path.exists(version_path):
                    # If not found in script_dir, try to find it in the parent directory
                    # This handles cases where the updater is in a subdirectory
                    version_path = os.path.join(os.path.dirname(script_dir), "version.py")

            if os.path.exists(version_path):
                # Read the version.py file directly
                with open(version_path, "r") as f:
                    content = f.read()

                # Extract the version using regex
                import re

                version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
                if version_match:
                    return version_match.group(1)
                else:
                    console.print(
                        "[red]Error: Could not find __version__ in version.py[/red]"
                    )
            else:
                console.print(f"[red]Error: version.py not found at {version_path}[/red]")
        except Exception as e:
            console.print(f"[red]Error reading version from version.py: {e}[/red]")
    return "0.0.0"


def fetch_latest_version_with_retry(
    logger: logging.Logger,
) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """Fetches the latest release info from GitHub with retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            logger.debug(
                f"[Attempt {attempt+1}/{MAX_RETRIES}] Fetching release info from GitHub..."
            )
            response = requests.get(REPO_URL, timeout=30)
            response.raise_for_status()
            release_info = response.json()

            latest_version = release_info.get("tag_name", "")
            if not latest_version:
                logger.error("Version tag not found in release.")
                raise ValueError("Version tag not found in release.")

            latest_version = latest_version.lstrip("v")
            console.print("[green][SUCCESS][/green] Successfully fetched version info")
            return latest_version, release_info
        except Exception as e:
            logger.error(
                f"[{attempt + 1}/{MAX_RETRIES}] Failed to fetch release info: {e}"
            )

            if attempt < MAX_RETRIES - 1:
                console.print(
                    f"[yellow][WARN][/yellow] Retrying in {RETRY_DELAY} seconds..."
                )
                time.sleep(RETRY_DELAY)
            else:
                console.print(
                    "[red][ERROR][/red] All attempts to fetch release info failed"
                )
                return None, None


def parse_version(version: str) -> Tuple[list, Optional[str]]:
    """Parse version string into components."""
    if "-" in version:
        core, prerelease = version.split("-", 1)
        return [int(x) for x in core.split(".")], prerelease
    return [int(x) for x in version.split(".")], None


def compare_versions(current: str, latest: str) -> bool:
    """Compares two version strings. Returns True if current >= latest."""
    try:
        current_parts, current_prerelease = parse_version(current)
        latest_parts, latest_prerelease = parse_version(latest)

        # Pad shorter version with zeros
        max_len = max(len(current_parts), len(latest_parts))
        current_parts.extend([0] * (max_len - len(current_parts)))
        latest_parts.extend([0] * (max_len - len(latest_parts)))

        # Compare version parts
        for cur, lat in zip(current_parts, latest_parts):
            if cur > lat:
                return True
            elif cur < lat:
                return False

        # Handle prerelease versions
        if current_prerelease is None and latest_prerelease is None:
            return True
        elif current_prerelease is None:
            return True  # Stable > prerelease
        elif latest_prerelease is None:
            return False  # Prerelease < stable
        else:
            return current_prerelease >= latest_prerelease

    except (ValueError, IndexError) as e:
        console.print(
            f"[yellow]Warning: Version parsing error: {e}. Assuming update needed.[/yellow]"
        )
        return False


def download_file(url: str, destination: str, logger: logging.Logger) -> bool:
    """Download file with progress indication."""
    try:
        with requests.get(url, stream=True, timeout=60) as response:
            response.raise_for_status()
            total_size = int(response.headers.get("content-length", 0))

            with open(destination, "wb") as file:
                if total_size > 0 and RICH_AVAILABLE:
                    # Use Rich progress bar
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        BarColumn(),
                        TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
                        console=console,
                    ) as progress:
                        task = progress.add_task(
                            "[cyan]Downloading...", total=total_size
                        )

                        downloaded = 0
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                file.write(chunk)
                                downloaded += len(chunk)
                                progress.update(task, advance=len(chunk))
                else:
                    # Simple download without progress
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)

            return os.path.exists(destination) and os.path.getsize(destination) > 0
    except Exception as e:
        logger.error(f"Download failed: {e}")
        console.print(f"[red][ERROR][/red] Download failed: {e}")
        return False


def download_release_with_retry(
    asset_url: str, asset_name: str, logger: logging.Logger
) -> Optional[str]:
    """Downloads the release zip with retry logic."""
    temp_zip_path = os.path.join(TEMP_DIR, "update.zip")

    for attempt in range(MAX_RETRIES):
        try:
            console.print(f"[bold blue]Downloading {asset_name}...[/bold blue]")

            if download_file(asset_url, temp_zip_path, logger):
                console.print("[green][SUCCESS][/green] Download complete!")
                return temp_zip_path
            else:
                raise IOError("Downloaded file is empty or not found.")

        except Exception as e:
            logger.error(f"[{attempt + 1}/{MAX_RETRIES}] Download failed: {e}")
            console.print(f"[red][ERROR][/red] Download failed: {e}")

            if attempt < MAX_RETRIES - 1:
                console.print(
                    f"[yellow][WARN][/yellow] Retrying in {RETRY_DELAY} seconds..."
                )
                time.sleep(RETRY_DELAY)
            else:
                console.print("[red][ERROR][/red] All download attempts failed")
                return None
    return None


def create_backup(script_dir: str, app_name: str, version: str) -> str:
    """Creates a backup of the current application and related files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir_name = f"backup_{version}_{timestamp}"
    backup_dir = os.path.join(script_dir, backup_dir_name)

    os.makedirs(backup_dir, exist_ok=True)

    files_to_backup = [app_name, VERSION_FILE, "deepseek.ico"]
    dirs_to_backup = ["injection"]

    console.print(
        Panel(
            f"[bold blue]Creating backup in {backup_dir_name}...[/bold blue]",
            border_style="blue",
        )
    )

    if RICH_AVAILABLE:
        backup_table = Table(show_header=True, header_style="bold magenta")
        backup_table.add_column("Item", style="cyan")
        backup_table.add_column("Status", style="green")
    else:
        console.print("Backup Status:")

    for item_name in files_to_backup:
        item_path = os.path.join(script_dir, item_name)
        if os.path.exists(item_path):
            try:
                shutil.copy2(item_path, os.path.join(backup_dir, item_name))
                if RICH_AVAILABLE:
                    backup_table.add_row(item_name, "[SUCCESS] Backed up")
                else:
                    console.print(f"  {item_name}: [SUCCESS] Backed up")
            except Exception as e:
                if RICH_AVAILABLE:
                    backup_table.add_row(item_name, f"[ERROR] Failed: {str(e)}")
                else:
                    console.print(f"  {item_name}: [ERROR] Failed: {str(e)}")
        else:
            if RICH_AVAILABLE:
                backup_table.add_row(item_name, "[ERROR] Not found")
            else:
                console.print(f"  {item_name}: [ERROR] Not found")

    for dir_name in dirs_to_backup:
        dir_path = os.path.join(script_dir, dir_name)
        if os.path.exists(dir_path):
            try:
                dest_path = os.path.join(backup_dir, dir_name)
                shutil.copytree(dir_path, dest_path)
                if RICH_AVAILABLE:
                    backup_table.add_row(f"{dir_name}/", "[SUCCESS] Backed up")
                else:
                    console.print(f"  {dir_name}/: [SUCCESS] Backed up")
            except Exception as e:
                if RICH_AVAILABLE:
                    backup_table.add_row(f"{dir_name}/", f"[ERROR] Failed: {str(e)}")
                else:
                    console.print(f"  {dir_name}/: [ERROR] Failed: {str(e)}")
        else:
            if RICH_AVAILABLE:
                backup_table.add_row(f"{dir_name}/", "[ERROR] Not found")
            else:
                console.print(f"  {dir_name}/: [ERROR] Not found")

    if RICH_AVAILABLE:
        console.print(backup_table)
    return backup_dir


def extract_and_install_update(
    zip_path: str, script_dir: str, app_name: str, logger: logging.Logger
) -> bool:
    """Extracts the update and installs new files."""
    console.print("[bold yellow]Extracting update...[/bold yellow]")
    extract_to_dir = os.path.join(TEMP_DIR, "extracted")

    # Clean up previous extraction
    if os.path.exists(extract_to_dir):
        shutil.rmtree(extract_to_dir)
    os.makedirs(extract_to_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_to_dir)
        console.print("[green][SUCCESS][/green] Extraction successful!")
    except zipfile.BadZipFile as e:
        logger.error(f"Failed to extract the zip file: {e}")
        console.print("[red][ERROR][/red] Failed to extract the zip file")
        return False

    console.print("[bold yellow]Installing new files...[/bold yellow]")

    # Prepare status tracking
    if RICH_AVAILABLE:
        update_table = Table(show_header=True, header_style="bold magenta")
        update_table.add_column("File/Folder", style="cyan")
        update_table.add_column("Status", style="green")
    else:
        console.print("Update Status:")

    success_count = 0
    total_count = 0

    # Copy all files from extracted directory
    for item in os.listdir(extract_to_dir):
        total_count += 1
        src_path = os.path.join(extract_to_dir, item)
        dest_path = os.path.join(script_dir, item)

        try:
            # Remove existing file/directory
            if os.path.exists(dest_path):
                if os.path.isdir(dest_path):
                    shutil.rmtree(dest_path)
                else:
                    os.remove(dest_path)

            # Copy new file/directory
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path)
            else:
                shutil.copy2(src_path, dest_path)

            logger.info(f"Updated: {item}")
            if RICH_AVAILABLE:
                update_table.add_row(item, "[SUCCESS] Updated")
            else:
                console.print(f"  {item}: [SUCCESS] Updated")
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to update {item}: {e}")
            if RICH_AVAILABLE:
                update_table.add_row(item, f"[ERROR] Failed: {str(e)}")
            else:
                console.print(f"  {item}: [ERROR] Failed: {str(e)}")

    if RICH_AVAILABLE:
        console.print(update_table)

    if success_count == total_count:
        console.print(
            f"[green][SUCCESS][/green] Successfully updated {success_count} items"
        )
        return True
    else:
        console.print(
            f"[red][ERROR][/red] Failed to update {total_count - success_count} out of {total_count} items"
        )
        return False


def restore_backup(backup_dir: str, script_dir: str, app_name: str):
    """Restores files from a backup."""
    console.print(
        Panel(
            f"[bold blue]Restoring from backup: {os.path.basename(backup_dir)}...[/bold blue]",
            border_style="blue",
        )
    )

    if RICH_AVAILABLE:
        restore_table = Table(show_header=True, header_style="bold magenta")
        restore_table.add_column("Item", style="cyan")
        restore_table.add_column("Status", style="green")
    else:
        console.print("Restore Status:")

    for item in os.listdir(backup_dir):
        src_path = os.path.join(backup_dir, item)
        dest_path = os.path.join(script_dir, item)

        try:
            # Remove existing file/directory
            if os.path.exists(dest_path):
                if os.path.isdir(dest_path):
                    shutil.rmtree(dest_path)
                else:
                    os.remove(dest_path)

            # Copy from backup
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path)
            else:
                shutil.copy2(src_path, dest_path)

            if RICH_AVAILABLE:
                restore_table.add_row(item, "[SUCCESS] Restored")
            else:
                console.print(f"  {item}: [SUCCESS] Restored")
        except Exception as e:
            if RICH_AVAILABLE:
                restore_table.add_row(item, f"[ERROR] Failed: {str(e)}")
            else:
                console.print(f"  {item}: [ERROR] Failed: {str(e)}")

    if RICH_AVAILABLE:
        console.print(restore_table)


def close_application(app_name: str, logger: logging.Logger) -> bool:
    """Close the running application before updating."""
    try:
        # Check if application is running
        result = subprocess.run(
            f'tasklist /FI "IMAGENAME eq {app_name}" /FO CSV',
            shell=True,
            capture_output=True,
            text=True,
        )

        if app_name in result.stdout:
            logger.info(f"{app_name} is running. Attempting to close...")
            console.print(
                f"[yellow]i[/yellow] Closing {app_name} to perform the update..."
            )

            # Force close the application
            subprocess.run(
                f'taskkill /F /IM "{app_name}"',
                shell=True,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # Wait for process to terminate
            time.sleep(2)
            logger.info(f"{app_name} closed.")
            return True
        else:
            logger.info(f"{app_name} is not running.")
            return True
    except subprocess.CalledProcessError as e:
        logger.warning(f"Failed to close {app_name}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error checking/closing application: {e}")
        return False


def find_update_asset(release_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Find the Windows asset in the release."""
    if not release_info or "assets" not in release_info:
        return None

    for asset in release_info["assets"]:
        if "windows.zip" in asset["name"].lower():
            return asset

    return None


def main():
    parser = argparse.ArgumentParser(description="DeepSeek Desktop Auto-Updater")
    parser.add_argument(
        "--auto", action="store_true", help="Run in auto mode (non-interactive)."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Keep console open after update for debugging.",
    )
    args = parser.parse_args()

    auto_mode = args.auto
    debug_mode = args.debug
    script_dir = get_script_directory()

    logger = setup_logging(script_dir)
    logger.info(f"Script directory: {script_dir}")

    os.makedirs(TEMP_DIR, exist_ok=True)
    logger.info(f"Temp directory: {TEMP_DIR}")

    # Get current version
    current_version = get_current_version(script_dir)
    logger.info(f"Current version: {current_version}")

    # Fetch latest version
    latest_version, release_info = fetch_latest_version_with_retry(logger)
    if not latest_version:
        if auto_mode:
            sys.exit(0)
        else:
            console.print(
                Panel(
                    "[bold red]Could not fetch latest version. Exiting.[/bold red]",
                    border_style="red",
                )
            )
            return

    logger.info(f"Latest version: {latest_version}")

    # Compare versions
    update_needed = not compare_versions(current_version, latest_version)
    logger.info(f"Update needed: {update_needed}")

    # Display version information
    if RICH_AVAILABLE:
        version_table = Table(show_header=False, box=box.ROUNDED)
        version_table.add_column("Current Version", style="cyan")
        version_table.add_column("Latest Version", style="green")
        version_table.add_row(current_version, latest_version)
        console.print(
            Panel(version_table, title="Version Information", border_style="blue")
        )
    else:
        console.print(f"Current Version: {current_version}")
        console.print(f"Latest Version:  {latest_version}")

    if not update_needed:
        console.print(
            Panel(
                f"[bold green]You already have the latest version ({current_version})![/bold green]",
                border_style="green",
            )
        )
        logger.info("Application is up to date. No action needed.")
        if auto_mode:
            sys.exit(0)
        return

    console.print(
        Panel(
            f"[bold yellow]Update available: {current_version} -> {latest_version}[/bold yellow]",
            border_style="yellow",
        )
    )

    # Close the running application before updating
    if not close_application(APP_NAME, logger):
        console.print(
            Panel(
                "[bold red]Failed to close application. Update cancelled.[/bold red]",
                border_style="red",
            )
        )
        if auto_mode:
            sys.exit(1)
        return

    # Find Windows asset
    asset_to_download = find_update_asset(release_info)
    if not asset_to_download:
        console.print(
            Panel(
                "[bold red]Error: Windows release asset not found.[/bold red]",
                border_style="red",
            )
        )
        if auto_mode:
            sys.exit(1)
        return

    # Download asset
    try:
        zip_path = download_release_with_retry(
            asset_to_download["browser_download_url"], asset_to_download["name"], logger
        )
        if not zip_path:
            console.print(
                Panel(
                    "[bold red]Failed to download the update.[/bold red]",
                    border_style="red",
                )
            )
            if auto_mode:
                sys.exit(1)
            return
    except Exception as e:
        logger.error(f"Download error: {e}")
        console.print(
            Panel(f"[bold red]Download error: {e}[/bold red]", border_style="red")
        )
        if auto_mode:
            sys.exit(1)
        return

    # Create backup
    backup_dir = create_backup(script_dir, APP_NAME, current_version)

    # Install update
    update_success = False
    try:
        if extract_and_install_update(zip_path, script_dir, APP_NAME, logger):
            version_file_path = os.path.join(script_dir, VERSION_FILE)
            try:
                # ALWAYS update the version file to the latest version after successful update
                # This ensures the version is correct regardless of what was in the update archive
                with open(version_file_path, "w", encoding="utf-8") as f:
                    f.write(latest_version)
                logger.info(f"Updated version file to: {latest_version}")
                update_success = True

                # Display success message
                if RICH_AVAILABLE:
                    success_table = Table(show_header=False, box=box.ROUNDED)
                    success_table.add_column("Info", style="green")
                    success_table.add_row("Update installed successfully!")
                    success_table.add_row(
                        f"Version: {current_version} -> {latest_version}"
                    )
                    console.print(
                        Panel(
                            success_table, title="Update Complete", border_style="green"
                        )
                    )
                else:
                    console.print("Update installed successfully!")
                    console.print(f"Version: {current_version} -> {latest_version}")
            except Exception as e:
                logger.error(f"Failed to update version file: {e}")
                console.print(f"[red][ERROR][/red] Failed to update version file: {e}")
        else:
            console.print(
                Panel(
                    "[bold red]Update failed. Restoring backup...[/bold red]",
                    border_style="red",
                )
            )
    except Exception as e:
        logger.error(f"Critical error during update: {e}")
        console.print(
            Panel(
                "[bold red]Critical error during update. Restoring backup...[/bold red]",
                border_style="red",
            )
        )

    # Handle update failure
    if not update_success:
        restore_backup(backup_dir, script_dir, APP_NAME)
        if auto_mode:
            sys.exit(1)
        return

    # Start application if in auto mode
    if auto_mode:
        app_path = os.path.join(script_dir, APP_NAME)
        if os.path.exists(app_path):
            logger.info(f"Auto-mode: Starting {APP_NAME}...")
            try:
                subprocess.Popen([app_path], close_fds=True)

                # Display completion message
                if RICH_AVAILABLE:
                    completion_table = Table(show_header=False, box=box.ROUNDED)
                    completion_table.add_column("Info", style="cyan")
                    completion_table.add_row("UPDATE COMPLETED SUCCESSFULLY!")
                    completion_table.add_row(
                        f"Version: {current_version} -> {latest_version}"
                    )
                    console.print(
                        Panel(
                            completion_table,
                            title="Update Complete",
                            border_style="cyan",
                        )
                    )
                else:
                    console.print("UPDATE COMPLETED SUCCESSFULLY!")
                    console.print(f"Version: {current_version} -> {latest_version}")
            except Exception as e:
                logger.error(f"Failed to start application: {e}")
                console.print(f"[red][ERROR][/red] Failed to start application: {e}")
        else:
            logger.error("Application executable not found after update.")
            console.print(
                Panel(
                    "[bold red]Application executable not found after update.[/bold red]",
                    border_style="red",
                )
            )
            restore_backup(backup_dir, script_dir, APP_NAME)
            if auto_mode:
                sys.exit(1)

    # Cleanup
    logger.info("Cleaning up temporary files...")
    try:
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        logger.info("Cleanup complete. Exiting.")
    except Exception as e:
        logger.warning(f"Failed to clean up temporary files: {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print(
            Panel(
                "[bold yellow]Update cancelled by user.[/bold yellow]",
                border_style="yellow",
            )
        )
        sys.exit(1)
    except Exception as e:
        console.print(
            Panel(
                f"[bold red]An unexpected error occurred: {e}[/bold red]",
                border_style="red",
            )
        )
        sys.exit(1)
