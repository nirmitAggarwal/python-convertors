import os
import win32com.client
from tkinter import Tk, Label, Button, filedialog, messagebox, StringVar

def convert_word_to_pdf(input_file, output_file):
    try:
        # Initialize the Word application
        word = win32com.client.Dispatch('Word.Application')
        
        # Open the Word document
        doc = word.Documents.Open(input_file)
        
        # Save the document as a PDF
        doc.SaveAs(output_file, FileFormat=17)  # 17 is the file format for PDF
        
        # Close the document and quit Word
        doc.Close()
        word.Quit()
    except Exception as e:
        raise e

def select_word_file():
    file_path = filedialog.askopenfilename(filetypes=[("Word files", "*.docx")])
    if file_path:
        word_file_path.set(file_path)
        output_file = os.path.splitext(file_path)[0] + '.pdf'
        pdf_file_path.set(output_file)

def convert():
    input_file = word_file_path.get()
    output_file = pdf_file_path.get()
    
    # Debugging output
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")

    if input_file and output_file:
        try:
            convert_word_to_pdf(input_file, output_file)
            messagebox.showinfo("Success", f"File converted successfully!\n{output_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert file:\n{str(e)}")
    else:
        messagebox.showwarning("Warning", "Please select a Word file to convert.")

# Create the main window
root = Tk()
root.title("Word to PDF Converter")

# Variables to hold file paths
word_file_path = StringVar()
pdf_file_path = StringVar()

# Create and place widgets
Label(root, text="Select a Word file:").grid(row=0, column=0, padx=10, pady=10)
Button(root, text="Browse", command=select_word_file).grid(row=0, column=1, padx=10, pady=10)

Label(root, text="Output PDF file:").grid(row=1, column=0, padx=10, pady=10)
Label(root, textvariable=pdf_file_path).grid(row=1, column=1, padx=10, pady=10)

Button(root, text="Convert", command=convert).grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Start the GUI event loop
root.mainloop()
