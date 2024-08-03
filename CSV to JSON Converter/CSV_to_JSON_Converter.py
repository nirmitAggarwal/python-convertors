import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import csv
import json

class CsvToJsonConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV to JSON Converter")
        self.root.geometry("600x400")

        self.label = tk.Label(root, text="CSV to JSON Converter", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.open_button = tk.Button(root, text="Open CSV File", command=self.open_csv)
        self.open_button.pack(pady=5)

        self.preview_button = tk.Button(root, text="Preview CSV Data", command=self.preview_csv, state=tk.DISABLED)
        self.preview_button.pack(pady=5)

        self.convert_button = tk.Button(root, text="Convert to JSON", command=self.convert_to_json, state=tk.DISABLED)
        self.convert_button.pack(pady=5)

        self.progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress.pack(pady=20)

        self.csv_data = None
        self.headers = None

    def open_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r") as file:
                    reader = csv.DictReader(file)
                    self.headers = reader.fieldnames
                    self.csv_data = list(reader)
                messagebox.showinfo("Success", "CSV file loaded successfully!")
                self.preview_button.config(state=tk.NORMAL)
                self.convert_button.config(state=tk.NORMAL)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV file: {e}")

    def preview_csv(self):
        if self.csv_data:
            preview_window = tk.Toplevel(self.root)
            preview_window.title("CSV Data Preview")
            preview_window.geometry("500x300")
            
            text_area = tk.Text(preview_window, wrap=tk.WORD)
            text_area.pack(expand=True, fill=tk.BOTH)
            text_area.insert(tk.END, json.dumps(self.csv_data, indent=4))
            text_area.config(state=tk.DISABLED)

    def convert_to_json(self):
        if self.csv_data:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
            )
            if save_path:
                try:
                    self.progress['value'] = 0
                    self.root.update_idletasks()

                    with open(save_path, "w") as json_file:
                        json.dump(self.csv_data, json_file, indent=4)
                        self.progress['value'] = 100
                        self.root.update_idletasks()
                        messagebox.showinfo("Success", "JSON file saved successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save JSON file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CsvToJsonConverter(root)
    root.mainloop()
