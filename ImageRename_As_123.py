import os
from tkinter import Tk, filedialog

def rename_files(folder_path):
    try:
        # Get the list of files in the folder
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        
        # Sort the files to maintain a consistent order
        files.sort()

        # Rename all files sequentially
        for i, file_name in enumerate(files, start=1):  # Remove the limit of 90 files
            # Get the file extension
            file_extension = os.path.splitext(file_name)[1]
            # Create the new file name
            new_name = f"{i}{file_extension}"
            new_path = os.path.join(folder_path, new_name)
            
            # Check if the target name already exists
            if os.path.exists(new_path):
                print(f"File '{new_name}' already exists. Skipping rename for '{file_name}'.")
                continue
            
            # Rename the file
            os.rename(
                os.path.join(folder_path, file_name),
                new_path
            )
        print(f"Renaming completed. Processed {len(files)} files.")
    except Exception as e:
        print(f"An error occurred: {e}")

# GUI for folder selection
def select_folder_and_rename():
    # Create a hidden root window
    root = Tk()
    root.withdraw()  # Hide the root window
    root.attributes('-topmost', True)  # Bring the dialog to the front

    # Ask the user to select a folder
    folder_path = filedialog.askdirectory(title="Select Folder to Rename Files")
    if folder_path:
        rename_files(folder_path)
    else:
        print("No folder was selected.")

# Run the GUI
if __name__ == "__main__":
    select_folder_and_rename()
