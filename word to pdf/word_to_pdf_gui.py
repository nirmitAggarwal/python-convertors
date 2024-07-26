import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from ttkthemes import ThemedStyle
from docx2pdf import convert
import threading
import os

class WordToPDFConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Word to PDF Converter")
        self.style = ThemedStyle(root)
        self.style.set_theme("breeze")
        self.files = []
        
        self.create_widgets()
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.add_files)

    def create_widgets(self):
        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.add_button = ttk.Button(self.frame, text="Add Files", command=self.browse_files)
        self.add_button.grid(row=0, column=0, padx=5, pady=5)

        self.convert_button = ttk.Button(self.frame, text="Convert", command=self.convert_files)
        self.convert_button.grid(row=0, column=1, padx=5, pady=5)

        self.progress = ttk.Progressbar(self.frame, orient="horizontal", mode="determinate")
        self.progress.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)

        self.file_listbox = tk.Listbox(self.frame, selectmode=tk.MULTIPLE, height=10)
        self.file_listbox.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)

    def browse_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Word Files", "*.docx")])
        if files:
            self.add_files_to_list(files)

    def add_files(self, event):
        files = self.root.tk.splitlist(event.data)
        self.add_files_to_list(files)

    def add_files_to_list(self, files):
        for file in files:
            if file not in self.files:
                self.files.append(file)
                self.file_listbox.insert(tk.END, file)

    def convert_files(self):
        if not self.files:
            messagebox.showwarning("No files", "Please add files to convert.")
            return

        self.progress["value"] = 0
        self.progress["maximum"] = len(self.files)

        def conversion_task():
            for file in self.files:
                try:
                    convert(file, os.path.splitext(file)[0] + ".pdf")
                    self.progress["value"] += 1
                except Exception as e:
                    messagebox.showerror("Conversion error", str(e))
                    self.progress["value"] += 1
                    continue
            messagebox.showinfo("Done", "Conversion completed.")
        
        threading.Thread(target=conversion_task).start()

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = WordToPDFConverter(root)
    root.mainloop()
