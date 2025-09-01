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

    # Check if update icon exists, otherwise fallback to main icon
    # Use absolute path to ensure we're in the correct directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(project_root, "assets")
    
    icon_path = None
    if os.path.exists(assets_dir):
        # Try update icon first
        update_icon_path = os.path.join(assets_dir, "update_icon.ico")
        if os.path.exists(update_icon_path):
            icon_path = update_icon_path
            print(f"Using update icon: {icon_path}")
        else:
            # Fallback to main icon
            main_icon_path = os.path.join(assets_dir, "deepseek.ico")
            if os.path.exists(main_icon_path):
                icon_path = main_icon_path
                print(f"Using main icon: {icon_path}")
            else:
                print("Warning: Neither update_icon.ico nor deepseek.ico found in assets directory.")
    else:
        print("Warning: Assets directory not found. Building auto-updater without custom icon.")

    # PyInstaller command
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",
        "--name",
        "auto-updater",
        "--distpath",
        output_dir,
        "--workpath",
        os.path.join(script_dir, "build_updater_temp"),
        "--specpath",
        os.path.join(script_dir, "build_updater_temp"),
    ]

    # Add icon if it exists
    if icon_path and os.path.exists(icon_path):
        pyinstaller_cmd.extend(["--icon", icon_path])

    pyinstaller_cmd.append(auto_update_script)

    print("Building auto-updater.exe...")
    print(f"Running: {' '.join(pyinstaller_cmd)}")

    try:
        result = subprocess.run(
            pyinstaller_cmd, check=True, capture_output=True, text=True, cwd=script_dir
        )
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
        print(
            "Error: 'pyinstaller' command not found. Make sure PyInstaller is installed and in your PATH."
        )
        print("You can install it using: pip install pyinstaller")
        return False
    finally:
        # Clean up temporary build artifacts
        temp_build_dir = os.path.join(script_dir, "build_updater_temp")
        if os.path.exists(temp_build_dir):
            shutil.rmtree(temp_build_dir, ignore_errors=True)
            print("Cleaned up temporary build directory.")


def main():
    parser = argparse.ArgumentParser(
        description="Build the DeepSeek Desktop Auto-Updater."
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory to save the built executable (default: temp directory).",
    )

    args = parser.parse_args()

    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # If no output directory specified, use a temporary directory
    if args.output_dir is None:
        output_dir = os.path.join(script_dir, "temp_build")
    else:
        output_dir = os.path.abspath(args.output_dir)

    # Build the updater
    if build_updater(script_dir, output_dir):
        exe_path = os.path.join(output_dir, "auto-updater.exe")
        print(f"\nSuccess! auto-updater.exe created at: {exe_path}")

        # Open the output directory only if it's not a temp directory and not the built directory
        if args.output_dir is not None and "built" not in output_dir:
            print(f"Opening output directory: {output_dir}")
            if sys.platform == "win32":
                os.startfile(output_dir)
    else:
        print("\nBuild failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
