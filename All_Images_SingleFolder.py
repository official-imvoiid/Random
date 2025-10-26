import os
import shutil

def flatten_directory(main_folder):
    """
    Moves all files from ALL subfolders (including nested ones) to main folder.
    Removes all empty subfolders after moving files.
    """
    
    # Check if main folder exists
    if not os.path.exists(main_folder):
        print(f"❌ Error: Folder '{main_folder}' does not exist!")
        return
    
    # Find all subfolders (including nested ones)
    all_files = []
    all_folders = []
    
    for root, dirs, files in os.walk(main_folder):
        # Skip the main folder itself
        if root != main_folder:
            all_folders.append(root)
            for file in files:
                all_files.append(os.path.join(root, file))
    
    if not all_files and not all_folders:
        print("✅ No subfolders or files found. Folder is already flat!")
        return
    
    # Show summary
    print(f"📂 Main folder: {main_folder}")
    print(f"📁 Found {len(all_folders)} subfolder(s)")
    print(f"📄 Found {len(all_files)} file(s) to move")
    
    if all_folders:
        print("\n🗂️  Subfolders that will be removed:")
        for folder in sorted(all_folders)[:10]:  # Show first 10
            print(f"   - {os.path.relpath(folder, main_folder)}")
        if len(all_folders) > 10:
            print(f"   ... and {len(all_folders) - 10} more")
    
    print("\n⚠️  This will:")
    print("   1. Move ALL files from subfolders to the main folder")
    print("   2. Delete ALL subfolders (after emptying them)")
    print("   3. Rename files if duplicates exist")
    
    confirm = input("\n❓ Continue? (yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("❌ Cancelled")
        return
    
    print("\n⏳ Processing...\n")
    
    files_moved = 0
    errors = []
    
    # Move all files to main folder
    for file_path in all_files:
        try:
            file_name = os.path.basename(file_path)
            destination = os.path.join(main_folder, file_name)
            
            # Handle duplicate names
            counter = 1
            base_name, extension = os.path.splitext(file_name)
            
            while os.path.exists(destination):
                new_name = f"{base_name}_{counter}{extension}"
                destination = os.path.join(main_folder, new_name)
                counter += 1
            
            shutil.move(file_path, destination)
            files_moved += 1
            
        except Exception as e:
            errors.append(f"Failed to move {file_path}: {str(e)}")
    
    # Remove all empty subfolders (from deepest to shallowest)
    folders_removed = 0
    for folder in sorted(all_folders, reverse=True):
        try:
            if os.path.exists(folder):
                os.rmdir(folder)
                folders_removed += 1
        except OSError as e:
            errors.append(f"Failed to remove {folder}: {str(e)}")
    
    # Show results
    print(f"\n✅ Complete!")
    print(f"   📄 Files moved: {files_moved}")
    print(f"   📁 Folders removed: {folders_removed}")
    
    if errors:
        print(f"\n⚠️  {len(errors)} error(s) occurred:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"   - {error}")
        if len(errors) > 5:
            print(f"   ... and {len(errors) - 5} more errors")

if __name__ == "__main__":
    # Use the directory where the script is located
    script_directory = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 60)
    print("🔧 FOLDER FLATTENER")
    print("=" * 60)
    
    flatten_directory(script_directory)
    
    print("\n" + "=" * 60)