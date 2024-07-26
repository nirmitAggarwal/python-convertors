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
        self.root.configure(bg='#0d0d0d')  # Dark background

        self.pdf_files = []
        self.output_folder = ""

        # Create Widgets
        self.create_widgets()

    def create_widgets(self):
        # Neon Style
        neon_blue = '#00bfff'
        neon_pink = '#ff69b4'
        neon_green = '#00ff00'

        # Drag and Drop Area
        self.drop_area = tk.Label(self.root, text="Drag and Drop PDF Files Here", bg='#1e1e1e', fg=neon_blue, font=('Arial', 14), width=60, height=10, relief=tk.RAISED, borderwidth=2)
        self.drop_area.pack(pady=20)
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind('<<Drop>>', self.on_drop)

        # Browse Button
        self.browse_button = tk.Button(self.root, text="Choose Output Folder", command=self.browse_folder, bg=neon_pink, fg='#ffffff', font=('Arial', 12), relief=tk.FLAT, borderwidth=2)
        self.browse_button.pack(pady=10)

        # Convert Button
        self.convert_button = tk.Button(self.root, text="Convert", command=self.convert_pdfs, bg=neon_green, fg='#ffffff', font=('Arial', 12), relief=tk.FLAT, borderwidth=2)
        self.convert_button.pack(pady=10)

        # Progress Bar
        self.progress = ttk.Progressbar(self.root, length=400, mode='determinate')
        self.progress.pack(pady=10)

        # Status Label
        self.status_label = tk.Label(self.root, text="", bg='#0d0d0d', fg=neon_blue, font=('Arial', 12))
        self.status_label.pack(pady=10)

        # Styling for Progress Bar
        self._configure_styles()

    def _configure_styles(self):
        style = ttk.Style()
        style.configure('Neon.TProgressbar',
                        troughcolor='#1e1e1e',
                        background='#00ff00',  # Neon green
                        bordercolor='#00ff00',  # Neon green
                        thickness=20)
        style.map('Neon.TProgressbar',
                  background=[('pressed', '#00ff00'),
                              ('active', '#00ff00')])

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
