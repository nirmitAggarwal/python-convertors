from fpdf import FPDF
from tkinter import Tk, filedialog

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Text to PDF Conversion', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

def convert_text_to_pdf(text_path, output_path):
    pdf = PDF()
    pdf.add_page()

    # Open the text file
    with open(text_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Add each line to the PDF
    for line in lines:
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 10, line)

    # Save the PDF
    pdf.output(output_path)

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
