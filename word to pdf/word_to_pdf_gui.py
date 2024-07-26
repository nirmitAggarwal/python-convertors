import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from docx2pdf import convert
import os
import threading

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Word files", "*.docx")])
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

def drop(event):
    file_path = event.data.strip('{}')
    if os.path.isfile(file_path) and file_path.lower().endswith('.docx'):
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)
    else:
        messagebox.showerror("Error", "Please drop a valid .docx file")

def convert_to_pdf():
    input_file = file_entry.get()
    if not input_file or not input_file.lower().endswith('.docx'):
        messagebox.showerror("Error", "Please select a valid Word file")
        return
    
    output_file = os.path.splitext(input_file)[0] + ".pdf"
    
    def conversion_task():
        try:
            progress_bar.start()
            convert(input_file, output_file)
            progress_bar.stop()
            messagebox.showinfo("Success", f"File converted successfully:\n{output_file}")
        except Exception as e:
            progress_bar.stop()
            messagebox.showerror("Error", str(e))
    
    threading.Thread(target=conversion_task).start()

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

# Progress bar
progress_bar = ttk.Progressbar(root, mode='indeterminate')
progress_bar.pack(pady=10, fill=tk.X)

# Run the application
root.mainloop()
