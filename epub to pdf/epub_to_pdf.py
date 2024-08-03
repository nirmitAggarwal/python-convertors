import os
import re
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import scrolledtext
from ebooklib import epub
from fpdf import FPDF
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

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
            self.pdf.set_creation_date(self.metadata.get("pub_date", ["Unknown"])[0])
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
        self.pdf.cell(0, 10, txt=watermark_text, ln=True, align='C')

    def extract_and_print_table_of_contents(self):
        """Extract and print the table of contents."""
        if self.book:
            toc = self.book.get_items_of_type(epub.EpubNav)
            for item in toc:
                content = item.get_body_content().decode('utf-8')
                soup = BeautifulSoup(content, 'html.parser')
                nav = soup.find('nav')
                if nav:
                    links = nav.find_all('a')
                    for link in links:
                        print(f"TOC Entry: {link.get_text()}")

    def extract_text_statistics(self):
        """Extract and print text statistics."""
        total_words = self.text_stats.get('word_count', 0)
        total_lines = self.text_stats.get('line_count', 0)
        total_characters = self.text_stats.get('character_count', 0)
        logging.info(f"Text Statistics - Words: {total_words}, Lines: {total_lines}, Characters: {total_characters}")

    def list_epub_items(self):
        """List all items in the EPUB file."""
        if self.book:
            for item in self.book.get_items():
                logging.info(f"Item type: {item.get_type()}, name: {item.get_name()}")

    def add_hyperlinks(self, content):
        """Add hyperlinks to the content."""
        links = re.findall(r'href=["\'](.*?)["\']', content)
        for link in links:
            content = content.replace(link, f"Link: {link}")
        return content

    def add_bookmarks(self, toc_entries):
        """Add bookmarks to the PDF for each TOC entry."""
        for entry in toc_entries:
            self.pdf.add_page()
            self.pdf.set_font(self.font, size=16)
            self.pdf.cell(200, 10, txt=entry, ln=True, align='C')
            self.pdf.set_font(self.font, size=self.font_size)

    def extract_images_from_epub(self):
        """Extract and list all images from the EPUB file."""
        images = []
        for item in self.book.get_items():
            if item.get_type() == epub.EpubImage:
                images.append(item.get_name())
        return images

    def parse_html_tables(self, html_content):
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

    def print_table(self, table):
        """Print parsed table for debugging."""
        for row in table:
            print(' | '.join(row))
        print()

    def debug_feature_example(self):
        """Example function to demonstrate additional features."""
        example_html = "<html><body><table><tr><td>Data1</td><td>Data2</td></tr></table></body></html>"
        tables = self.parse_html_tables(example_html)
        for table in tables:
            self.print_table(table)

    def list_epub_chapters(self):
        """List all chapter titles in the EPUB file."""
        chapters = []
        for item in self.book.get_items():
            if item.get_type() == epub.EpubHtml:
                soup = BeautifulSoup(item.get_body_content().decode('utf-8'), 'html.parser')
                title = soup.find('title')
                if title:
                    chapters.append(title.get_text())
        return chapters

    def extract_epub_text(self):
        """Extract and return all text content from the EPUB file."""
        text_content = []
        for item in self.book.get_items():
            if item.get_type() == epub.EpubHtml:
                soup = BeautifulSoup(item.get_body_content().decode('utf-8'), 'html.parser')
                text = self.clean_html(soup)
                text_content.append(text)
        return "\n\n".join(text_content)

    def generate_summary(self, text_content):
        """Generate a summary of the text content."""
        sentences = text_content.split('.')
        summary = ". ".join(sentences[:5]) + "."
        return summary

    def add_summary_to_pdf(self, summary):
        """Add summary to the PDF."""
        self.pdf.add_page()
        self.pdf.set_font(self.font, size=16)
        self.pdf.cell(200, 10, txt="Summary", ln=True, align='C')
        self.pdf.set_font(self.font, size=12)
        self.pdf.multi_cell(0, 10, txt=summary)

    def interactive_prompt(self):
        """Simulate an interactive user prompt."""
        print("Interactive Prompt:")
        user_font = input("Enter font name (default Arial): ") or "Arial"
        user_font_size = input("Enter font size (default 12): ") or 12
        user_page_size = input("Enter page size (A4, A3, Letter, default A4): ") or "A4"
        print(f"Selected font: {user_font}, Font size: {user_font_size}, Page size: {user_page_size}")

class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EPUB to PDF Converter")
        
        self.converter = None
        
        # Define UI elements
        self.create_widgets()

    def create_widgets(self):
        self.lbl_input = tk.Label(self.root, text="Select EPUB file:")
        self.lbl_input.grid(row=0, column=0, padx=10, pady=5)

        self.btn_input = tk.Button(self.root, text="Browse", command=self.load_file)
        self.btn_input.grid(row=0, column=1, padx=10, pady=5)

        self.lbl_output = tk.Label(self.root, text="Save PDF as:")
        self.lbl_output.grid(row=1, column=0, padx=10, pady=5)

        self.btn_output = tk.Button(self.root, text="Browse", command=self.save_file)
        self.btn_output.grid(row=1, column=1, padx=10, pady=5)

        self.txt_log = scrolledtext.ScrolledText(self.root, width=80, height=20)
        self.txt_log.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        self.btn_convert = tk.Button(self.root, text="Convert", command=self.convert_epub_to_pdf)
        self.btn_convert.grid(row=3, column=0, columnspan=2, pady=10)

        self.epub_path = ""
        self.pdf_path = ""

    def load_file(self):
        self.epub_path = filedialog.askopenfilename(filetypes=[("EPUB Files", "*.epub")])
        self.txt_log.insert(tk.END, f"Selected EPUB file: {self.epub_path}\n")

    def save_file(self):
        self.pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        self.txt_log.insert(tk.END, f"Save PDF as: {self.pdf_path}\n")

    def convert_epub_to_pdf(self):
        if not self.epub_path or not self.pdf_path:
            messagebox.showwarning("Input Error", "Please specify both EPUB file and output PDF path.")
            return
        
        self.txt_log.insert(tk.END, "Starting conversion...\n")
        self.converter = EPUBtoPDFConverter(self.epub_path, self.pdf_path)
        
        result = self.converter.convert()
        self.txt_log.insert(tk.END, result + "\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()
