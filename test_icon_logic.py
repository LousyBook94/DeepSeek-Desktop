import os

def test_icon_selection():
    # Test the icon selection logic
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Test paths
    update_icon_path = os.path.abspath(
        os.path.join(os.path.dirname(script_dir), "assets", "update_icon.ico")
    )
    
    main_icon_path = os.path.abspath(
        os.path.join(os.path.dirname(script_dir), "assets", "deepseek.ico")
    )
    
    print(f"Script directory: {script_dir}")
    print(f"Update icon path: {update_icon_path}")
    print(f"Main icon path: {main_icon_path}")
    
    # Check if files exist
    print(f"\nUpdate icon exists: {os.path.exists(update_icon_path)}")
    print(f"Main icon exists: {os.path.exists(main_icon_path)}")
    
    # Test the icon selection logic
    icon_path = update_icon_path
    if not os.path.exists(icon_path):
        print("Update icon not found, falling back to main icon")
        icon_path = main_icon_path
    else:
        print("Using update icon")
    
    if not os.path.exists(icon_path):
        icon_path = None
        print("No icon found")
    else:
        print(f"Selected icon: {icon_path}")

if __name__ == "__main__":
    test_icon_selection()