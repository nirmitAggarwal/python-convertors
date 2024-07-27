import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from docx2pdf import convert
from threading import Thread
import os

class WordToPDFConverter(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("Word to PDF Converter")
        self.geometry("600x400")
        
        self.input_files = []
        self.output_folder = os.getcwd()

        # Input Frame
        self.input_frame = tk.Frame(self)
        self.input_frame.pack(pady=20)

        self.input_label = tk.Label(self.input_frame, text="Drag and Drop Files Here or Click 'Browse Files'")
        self.input_label.pack()

        self.browse_button = tk.Button(self.input_frame, text="Browse Files", command=self.browse_files)
        self.browse_button.pack(pady=10)

        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_files)

        # Output Frame
        self.output_frame = tk.Frame(self)
        self.output_frame.pack(pady=20)

        self.output_label = tk.Label(self.output_frame, text=f"Output Folder: {self.output_folder}")
        self.output_label.pack()

        self.browse_output_button = tk.Button(self.output_frame, text="Browse Output Folder", command=self.browse_output_folder)
        self.browse_output_button.pack(pady=10)

        # Progress Frame
        self.progress_frame = tk.Frame(self)
        self.progress_frame.pack(pady=20)

        self.progress_label = tk.Label(self.progress_frame, text="")
        self.progress_label.pack()

        self.progress_bar = ttk.Progressbar(self.progress_frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack()

        # Convert Button
        self.convert_button = tk.Button(self, text="Convert to PDF", command=self.convert_to_pdf)
        self.convert_button.pack(pady=20)

    def browse_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Word files", "*.docx")])
        if files:
            self.input_files.extend(files)
            self.input_label.config(text=f"{len(self.input_files)} files selected")

    def drop_files(self, event):
        files = self.splitlist(event.data)
        self.input_files.extend(files)
        self.input_label.config(text=f"{len(self.input_files)} files selected")

    def browse_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            self.output_label.config(text=f"Output Folder: {self.output_folder}")

    def convert_to_pdf(self):
        if not self.input_files:
            messagebox.showwarning("No files selected", "Please select one or more DOCX files to convert.")
            return

        self.progress_label.config(text="Conversion in progress...")
        self.progress_bar["maximum"] = len(self.input_files)
        self.progress_bar["value"] = 0

        self.convert_button.config(state="disabled")
        self.browse_button.config(state="disabled")
        self.browse_output_button.config(state="disabled")

        thread = Thread(target=self.perform_conversion)
        thread.start()

    def perform_conversion(self):
        try:
            for idx, file in enumerate(self.input_files):
                output_file = os.path.join(self.output_folder, os.path.basename(file).replace(".docx", ".pdf"))
                convert(file, output_file)
                self.progress_bar["value"] = idx + 1
                self.update_idletasks()
            
            messagebox.showinfo("Conversion Complete", "All files have been converted to PDF.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during conversion: {e}")
        finally:
            self.progress_label.config(text="")
            self.convert_button.config(state="normal")
            self.browse_button.config(state="normal")
            self.browse_output_button.config(state="normal")

if __name__ == "__main__":
    app = WordToPDFConverter()
    app.mainloop()
