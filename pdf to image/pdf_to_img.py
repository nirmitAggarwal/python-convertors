import os
from pdf2image import convert_from_path

def pdf_to_images(pdf_path, output_folder='output_images', poppler_path='./poppler-24.07.0/Library/bin'):
    """
    Converts each page of a PDF into images and stores them in a list.
    
    Args:
    - pdf_path (str): Path to the PDF file.
    - output_folder (str): Folder to save the images. Default is 'output_images'.
    - poppler_path (str): Path to the poppler bin folder.
    
    Returns:
    - List of file paths to the saved images.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    images = convert_from_path(pdf_path, poppler_path=poppler_path)
    image_files = []
    
    for i, image in enumerate(images):
        image_path = os.path.join(output_folder, f'page_{i + 1}.png')
        image.save(image_path, 'PNG')
        image_files.append(image_path)
    
    return image_files

# Example usage
pdf_path = 'sample.pdf'
images = pdf_to_images(pdf_path)

print("Images saved at:")
for image_path in images:
    print(image_path)
