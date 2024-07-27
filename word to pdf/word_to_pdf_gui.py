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
        self.configure(bg="#1a1a1a")

        self.input_files = []
        self.output_folder = os.getcwd()

        # Load custom font
        self.font = ("Helvetica", 12)

        # Input Frame
        self.input_frame = tk.Frame(self, bg="#1a1a1a")
        self.input_frame.pack(pady=20)

        self.input_label = tk.Label(self.input_frame, text="Drag and Drop Files Here or Click 'Browse Files'", font=self.font, fg="#39ff14", bg="#1a1a1a")
        self.input_label.pack()

        self.browse_button = tk.Button(self.input_frame, text="Browse Files", command=self.browse_files, font=self.font, bg="#39ff14", fg="#000000", activebackground="#39ff14", activeforeground="#000000")
        self.browse_button.pack(pady=10)

        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_files)

        # Output Frame
        self.output_frame = tk.Frame(self, bg="#1a1a1a")
        self.output_frame.pack(pady=20)

        self.output_label = tk.Label(self.output_frame, text=f"Output Folder: {self.output_folder}", font=self.font, fg="#39ff14", bg="#1a1a1a")
        self.output_label.pack()

        self.browse_output_button = tk.Button(self.output_frame, text="Browse Output Folder", command=self.browse_output_folder, font=self.font, bg="#39ff14", fg="#000000", activebackground="#39ff14", activeforeground="#000000")
        self.browse_output_button.pack(pady=10)

        # Progress Frame
        self.progress_frame = tk.Frame(self, bg="#1a1a1a")
        self.progress_frame.pack(pady=20)

        self.progress_label = tk.Label(self.progress_frame, text="", font=self.font, fg="#39ff14", bg="#1a1a1a")
        self.progress_label.pack()

        self.progress_bar = ttk.Progressbar(self.progress_frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack()

        # Convert Button
        self.convert_button = tk.Button(self, text="Convert to PDF", command=self.convert_to_pdf, font=self.font, bg="#39ff14", fg="#000000", activebackground="#39ff14", activeforeground="#000000")
        self.convert_button.pack(pady=20)

        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TProgressbar", troughcolor="#1a1a1a", background="#39ff14", thickness=20)

        # Adding hover effect
        self.add_hover_effect(self.browse_button)
        self.add_hover_effect(self.browse_output_button)
        self.add_hover_effect(self.convert_button)

    def add_hover_effect(self, widget):
        widget.bind("<Enter>", lambda e: widget.config(bg="#00ff00"))
        widget.bind("<Leave>", lambda e: widget.config(bg="#39ff14"))

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
