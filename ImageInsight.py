import os
from pathlib import Path
from PIL import Image
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog
from math import gcd

def format_bytes(bytes_size):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def get_aspect_ratio(width, height):
    """Calculate aspect ratio in simplest form"""
    divisor = gcd(width, height)
    return f"{width//divisor}:{height//divisor}"

def analyze_dataset(folder_path):
    """Analyze all images in the selected folder"""
    print(f"\n{'='*70}")
    print(f"Analyzing Dataset: {folder_path}")
    print(f"{'='*70}\n")
    
    # Supported image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff', '.tif'}
    
    # Statistics containers
    resolutions = defaultdict(int)
    aspect_ratios = defaultdict(int)
    formats = defaultdict(int)
    total_size = 0
    image_count = 0
    min_width = float('inf')
    max_width = 0
    min_height = float('inf')
    max_height = 0
    errors = []
    
    # Walk through all files in folder and subfolders
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            file_path = Path(root) / filename
            
            # Check if it's an image file
            if file_path.suffix.lower() not in image_extensions:
                continue
            
            try:
                # Get file size
                file_size = file_path.stat().st_size
                total_size += file_size
                
                # Get image format
                file_format = file_path.suffix.upper().replace('.', '')
                formats[file_format] += 1
                
                # Open and analyze image
                with Image.open(file_path) as img:
                    width, height = img.size
                    
                    # Track resolution
                    resolution = f"{width}x{height}"
                    resolutions[resolution] += 1
                    
                    # Track aspect ratio
                    aspect_ratio = get_aspect_ratio(width, height)
                    aspect_ratios[aspect_ratio] += 1
                    
                    # Track min/max dimensions
                    min_width = min(min_width, width)
                    max_width = max(max_width, width)
                    min_height = min(min_height, height)
                    max_height = max(max_height, height)
                    
                    image_count += 1
                    
            except Exception as e:
                errors.append(f"{filename}: {str(e)}")
    
    # Print results
    if image_count == 0:
        print("❌ No images found in the selected folder!\n")
        return
    
    print(f"📊 OVERVIEW")
    print(f"{'-'*70}")
    print(f"Total Images:        {image_count}")
    print(f"Total Size:          {format_bytes(total_size)}")
    print(f"Unique Resolutions:  {len(resolutions)}")
    print(f"Unique Aspect Ratios: {len(aspect_ratios)}")
    
    print(f"\n📏 DIMENSION RANGE")
    print(f"{'-'*70}")
    print(f"Width:   {min_width}px - {max_width}px")
    print(f"Height:  {min_height}px - {max_height}px")
    
    print(f"\n🖼️  FILE FORMATS")
    print(f"{'-'*70}")
    for fmt, count in sorted(formats.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / image_count) * 100
        print(f"{fmt:<10} {count:>6} images ({percentage:>5.1f}%)")
    
    print(f"\n📐 RESOLUTION DISTRIBUTION (Top 20)")
    print(f"{'-'*70}")
    sorted_resolutions = sorted(resolutions.items(), key=lambda x: x[1], reverse=True)
    for i, (resolution, count) in enumerate(sorted_resolutions[:20], 1):
        percentage = (count / image_count) * 100
        bar_length = int(percentage / 2)
        bar = '█' * bar_length
        print(f"{i:2}. {resolution:<15} {count:>6} ({percentage:>5.1f}%) {bar}")
    
    if len(sorted_resolutions) > 20:
        remaining = len(sorted_resolutions) - 20
        print(f"    ... and {remaining} more resolutions")
    
    print(f"\n🎯 ASPECT RATIO DISTRIBUTION")
    print(f"{'-'*70}")
    sorted_ratios = sorted(aspect_ratios.items(), key=lambda x: x[1], reverse=True)
    for ratio, count in sorted_ratios[:15]:
        percentage = (count / image_count) * 100
        bar_length = int(percentage / 2)
        bar = '█' * bar_length
        print(f"{ratio:<10} {count:>6} images ({percentage:>5.1f}%) {bar}")
    
    if len(sorted_ratios) > 15:
        remaining = len(sorted_ratios) - 15
        print(f"... and {remaining} more aspect ratios")
    
    if errors:
        print(f"\n⚠️  ERRORS ({len(errors)} files)")
        print(f"{'-'*70}")
        for error in errors[:10]:
            print(f"  • {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
    
    print(f"\n{'='*70}\n")

def main():
    """Main function with folder picker"""
    # Create Tkinter root window (hidden)
    root = tk.Tk()
    root.withdraw()
    
    print("\n" + "="*70)
    print("IMAGE DATASET ANALYZER")
    print("="*70)
    print("\nOpening folder picker...")
    
    # Open folder picker dialog
    folder_path = filedialog.askdirectory(
        title="Select Image Dataset Folder"
    )
    
    # Close Tkinter
    root.destroy()
    
    if not folder_path:
        print("\n❌ No folder selected. Exiting...\n")
        return
    
    # Analyze the dataset
    analyze_dataset(folder_path)
    
    print("Analysis complete! Press Enter to exit...")
    input()

if __name__ == "__main__":
    main()