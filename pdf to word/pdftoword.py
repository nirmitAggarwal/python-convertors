import os
from pdf2docx import Converter

def pdf_to_word(pdf_file, word_file):
    # Create a Converter object
    cv = Converter(pdf_file)
    
    # Convert PDF to Word
    cv.convert(word_file, start=0, end=None)
    
    # Close the Converter object
    cv.close()

if __name__ == "__main__":
    # Use absolute path to the PDF file
    pdf_file = os.path.abspath('pdf to word\sample.pdf')
    
    # Use absolute path to the output Word file
    word_file = os.path.abspath('pdf to word\output.docx')
    
    # Convert PDF to Word
    pdf_to_word(pdf_file, word_file)
    
    print(f"Conversion complete: {word_file}")
