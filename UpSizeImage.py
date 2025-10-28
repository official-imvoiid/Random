import os
from tkinter import Tk, filedialog
from PIL import Image

def upscale_image(image, scale_factor=2):
    width, height = image.size
    new_size = (int(width * scale_factor), int(height * scale_factor))
    return image.resize(new_size, Image.ANTIALIAS)

def main():
    # Hide the root window of Tkinter.
    root = Tk()
    root.withdraw()
    
    # Ask for the folder that holds your images.
    source_folder = filedialog.askdirectory(title="Select Source Folder (Images)")
    if not source_folder:
        print("No source folder selected. Exiting.")
        return

    # Ask for the folder where the upscaled images will reside.
    destination_folder = filedialog.askdirectory(title="Select Destination Folder")
    if not destination_folder:
        print("No destination folder selected. Exiting.")
        return

    # Process each image file found in the source folder.
    for filename in os.listdir(source_folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
            image_path = os.path.join(source_folder, filename)
            try:
                with Image.open(image_path) as img:
                    # Upscale the image; only size is amplified.
                    upscaled = upscale_image(img)
                    dest_path = os.path.join(destination_folder, filename)
                    upscaled.save(dest_path)
                    print(f"Processed {filename}")
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

if __name__ == '__main__':
    main()
