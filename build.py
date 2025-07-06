import os
import shutil
import subprocess
import sys
import zipfile  # For creating build.zip

def build_app():
    # Ensure required files exist
    if not os.path.exists("injection"):
        print("Error: injection directory not found!")
        return
    if not os.path.exists("deepseek.ico"):
        print("Error: deepseek.ico icon not found!")
        return
    
    # Create clean build directories
    temp_dir = "temp_build"
    dist_dir = "built"
    
    # Remove previous build artifacts
    shutil.rmtree(temp_dir, ignore_errors=True)
    shutil.rmtree(dist_dir, ignore_errors=True)
    shutil.rmtree("build", ignore_errors=True)  # Remove intermediate build directory
    
    # Create fresh directories
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(dist_dir, exist_ok=True)
    
    # Get absolute path to icon
    icon_path = os.path.abspath("deepseek.ico")
    
    # PyInstaller command with absolute icon path
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",  # Create Windows GUI app (no console)
        f"--icon={icon_path}",
        f"--distpath={dist_dir}",
        f"--workpath={temp_dir}",
        f"--specpath={temp_dir}",
        "-n", "DeepSeekChat",
        "main.py"
    ]
    
    # Run PyInstaller
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print build output
    print(result.stdout)
    if result.stderr:
        print("Build errors:", result.stderr)
    
    # Clean up temporary build artifacts
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    # Define resources to copy to built directory
    resources_to_copy = [
        ("injection", "injection"),  # (source, destination)
        ("deepseek.ico", "deepseek.ico")
    ]
    
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
    
    # Create build.zip in the zipped directory
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, dist_dir)
                zipf.write(file_path, arcname)
    
    print("\nBuild complete! Executable and resources are in ./built/ directory")
    print(f"Zip archive created at {zip_path}")
    
    # Open the output directory in Explorer
    os.startfile(os.path.abspath(dist_dir))

if __name__ == "__main__":
    build_app()