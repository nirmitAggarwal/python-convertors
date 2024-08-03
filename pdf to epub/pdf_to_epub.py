import os
import fitz  # PyMuPDF
import ebooklib
from ebooklib import epub
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
from io import BytesIO

# Function to extract text from PDF
def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

# Function to extract images from PDF
def extract_images(pdf_path):
    doc = fitz.open(pdf_path)
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            images.append(image_bytes)
    return images

# Function to convert images to EPUB format
def add_images_to_epub(epub_book, images):
    for img_index, img_data in enumerate(images):
        image = epub.EpubItem(
            file_name=f"image_{img_index}.png", 
            media_type="image/png", 
            content=img_data
        )
        epub_book.add_item(image)

# Function to create EPUB book
def create_epub(text, images, title, author):
    book = epub.EpubBook()
    
    book.set_title(title)
    book.set_author(author)
    
    # Add text
    chapter = epub.EpubHtml(title='Chapter 1', file_name='chap_01.xhtml', lang='en')
    chapter.content = f'<h1>Chapter 1</h1><p>{text}</p>'
    book.add_item(chapter)
    
    # Add images
    add_images_to_epub(book, images)
    
    # Define Table Of Contents
    book.toc = (epub.Link('chap_01.xhtml', 'Chapter 1', 'chap_01'),)
    
    # Add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # Define CSS style
    style = 'BODY {color: white;}'
    nav_css = epub.EpubItem(
        uid="style_nav", 
        file_name="style/nav.css", 
        media_type="text/css", 
        content=style
    )
    book.add_item(nav_css)
    
    # Create spine
    book.spine = ['nav', chapter]
    
    return book

# Function to save EPUB book
def save_epub(book, output_path):
    epub.write_epub(output_path, book, {})

# Function to handle the conversion process
def convert_pdf_to_epub(pdf_path, output_path, title, author):
    try:
        text = extract_text(pdf_path)
        images = extract_images(pdf_path)
        epub_book = create_epub(text, images, title, author)
        save_epub(epub_book, output_path)
        print(f"Successfully converted {pdf_path} to {output_path}")
    except Exception as e:
        print(f"Error: {e}")

# GUI for selecting files and starting conversion
def start_gui():
    root = tk.Tk()
    root.title("PDF to EPUB Converter")

    def select_files():
        files = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        file_list.delete(0, tk.END)
        for file in files:
            file_list.insert(tk.END, file)

    def convert_files():
        output_dir = filedialog.askdirectory()
        if not output_dir:
            messagebox.showerror("Error", "Output directory not selected")
            return
        
        title = title_entry.get()
        author = author_entry.get()
        
        for file in file_list.get(0, tk.END):
            output_path = os.path.join(output_dir, os.path.splitext(os.path.basename(file))[0] + ".epub")
            convert_pdf_to_epub(file, output_path, title, author)
        
        messagebox.showinfo("Success", "Conversion completed")

    select_button = tk.Button(root, text="Select PDF Files", command=select_files)
    select_button.pack(pady=5)

    file_list = tk.Listbox(root, selectmode=tk.MULTIPLE, width=80, height=10)
    file_list.pack(pady=5)

    title_label = tk.Label(root, text="Title:")
    title_label.pack(pady=5)
    title_entry = tk.Entry(root, width=50)
    title_entry.pack(pady=5)

    author_label = tk.Label(root, text="Author:")
    author_label.pack(pady=5)
    author_entry = tk.Entry(root, width=50)
    author_entry.pack(pady=5)

    convert_button = tk.Button(root, text="Convert to EPUB", command=convert_files)
    convert_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    start_gui()
