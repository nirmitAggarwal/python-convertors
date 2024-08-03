import tkinter as tk
from tkinter import filedialog, messagebox
import json
import csv
import os

class JsonToCsvConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON to CSV Converter")
        self.root.geometry("400x200")

        self.label = tk.Label(root, text="JSON to CSV Converter", font=("Helvetica", 16))
        self.label.pack(pady=20)

        self.open_button = tk.Button(root, text="Open JSON File", command=self.open_json)
        self.open_button.pack(pady=10)

        self.convert_button = tk.Button(root, text="Convert to CSV", command=self.convert_to_csv, state=tk.DISABLED)
        self.convert_button.pack(pady=10)

        self.json_data = None

    def open_json(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r") as file:
                    self.json_data = json.load(file)
                messagebox.showinfo("Success", "JSON file loaded successfully!")
                self.convert_button.config(state=tk.NORMAL)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load JSON file: {e}")

    def convert_to_csv(self):
        if self.json_data:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
            )
            if save_path:
                try:
                    with open(save_path, "w", newline='') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        if isinstance(self.json_data, list):
                            # Extract headers from keys of the first dictionary
                            headers = self.json_data[0].keys()
                            csv_writer.writerow(headers)
                            for entry in self.json_data:
                                csv_writer.writerow(entry.values())
                        elif isinstance(self.json_data, dict):
                            # Handle a single dictionary as a list with one element
                            headers = self.json_data.keys()
                            csv_writer.writerow(headers)
                            csv_writer.writerow(self.json_data.values())
                        messagebox.showinfo("Success", "CSV file saved successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save CSV file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = JsonToCsvConverter(root)
    root.mainloop()
