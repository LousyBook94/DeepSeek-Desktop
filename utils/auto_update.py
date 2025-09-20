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
import logging
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn
from rich.table import Table
from rich.text import Text
from rich.prompt import Confirm
from rich.layout import Layout
from rich.live import Live
from rich.align import Align
from rich import box

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
        
# Initialize Rich console
console = Console()

class AutoUpdater:
    """Auto-updater class for DeepSeek Desktop with callback support"""
    
    def __init__(self, script_dir=None, callback=None):
        self.script_dir = script_dir or get_script_directory()
        self.callback = callback
        self.logger = self._setup_logging()
        self.logger.info(f"AutoUpdater initialized with script directory: {self.script_dir}")
        
    def _setup_logging(self):
        """Set up logging to file and console"""
        log_path = os.path.join(self.script_dir, "update.log")
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_path, mode='w'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger()
    
    def _emit_callback(self, event_type, data=None):
        """Emit callback event if callback is provided"""
        if self.callback:
            try:
                self.callback(event_type, data)
            except Exception as e:
                self.logger.error(f"Callback error: {e}")
    
    def get_current_version(self):
        """Reads the current version from the VERSION_FILE."""
        version_path = os.path.join(self.script_dir, VERSION_FILE)
        if os.path.exists(version_path):
            with open(version_path, 'r') as f:
                return f.read().strip()
        return "0.0.0"
    
    def fetch_latest_version_with_retry(self):
        """Fetches the latest release info from GitHub with retry logic."""
        self._emit_callback('fetching_version', {'status': 'starting'})
        
        for attempt in range(MAX_RETRIES):
            try:
                self.logger.debug(f"[Attempt {attempt+1}/{MAX_RETRIES}] Fetching release info from GitHub...")
                response = requests.get(REPO_URL, timeout=60)
                response.raise_for_status()
                release_info = response.json()
                
                latest_version = release_info.get("tag_name", "")
                if not latest_version:
                    self.logger.error("Version tag not found in release.")
                    raise ValueError("Version tag not found in release.")
                    
                latest_version = latest_version.lstrip('v')
                console.print(f"[green]✓[/green] Successfully fetched version info")
                self._emit_callback('version_fetched', {'version': latest_version, 'release_info': release_info})
                return latest_version, release_info
            except Exception as e:
                error_msg = f"[{attempt + 1}/{MAX_RETRIES}] Failed to fetch release info: {e}"
                try:
                    if 'response' in locals():
                        error_msg += f"\nResponse status: {response.status_code}"
                except:
                    pass
                self.logger.error(error_msg)
                
                if attempt < MAX_RETRIES - 1:
                    console.print(f"[yellow]⚠[/yellow] Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    console.print(f"[red]✗[/red] All attempts to fetch release info failed")
                    self._emit_callback('fetch_failed', {'error': str(e)})
                    return None, None
    
    def compare_versions(self, current, latest):
        """Compares two version strings. Returns True if current >= latest (no update needed)."""
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
                    return True  # Current is newer, no update needed
                elif cur < lat:
                    return False  # Latest is newer, update needed
            
            # Core versions are equal, compare prerelease tags
            if current_prerelease is None and latest_prerelease is None:
                return True  # Equal versions, no update needed
            elif current_prerelease is None:
                return True  # Current is stable, latest is prerelease, no update needed
            elif latest_prerelease is None:
                return False  # Current is prerelease, latest is stable, update needed
            else:
                # Both are prereleases, current should be newer or equal to avoid update
                return current_prerelease >= latest_prerelease
                
        except ValueError as e:
            print(f"Warning: Version parsing error: {e}. Assuming update needed.")
            return False
    
    def download_release_with_retry(self, asset_url, asset_name):
        """Downloads the release zip with retry logic and progress."""
        self._emit_callback('download_start', {'asset_name': asset_name})
        temp_zip_path = os.path.join(TEMP_DIR, "update.zip")
        
        for attempt in range(MAX_RETRIES):
            try:
                console.print(f"[bold blue]Downloading {asset_name}...[/bold blue]")
                
                with requests.get(asset_url, stream=True, timeout=60) as r:
                    r.raise_for_status()
                    total_size = int(r.headers.get('content-length', 0))
                    
                    # Custom progress tracking for ETA and speed
                    downloaded = 0
                    start_time = time.time()
                    
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        BarColumn(),
                        TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
                        TextColumn("[progress.file_size]{task.fields[downloaded_str]} / {task.fields[total_size_str]}"),
                        TextColumn("[progress.rate]{task.fields[speed]}"),
                        TextColumn("[progress.eta]{task.fields[eta]}"),
                        console=console,
                        expand=True
                    ) as progress:
                        task = progress.add_task("[cyan]Downloading",
                                                total=total_size,
                                                downloaded_str="0 B",
                                                total_size_str="0 B",
                                                speed="0 B/s",
                                                eta="Calculating...")
                        
                        with open(temp_zip_path, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    downloaded += len(chunk)
                                    
                                    # Calculate progress metrics
                                    elapsed = time.time() - start_time
                                    speed = downloaded / elapsed if elapsed > 0 else 0
                                    
                                    # Calculate ETA
                                    if speed > 0:
                                        remaining = (total_size - downloaded) / speed
                                        eta_str = time.strftime("%H:%M:%S", time.gmtime(remaining))
                                    else:
                                        eta_str = "Calculating..."
                                    
                                    # Format size strings
                                    downloaded_str = self._format_size(downloaded)
                                    total_size_str = self._format_size(total_size)
                                    speed_str = self._format_size(speed) + "/s"
                                    
                                    progress.update(task,
                                                  advance=len(chunk),
                                                  downloaded_str=downloaded_str,
                                                  total_size_str=total_size_str,
                                                  speed=speed_str,
                                                  eta=eta_str)
                
                # Emit progress callback
                progress_data = {
                    'downloaded': downloaded,
                    'total': total_size,
                    'percentage': (downloaded / total_size * 100) if total_size > 0 else 0,
                    'speed': speed if 'speed' in locals() else 0,
                    'eta': eta_str if 'eta_str' in locals() else "Calculating..."
                }
                self._emit_callback('download_progress', progress_data)
                
                if os.path.exists(temp_zip_path) and os.path.getsize(temp_zip_path) > 0:
                    elapsed = time.time() - start_time
                    console.print(f"[green]✓[/green] Download complete! Elapsed time: {self._format_time(elapsed)}")
                    self._emit_callback('download_complete', {'elapsed_time': elapsed})
                    return temp_zip_path
                else:
                    raise IOError("Downloaded file is empty or not found.")

            except Exception as e:
                self.logger.error(f"[{attempt + 1}/{MAX_RETRIES}] Download failed: {e}")
                console.print(f"[red]✗[/red] Download failed: {e}")
                
                if attempt < MAX_RETRIES - 1:
                    console.print(f"[yellow]⚠[/yellow] Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    console.print(f"[red]✗[/red] All download attempts failed")
                    self._emit_callback('download_failed', {'error': str(e)})
                    raise
        return None
    
    def _format_size(self, size_bytes):
        """Format size in bytes to human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def _format_time(self, seconds):
        """Format time in seconds to HH:MM:SS format."""
        return time.strftime("%H:%M:%S", time.gmtime(seconds))
    
    def create_backup(self, version):
        """Creates a backup of the current application and related files."""
        self._emit_callback('backup_start', {'version': version})
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir_name = f"backup_{version}_{timestamp}"
        backup_dir = os.path.join(self.script_dir, backup_dir_name)
        
        os.makedirs(backup_dir, exist_ok=True)
        
        files_to_backup = [APP_NAME, VERSION_FILE, "deepseek.ico"]
        dirs_to_backup = ["injection"]

        console.print(Panel(f"[bold blue]Creating backup in {backup_dir_name}...[/bold blue]", border_style="blue"))
        
        backup_table = Table(show_header=True, header_style="bold magenta")
        backup_table.add_column("Item", style="cyan")
        backup_table.add_column("Status", style="green")
        
        for item_name in files_to_backup:
            item_path = os.path.join(self.script_dir, item_name)
            if os.path.exists(item_path):
                shutil.copy2(item_path, os.path.join(backup_dir, item_name))
                backup_table.add_row(item_name, "✓ Backed up")
            else:
                backup_table.add_row(item_name, "✗ Not found")

        for dir_name in dirs_to_backup:
            dir_path = os.path.join(self.script_dir, dir_name)
            if os.path.exists(dir_path):
                dest_path = os.path.join(backup_dir, dir_name)
                shutil.copytree(dir_path, dest_path)
                backup_table.add_row(f"{dir_name}/", "✓ Backed up")
            else:
                backup_table.add_row(f"{dir_name}/", "✗ Not found")
        
        console.print(backup_table)
        self._emit_callback('backup_complete', {'backup_dir': backup_dir})
        return backup_dir
    
    def extract_and_install_update(self, zip_path):
        """Extracts the update and installs new files."""
        self._emit_callback('extract_start', {})
        console.print("[bold yellow]Extracting update...[/bold yellow]")
        extract_to_dir = os.path.join(TEMP_DIR, "extracted")
        
        if os.path.exists(extract_to_dir):
            shutil.rmtree(extract_to_dir)
        os.makedirs(extract_to_dir, exist_ok=True)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to_dir)
            console.print("[green]✓[/green] Extraction successful!")
            self._emit_callback('extract_complete', {})
        except zipfile.BadZipFile:
            self.logger.error("Failed to extract the zip file (it might be corrupted).")
            console.print("[red]✗[/red] Failed to extract the zip file")
            return False

        console.print("[bold yellow]Installing new files...[/bold yellow]")
        
        # Create a table for the update progress
        update_table = Table(show_header=True, header_style="bold magenta")
        update_table.add_column("File/Folder", style="cyan")
        update_table.add_column("Status", style="green")
        
        # Copy all files from extracted directory
        success_count = 0
        total_count = 0
        
        for item in os.listdir(extract_to_dir):
            total_count += 1
            src_path = os.path.join(extract_to_dir, item)
            dest_path = os.path.join(self.script_dir, item)
            
            try:
                if os.path.isdir(src_path):
                    if os.path.exists(dest_path):
                        shutil.rmtree(dest_path)
                    shutil.copytree(src_path, dest_path)
                else:
                    shutil.copy2(src_path, dest_path)
                self.logger.info(f"Updated: {item}")
                update_table.add_row(item, "✓ Updated")
                success_count += 1
            except Exception as e:
                self.logger.error(f"Failed to update {item}: {e}")
                update_table.add_row(item, f"✗ Failed: {str(e)}")
        
        console.print(update_table)
        
        if success_count == total_count:
            console.print(f"[green]✓[/green] Successfully updated {success_count} items")
            self._emit_callback('install_complete', {'success_count': success_count, 'total_count': total_count})
            return True
        else:
            console.print(f"[red]✗[/red] Failed to update {total_count - success_count} out of {total_count} items")
            self._emit_callback('install_failed', {'success_count': success_count, 'total_count': total_count})
            return False
    
    def restore_backup(self, backup_dir):
        """Restores files from a backup."""
        self._emit_callback('restore_start', {'backup_dir': backup_dir})
        console.print(Panel(f"[bold blue]Restoring from backup: {os.path.basename(backup_dir)}...[/bold blue]", border_style="blue"))
        
        restore_table = Table(show_header=True, header_style="bold magenta")
        restore_table.add_column("Item", style="cyan")
        restore_table.add_column("Status", style="green")
        
        for item in os.listdir(backup_dir):
            src_path = os.path.join(backup_dir, item)
            dest_path = os.path.join(self.script_dir, item)
            
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
                restore_table.add_row(item, "✓ Restored")
            except Exception as e:
                restore_table.add_row(item, f"✗ Failed: {str(e)}")
        
        console.print(restore_table)
        self._emit_callback('restore_complete', {})
    
    def check_for_updates(self):
        """Check if updates are available and return update info"""
        current_version = self.get_current_version()
        self.logger.info(f"Current version: {current_version}")
        
        latest_version, release_info = self.fetch_latest_version_with_retry()
        if not latest_version:
            return False, None, None
            
        self.logger.info(f"Latest version: {latest_version}")

        update_needed = not self.compare_versions(current_version, latest_version)
        self.logger.info(f"Update needed: {update_needed}")
        
        return update_needed, current_version, latest_version
    
    def perform_update(self, auto_mode=False):
        """Perform the complete update process"""
        self._emit_callback('update_start', {'auto_mode': auto_mode})
        
        # Check if update is needed
        update_needed, current_version, latest_version = self.check_for_updates()
        
        if not update_needed:
            console.print(Panel(f"[bold green]You already have the latest version ({current_version})![/bold green]", border_style="green"))
            self.logger.info("No update needed. Exiting without restarting application.")
            self._emit_callback('update_not_needed', {'current_version': current_version})
            return True
        
        # Check if application is running and close it if needed
        try:
            subprocess.check_output(
                f'tasklist /FI "IMAGENAME eq {APP_NAME}" /FO CSV | find "{APP_NAME}"',
                shell=True,
                stderr=subprocess.DEVNULL
            )
            self.logger.info(f"{APP_NAME} is running. Attempting to close...")
            subprocess.run(
                f'taskkill /F /IM "{APP_NAME}"',
                shell=True,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(3)
            self.logger.info(f"{APP_NAME} closed.")
        except subprocess.CalledProcessError:
            self.logger.info(f"{APP_NAME} is not running.")
        
        console.print(Panel(f"[bold yellow]Update available: {current_version} -> {latest_version}[/bold yellow]", border_style="yellow"))

        # Find Windows asset
        asset_to_download = None
        if update_needed and latest_version:
            # Fetch release info again to get assets
            _, release_info = self.fetch_latest_version_with_retry()
            if release_info and isinstance(release_info, dict) and "assets" in release_info:
                for asset in release_info["assets"]:
                    if "windows.zip" in asset["name"].lower():
                        asset_to_download = asset
                        break
        
        if not asset_to_download:
            console.print(Panel("[bold red]Error: Windows release asset not found.[/bold red]", border_style="red"))
            self._emit_callback('update_failed', {'error': 'Windows release asset not found'})
            return False

        # Download asset
        try:
            zip_path = self.download_release_with_retry(
                asset_to_download["browser_download_url"],
                asset_to_download["name"]
            )
            if not zip_path:
                console.print(Panel("[bold red]Failed to download the update.[/bold red]", border_style="red"))
                self._emit_callback('update_failed', {'error': 'Failed to download update'})
                return False
        except Exception as e:
            self.logger.error(f"Download error: {e}")
            console.print(Panel(f"[bold red]Download error: {e}[/bold red]", border_style="red"))
            self._emit_callback('update_failed', {'error': str(e)})
            return False

        # Create backup
        backup_dir = self.create_backup(current_version)
        
        # Install update
        try:
            if self.extract_and_install_update(zip_path):
                with open(os.path.join(self.script_dir, VERSION_FILE), 'w') as f:
                    f.write(latest_version)
                self.logger.info(f"Updated version to: {latest_version}")
                
                # Create a success panel
                success_table = Table(show_header=False, box=box.ROUNDED)
                success_table.add_column("Info", style="green")
                success_table.add_row("Update installed successfully!")
                success_table.add_row(f"Version: {current_version} -> {latest_version}")
                
                console.print(Panel(success_table, title="Update Complete", border_style="green"))
                self._emit_callback('update_success', {'new_version': latest_version})
                
                # Start application
                app_path = os.path.join(self.script_dir, APP_NAME)
                if os.path.exists(app_path):
                    self.logger.info(f"Starting {APP_NAME}...")
                    subprocess.Popen([app_path])
                    
                    # Create a completion panel
                    completion_table = Table(show_header=False, box=box.ROUNDED)
                    completion_table.add_column("Info", style="cyan")
                    completion_table.add_row("UPDATE COMPLETED SUCCESSFULLY!")
                    completion_table.add_row(f"Version: {current_version} -> {latest_version}")
                    
                    console.print(Panel(completion_table, title="Update Complete", border_style="cyan"))
                    return True
            else:
                console.print(Panel("[bold red]Update failed. Restoring backup...[/bold red]", border_style="red"))
                self.restore_backup(backup_dir)
                self._emit_callback('update_failed', {'error': 'Update installation failed'})
                return False
        except Exception as e:
            self.logger.error(f"Critical error during update: {e}")
            console.print(Panel("[bold red]Restoring backup...[/bold red]", border_style="red"))
            self.restore_backup(backup_dir)
            self._emit_callback('update_failed', {'error': str(e)})
            return False

        # Cleanup
        self.logger.info("Cleaning up temporary files...")
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        self.logger.info("Cleanup complete. Exiting.")
        return True

def main():
    """Main function for standalone execution"""
    parser = argparse.ArgumentParser(description="DeepSeek Desktop Auto-Updater")
    parser.add_argument("--auto", action="store_true", help="Run in auto mode (non-interactive).")
    parser.add_argument("--debug", action="store_true", help="Keep console open after update for debugging.")
    args = parser.parse_args()

    auto_mode = args.auto
    debug_mode = args.debug
    script_dir = get_script_directory()
    
    # Create AutoUpdater instance
    updater = AutoUpdater(script_dir)
    
    # Run update
    success = updater.perform_update(auto_mode)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print(Panel("[bold yellow]Update cancelled by user.[/bold yellow]", border_style="yellow"))
        sys.exit(1)
    except Exception as e:
        console.print(Panel(f"[bold red]An unexpected error occurred: {e}[/bold red]", border_style="red"))
        sys.exit(1)