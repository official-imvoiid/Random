import json
import re
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import sys
import ast

def count_occurrences(text, phrase):
    pattern = re.escape(phrase)
    return len(re.findall(pattern, text, flags=re.IGNORECASE))

def clean_text(text, phrases_to_remove):
    for phrase in phrases_to_remove:
        pattern = r'\s*' + re.escape(phrase) + r'\s*'
        text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
    return text

def clean_json_data(data, phrases_to_remove):
    if isinstance(data, list):
        return [clean_json_data(item, phrases_to_remove) for item in data]
    elif isinstance(data, dict):
        return {key: clean_json_data(value, phrases_to_remove) for key, value in data.items()}
    elif isinstance(data, str):
        for phrase in phrases_to_remove:
            occ = count_occurrences(data, phrase)
            if occ:
                print(f"Found {occ} occurrence(s) of a phrase in a string.")
        cleaned = clean_text(data, phrases_to_remove)
        return cleaned.strip()
    else:
        return data

def process_json_file(file_path, phrases_to_remove):
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Failed to load JSON file:\n{e}")
            sys.exit(1)

    full_text = json.dumps(data)
    print("Occurrences before cleaning:")
    for phrase in phrases_to_remove:
        occ = count_occurrences(full_text, phrase)
        print(f"  '{phrase}': {occ}")

    cleaned_data = clean_json_data(data, phrases_to_remove)

    full_text_cleaned = json.dumps(cleaned_data)
    print("Occurrences after cleaning:")
    for phrase in phrases_to_remove:
        occ = count_occurrences(full_text_cleaned, phrase)
        print(f"  '{phrase}': {occ}")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, indent=4, ensure_ascii=False)

def main():
    root = tk.Tk()
    root.withdraw()  # Hide main window

    file_path = filedialog.askopenfilename(
        title="Select the JSON file to edit",
        filetypes=[("JSON Files", "*.json")]
    )
    if not file_path:
        messagebox.showinfo("No File Selected", "No file was selected. Exiting program.")
        sys.exit(0)

    phrases_input = simpledialog.askstring(
        "Phrases List",
        "Enter phrases_to_remove as a Python list literal.\nLeave blank to use an empty list."
    )
    if phrases_input and phrases_input.strip():
        try:
            phrases_to_remove = ast.literal_eval(phrases_input)
            if not isinstance(phrases_to_remove, list):
                raise ValueError("Input is not a list.")
        except Exception as e:
            messagebox.showerror("Invalid Input", f"Failed to parse the list:\n{e}")
            sys.exit(1)
    else:
        phrases_to_remove = []

    processing_window = tk.Toplevel()
    processing_window.title("Processing")
    tk.Label(processing_window, text="Editing file... Please wait.").pack(padx=20, pady=20)
    processing_window.update()

    try:
        process_json_file(file_path, phrases_to_remove)
    except Exception as e:
        processing_window.destroy()
        messagebox.showerror("Error", f"An error occurred during processing:\n{e}")
        sys.exit(1)
    finally:
        processing_window.destroy()

    messagebox.showinfo("Done", "Editing complete. File has been updated.")
    sys.exit(0)

if __name__ == "__main__":
    main()
