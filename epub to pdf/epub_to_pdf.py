import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from ebooklib import epub
from fpdf import FPDF
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EPUBtoPDFConverter:
    def __init__(self, epub_path, pdf_path, font="Arial", font_size=12, page_size="A4"):
        self.epub_path = epub_path
        self.pdf_path = pdf_path
        self.pdf = FPDF(format=page_size)
        self.font = font
        self.font_size = font_size
        self.book = None
        self.metadata = {}
        self.text_stats = {}
        self.debug_mode = False
        self.page_layout = page_size  # Page layout for the PDF

    def convert(self):
        logging.info("Starting conversion.")
        try:
            self.load_epub()
            self.add_metadata()
            self.create_pdf()
            self.save_pdf()
            self.add_summary_and_report()
            return "Conversion completed successfully."
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return f"An error occurred: {e}"

    def load_epub(self):
        logging.info(f"Loading EPUB file: {self.epub_path}")
        if os.path.exists(self.epub_path):
            try:
                self.book = epub.read_epub(self.epub_path)
                logging.info("EPUB file loaded successfully.")
            except Exception as e:
                logging.error(f"Error loading EPUB file: {e}")
                raise
        else:
            logging.error(f"EPUB file '{self.epub_path}' not found!")
            raise FileNotFoundError(f"EPUB file '{self.epub_path}' not found!")

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
            self.pdf.set_title(self.metadata.get("title", ["Untitled"])[0])
            self.pdf.set_author(self.metadata.get("author", ["Unknown"])[0])
            self.pdf.set_subject(f"Language: {self.metadata.get('language', ['Unknown'])[0]}")
            self.pdf.set_creator(self.metadata.get("publisher", ["Unknown"])[0])
            logging.info(f"Metadata added: {self.metadata}")
    
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
        try:
            content = item.get_body_content().decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            text = self.clean_html(soup)
            lines = text.splitlines()
            for line in lines:
                if line.strip():
                    self.pdf.multi_cell(0, 10, txt=line)
                    self.update_text_statistics(line)
        except Exception as e:
            logging.error(f"Error processing HTML item {item.get_name()}: {e}")

    def process_image_item(self, item):
        try:
            image_data = item.get_content()
            image = Image.open(BytesIO(image_data))
            image_path = f"/tmp/{item.get_name()}"
            image.save(image_path)
            self.pdf.add_page()
            self.pdf.image(image_path, x=10, y=10, w=180)
            logging.info(f"Processed image: {item.get_name()}")
        except Exception as e:
            logging.error(f"Error processing image {item.get_name()}: {e}")

    def process_nav_item(self, item):
        logging.info("Processing table of contents.")
        try:
            content = item.get_body_content().decode('utf-8')
            toc_entries = self.extract_toc(content)
            self.add_toc_to_pdf(toc_entries)
        except Exception as e:
            logging.error(f"Error processing TOC: {e}")

    def extract_toc(self, html):
        logging.info("Extracting TOC.")
        toc_entries = []
        soup = BeautifulSoup(html, 'html.parser')
        nav = soup.find('nav')
        if nav:
            links = nav.find_all('a')
            toc_entries = [link.get_text() for link in links]
        return toc_entries

    def add_toc_to_pdf(self, toc_entries):
        try:
            self.pdf.add_page()
            self.pdf.set_font(self.font, size=16)
            self.pdf.cell(200, 10, txt="Table of Contents", ln=True, align='C')
            self.pdf.set_font(self.font, size=self.font_size)
            for entry in toc_entries:
                self.pdf.cell(200, 10, txt=entry, ln=True)
        except Exception as e:
            logging.error(f"Error adding TOC to PDF: {e}")

    def clean_html(self, soup):
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()
        text = soup.get_text()
        for ul in soup.find_all('ul'):
            text += "\n" + " ".join([li.get_text() for li in ul.find_all('li')])
        for ol in soup.find_all('ol'):
            text += "\n" + " ".join([li.get_text() for li in ol.find_all('li')])
        for heading in soup.find_all(re.compile('^h[1-6]$')):
            text += "\n" + heading.get_text() + "\n"
        for link in soup.find_all('a'):
            text += "\n" + link.get_text() + " (Link: " + link.get('href', '') + ")"
        text = re.sub('\s+', ' ', text).strip()
        return text

    def update_text_statistics(self, line):
        """Update text statistics."""
        words = line.split()
        self.text_stats['word_count'] = self.text_stats.get('word_count', 0) + len(words)
        self.text_stats['line_count'] = self.text_stats.get('line_count', 0) + 1
        self.text_stats['character_count'] = self.text_stats.get('character_count', 0) + len(line)

    def generate_report(self):
        """Generate a report of the text statistics."""
        report = f"Text Statistics:\n"
        report += f"Total Words: {self.text_stats.get('word_count', 0)}\n"
        report += f"Total Lines: {self.text_stats.get('line_count', 0)}\n"
        report += f"Total Characters: {self.text_stats.get('character_count', 0)}\n"
        return report

    def add_report_to_pdf(self, report):
        """Add text statistics report to the PDF."""
        self.pdf.add_page()
        self.pdf.set_font(self.font, size=16)
        self.pdf.cell(200, 10, txt="Text Statistics Report", ln=True, align='C')
        self.pdf.set_font(self.font, size=self.font_size)
        self.pdf.multi_cell(0, 10, txt=report)
        logging.info("Added text statistics report to PDF.")

    def save_pdf(self):
        try:
            logging.info(f"Saving PDF to: {self.pdf_path}")
            self.pdf.output(self.pdf_path)
            logging.info(f"PDF saved as '{self.pdf_path}'")
        except Exception as e:
            logging.error(f"Error saving PDF: {e}")

    def add_custom_page_layouts(self, layout="A4"):
        """Add support for custom page layouts."""
        if layout == "A4":
            self.pdf.set_page_orientation('P')
        elif layout == "A3":
            self.pdf.set_page_orientation('L')
        elif layout == "Letter":
            self.pdf.set_page_orientation('P')
        else:
            logging.warning(f"Unknown layout: {layout}. Defaulting to A4.")
            self.pdf.set_page_orientation('P')

    def add_watermark(self, watermark_text):
        """Add a watermark to each page."""
        self.pdf.set_font(self.font, size=40)
        self.pdf.set_text_color(200, 200, 200)
        self.pdf.set_xy(10, 10)
        self.pdf.cell(0, 10, txt=watermark_text, align='C')

    def add_summary_and_report(self):
        """Add summary and report to the PDF."""
        text_content = self.extract_epub_text()
        summary = self.generate_summary(text_content)
        self.add_summary_to_pdf(summary)
        report = self.generate_report()
        self.add_report_to_pdf(report)

    def extract_epub_text(self):
        """Extract text content from EPUB file."""
        text = ""
        for item in self.book.get_items():
            if item.get_type() == epub.EpubHtml:
                content = item.get_body_content().decode('utf-8')
                soup = BeautifulSoup(content, 'html.parser')
                text += self.clean_html(soup) + "\n"
        return text

    def generate_summary(self, text):
        """Generate a summary from the text."""
        summary = text[:1000]  # Take first 1000 characters for summary
        return f"Summary:\n{summary}"

    def add_summary_to_pdf(self, summary):
        """Add a summary to the PDF."""
        self.pdf.add_page()
        self.pdf.set_font(self.font, size=16)
        self.pdf.cell(200, 10, txt="Summary", ln=True, align='C')
        self.pdf.set_font(self.font, size=self.font_size)
        self.pdf.multi_cell(0, 10, txt=summary)
        logging.info("Added summary to PDF.")

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
    root = tk.Tk()
    app = EPUBtoPDFGUI(root)
    root.mainloop()
