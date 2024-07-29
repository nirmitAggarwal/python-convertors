import os
from fpdf import FPDF
from tkinter import Tk, Label, Button, filedialog, messagebox, Text, OptionMenu, StringVar, Scrollbar, Frame, Entry

class PDF(FPDF):
    def header(self):
        if self.custom_header:
            self.set_font(self.font_style, 'B', self.font_size)
            self.cell(0, 10, self.custom_header, 0, 1, self.header_alignment)

    def footer(self):
        if self.custom_footer:
            self.set_y(-15)
            self.set_font(self.font_style, 'I', self.font_size)
            self.cell(0, 10, f'Page {self.page_no()} {self.custom_footer}', 0, 0, self.footer_alignment)

    def add_chapter_title(self, title):
        self.set_font(self.font_style, 'B', self.font_size)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)

    def add_chapter_body(self, body):
        self.set_font(self.font_style, '', self.font_size)
        self.multi_cell(0, 10, body)
        self.ln()

class TextToPDFConverter:
    def __init__(self, master):
        self.master = master
        master.title("Text to PDF Converter")
        
        self.font_styles = ['Arial', 'Courier', 'Times']
        self.alignments = ['L', 'C', 'R']

        self.label = Label(master, text="Convert your Text file to PDF")
        self.label.pack(pady=10)

        self.select_button = Button(master, text="Select Text File", command=self.select_text_file)
        self.select_button.pack(pady=5)

        self.preview_frame = Frame(master)
        self.preview_frame.pack(pady=5)

        self.text_preview = Text(self.preview_frame, height=15, width=80)
        self.text_preview.pack(side="left", fill="both", expand=True)

        self.scrollbar = Scrollbar(self.preview_frame, command=self.text_preview.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.text_preview.config(yscrollcommand=self.scrollbar.set)

        self.font_label = Label(master, text="Select Font")
        self.font_label.pack(pady=5)
        self.font_var = StringVar(master)
        self.font_var.set(self.font_styles[0])
        self.font_menu = OptionMenu(master, self.font_var, *self.font_styles)
        self.font_menu.pack(pady=5)

        self.font_size_label = Label(master, text="Font Size")
        self.font_size_label.pack(pady=5)
        self.font_size_entry = Entry(master)
        self.font_size_entry.pack(pady=5)
        self.font_size_entry.insert(0, "12")

        self.header_label = Label(master, text="Header Text")
        self.header_label.pack(pady=5)
        self.header_entry = Entry(master)
        self.header_entry.pack(pady=5)

        self.footer_label = Label(master, text="Footer Text")
        self.footer_label.pack(pady=5)
        self.footer_entry = Entry(master)
        self.footer_entry.pack(pady=5)

        self.alignment_label = Label(master, text="Text Alignment")
        self.alignment_label.pack(pady=5)
        self.alignment_var = StringVar(master)
        self.alignment_var.set(self.alignments[0])
        self.alignment_menu = OptionMenu(master, self.alignment_var, *self.alignments)
        self.alignment_menu.pack(pady=5)

        self.margin_label = Label(master, text="Margins (Left, Top, Right, Bottom)")
        self.margin_label.pack(pady=5)
        self.margin_entry = Entry(master)
        self.margin_entry.pack(pady=5)
        self.margin_entry.insert(0, "10,10,10,10")

        self.convert_button = Button(master, text="Convert to PDF", command=self.convert_to_pdf, state="disabled")
        self.convert_button.pack(pady=5)

        self.text_file_path = ""

    def select_text_file(self):
        self.text_file_path = filedialog.askopenfilename(title="Select Text File", filetypes=(("Text files", "*.txt"),))
        if self.text_file_path:
            self.convert_button.config(state="normal")
            self.preview_text_file()
            messagebox.showinfo("Selected File", f"Selected: {self.text_file_path}")
        else:
            messagebox.showwarning("No file selected", "Please select a text file to convert.")

    def preview_text_file(self):
        self.text_preview.delete('1.0', 'end')
        with open(self.text_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            self.text_preview.insert('1.0', content)

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
        pdf.custom_header = self.header_entry.get()
        pdf.custom_footer = self.footer_entry.get()
        pdf.font_style = self.font_var.get()
        pdf.font_size = int(self.font_size_entry.get())
        pdf.header_alignment = self.alignment_var.get()
        pdf.footer_alignment = self.alignment_var.get()

        margins = list(map(int, self.margin_entry.get().split(',')))
        pdf.set_left_margin(margins[0])
        pdf.set_top_margin(margins[1])
        pdf.set_right_margin(margins[2])
        pdf.set_auto_page_break(auto=True, margin=margins[3])

        pdf.add_page()

        # Open the text file
        with open(text_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Add each line to the PDF
        for line in lines:
            pdf.set_font(pdf.font_style, '', pdf.font_size)
            pdf.multi_cell(0, 10, line, 0, pdf.header_alignment)

        # Save the PDF
        pdf.output(output_path)


def main():
    root = Tk()
    converter = TextToPDFConverter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
