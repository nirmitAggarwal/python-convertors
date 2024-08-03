import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pdfkit

class HtmlToPdfConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("HTML to PDF Converter")
        self.root.geometry("700x500")

        # Dark Mode Toggle
        self.dark_mode = tk.BooleanVar(value=False)

        # Initialize GUI components
        self.initialize_gui()

    def initialize_gui(self):
        # Create and configure GUI elements
        self.label = tk.Label(self.root, text="HTML to PDF Converter", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.open_button = tk.Button(self.root, text="Open HTML File", command=self.open_html)
        self.open_button.pack(pady=5)

        self.preview_button = tk.Button(self.root, text="Preview HTML Content", command=self.preview_html, state=tk.DISABLED)
        self.preview_button.pack(pady=5)

        self.convert_button = tk.Button(self.root, text="Convert to PDF", command=self.convert_to_pdf, state=tk.DISABLED)
        self.convert_button.pack(pady=5)

        self.custom_options_button = tk.Button(self.root, text="Set PDF Options", command=self.set_pdf_options, state=tk.DISABLED)
        self.custom_options_button.pack(pady=5)

        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress.pack(pady=20)

        # Apply initial dark mode settings
        self.toggle_dark_mode()

        self.html_path = None
        self.pdf_options = {}

    def toggle_dark_mode(self):
        # Apply dark mode colors to the GUI elements
        if self.dark_mode.get():
            self.root.configure(bg='#2E2E2E')
            self.label.configure(bg='#2E2E2E', fg='#FFFFFF')
            self.open_button.configure(bg='#4A4A4A', fg='#FFFFFF')
            self.preview_button.configure(bg='#4A4A4A', fg='#FFFFFF')
            self.convert_button.configure(bg='#4A4A4A', fg='#FFFFFF')
            self.custom_options_button.configure(bg='#4A4A4A', fg='#FFFFFF')
        else:
            self.root.configure(bg='#FFFFFF')
            self.label.configure(bg='#FFFFFF', fg='#000000')
            self.open_button.configure(bg='#DDDDDD', fg='#000000')
            self.preview_button.configure(bg='#DDDDDD', fg='#000000')
            self.convert_button.configure(bg='#DDDDDD', fg='#000000')
            self.custom_options_button.configure(bg='#DDDDDD', fg='#000000')

    def open_html(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("HTML Files", "*.html"), ("All Files", "*.*")]
        )
        if file_path:
            self.html_path = file_path
            self.preview_button.config(state=tk.NORMAL)
            self.convert_button.config(state=tk.NORMAL)
            self.custom_options_button.config(state=tk.NORMAL)
            messagebox.showinfo("Success", "HTML file loaded successfully!")

    def preview_html(self):
        if self.html_path:
            preview_window = tk.Toplevel(self.root)
            preview_window.title("HTML Content Preview")
            preview_window.geometry("700x400")

            with open(self.html_path, "r") as file:
                html_content = file.read()

            text_area = tk.Text(preview_window, wrap=tk.WORD)
            text_area.pack(expand=True, fill=tk.BOTH)
            text_area.insert(tk.END, html_content)
            text_area.config(state=tk.DISABLED)

    def set_pdf_options(self):
        options_window = tk.Toplevel(self.root)
        options_window.title("PDF Options")
        options_window.geometry("400x300")

        tk.Label(options_window, text="Page Size").pack(pady=5)
        self.page_size_entry = tk.Entry(options_window)
        self.page_size_entry.pack(pady=5)

        tk.Label(options_window, text="Margins (top, bottom, left, right)").pack(pady=5)
        self.margins_entry = tk.Entry(options_window)
        self.margins_entry.pack(pady=5)

        tk.Button(options_window, text="Apply", command=self.apply_pdf_options).pack(pady=10)

    def apply_pdf_options(self):
        page_size = self.page_size_entry.get()
        margins = self.margins_entry.get().split(',')

        self.pdf_options = {}
        if page_size:
            self.pdf_options['page-size'] = page_size
        if len(margins) == 4:
            self.pdf_options['margin-top'] = margins[0].strip()
            self.pdf_options['margin-bottom'] = margins[1].strip()
            self.pdf_options['margin-left'] = margins[2].strip()
            self.pdf_options['margin-right'] = margins[3].strip()

        messagebox.showinfo("Success", "PDF options applied successfully!")

    def convert_to_pdf(self):
        if self.html_path:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
            )
            if save_path:
                try:
                    self.progress['value'] = 0
                    self.root.update_idletasks()

                    # Configure pdfkit to use wkhtmltopdf
                    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
                    pdfkit.from_file(self.html_path, save_path, options=self.pdf_options, configuration=config)

                    self.progress['value'] = 100
                    self.root.update_idletasks()
                    messagebox.showinfo("Success", "PDF file saved successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save PDF file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HtmlToPdfConverter(root)
    root.mainloop()
