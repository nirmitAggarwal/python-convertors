import os
from ebooklib import epub
from fpdf import FPDF
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EPUBtoPDFConverter:
    def __init__(self, epub_path, pdf_path):
        self.epub_path = epub_path
        self.pdf_path = pdf_path
        self.pdf = FPDF()
        self.book = None
        self.toc = []

    def convert(self):
        logging.info("Starting conversion.")
        self.load_epub()
        self.add_metadata()
        self.create_pdf()
        self.save_pdf()
        logging.info("Conversion completed successfully.")

    def load_epub(self):
        logging.info(f"Loading EPUB file: {self.epub_path}")
        if os.path.exists(self.epub_path):
            self.book = epub.read_epub(self.epub_path)
            logging.info("EPUB file loaded successfully.")
        else:
            logging.error(f"EPUB file '{self.epub_path}' not found!")
            raise FileNotFoundError(f"EPUB file '{self.epub_path}' not found!")

    def add_metadata(self):
        if self.book:
            title = self.book.get_metadata('DC', 'title')
            author = self.book.get_metadata('DC', 'creator')
            if title:
                self.pdf.set_title(title[0][0])
                logging.info(f"Title: {title[0][0]}")
            if author:
                self.pdf.set_author(author[0][0])
                logging.info(f"Author: {author[0][0]}")

    def create_pdf(self):
        logging.info("Creating PDF content.")
        self.pdf.add_page()
        self.pdf.set_font("Arial", size=12)
        
        for item in self.book.get_items():
            if item.get_type() == epub.EpubHtml:
                self.process_html_item(item)
            elif item.get_type() == epub.EpubImage:
                self.process_image_item(item)
            elif item.get_type() == epub.EpubNav:
                self.process_nav_item(item)

    def process_html_item(self, item):
        content = item.get_body_content().decode('utf-8')
        text = self.clean_html(content)
        lines = text.splitlines()
        for line in lines:
            if line.strip():
                self.pdf.cell(200, 10, txt=line, ln=True)
    
    def process_image_item(self, item):
        # Placeholder for image processing
        logging.info(f"Processing image: {item.get_name()}")

    def process_nav_item(self, item):
        # Placeholder for navigation processing (Table of Contents)
        logging.info("Processing table of contents.")
        content = item.get_body_content().decode('utf-8')
        toc_entries = self.extract_toc(content)
        self.add_toc_to_pdf(toc_entries)

    def extract_toc(self, html):
        # Placeholder for extracting TOC from HTML
        logging.info("Extracting TOC.")
        return ["Chapter 1", "Chapter 2", "Chapter 3"]

    def add_toc_to_pdf(self, toc_entries):
        self.pdf.add_page()
        self.pdf.set_font("Arial", size=16)
        self.pdf.cell(200, 10, txt="Table of Contents", ln=True, align='C')
        self.pdf.set_font("Arial", size=12)
        for entry in toc_entries:
            self.pdf.cell(200, 10, txt=entry, ln=True)
    
    def clean_html(self, html):
        clean_text = re.sub('<[^<]+?>', '', html)
        clean_text = re.sub('\s+', ' ', clean_text).strip()
        return clean_text

    def save_pdf(self):
        logging.info(f"Saving PDF to: {self.pdf_path}")
        self.pdf.output(self.pdf_path)
        logging.info(f"PDF saved as '{self.pdf_path}'")

if __name__ == "__main__":
    epub_path = "example.epub"
    pdf_path = "output.pdf"
    
    try:
        converter = EPUBtoPDFConverter(epub_path, pdf_path)
        converter.convert()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
