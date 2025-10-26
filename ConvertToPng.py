import os
from tkinter import Tk, filedialog, messagebox
from PIL import Image

# Function to convert images to PNG format
def convert_images(input_folder, output_folder):
    # Loop through all files in the input folder
    for file_name in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file_name)

        # Check if the file is an image (if it can be opened by PIL)
        try:
            img = Image.open(file_path)

            # Create the output path with .png extension
            output_path = os.path.join(output_folder, os.path.splitext(file_name)[0] + ".png")

            # Save the image as PNG
            img.save(output_path, "PNG")

        except Exception as e:
            print(f"Skipping file {file_name} - Unable to open as image.")
            continue

def select_folder(title="Select Folder"):
    """ Opens a folder selection dialog and returns the folder path """
    folder_path = filedialog.askdirectory(title=title)
    return folder_path

def main():
    # Create the main tkinter window, but don't show it
    root = Tk()
    root.withdraw()

    # Select the input folder (images to convert)
    input_folder = select_folder("Select Folder to Convert Images")
    if not input_folder:
        messagebox.showerror("Error", "No input folder selected!")
        return

    # Select the output folder (where converted images will be saved)
    output_folder = select_folder("Select Destination Folder for PNGs")
    if not output_folder:
        messagebox.showerror("Error", "No output folder selected!")
        return

    # Convert images
    convert_images(input_folder, output_folder)

    # Show a success message
    messagebox.showinfo("Success", f"Images successfully converted to {output_folder}")

if __name__ == "__main__":
    main()
