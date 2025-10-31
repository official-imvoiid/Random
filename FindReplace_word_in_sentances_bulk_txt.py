import tkinter as tk
from tkinter import filedialog
import os
import re

def select_items():
    """GUI to select files or folder (only .txt files)"""
    root = tk.Tk()
    root.withdraw()
    
    print("\n=== BULK FIND/REPLACE IN TXT FILES ===")
    print("1. Select TXT Files")
    print("2. Select Folder (will process .txt files only)")
    choice = input("Choose option (1/2): ").strip()
    
    items = []
    if choice == "1":
        files = filedialog.askopenfilenames(
            title="Select TXT Files",
            filetypes=[("Text files", "*.txt")]
        )
        items = list(files)
    elif choice == "2":
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            all_items = [os.path.join(folder, f) for f in os.listdir(folder)]
            items = [f for f in all_items if f.lower().endswith('.txt')]
            items = sorted(items)
    
    root.destroy()
    return items

def get_find_replace_pairs():
    """Get find/replace pairs one per line, finish with 2 empty lines"""
    print("\n--- Enter Find/Replace Pairs ---")
    print("Type the WORD to FIND (whole word only), press Enter")
    print("Type what to REPLACE it with (leave empty to REMOVE), press Enter")
    print("Repeat for more pairs")
    print("Press Enter TWICE (two empty lines) when done\n")
    
    pairs = []
    empty_count = 0
    expecting_find = True
    current_find = None
    
    while True:
        if expecting_find:
            line = input("Find: ").strip()
        else:
            line = input("Replace with (empty to remove): ")
        
        if expecting_find and not line:
            empty_count += 1
            if empty_count >= 2:
                break
            continue
        
        if expecting_find:
            empty_count = 0
            current_find = line
            expecting_find = False
        else:
            empty_count = 0
            pairs.append((current_find, line.strip()))
            if line.strip():
                print(f"  ✓ Added: '{current_find}' → '{line.strip()}'\n")
            else:
                print(f"  ✓ Added: '{current_find}' → [REMOVE]\n")
            expecting_find = True
            current_find = None
    
    return pairs

def find_replace_in_files(items):
    """Apply multiple find/replace operations inside .txt files"""
    txt_files = [f for f in items if f.lower().endswith('.txt')]
    if not txt_files:
        print("No .txt files found!")
        return
    
    print(f"\n✓ Found {len(txt_files)} .txt file(s)")

    # Get find/replace pairs
    pairs = get_find_replace_pairs()
    
    if not pairs:
        print("No find/replace pairs entered!")
        return
    
    print(f"\n✓ Total pairs: {len(pairs)}")
    for find_text, replace_text in pairs:
        if replace_text:
            print(f"  '{find_text}' → '{replace_text}'")
        else:
            print(f"  '{find_text}' → [REMOVE]")

    def transform_content(content):
        """Apply all find/replace pairs to content"""
        new_content = content
        for find_text, replace_text in pairs:
            # Match whole words only using word boundaries
            pattern = r'\b' + re.escape(find_text) + r'\b'
            new_content = re.sub(pattern, replace_text, new_content, flags=re.IGNORECASE)
        
        # Clean up multiple spaces (but preserve newlines)
        new_content = re.sub(r' +', ' ', new_content)
        return new_content

    
    confirm = input(f"\nApply to {len(txt_files)} .txt files? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Cancelled.")
        return

    # Apply changes
    success = 0
    skipped = 0
    errors = []

    for file_path in txt_files:
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Transform content
            new_content = transform_content(original_content)
            
            # Skip if no change
            if original_content == new_content:
                skipped += 1
                continue
            
            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            success += 1

        except Exception as e:
            errors.append(f"{os.path.basename(file_path)}: {str(e)}")

    # Summary
    print(f"\n✓ Modified: {success}")
    print(f"  Skipped: {skipped} (no changes)")
    if errors:
        print(f"  Errors: {len(errors)}")
        for err in errors[:5]:
            print(f"    - {err}")
        if len(errors) > 5:
            print(f"    ... and {len(errors)-5} more.")

if __name__ == "__main__":
    items = select_items()
    if items:
        find_replace_in_files(items)
    input("\nPress Enter to exit...")