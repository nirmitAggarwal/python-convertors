import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from ttkthemes import ThemedTk
from tkinter import ttk

def csv_to_excel(csv_file_path, excel_file_path, progress_bar):
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file_path)
        progress_bar['value'] = 50
        root.update_idletasks()
        
        # Write the DataFrame to an Excel file
        df.to_excel(excel_file_path, index=False)
        progress_bar['value'] = 100
        root.update_idletasks()
        
        messagebox.showinfo("Success", f"CSV file has been successfully converted to Excel file at {excel_file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        progress_bar['value'] = 0

def browse_csv_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    csv_entry.delete(0, tk.END)
    csv_entry.insert(0, file_path)

def browse_excel_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    excel_entry.delete(0, tk.END)
    excel_entry.insert(0, file_path)

def convert_file():
    csv_file_path = csv_entry.get()
    excel_file_path = excel_entry.get()
    if csv_file_path and excel_file_path:
        csv_to_excel(csv_file_path, excel_file_path, progress_bar)
    else:
        messagebox.showwarning("Input required", "Please select both CSV file and Excel file path.")

# Create the main window with a dark theme
root = ThemedTk(theme="equilux")
root.title("CSV to Excel Converter")

# Style
style = ttk.Style(root)
root.configure(bg='#2b2b2b')

style.configure("TLabel", foreground='#ffffff', background='#2b2b2b')
style.configure("TButton", foreground='#ffffff', background='#444444', borderwidth=1, focusthickness=3, focuscolor='none', relief="flat")
style.map("TButton", background=[('active', '#666666')])
style.configure("TEntry", fieldbackground='#444444', foreground='#ffffff', borderwidth=1)
style.map("TEntry", background=[('active', '#555555')])
style.configure("TProgressbar", troughcolor='#444444', background='#00ff00', borderwidth=0)

# CSV file selection
csv_label = ttk.Label(root, text="Select CSV file:")
csv_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
csv_entry = ttk.Entry(root, width=50)
csv_entry.grid(row=0, column=1, padx=10, pady=10)
csv_browse_button = ttk.Button(root, text="Browse", command=browse_csv_file)
csv_browse_button.grid(row=0, column=2, padx=10, pady=10)

# Excel file selection
excel_label = ttk.Label(root, text="Save as Excel file:")
excel_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
excel_entry = ttk.Entry(root, width=50)
excel_entry.grid(row=1, column=1, padx=10, pady=10)
excel_browse_button = ttk.Button(root, text="Browse", command=browse_excel_file)
excel_browse_button.grid(row=1, column=2, padx=10, pady=10)

# Convert button
convert_button = ttk.Button(root, text="Convert", command=convert_file)
convert_button.grid(row=2, columnspan=3, pady=20)

# Progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.grid(row=3, columnspan=3, pady=10)

# Run the GUI event loop
root.mainloop()
