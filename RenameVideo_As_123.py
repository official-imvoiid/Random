import os
import tkinter as tk
from tkinter import filedialog

# Create a hidden root window
root = tk.Tk()
root.withdraw()

# Open folder selection dialog
directory = filedialog.askdirectory(title="Select Folder Containing Video Files")

# Exit if no folder selected
if not directory:
    print("No folder selected. Exiting...")
    exit()

print(f"Selected folder: {directory}\n")

# Common video file extensions
video_extensions = ('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpeg', '.mpg')

# Get all video files in the directory
video_files = [f for f in os.listdir(directory) 
               if os.path.isfile(os.path.join(directory, f)) 
               and f.lower().endswith(video_extensions)]

# Sort files to maintain consistent ordering
video_files.sort()

if not video_files:
    print("No video files found in the selected folder.")
    exit()

# Rename each file
for index, filename in enumerate(video_files, start=1):
    # Get the file extension
    _, ext = os.path.splitext(filename)
    
    # Create new filename
    new_name = f"{index}{ext}"
    
    # Skip if the file is already named correctly
    if filename == new_name:
        print(f"Skipped: {filename} (already correct)")
        continue
    
    # Full paths
    old_path = os.path.join(directory, filename)
    new_path = os.path.join(directory, new_name)
    
    # Rename the file
    try:
        os.rename(old_path, new_path)
        print(f"Renamed: {filename} -> {new_name}")
    except Exception as e:
        print(f"Error renaming {filename}: {e}")

print(f"\nTotal files processed: {len(video_files)}")