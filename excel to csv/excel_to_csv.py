import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

def excel_to_csv(excel_file_path, sheet_name, csv_file_path):
    try:
        # Read the Excel file
        df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
        # Convert the DataFrame to a CSV file
        df.to_csv(csv_file_path, index=False)
        messagebox.showinfo("Success", f"Excel file '{excel_file_path}' has been converted to CSV file '{csv_file_path}'")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to convert Excel to CSV: {e}")

def browse_excel_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    excel_file_path.set(file_path)

def browse_save_location():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    csv_file_path.set(file_path)

def convert_file():
    if not excel_file_path.get() or not csv_file_path.get():
        messagebox.showerror("Error", "Please select both Excel file and CSV save location.")
        return

    sheet_name = sheet_name_entry.get()
    if not sheet_name:
        messagebox.showerror("Error", "Please enter the sheet name.")
        return

    excel_to_csv(excel_file_path.get(), sheet_name, csv_file_path.get())

# Create the main window
root = tk.Tk()
root.title("Excel to CSV Converter")

# Create and place widgets
tk.Label(root, text="Excel File:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
excel_file_path = tk.StringVar()
tk.Entry(root, textvariable=excel_file_path, width=40).grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=browse_excel_file).grid(row=0, column=2, padx=10, pady=10)

tk.Label(root, text="Sheet Name:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
sheet_name_entry = tk.Entry(root, width=40)
sheet_name_entry.grid(row=1, column=1, padx=10, pady=10)
sheet_name_entry.insert(0, "Sheet1")  # Default sheet name

tk.Label(root, text="Save CSV As:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
csv_file_path = tk.StringVar()
tk.Entry(root, textvariable=csv_file_path, width=40).grid(row=2, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=browse_save_location).grid(row=2, column=2, padx=10, pady=10)

tk.Button(root, text="Convert", command=convert_file).grid(row=3, column=0, columnspan=3, pady=20)

# Run the GUI event loop
root.mainloop()
