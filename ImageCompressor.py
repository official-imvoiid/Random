#!/usr/bin/env python3
"""
Image Compression Script with Folder Picker
Opens a popup to select folder, then compresses automatically
Output: ImageCompressed_[timestamp]
"""

import os
from PIL import Image
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

def select_folder():
    """Open folder picker dialog"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.attributes('-topmost', True)  # Bring dialog to front
    
    folder = filedialog.askdirectory(title="Select folder with images to compress")
    root.destroy()
    
    return folder

def compress_image(input_path, output_path, quality=85, max_width=1920):
    """Compress a single image"""
    try:
        with Image.open(input_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            
            # Resize if image is too large
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Save with compression
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
            
            return True
    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False

def compress_folder(input_folder, quality=85, max_width=1920):
    """Compress all images in a folder"""
    input_path = Path(input_folder)
    
    if not input_path.exists():
        print(f"Error: Folder '{input_folder}' does not exist!")
        return
    
    # Create output folder with timestamp in the same directory as the script
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    script_dir = Path(__file__).parent.resolve()  # Get script's directory
    output_path = script_dir / f"ImageCompressed_{timestamp}"
    output_path.mkdir(exist_ok=True)
    
    # Supported image formats
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    
    # Get all image files
    image_files = [f for f in input_path.rglob('*') 
                   if f.suffix.lower() in image_extensions and f.is_file()]
    
    if not image_files:
        print(f"No images found in '{input_folder}'")
        return
    
    print(f"\n{'='*60}")
    print(f"IMAGE COMPRESSION STARTED")
    print(f"{'='*60}")
    print(f"Input folder: {input_path}")
    print(f"Output will be saved in script's location as: {output_path.name}")
    print(f"Found {len(image_files)} images to compress")
    print(f"Settings: Quality={quality}, Max Width={max_width}px")
    print(f"{'='*60}\n")
    
    total_size_before = 0
    total_size_after = 0
    success_count = 0
    
    for i, img_file in enumerate(image_files, 1):
        # Calculate relative path to preserve folder structure
        relative_path = img_file.relative_to(input_path)
        output_file = output_path / relative_path.parent / f"{relative_path.stem}.jpg"
        
        # Create subdirectories if needed
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Get original size
        original_size = img_file.stat().st_size
        total_size_before += original_size
        
        print(f"[{i}/{len(image_files)}] Processing: {img_file.name}...", end=" ")
        
        if compress_image(str(img_file), str(output_file), quality, max_width):
            compressed_size = output_file.stat().st_size
            total_size_after += compressed_size
            reduction = (1 - compressed_size / original_size) * 100
            print(f"✓ Reduced by {reduction:.1f}% ({original_size/1024/1024:.1f}MB → {compressed_size/1024/1024:.1f}MB)")
            success_count += 1
        else:
            print("✗ Failed")
    
    print(f"\n{'='*60}")
    print(f"COMPRESSION COMPLETE!")
    print(f"{'='*60}")
    print(f"Successfully compressed: {success_count}/{len(image_files)} images")
    print(f"Total size before: {total_size_before/1024/1024/1024:.2f} GB")
    print(f"Total size after: {total_size_after/1024/1024/1024:.2f} GB")
    print(f"Total reduction: {(1 - total_size_after/total_size_before)*100:.1f}%")
    print(f"Space saved: {(total_size_before - total_size_after)/1024/1024/1024:.2f} GB")
    print(f"\nOutput saved to: {output_path}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    print("\n🖼️  IMAGE COMPRESSOR")
    print("Opening folder picker...\n")
    
    # Open folder picker popup
    input_folder = select_folder()
    
    if not input_folder:
        print("No folder selected. Exiting.")
    else:
        # You can change these settings here:
        QUALITY = 85      # 50-95 (lower = smaller size, lower quality)
        MAX_WIDTH = 1920  # Maximum width in pixels
        
        compress_folder(input_folder, quality=QUALITY, max_width=MAX_WIDTH)
    
    input("\nPress Enter to exit...")
