import logging
from ebooklib import epub
from fpdf import FPDF
from bs4 import BeautifulSoup
from PIL import Image
import io

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

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    epub_path = "path/to/your/epubfile.epub"  # Update this path
    pdf_path = "path/to/your/outputfile.pdf"  # Update this path
    converter = EPUBtoPDFConverter(epub_path, pdf_path)
    result = converter.convert()
    print(result)
