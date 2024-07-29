from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from tkinter import Tk, filedialog
import os

def convert_text_to_pdf(text_path, output_path):
    # Create a PDF canvas
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # Open the text file
    with open(text_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Set the starting position
    y_position = height - 40
    line_height = 14

    # Add each line to the PDF
    for line in lines:
        c.drawString(40, y_position, line.strip())
        y_position -= line_height
        if y_position <= 40:  # Move to next page if the bottom is reached
            c.showPage()
            y_position = height - 40

    # Save the PDF
    c.save()

def main():
    root = Tk()
    root.withdraw()  # Hide the main window
    # Ask user to select a text file
    text_file = filedialog.askopenfilename(title="Select Text File", filetypes=(("Text files", "*.txt"),))
    if text_file:
        # Ask user to specify the output PDF file
        output_file = filedialog.asksaveasfilename(defaultextension=".pdf", title="Save PDF File", filetypes=(("PDF files", "*.pdf"),))
        if output_file:
            convert_text_to_pdf(text_file, output_file)
            print(f"PDF saved successfully at {output_file}")
        else:
            print("No output file selected.")
    else:
        print("No text file selected.")

if __name__ == "__main__":
    main()
