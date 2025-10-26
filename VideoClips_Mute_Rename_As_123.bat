rem = r"""
@echo off
python "%~f0" %*
goto :EOF
"""

# --- PYTHON CODE BELOW --- (executes from here)
import os
import subprocess
import tkinter as tk
from tkinter import filedialog

def mute_and_rename_mp4s(folder_path):
    files = [f for f in os.listdir(folder_path) if f.lower().endswith('.mp4')]
    files.sort()

    for i, filename in enumerate(files, start=1):
        src = os.path.join(folder_path, filename)
        temp_output = os.path.join(folder_path, f"temp_{i}.mp4")
        final_output = os.path.join(folder_path, f"{i}.mp4")

        command = [
            "ffmpeg",
            "-i", src,
            "-c:v", "copy",
            "-an",
            "-y",
            temp_output
        ]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        os.remove(src)
        os.rename(temp_output, final_output)

def main():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Select folder containing .mp4 files")
    
    if folder_selected:
        mute_and_rename_mp4s(folder_selected)
        print("Operation complete.")
    else:
        print("No folder selected.")

if __name__ == "__main__":
    main()