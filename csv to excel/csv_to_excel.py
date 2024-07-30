import os
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from fpdf import FPDF


class PDF(FPDF):
    def header(self):
        if self.custom_header:
            self.set_font(self.font_style, 'B', self.font_size)
            self.set_text_color(*self.text_color)
            self.cell(0, 10, self.custom_header, 0, 1, self.header_alignment)

    def footer(self):
        if self.custom_footer:
            self.set_y(-15)
            self.set_font(self.font_style, 'I', self.font_size)
            self.set_text_color(*self.text_color)
            self.cell(0, 10, f'Page {self.page_no()} {self.custom_footer}', 0, 0, self.footer_alignment)

    def add_chapter_title(self, title):
        self.set_font(self.font_style, 'B', self.font_size)
        self.set_text_color(*self.text_color)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)

    def add_chapter_body(self, body):
        self.set_font(self.font_style, '', self.font_size)
        self.set_text_color(*self.text_color)
        self.multi_cell(0, self.line_height, body)
        self.ln()


class TextToPDFConverter:
    def __init__(self, master):
        self.master = master
        master.title("Text to PDF Converter")

        # Font Styles and Alignments
        self.font_styles = ['Arial', 'Courier', 'Times']
        self.alignments = ['L', 'C', 'R']
        self.page_sizes = ['A4', 'Letter']

        # Create a Scrollable Frame
        self.canvas = tk.Canvas(master)
        self.scroll_y = tk.Scrollbar(master, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll_y.pack(side="right", fill="y")

        # Create UI Components within the scrollable frame
        self.create_widgets()
        self.load_settings()

    def create_widgets(self):
        tk.Label(self.scrollable_frame, text="Convert your Text file to PDF").pack(pady=10)

        self.select_button = tk.Button(self.scrollable_frame, text="Select Text File", command=self.select_text_file)
        self.select_button.pack(pady=5)

        self.preview_frame = tk.Frame(self.scrollable_frame)
        self.preview_frame.pack(pady=5)

        self.text_preview = tk.Text(self.preview_frame, height=15, width=80)
        self.text_preview.pack(side="left", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self.preview_frame, command=self.text_preview.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.text_preview.config(yscrollcommand=self.scrollbar.set)

        tk.Label(self.scrollable_frame, text="Select Font").pack(pady=5)
        self.font_var = tk.StringVar(self.scrollable_frame)
        self.font_var.set(self.font_styles[0])
        tk.OptionMenu(self.scrollable_frame, self.font_var, *self.font_styles).pack(pady=5)

        tk.Label(self.scrollable_frame, text="Font Size").pack(pady=5)
        self.font_size_entry = tk.Entry(self.scrollable_frame)
        self.font_size_entry.pack(pady=5)
        self.font_size_entry.insert(0, "12")

        tk.Label(self.scrollable_frame, text="Header Text").pack(pady=5)
        self.header_entry = tk.Entry(self.scrollable_frame)
        self.header_entry.pack(pady=5)

        tk.Label(self.scrollable_frame, text="Footer Text").pack(pady=5)
        self.footer_entry = tk.Entry(self.scrollable_frame)
        self.footer_entry.pack(pady=5)

        tk.Label(self.scrollable_frame, text="Text Alignment").pack(pady=5)
        self.alignment_var = tk.StringVar(self.scrollable_frame)
        self.alignment_var.set(self.alignments[0])
        tk.OptionMenu(self.scrollable_frame, self.alignment_var, *self.alignments).pack(pady=5)

        tk.Label(self.scrollable_frame, text="Page Size").pack(pady=5)
        self.page_size_var = tk.StringVar(self.scrollable_frame)
        self.page_size_var.set(self.page_sizes[0])
        tk.OptionMenu(self.scrollable_frame, self.page_size_var, *self.page_sizes).pack(pady=5)

        tk.Label(self.scrollable_frame, text="Margins (Left, Top, Right, Bottom)").pack(pady=5)
        self.margin_entry = tk.Entry(self.scrollable_frame)
        self.margin_entry.pack(pady=5)
        self.margin_entry.insert(0, "10,10,10,10")

        tk.Label(self.scrollable_frame, text="Line Spacing").pack(pady=5)
        self.line_spacing_entry = tk.Entry(self.scrollable_frame)
        self.line_spacing_entry.pack(pady=5)
        self.line_spacing_entry.insert(0, "10")

        tk.Label(self.scrollable_frame, text="Text Color").pack(pady=5)
        self.text_color_button = tk.Button(self.scrollable_frame, text="Choose Color", command=self.choose_text_color)
        self.text_color_button.pack(pady=5)

        tk.Label(self.scrollable_frame, text="Background Color").pack(pady=5)
        self.bg_color_button = tk.Button(self.scrollable_frame, text="Choose Color", command=self.choose_bg_color)
        self.bg_color_button.pack(pady=5)

        self.convert_button = tk.Button(self.scrollable_frame, text="Convert to PDF", command=self.convert_to_pdf, state="disabled")
        self.convert_button.pack(pady=5)

        self.text_file_path = ""
        self.text_color = (0, 0, 0)  # Default black
        self.bg_color = (255, 255, 255)  # Default white

    def load_settings(self):
        # Load saved settings if available (e.g., from a config file)
        pass

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

    def choose_text_color(self):
        color = colorchooser.askcolor(title="Choose Text Color")[0]
        if color:
            self.text_color = tuple(map(int, color))

    def choose_bg_color(self):
        color = colorchooser.askcolor(title="Choose Background Color")[0]
        if color:
            self.bg_color = tuple(map(int, color))

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
        pdf.text_color = self.text_color
        pdf.line_height = int(self.line_spacing_entry.get())

        margins = list(map(int, self.margin_entry.get().split(',')))
        pdf.set_left_margin(margins[0])
        pdf.set_top_margin(margins[1])
        pdf.set_right_margin(margins[2])
        pdf.set_auto_page_break(auto=True, margin=margins[3])

        page_size = self.page_size_var.get()
        if page_size == 'A4':
            pdf.add_page('P', 'A4')
        else:
            pdf.add_page('P', 'Letter')

        # Set background color
        pdf.set_fill_color(*self.bg_color)
        pdf.rect(0, 0, pdf.w, pdf.h, 'F')

        # Open the text file
        with open(text_path, 'r', encoding='utf-8') as file:
            for line in file:
                pdf.add_chapter_body(line)

        pdf.output(output_path)


if __name__ == "__main__":
    root = tk.Tk()
    app = TextToPDFConverter(root)
    root.mainloop()
