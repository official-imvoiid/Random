import tkinter as tk
from tkinter import filedialog
import os

def select_items():
    """Simple GUI to select files or folders"""
    root = tk.Tk()
    root.withdraw()
    
    print("\n=== BULK RENAME - SEQUENTIAL NUMBERING ===")
    print("1. Select Files")
    print("2. Select Folder")
    choice = input("Choose option (1/2): ").strip()
    
    items = []
    if choice == "1":
        files = filedialog.askopenfilenames(title="Select Files to Rename")
        items = list(files)
    elif choice == "2":
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            items = [os.path.join(folder, item) for item in os.listdir(folder)]
            items = sorted(items)
    
    root.destroy()
    return items

def rename_sequential(items):
    """Rename files with sequential numbering"""
    if not items:
        print("No items selected!")
        return
    
    print(f"\n✓ Selected {len(items)} items")
    
    # Get user preferences
    print("\n--- Rename Pattern ---")
    print("Examples: name_001 | 001_name | 001 | name")
    
    base_name = input("\nBase name (or empty): ").strip()
    start_num = int(input("Start number (e.g., 1, 600): ").strip() or "1")
    
    if start_num > 0:
        digits = int(input("Digits (e.g., 3 for 001): ").strip() or "3")
        if base_name:
            position = input("Position (prefix/suffix): ").strip().lower() or "suffix"
        else:
            position = 'prefix'
        separator = input("Separator (_, -, empty): ").strip()
    
    # Get range
    print(f"\nTotal items: {len(items)}")
    range_input = input("Range (e.g., '1-700', '600-700', Enter=all): ").strip()
    
    if range_input:
        if '-' in range_input:
            start_idx, end_idx = map(int, range_input.split('-'))
            items = items[start_idx-1:end_idx]
        else:
            items = items[:int(range_input)]
    
    # Confirm
    confirm = input(f"\nRename {len(items)} items? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Cancelled.")
        return
    
    # Apply rename
    success = 0
    errors = []
    
    for i, item_path in enumerate(items):
        try:
            parent_dir = os.path.dirname(item_path)
            ext = os.path.splitext(item_path)[1]
            
            if start_num == 0:
                new_name = f"{base_name}{ext}"
            elif base_name:
                num = str(start_num + i).zfill(digits)
                new_name = f"{num}{separator}{base_name}{ext}" if position == 'prefix' else f"{base_name}{separator}{num}{ext}"
            else:
                new_name = f"{str(start_num + i).zfill(digits)}{ext}"
            
            new_path = os.path.join(parent_dir, new_name)
            
            if not os.path.exists(new_path):
                os.rename(item_path, new_path)
                success += 1
            else:
                errors.append(f"{new_name} exists")
                
        except Exception as e:
            errors.append(str(e))
    
    print(f"\n✓ Renamed {success} items")
    if errors:
        print(f"✗ Errors: {len(errors)}")

if __name__ == "__main__":
    items = select_items()
    if items:
        rename_sequential(items)
    input("\nPress Enter to exit...")