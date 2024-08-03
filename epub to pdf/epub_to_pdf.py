import logging
from ebooklib import epub
from fpdf import FPDF
from bs4 import BeautifulSoup
from PIL import Image
import io
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class EPUBtoPDFConverter:
    def __init__(self, epub_path, pdf_path):
        self.epub_path = epub_path
        self.pdf_path = pdf_path
        self.book = None
        self.pdf = FPDF()
        self.font = 'Arial'
        self.font_size = 12
        self.metadata = {}

    def convert(self):
        logging.info("Starting conversion.")
        self.load_epub()
        if self.book:
            self.create_pdf()
            self.add_metadata()
            self.save_pdf()
        return "Conversion completed successfully."

    def load_epub(self):
        logging.info(f"Loading EPUB file: {self.epub_path}")
        try:
            self.book = epub.read_epub(self.epub_path)
            logging.info("EPUB file loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading EPUB file: {e}")

    def create_pdf(self):
        logging.info("Creating PDF content.")
        self.pdf.add_page()
        self.pdf.set_font(self.font, size=self.font_size)

        for item in self.book.get_items():
            try:
                if item.get_type() == epub.EpubHtml:
                    self.process_html_item(item)
                elif item.get_type() == epub.EpubImage:
                    self.process_image_item(item)
                elif item.get_type() == epub.EpubNav:
                    self.process_nav_item(item)
                else:
                    logging.warning(f"Unsupported item type: {item.get_type()}")
            except Exception as e:
                logging.error(f"Error processing item: {e}")

    def process_html_item(self, item):
        logging.info(f"Processing HTML item: {item.get_id()}")
        content = item.get_body_content().decode('utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        text = self.clean_html(soup)
        self.pdf.multi_cell(0, 10, txt=text)
        logging.info("Added HTML content to PDF.")

    def process_image_item(self, item):
        logging.info(f"Processing image item: {item.get_id()}")
        image_data = io.BytesIO(item.get_body_content())
        image = Image.open(image_data)
        image_path = f"temp_{item.get_id()}.jpg"
        image.save(image_path)
        self.pdf.add_page()
        self.pdf.image(image_path, x=10, y=10)
        logging.info("Added image to PDF.")

    def process_nav_item(self, item):
        logging.info(f"Processing navigation item: {item.get_id()}")
        # Implement handling for navigation items if needed
        logging.info("Navigation items are not processed.")

    def clean_html(self, soup):
        """Clean HTML content for PDF."""
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()
        return '\n'.join(p.get_text() for p in soup.find_all('p'))

    def add_metadata(self):
        if self.book:
            self.metadata = {
                "title": self.book.get_metadata('DC', 'title'),
                "author": self.book.get_metadata('DC', 'creator'),
                "language": self.book.get_metadata('DC', 'language'),
                "pub_date": self.book.get_metadata('DC', 'date'),
                "publisher": self.book.get_metadata('DC', 'publisher'),
                "identifier": self.book.get_metadata('DC', 'identifier')
            }
            self.pdf.set_title(self.metadata.get("title", ["Untitled"])[0] or '')
            self.pdf.set_author(self.metadata.get("author", ["Unknown"])[0] or '')
            self.pdf.set_subject(f"Language: {self.metadata.get('language', ['Unknown'])[0] or ''}")
            self.pdf.set_creator(self.metadata.get("publisher", ["Unknown"])[0] or '')
            logging.info(f"Metadata added: {self.metadata}")

    def save_pdf(self):
        try:
            logging.info(f"Saving PDF to: {self.pdf_path}")
            self.pdf.output(self.pdf_path)
            logging.info(f"PDF saved as '{self.pdf_path}'")
        except Exception as e:
            logging.error(f"Error saving PDF: {e}")

class EPUBtoPDFGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EPUB to PDF Converter")
        self.create_widgets()

    def create_widgets(self):
        # EPUB File Selection
        tk.Label(self.root, text="Select EPUB file:").grid(row=0, column=0, padx=10, pady=10)
        self.epub_entry = tk.Entry(self.root, width=50)
        self.epub_entry.grid(row=0, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=self.load_epub).grid(row=0, column=2, padx=10, pady=10)

        # PDF Output File Selection
        tk.Label(self.root, text="Save PDF as:").grid(row=1, column=0, padx=10, pady=10)
        self.pdf_entry = tk.Entry(self.root, width=50)
        self.pdf_entry.grid(row=1, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=self.save_pdf).grid(row=1, column=2, padx=10, pady=10)

        # Convert Button
        tk.Button(self.root, text="Convert", command=self.convert_epub_to_pdf).grid(row=2, column=0, columnspan=3, pady=20)

        # Log Area
        self.log_area = scrolledtext.ScrolledText(self.root, width=70, height=15, wrap=tk.WORD)
        self.log_area.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

    def load_epub(self):
        file_path = filedialog.askopenfilename(filetypes=[("EPUB files", "*.epub")])
        if file_path:
            self.epub_entry.delete(0, tk.END)
            self.epub_entry.insert(0, file_path)

    def save_pdf(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.pdf_entry.delete(0, tk.END)
            self.pdf_entry.insert(0, file_path)

    def convert_epub_to_pdf(self):
        epub_path = self.epub_entry.get()
        pdf_path = self.pdf_entry.get()
        if not epub_path or not pdf_path:
            messagebox.showerror("Input Error", "Please select both EPUB file and output PDF file.")
            return
        converter = EPUBtoPDFConverter(epub_path, pdf_path)
        result = converter.convert()
        self.log_area.insert(tk.END, result + "\n")
        self.log_area.yview(tk.END)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    root = tk.Tk()
    app = EPUBtoPDFGUI(root)
    root.mainloop()
