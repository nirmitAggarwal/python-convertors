import os
from fpdf import FPDF
from tkinter import Tk, Label, Button, filedialog, messagebox


class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Text to PDF Conversion', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')


class TextToPDFConverter:
    def __init__(self, master):
        self.master = master
        master.title("Text to PDF Converter")

        self.label = Label(master, text="Convert your Text file to PDF")
        self.label.pack(pady=10)

        self.select_button = Button(master, text="Select Text File", command=self.select_text_file)
        self.select_button.pack(pady=5)

        self.convert_button = Button(master, text="Convert to PDF", command=self.convert_to_pdf, state="disabled")
        self.convert_button.pack(pady=5)

        self.text_file_path = ""

    def select_text_file(self):
        self.text_file_path = filedialog.askopenfilename(title="Select Text File", filetypes=(("Text files", "*.txt"),))
        if self.text_file_path:
            self.convert_button.config(state="normal")
            messagebox.showinfo("Selected File", f"Selected: {self.text_file_path}")
        else:
            messagebox.showwarning("No file selected", "Please select a text file to convert.")

    def convert_to_pdf(self):
        if not self.text_file_path:
            messagebox.showerror("Error", "No text file selected.")
            return

        output_file_path = filedialog.asksaveasfilename(defaultextension=".pdf", title="Save PDF File", filetypes=(("PDF files", "*.pdf"),))
        if output_file_path:
            self.create_pdf(self.text_file_path, output_file_path)
            messagebox.showinfo("Success", f"PDF saved successfully at {output_file_path}")
        else:
            messagebox.showwarning("No output file selected", "Please specify an output file.")

    def create_pdf(self, text_path, output_path):
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
    converter = TextToPDFConverter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
