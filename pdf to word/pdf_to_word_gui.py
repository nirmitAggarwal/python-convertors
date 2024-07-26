import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
from pdf2docx import Converter
from plyer import notification

class PDFtoWordApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to DOCX Converter")
        self.root.geometry("500x400")

        self.pdf_files = []
        self.output_folder = ""

        # Create Widgets
        self.create_widgets()

    def create_widgets(self):
        # Drag and Drop Area
        self.drop_area = tk.Label(self.root, text="Drag and Drop PDF Files Here", bg="lightgray", width=60, height=10)
        self.drop_area.pack(pady=20)
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind('<<Drop>>', self.on_drop)

        # Browse Button
        self.browse_button = tk.Button(self.root, text="Choose Output Folder", command=self.browse_folder)
        self.browse_button.pack(pady=10)

        # Convert Button
        self.convert_button = tk.Button(self.root, text="Convert", command=self.convert_pdfs)
        self.convert_button.pack(pady=10)

        # Progress Bar
        self.progress = ttk.Progressbar(self.root, length=400, mode='determinate')
        self.progress.pack(pady=10)
        
        # Status Label
        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack(pady=10)

    def on_drop(self, event):
        file_paths = self.root.tk.splitlist(event.data)
        self.pdf_files = [path for path in file_paths if path.lower().endswith(".pdf")]
        if self.pdf_files:
            messagebox.showinfo("Files Added", f"{len(self.pdf_files)} PDF files loaded.")

    def browse_folder(self):
        self.output_folder = filedialog.askdirectory()
        if self.output_folder:
            messagebox.showinfo("Folder Selected", f"Output will be saved to: {self.output_folder}")

    def convert_pdfs(self):
        if not self.pdf_files:
            messagebox.showwarning("No Files", "Please drag and drop PDF files.")
            return

        if not self.output_folder:
            messagebox.showwarning("No Folder", "Please choose an output folder.")
            return

        total_files = len(self.pdf_files)
        self.progress['maximum'] = total_files
        self.progress['value'] = 0
        self.status_label.config(text="Converting...")

        for i, pdf_file in enumerate(self.pdf_files):
            try:
                docx_file = os.path.join(self.output_folder, os.path.basename(pdf_file).replace('.pdf', '.docx'))
                converter = Converter(pdf_file)
                converter.convert(docx_file, start=0, end=None)
                converter.close()
                self.progress['value'] = i + 1
                self.root.update_idletasks()
            except Exception as e:
                messagebox.showerror("Conversion Error", f"Error converting {pdf_file}: {e}")
                return

        self.status_label.config(text="Conversion Complete")
        notification.notify(
            title='PDF to DOCX Converter',
            message='All PDF files have been converted successfully!',
            timeout=10
        )

if __name__ == "__main__":
    root = TkinterDnD.Tk()  # Correctly initialize TkinterDnD
    app = PDFtoWordApp(root)
    root.mainloop()
