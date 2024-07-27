from PIL import Image
import os

def convert_images_to_pdf(image_files, output_pdf_path):
    # Open the first image
    image_list = []
    for image_file in image_files:
        img = Image.open(image_file)
        # Convert to RGB mode if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        image_list.append(img)
    
    # Save the images as a single PDF
    image_list[0].save(output_pdf_path, save_all=True, append_images=image_list[1:])

if __name__ == '__main__':
    # List of image files to be converted
    image_files = ['image1.jpg', 'image2.png', 'image3.bmp']
    # Output PDF path
    output_pdf_path = 'output.pdf'
    
    convert_images_to_pdf(image_files, output_pdf_path)
    print(f'Successfully converted images to {output_pdf_path}')
