import os

def test_icon_paths():
    # Exact copy of the logic from build-updater.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    print(f"Script directory: {script_dir}")
    print(f"Project root: {project_root}")
    
    # Check if project_root is correct
    if not os.path.exists(os.path.join(project_root, "assets")):
        print("ERROR: assets directory not found in project_root!")
        return
    
    icon_path = os.path.abspath(
        os.path.join(project_root, "assets", "update_icon.ico")
    )
    print(f"Update icon path: {icon_path}")
    print(f"Update icon exists: {os.path.exists(icon_path)}")
    
    if not os.path.exists(icon_path):
        # Fallback to main icon
        icon_path = os.path.abspath(
            os.path.join(project_root, "assets", "deepseek.ico")
        )
        print(f"Main icon path: {icon_path}")
        print(f"Main icon exists: {os.path.exists(icon_path)}")

if __name__ == "__main__":
    test_icon_paths()