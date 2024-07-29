import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os

def excel_to_csv(excel_file_path, sheet_name, csv_file_path, progress_var):
    try:
        progress_var.set(10)
        root.update_idletasks()
        
        # Read the Excel file
        df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
        progress_var.set(60)
        root.update_idletasks()
        
        # Convert the DataFrame to a CSV file
        df.to_csv(csv_file_path, index=False)
        progress_var.set(100)
        root.update_idletasks()
        
        messagebox.showinfo("Success", f"Excel file '{os.path.basename(excel_file_path)}' has been converted to CSV file '{os.path.basename(csv_file_path)}'")
        progress_var.set(0)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to convert Excel to CSV: {e}")
        progress_var.set(0)

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

    excel_to_csv(excel_file_path.get(), sheet_name, csv_file_path.get(), progress_var)

# Create the main window
root = tk.Tk()
root.title("Excel to CSV Converter")
root.geometry("500x300")
root.resizable(False, False)
root.configure(bg="#2b2b2b")

# Styles
style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", background="#2b2b2b", foreground="#e1e1e1", font=("Helvetica", 10))
style.configure("TButton", background="#4f4f4f", foreground="#e1e1e1", font=("Helvetica", 10), padding=5)
style.map("TButton", background=[("active", "#6c6c6c")])
style.configure("TEntry", background="#4f4f4f", foreground="#e1e1e1", fieldbackground="#4f4f4f", font=("Helvetica", 10))
style.configure("TProgressbar", thickness=20, background="#4caf50")

# Create and place widgets
ttk.Label(root, text="Excel File:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
excel_file_path = tk.StringVar()
ttk.Entry(root, textvariable=excel_file_path, width=40).grid(row=0, column=1, padx=10, pady=10)
ttk.Button(root, text="Browse", command=browse_excel_file).grid(row=0, column=2, padx=10, pady=10)

ttk.Label(root, text="Sheet Name:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
sheet_name_entry = ttk.Entry(root, width=40)
sheet_name_entry.grid(row=1, column=1, padx=10, pady=10)
sheet_name_entry.insert(0, "Sheet1")  # Default sheet name

ttk.Label(root, text="Save CSV As:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
csv_file_path = tk.StringVar()
ttk.Entry(root, textvariable=csv_file_path, width=40).grid(row=2, column=1, padx=10, pady=10)
ttk.Button(root, text="Browse", command=browse_save_location).grid(row=2, column=2, padx=10, pady=10)

ttk.Button(root, text="Convert", command=convert_file).grid(row=3, column=0, columnspan=3, pady=20)

# Progress bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

# Run the GUI event loop
root.mainloop()
