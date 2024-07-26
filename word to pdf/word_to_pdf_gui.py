import os
import win32com.client

def convert_word_to_pdf(input_file, output_file):
    # Initialize the Word application
    word = win32com.client.Dispatch('Word.Application')
    
    # Open the Word document
    doc = word.Documents.Open(input_file)
    
    # Save the document as a PDF
    doc.SaveAs(output_file, FileFormat=17)  # 17 is the file format for PDF
    
    # Close the document and quit Word
    doc.Close()
    word.Quit()

if __name__ == "__main__":
    # Define the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct absolute paths for the input and output files
    input_file = os.path.join(script_dir, 'sample.docx')  # Replace with your input file name
    output_file = os.path.join(script_dir, 'output.pdf') # Replace with your desired output file name
    
    # Convert Word to PDF
    convert_word_to_pdf(input_file, output_file)
