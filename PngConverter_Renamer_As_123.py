import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import shutil
import tempfile

def convert_and_rename_images(source_folder, recursive=False):
    """
    Convert non-PNG images to PNG and rename all images sequentially.
    
    Args:
        source_folder (str): Path to the source folder
        recursive (bool): Whether to process subfolders recursively
    """
    # Supported image formats for conversion
    supported_formats = {'.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.tif', '.webp', '.ico'}
    
    # Get all image files
    image_files = []
    
    if recursive:
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext == '.png' or file_ext in supported_formats:
                    image_files.append(file_path)
    else:
        for file in os.listdir(source_folder):
            file_path = os.path.join(source_folder, file)
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext == '.png' or file_ext in supported_formats:
                    image_files.append(file_path)
    
    if not image_files:
        messagebox.showinfo("No Images", "No image files found in the selected folder.")
        return
    
    # Sort files to ensure consistent ordering
    image_files.sort()
    
    # Create a temporary list to store converted files
    converted_files = []
    conversion_count = 0
    
    # Process each image file
    for i, file_path in enumerate(image_files, 1):
        file_ext = os.path.splitext(file_path)[1].lower()
        directory = os.path.dirname(file_path)
        
        if file_ext == '.png':
            # Already PNG, just add to the list for renaming
            converted_files.append(file_path)
        else:
            # Convert to PNG
            try:
                with Image.open(file_path) as img:
                    # Convert to RGB if necessary (for formats like RGBA)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Keep transparency for RGBA and LA modes
                        if img.mode == 'P' and 'transparency' in img.info:
                            img = img.convert('RGBA')
                    elif img.mode not in ('RGB', 'RGBA'):
                        img = img.convert('RGB')
                    
                    # Create temporary PNG file with unique name
                    temp_png_path = os.path.join(directory, f"temp_converted_{i}_{os.getpid()}.png")
                    img.save(temp_png_path, 'PNG')
                    
                    # Remove original file
                    os.remove(file_path)
                    
                    # Add converted file to list
                    converted_files.append(temp_png_path)
                    conversion_count += 1
                    
            except Exception as e:
                print(f"Error converting {file_path}: {str(e)}")
                messagebox.showwarning("Conversion Error", f"Failed to convert {os.path.basename(file_path)}: {str(e)}")
                continue
    
    # Now rename all files sequentially using a safe two-step process
    if recursive:
        # For recursive mode, process each directory separately
        dir_files = {}
        for file_path in converted_files:
            directory = os.path.dirname(file_path)
            if directory not in dir_files:
                dir_files[directory] = []
            dir_files[directory].append(file_path)
        
        # Rename files in each directory
        for directory, files in dir_files.items():
            files.sort()
            rename_files_safely(files, directory)
    else:
        # For non-recursive mode, rename all files in the main directory
        converted_files.sort()
        rename_files_safely(converted_files, source_folder)
    
    # Show completion message
    total_files = len(converted_files)
    messagebox.showinfo("Process Complete", 
                       f"Process completed!\n"
                       f"Total files processed: {total_files}\n"
                       f"Files converted to PNG: {conversion_count}\n"
                       f"Files renamed: {total_files}")

def rename_files_safely(file_list, directory):
    """
    Safely rename files to sequential numbers, avoiding conflicts with existing names.
    """
    # First pass: rename all files to temporary names to avoid conflicts
    temp_names = []
    for i, file_path in enumerate(file_list):
        temp_name = f"temp_rename_{i}_{os.getpid()}.png"
        temp_path = os.path.join(directory, temp_name)
        
        if file_path != temp_path:
            try:
                os.rename(file_path, temp_path)
                temp_names.append(temp_path)
            except Exception as e:
                print(f"Error creating temporary name for {file_path}: {str(e)}")
                temp_names.append(file_path)  # Keep original if rename fails
        else:
            temp_names.append(file_path)
    
    # Second pass: rename from temporary names to final sequential names
    for i, temp_path in enumerate(temp_names, 1):
        final_name = f"{i}.png"
        final_path = os.path.join(directory, final_name)
        
        if temp_path != final_path:
            try:
                # If final path exists and is different from temp_path, remove it first
                if os.path.exists(final_path) and os.path.abspath(temp_path) != os.path.abspath(final_path):
                    os.remove(final_path)
                
                os.rename(temp_path, final_path)
            except Exception as e:
                print(f"Error renaming {temp_path} to {final_path}: {str(e)}")

def main():
    # Create main window (hidden)
    root = tk.Tk()
    root.withdraw()
    
    # Ask for source folder
    source_folder = filedialog.askdirectory(title="Select Source Folder")
    
    if not source_folder:
        messagebox.showinfo("Cancelled", "No folder selected. Exiting.")
        return
    
    # Ask if user wants recursive processing
    recursive = messagebox.askyesno("Recursive Processing", 
                                   "Do you want to process subfolders recursively?\n\n"
                                   "Yes: Process all subfolders\n"
                                   "No: Process only the selected folder")
    
    # Confirm before proceeding
    confirm_msg = f"Selected folder: {source_folder}\n"
    confirm_msg += f"Recursive processing: {'Yes' if recursive else 'No'}\n\n"
    confirm_msg += "This will:\n"
    confirm_msg += "• Convert non-PNG images to PNG format\n"
    confirm_msg += "• Delete original non-PNG files after conversion\n"
    confirm_msg += "• Rename all PNG files to 1.png, 2.png, 3.png, etc.\n\n"
    confirm_msg += "Do you want to continue?"
    
    if not messagebox.askyesno("Confirm Operation", confirm_msg):
        messagebox.showinfo("Cancelled", "Operation cancelled.")
        return
    
    try:
        convert_and_rename_images(source_folder, recursive)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    root.destroy()

if __name__ == "__main__":
    main()