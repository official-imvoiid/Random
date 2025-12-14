#!/usr/bin/env python3

import os
import sys
from pathlib import Path


def get_folder_path():
    """Prompt user to enter a folder path or file path"""
    print("\n" + "="*60)
    print("TEXT PREPENDER - Add text to start of all .txt files")
    print("="*60)
    print("\nYou can enter:")
    print("  1. A folder path (to process all .txt files in that folder)")
    print("  2. A file path (to process all .txt files in that file's folder)")
    print("\n")
    
    while True:
        path = input("Enter folder path or file path: ").strip().strip('"').strip("'")
        
        if not path:
            print("Error: Path cannot be empty. Please try again.\n")
            continue
        
        # Convert to Path object
        path_obj = Path(path)
        
        # If it's a file, get its directory
        if path_obj.is_file():
            folder = path_obj.parent
            print(f"\n✓ File selected: {path}")
            print(f"✓ Will process all .txt files in: {folder}")
            return folder
        # If it's a directory
        elif path_obj.is_dir():
            print(f"\n✓ Folder selected: {path}")
            return path_obj
        else:
            print(f"Error: Path does not exist: {path}")
            print("Please check the path and try again.\n")


def get_prepend_text():
    """Prompt user to enter text to prepend"""
    print("\n" + "-"*60)
    print("Enter the text/word/sentence to add at the START of all .txt files")
    print("(This will be added directly before existing content, no newline)")
    print("-"*60)
    
    text = input("\nEnter text to prepend: ")
    
    if not text:
        print("\nWarning: No text entered. Nothing will be added.")
        return None
    
    return text


def process_txt_files(folder_path, prepend_text):
    """Process all .txt files in the folder"""
    
    # Find all .txt files
    txt_files = list(folder_path.glob("*.txt"))
    
    if not txt_files:
        print(f"\n✗ No .txt files found in: {folder_path}")
        return
    
    print(f"\n✓ Found {len(txt_files)} .txt file(s):")
    for i, file in enumerate(txt_files, 1):
        print(f"  {i}. {file.name}")
    
    # Confirm action
    print("\n" + "#"*40)
    print("WARNING: This action cannot be undone!")
    print("#"*40)
    confirm = input("\nProceed with prepending text to these files? (yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("\n✗ Operation cancelled.")
        return
    
    # Process files
    processed = 0
    errors = []
    
    print("\nProcessing files...")
    for txt_file in txt_files:
        try:
            # Read existing content
            with open(txt_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Write prepended text + original content (NO newline added)
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(prepend_text + original_content)
            
            processed += 1
            print(f"  ✓ {txt_file.name}")
            
        except Exception as e:
            errors.append(f"{txt_file.name}: {str(e)}")
            print(f"  ✗ {txt_file.name} - Error: {str(e)}")
    
    # Show results
    print("\n" + "="*60)
    print(f"COMPLETE: Successfully processed {processed}/{len(txt_files)} file(s)")
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
    print("="*60)


def main():
    try:
        # Get folder path
        folder = get_folder_path()
        
        # Get text to prepend
        prepend_text = get_prepend_text()
        
        if prepend_text is None:
            print("\n✗ Operation cancelled - no text provided.")
            return
        
        # Process files
        process_txt_files(folder, prepend_text)
        
    except KeyboardInterrupt:
        print("\n\n✗ Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ An error occurred: {str(e)}")
        sys.exit(1)
    
    # Wait before closing (for Windows users who double-click)
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
