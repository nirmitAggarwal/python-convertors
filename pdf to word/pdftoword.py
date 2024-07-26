import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from pdf2docx import Converter
from threading import Thread
from plyer import notification

class PDFToWordConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Word Converter")
        self.root.geometry("400x350")

        self.create_widgets()
        self.setup_drag_and_drop()

    def create_widgets(self):
        # PDF File selection
        self.pdf_label = tk.Label(self.root, text="Select PDF file:")
        self.pdf_label.pack(pady=10)

        self.pdf_button = tk.Button(self.root, text="Browse", command=self.select_pdf)
        self.pdf_button.pack()

        self.pdf_path = tk.StringVar()
        self.pdf_entry = tk.Entry(self.root, textvariable=self.pdf_path, width=50)
        self.pdf_entry.pack(pady=5)

        # Output Folder selection
        self.folder_label = tk.Label(self.root, text="Select output folder (optional):")
        self.folder_label.pack(pady=10)

        self.folder_button = tk.Button(self.root, text="Browse", command=self.select_folder)
        self.folder_button.pack()

        self.folder_path = tk.StringVar()
        self.folder_entry = tk.Entry(self.root, textvariable=self.folder_path, width=50)
        self.folder_entry.pack(pady=5)

        # Loading Label
        self.loading_label = tk.Label(self.root, text="", fg="blue")
        self.loading_label.pack(pady=10)

        # Progress Bar
        self.progress = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress, maximum=100, mode='determinate')
        self.progress_bar.pack(pady=10, fill=tk.X, padx=20)

        # Convert button
        self.convert_button = tk.Button(self.root, text="Convert", command=self.start_conversion)
        self.convert_button.pack(pady=20)

    def setup_drag_and_drop(self):
        # Register the window for drag-and-drop
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)

    def on_drop(self, event):
        # Extract the file path from the event
        file_path = event.data.strip().strip('{}')
        if os.path.isfile(file_path):
            self.pdf_path.set(file_path)
        else:
            messagebox.showwarning("Drop Error", "Dropped item is not a valid file.")

    def select_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.pdf_path.set(file_path)

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_path.set(folder_path)

    def start_conversion(self):
        pdf_file = self.pdf_path.get()
        output_folder = self.folder_path.get()

        if not pdf_file:
            messagebox.showwarning("Input Error", "Please select a PDF file.")
            return

        if not os.path.isfile(pdf_file):
            messagebox.showerror("File Error", "The selected PDF file does not exist.")
            return

        # Determine output folder
        if not output_folder:
            output_folder = os.path.dirname(pdf_file)

        # Disable button and show loading message
        self.convert_button.config(state=tk.DISABLED)
        self.loading_label.config(text="Converting... Please wait...")
        self.progress.set(0)

        # Start the conversion in a separate thread
        thread = Thread(target=self.convert_pdf_to_word, args=(pdf_file, output_folder))
        thread.start()

    def convert_pdf_to_word(self, pdf_file, output_folder):
        # Generate the output Word file path
        word_file = os.path.join(output_folder, os.path.splitext(os.path.basename(pdf_file))[0] + '.docx')

        try:
            cv = Converter(pdf_file)
            cv.convert(word_file, start=0, end=None)

            # Simulate progress update
            for i in range(0, 101, 10):
                self.root.after(i * 100, self.update_progress, i)
            
            cv.close()

            # Show a notification
            self.root.after(0, self.show_notification, word_file)
        except Exception as e:
            self.root.after(0, self.show_error, f"An error occurred: {str(e)}")
        finally:
            # Update GUI elements in the main thread
            self.root.after(0, self.update_gui_after_conversion)

    def update_progress(self, value):
        self.progress.set(value)

    def show_notification(self, word_file):
        try:
            notification.notify(
                title='Conversion Complete',
                message=f"Conversion complete: {word_file}",
                timeout=10
            )
            print("Notification sent successfully")
        except Exception as e:
            print(f"Failed to send notification: {str(e)}")

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def update_gui_after_conversion(self):
        # Re-enable the Convert button and hide the loading message
        self.convert_button.config(state=tk.NORMAL)
        self.loading_label.config(text="")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = PDFToWordConverterApp(root)
    root.mainloop()
