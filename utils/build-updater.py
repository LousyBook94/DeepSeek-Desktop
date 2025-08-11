import os
import sys
import shutil
import subprocess
import argparse

def build_updater(script_dir, output_dir):
    """
    Builds the auto-update.py script into a standalone executable.
    """
    auto_update_script = os.path.join(script_dir, "auto_update.py")
    if not os.path.exists(auto_update_script):
        print(f"Error: auto_update.py not found in {script_dir}")
        return False

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # PyInstaller command
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",
        "--name", "auto-updater",
        "--distpath", output_dir,
        "--workpath", os.path.join(script_dir, "build_updater_temp"),
        "--specpath", os.path.join(script_dir, "build_updater_temp"),
        auto_update_script
    ]

    print("Building auto-updater.exe...")
    print(f"Running: {' '.join(pyinstaller_cmd)}")

    try:
        result = subprocess.run(pyinstaller_cmd, check=True, capture_output=True, text=True, cwd=script_dir)
        print("Build successful!")
        if result.stdout:
            print("PyInstaller Output:\n", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error code {e.returncode}")
        if e.stdout:
            print("PyInstaller STDOUT:\n", e.stdout)
        if e.stderr:
            print("PyInstaller STDERR:\n", e.stderr)
        return False
    except FileNotFoundError:
        print("Error: 'pyinstaller' command not found. Make sure PyInstaller is installed and in your PATH.")
        print("You can install it using: pip install pyinstaller")
        return False
    finally:
        # Clean up temporary build artifacts
        temp_build_dir = os.path.join(script_dir, "build_updater_temp")
        if os.path.exists(temp_build_dir):
            shutil.rmtree(temp_build_dir, ignore_errors=True)
            print("Cleaned up temporary build directory.")

def main():
    parser = argparse.ArgumentParser(description="Build the DeepSeek Desktop Auto-Updater.")
    parser.add_argument(
        "--output-dir",
        default=os.path.dirname(__file__),
        help="Directory to save the built executable (default: same directory as build-updater.py)."
    )

    args = parser.parse_args()

    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.abspath(args.output_dir)
    

    # Build the updater
    if build_updater(script_dir, output_dir):
        exe_path = os.path.join(output_dir, "auto-updater.exe")
        print(f"\nSuccess! auto-updater.exe created at: {exe_path}")
        
        # Open the output directory
        print(f"Opening output directory: {output_dir}")
        if sys.platform == "win32":
            os.startfile(output_dir)
    else:
        print("\nBuild failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()