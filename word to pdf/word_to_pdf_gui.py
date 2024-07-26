import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from docx2pdf import convert
import os

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Word files", "*.docx")])
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

def drop(event):
    file_entry.delete(0, tk.END)
    file_entry.insert(0, event.data)

def convert_to_pdf():
    input_file = file_entry.get()
    if not input_file:
        messagebox.showerror("Error", "Please select a Word file")
        return
    
    output_file = os.path.splitext(input_file)[0] + ".pdf"
    
    try:
        convert(input_file, output_file)
        messagebox.showinfo("Success", f"File converted successfully:\n{output_file}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Create the main window
root = TkinterDnD.Tk()
root.title("Word to PDF Converter")

# Create and place widgets
tk.Label(root, text="Select or Drag and Drop Word File:").pack(pady=10)

file_entry = tk.Entry(root, width=50)
file_entry.pack(pady=5)

file_entry.drop_target_register(DND_FILES)
file_entry.dnd_bind('<<Drop>>', drop)

tk.Button(root, text="Browse", command=select_file).pack(pady=5)
tk.Button(root, text="Convert to PDF", command=convert_to_pdf).pack(pady=10)

# Run the application
root.mainloop()
