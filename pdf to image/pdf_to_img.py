import os
import fitz  # PyMuPDF
import zipfile
from tkinter import Tk, Label, Button, Canvas, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk

# Function to convert PDF to images and save as a zip file
def convert_pdf_to_images(pdf_path):
    # Create a directory for the images
    img_dir = os.path.join(os.path.dirname(pdf_path), "pdf_images")
    os.makedirs(img_dir, exist_ok=True)

    # Open the PDF
    pdf_document = fitz.open(pdf_path)

    # Iterate through pages and save as images
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        img_path = os.path.join(img_dir, f"page_{page_num + 1}.png")
        pix.save(img_path)
    
    # Create a zip file of the images
    zip_path = os.path.join(os.path.dirname(pdf_path), "pdf_images.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(img_dir):
            for file in files:
                zipf.write(os.path.join(root, file), arcname=file)
    
    # Remove the temporary images directory
    for file in os.listdir(img_dir):
        os.remove(os.path.join(img_dir, file))
    os.rmdir(img_dir)

    messagebox.showinfo("Success", f"PDF converted to images and saved as {zip_path}")

# Function to handle file browsing
def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        pdf_label.config(text=file_path)
        convert_pdf_to_images(file_path)

# Function to handle drag and drop
def drop(event):
    file_path = event.data
    if file_path.endswith('.pdf'):
        pdf_label.config(text=file_path)
        convert_pdf_to_images(file_path)
    else:
        messagebox.showerror("Error", "Please drop a PDF file.")

# Create the main window
root = TkinterDnD.Tk()
root.title("PDF to Images Converter")

# Create and place the widgets
pdf_label = Label(root, text="Drag and drop a PDF file here or click 'Browse' to select a PDF", width=50, height=10, bg="white", relief="groove")
pdf_label.pack(padx=10, pady=10)
pdf_label.drop_target_register(DND_FILES)
pdf_label.dnd_bind('<<Drop>>', drop)

browse_button = Button(root, text="Browse", command=browse_file)
browse_button.pack(pady=5)

# Run the application
root.mainloop()
