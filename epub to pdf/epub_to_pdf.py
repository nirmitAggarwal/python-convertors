import os
from ebooklib import epub
from fpdf import FPDF
import re
import logging
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup

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
        self.toc = []

    def convert(self):
        logging.info("Starting conversion.")
        try:
            self.load_epub()
            self.add_metadata()
            self.create_pdf()
            self.save_pdf()
        except Exception as e:
            logging.error(f"An error occurred: {e}")

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
            title = self.book.get_metadata('DC', 'title')
            author = self.book.get_metadata('DC', 'creator')
            language = self.book.get_metadata('DC', 'language')
            pub_date = self.book.get_metadata('DC', 'date')
            publisher = self.book.get_metadata('DC', 'publisher')
            identifier = self.book.get_metadata('DC', 'identifier')
            
            if title:
                self.pdf.set_title(title[0][0])
                logging.info(f"Title: {title[0][0]}")
            if author:
                self.pdf.set_author(author[0][0])
                logging.info(f"Author: {author[0][0]}")
            if language:
                self.pdf.set_subject(f"Language: {language[0][0]}")
                logging.info(f"Language: {language[0][0]}")
            if pub_date:
                self.pdf.set_creation_date(pub_date[0][0])
                logging.info(f"Publication Date: {pub_date[0][0]}")
            if publisher:
                self.pdf.set_creator(publisher[0][0])
                logging.info(f"Publisher: {publisher[0][0]}")
            if identifier:
                self.pdf.set_subject(f"Identifier: {identifier[0][0]}")
                logging.info(f"Identifier: {identifier[0][0]}")

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
                    self.pdf.cell(200, 10, txt=line, ln=True)
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
        # Remove scripts and styles
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()
        # Extract text
        text = soup.get_text()
        # Handle lists
        for ul in soup.find_all('ul'):
            text += "\n" + " ".join([li.get_text() for li in ul.find_all('li')])
        for ol in soup.find_all('ol'):
            text += "\n" + " ".join([li.get_text() for li in ol.find_all('li')])
        # Handle headings
        for heading in soup.find_all(re.compile('^h[1-6]$')):
            text += "\n" + heading.get_text() + "\n"
        # Handle links
        for link in soup.find_all('a'):
            text += "\n" + link.get_text() + " (Link: " + link.get('href', '') + ")"
        # Remove extra whitespace
        text = re.sub('\s+', ' ', text).strip()
        return text

    def save_pdf(self):
        try:
            logging.info(f"Saving PDF to: {self.pdf_path}")
            self.pdf.output(self.pdf_path)
            logging.info(f"PDF saved as '{self.pdf_path}'")
        except Exception as e:
            logging.error(f"Error saving PDF: {e}")

if __name__ == "__main__":
    epub_path = "example.epub"
    pdf_path = "output.pdf"
    
    try:
        converter = EPUBtoPDFConverter(epub_path, pdf_path, font="Times", font_size=14, page_size="A4")
        converter.convert()
    except Exception as e:
        logging.error(f"An error occurred: {e}")

# Additional feature functions
def extract_images_from_epub(epub_file):
    """Extract and list all images from the EPUB file."""
    book = epub.read_epub(epub_file)
    images = []
    for item in book.get_items():
        if item.get_type() == epub.EpubImage:
            images.append(item.get_name())
    return images

def parse_html_tables(html_content):
    """Parse tables from HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')
    parsed_tables = []
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            parsed_tables.append([col.get_text() for col in cols])
    return parsed_tables

def print_table(table):
    """Print parsed table for debugging."""
    for row in table:
        print(' | '.join(row))
    print()

def debug_feature_example():
    """Example function to demonstrate additional features."""
    example_html = "<html><body><table><tr><td>Data1</td><td>Data2</td></tr></table></body></html>"
    tables = parse_html_tables(example_html)
    for table in tables:
        print_table(table)

# Example call to demonstrate additional features
debug_feature_example()

def list_epub_chapters(epub_file):
    """List all chapter titles in the EPUB file."""
    book = epub.read_epub(epub_file)
    chapters = []
    for item in book.get_items():
        if item.get_type() == epub.EpubHtml:
            soup = BeautifulSoup(item.get_body_content().decode('utf-8'), 'html.parser')
            title = soup.find('title')
            if title:
                chapters.append(title.get_text())
    return chapters

def extract_epub_text(epub_file):
    """Extract and return all text content from the EPUB file."""
    book = epub.read_epub(epub_file)
    text_content = []
    for item in book.get_items():
        if item.get_type() == epub.EpubHtml:
            soup = BeautifulSoup(item.get_body_content().decode('utf-8'), 'html.parser')
            text = clean_html(soup)
            text_content.append(text)
    return "\n\n".join(text_content)

def clean_html(soup):
    """Clean HTML content for text extraction."""
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

def generate_summary(text_content):
    """Generate a summary of the text content."""
    # Simple summary generation (could be improved with NLP techniques)
    sentences = text_content.split('.')
    summary = ". ".join(sentences[:5]) + "."
    return summary

def add_summary_to_pdf(summary):
    """Add summary to the PDF."""
    self.pdf.add_page()
    self.pdf.set_font(self.font, size=16)
    self.pdf.cell(200, 10, txt="Summary", ln=True, align='C')
    self.pdf.set_font(self.font, size=self.font_size)
    self.pdf.multi_cell(0, 10, txt=summary)
    logging.info("Added summary to PDF.")

if __name__ == "__main__":
    epub_path = "example.epub"
    pdf_path = "output.pdf"
    
    try:
        converter = EPUBtoPDFConverter(epub_path, pdf_path, font="Times", font_size=14, page_size="A4")
        text_content = extract_epub_text(epub_path)
        summary = generate_summary(text_content)
        converter.convert()
        add_summary_to_pdf(summary)
    except Exception as e:
        logging.error(f"An error occurred: {e}")

# Additional feature functions
def list_epub_chapters(epub_file):
    """List all chapter titles in the EPUB file."""
    book = epub.read_epub(epub_file)
    chapters = []
    for item in book.get_items():
        if item.get_type() == epub.EpubHtml:
            soup = BeautifulSoup(item.get_body_content().decode('utf-8'), 'html.parser')
            title = soup.find('title')
            if title:
                chapters.append(title.get_text())
    return chapters

def extract_epub_text(epub_file):
    """Extract and return all text content from the EPUB file."""
    book = epub.read_epub(epub_file)
    text_content = []
    for item in book.get_items():
        if item.get_type() == epub.EpubHtml:
            soup = BeautifulSoup(item.get_body_content().decode('utf-8'), 'html.parser')
            text = clean_html(soup)
            text_content.append(text)
    return "\n\n".join(text_content)

def generate_summary(text_content):
    """Generate a summary of the text content."""
    sentences = text_content.split('.')
    summary = ". ".join(sentences[:5]) + "."
    return summary

def add_summary_to_pdf(pdf, summary):
    """Add summary to the PDF."""
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt="Summary", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=summary)

if __name__ == "__main__":
    epub_path = "example.epub"
    pdf_path = "output.pdf"
    
    try:
        converter = EPUBtoPDFConverter(epub_path, pdf_path, font="Times", font_size=14, page_size="A4")
        text_content = extract_epub_text(epub_path)
        summary = generate_summary(text_content)
        converter.convert()
        add_summary_to_pdf(converter.pdf, summary)
    except Exception as e:
        logging.error(f"An error occurred: {e}")

