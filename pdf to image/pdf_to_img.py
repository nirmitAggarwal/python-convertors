import os
import fitz  # PyMuPDF

def pdf_to_images(pdf_path, output_folder='./pdf to image/output_images'):
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

# Example usage
pdf_path = r'C:\Users\nirmit\Desktop\python convertors\pdf to image\sample.pdf'
images = pdf_to_images(pdf_path)

print("Images saved at:")
for image_path in images:
    print(image_path)
