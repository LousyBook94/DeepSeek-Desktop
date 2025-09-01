import os
import shutil
import subprocess
import sys
import argparse
import zipfile  # For creating build.zip


def get_version_from_workflow():
    """Extract version from version.py file"""
    try:
        import version

        return version.__version__
    except ImportError:
        print("Warning: version.py not found, using default version")
        return "0.0.0"
    except Exception as e:
        print(f"Error reading version from version.py: {e}")
        return "0.0.0"


def build_app(fresh=False):
    # Ensure required files exist
    if not os.path.exists("injection"):
        print("Error: injection directory not found!")
        return

    # Create clean build directories
    temp_dir = "temp_build"
    dist_dir = "built"

    # Remove previous build artifacts, but preserve the data directory
    if os.path.exists(dist_dir):
        # Save the data directory if it exists
        data_dir = os.path.join(dist_dir, "data")
        temp_data_dir = None
        if os.path.exists(data_dir):
            temp_data_dir = os.path.join(temp_dir, "data_temp")
            shutil.move(data_dir, temp_data_dir)

        # Remove the dist directory
        shutil.rmtree(dist_dir, ignore_errors=True)

        # Restore the data directory
        if temp_data_dir and os.path.exists(temp_data_dir):
            os.makedirs(dist_dir, exist_ok=True)
            shutil.move(temp_data_dir, data_dir)

    # Remove other temporary directories
    shutil.rmtree(temp_dir, ignore_errors=True)
    shutil.rmtree("build", ignore_errors=True)  # Remove intermediate build directory

    # Create fresh directories
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(dist_dir, exist_ok=True)

    # Check if icon exists
    icon_path = os.path.abspath("assets/deepseek.ico")
    if not os.path.exists(icon_path):
        icon_path = None
        print("Warning: Icon file not found. Building without custom icon.")

    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",  # Create Windows GUI app (no console)
        f"--distpath={dist_dir}",
        f"--workpath={temp_dir}",
        f"--specpath={temp_dir}",
        "-n",
        "DeepSeekChat",
    ]

    # Add icon if it exists
    if icon_path:
        cmd.extend(["--icon", icon_path])

    cmd.append("main.py")

    # Run PyInstaller
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Print build output
    print(result.stdout)
    if result.stderr:
        print("Build errors:", result.stderr)

    # Clean up temporary build artifacts
    shutil.rmtree(temp_dir, ignore_errors=True)

    # Get version for logging
    version = get_version_from_workflow()
    print(f"Building with version: {version}")

    # Define resources to copy to built directory
    resources_to_copy = [("injection", "injection")]  # (source, destination)

    # --- Auto-Updater Logic ---
    updater_script_dir = os.path.join(os.path.dirname(__file__), "utils")
    final_exe_path = os.path.join(dist_dir, "auto-updater.exe")

    # Check if auto-updater.exe already exists in built folder or if --fresh flag is used
    if fresh or not os.path.exists(final_exe_path):
        print(
            f"{'--fresh flag used. Regenerating' if fresh else 'auto-updater.exe not found in built/.'} Generating auto-updater.exe now..."
        )
        build_updater_script = os.path.join(updater_script_dir, "build-updater.py")

        if not os.path.exists(build_updater_script):
            print(f"Error: build-updater.py not found in {updater_script_dir}!")
            return

        # Run build-updater.py directly to built directory
        result = subprocess.run(
            [sys.executable, build_updater_script, "--output-dir", dist_dir],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print("Failed to build auto-updater.exe!")
            print("Error:", result.stderr)
            return

        print("auto-updater.exe generated successfully!")
    else:
        print(f"auto-updater.exe already exists at {final_exe_path}")

    # Copy resources
    for src, dest in resources_to_copy:
        src_path = os.path.abspath(src)
        dest_path = os.path.join(dist_dir, dest)

        if os.path.isdir(src_path):
            shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
        else:
            shutil.copy(src_path, dest_path)

    # Create zipped directory if it doesn't exist
    zip_dir = "zipped"
    os.makedirs(zip_dir, exist_ok=True)
    zip_path = os.path.join(zip_dir, "build.zip")

    # Create build.zip in the zipped directory (excluding data directory)
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for root, dirs, files in os.walk(dist_dir):
            # Skip the data directory
            if "data" in root.split(os.sep):
                continue
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, dist_dir)
                zipf.write(file_path, arcname)

    print("\nBuild complete! Executable and resources are in ./built/ directory")
    print(f"Zip archive created at {zip_path}")

    # Open the output directory in Explorer
    os.startfile(os.path.abspath(dist_dir))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build the DeepSeek Desktop application and its updater."
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Force regeneration of the auto-updater.exe.",
    )
    args = parser.parse_args()
    build_app(fresh=args.fresh)
