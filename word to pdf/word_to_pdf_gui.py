import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from docx2pdf import convert
from threading import Thread
import os
import requests

# Function to add Google Fonts
def fetch_google_font(font_name):
    font_url = f"https://fonts.googleapis.com/css2?family={font_name.replace(' ', '+')}&display=swap"
    try:
        response = requests.get(font_url)
        response.raise_for_status()
        with open(f"{font_name.replace(' ', '_')}.css", "w") as f:
            f.write(response.text)
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch Google Font: {e}")
        return False

# Fetch the Google Font "Poppins"
fetch_google_font("Poppins")

class WordToPDFConverter(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("Word to PDF Converter")
        self.geometry("600x400")
        self.configure(bg="#f0f4f8")

        self.input_files = []
        self.output_folder = os.getcwd()

        # Load custom font
        self.font = ("Poppins", 12)

        # Input Frame
        self.input_frame = tk.Frame(self, bg="#f0f4f8")
        self.input_frame.pack(pady=20)

        self.input_label = tk.Label(self.input_frame, text="Drag and Drop Files Here or Click 'Browse Files'", font=self.font, bg="#f0f4f8", fg="#333")
        self.input_label.pack()

        self.browse_button = tk.Button(self.input_frame, text="Browse Files", command=self.browse_files, font=self.font, bg="#3b82f6", fg="#fff", relief="flat", padx=20, pady=10, bd=5, highlightbackground="#3b82f6", highlightcolor="#3b82f6")
        self.browse_button.pack(pady=10)
        self.add_neomorphism_effect(self.browse_button, inset=False)

        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_files)

        # Output Frame
        self.output_frame = tk.Frame(self, bg="#f0f4f8")
        self.output_frame.pack(pady=20)

        self.output_label = tk.Label(self.output_frame, text=f"Output Folder: {self.output_folder}", font=self.font, bg="#f0f4f8", fg="#333")
        self.output_label.pack()

        self.browse_output_button = tk.Button(self.output_frame, text="Browse Output Folder", command=self.browse_output_folder, font=self.font, bg="#3b82f6", fg="#fff", relief="flat", padx=20, pady=10, bd=5, highlightbackground="#3b82f6", highlightcolor="#3b82f6")
        self.browse_output_button.pack(pady=10)
        self.add_neomorphism_effect(self.browse_output_button, inset=False)

        # Progress Frame
        self.progress_frame = tk.Frame(self, bg="#f0f4f8")
        self.progress_frame.pack(pady=20)

        self.progress_label = tk.Label(self.progress_frame, text="", font=self.font, bg="#f0f4f8", fg="#333")
        self.progress_label.pack()

        self.progress_bar = ttk.Progressbar(self.progress_frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack()
        self.style_progress_bar()

        # Convert Button
        self.convert_button = tk.Button(self, text="Convert to PDF", command=self.convert_to_pdf, font=self.font, bg="#3b82f6", fg="#fff", relief="flat", padx=20, pady=10, bd=5, highlightbackground="#3b82f6", highlightcolor="#3b82f6")
        self.convert_button.pack(pady=20)
        self.add_neomorphism_effect(self.convert_button, inset=False)

    def add_neomorphism_effect(self, widget, inset=True):
        widget.config(bd=0, highlightthickness=0)
        if inset:
            widget.config(highlightbackground="#a5b4fc", highlightcolor="#a5b4fc")
            widget.bind("<Enter>", lambda e: widget.config(bg="#2563eb", relief="sunken", highlightbackground="#a5b4fc", highlightcolor="#a5b4fc"))
            widget.bind("<Leave>", lambda e: widget.config(bg="#3b82f6", relief="flat"))
        else:
            widget.config(highlightbackground="#a5b4fc", highlightcolor="#a5b4fc")
            widget.bind("<Enter>", lambda e: widget.config(bg="#2563eb", relief="raised", highlightbackground="#a5b4fc", highlightcolor="#a5b4fc"))
            widget.bind("<Leave>", lambda e: widget.config(bg="#3b82f6", relief="flat"))

    def style_progress_bar(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TProgressbar", troughcolor="#e0e7ff", background="#3b82f6", thickness=20, bordercolor="#f0f4f8", lightcolor="#f0f4f8", darkcolor="#f0f4f8")

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
