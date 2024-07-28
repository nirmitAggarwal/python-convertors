import os
import tkinter as tk
from tkinter import filedialog, messagebox
import fitz  # PyMuPDF
from tkdnd_wrapper import TkDND

def pdf_to_images(pdf_path, output_folder='output_images'):
    """
    Converts each page of a PDF into images and stores them in a list.
    
    Args:
    - pdf_path (str): Path to the PDF file.
    - output_folder (str): Folder to save the images. Default is 'output_images'.
    
    Returns:
    - List of file paths to the saved images.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pdf_document = fitz.open(pdf_path)
    image_files = []
    
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)  # load page
        pix = page.get_pixmap()  # render page to an image
        image_path = os.path.join(output_folder, f'page_{page_num + 1}.png')
        pix.save(image_path)
        image_files.append(image_path)
    
    pdf_document.close()
    return image_files

def select_pdf_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        pdf_entry.delete(0, tk.END)
        pdf_entry.insert(0, file_path)

def select_output_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, folder_path)

def convert_pdf_to_images():
    pdf_path = pdf_entry.get()
    output_folder = output_entry.get()
    if not pdf_path or not output_folder:
        messagebox.showerror("Error", "Please select both a PDF file and an output folder.")
        return

    try:
        images = pdf_to_images(pdf_path, output_folder)
        messagebox.showinfo("Success", f"Images saved at: {', '.join(images)}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def on_drop(event):
    pdf_entry.delete(0, tk.END)
    pdf_entry.insert(0, event.data)

# Create the main window
root = tk.Tk()
root.title("PDF to Image Converter")

# Add TkDND support
dnd = TkDND(root)

# PDF file selection
tk.Label(root, text="Select PDF file:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
pdf_entry = tk.Entry(root, width=50)
pdf_entry.grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Browse...", command=select_pdf_file).grid(row=0, column=2, padx=10, pady=10)

# Output folder selection
tk.Label(root, text="Select output folder:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=1, column=1, padx=10, pady=10)
tk.Button(root, text="Browse...", command=select_output_folder).grid(row=1, column=2, padx=10, pady=10)

# Convert button
tk.Button(root, text="Convert", command=convert_pdf_to_images).grid(row=2, column=0, columnspan=3, pady=20)

# Set up drag-and-drop for the PDF entry
dnd.bindtarget(pdf_entry, on_drop, 'text/uri-list')

# Start the GUI event loop
root.mainloop()
