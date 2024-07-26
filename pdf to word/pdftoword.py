import os
import tkinter as tk
from tkinter import filedialog, messagebox
from pdf2docx import Converter
from threading import Thread
from plyer import notification

class PDFToWordConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Word Converter")
        self.root.geometry("400x200")

        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        # PDF File selection
        self.pdf_label = tk.Label(self.root, text="Select PDF file:")
        self.pdf_label.pack(pady=10)

        self.pdf_button = tk.Button(self.root, text="Browse", command=self.select_pdf)
        self.pdf_button.pack()

        self.pdf_path = tk.StringVar()
        self.pdf_entry = tk.Entry(self.root, textvariable=self.pdf_path, width=50)
        self.pdf_entry.pack(pady=5)

        # Loading Label
        self.loading_label = tk.Label(self.root, text="", fg="blue")
        self.loading_label.pack(pady=10)

        # Convert button
        self.convert_button = tk.Button(self.root, text="Convert", command=self.start_conversion)
        self.convert_button.pack(pady=20)

    def select_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.pdf_path.set(file_path)

    def start_conversion(self):
        pdf_file = self.pdf_path.get()

        if not pdf_file:
            messagebox.showwarning("Input Error", "Please select a PDF file.")
            return

        if not os.path.isfile(pdf_file):
            messagebox.showerror("File Error", "The selected PDF file does not exist.")
            return

        # Disable button and show loading message
        self.convert_button.config(state=tk.DISABLED)
        self.loading_label.config(text="Converting... Please wait...")

        # Start the conversion in a separate thread
        thread = Thread(target=self.convert_pdf_to_word, args=(pdf_file,))
        thread.start()

    def convert_pdf_to_word(self, pdf_file):
        # Generate the output Word file path
        word_file = os.path.splitext(pdf_file)[0] + '.docx'

        try:
            cv = Converter(pdf_file)
            cv.convert(word_file, start=0, end=None)
            cv.close()

            # Show a notification
            self.root.after(0, self.show_notification, word_file)
        except Exception as e:
            self.root.after(0, self.show_error, f"An error occurred: {str(e)}")
        finally:
            # Update GUI elements in the main thread
            self.root.after(0, self.update_gui_after_conversion)

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
    root = tk.Tk()
    app = PDFToWordConverterApp(root)
    root.mainloop()
