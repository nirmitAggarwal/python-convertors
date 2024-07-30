import os
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, ttk
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

    def add_chapter_body(self, body):
        self.set_font(self.font_style, '', self.font_size)
        self.set_text_color(*self.text_color)
        self.multi_cell(0, self.line_height, body)
        self.ln()

class TextToPDFConverter:
    def __init__(self, master):
        self.master = master
        master.title("Text to PDF Converter")
        master.geometry("800x600")

        # Define style
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 12), padding=5)
        self.style.configure("TLabel", font=("Arial", 12))
        self.style.configure("TEntry", font=("Arial", 12), padding=5)
        self.style.configure("TOptionMenu", font=("Arial", 12))

        # Font Styles and Alignments
        self.font_styles = ['Arial', 'Courier', 'Times']
        self.alignments = ['L', 'C', 'R']
        self.page_sizes = ['A4', 'Letter']

        # Create a Scrollable Frame
        self.canvas = tk.Canvas(master)
        self.scroll_y = ttk.Scrollbar(master, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

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
        ttk.Label(self.scrollable_frame, text="Convert your Text file to PDF").grid(row=0, column=0, columnspan=2, pady=10)

        self.select_button = ttk.Button(self.scrollable_frame, text="Select Text File", command=self.select_text_file)
        self.select_button.grid(row=1, column=0, columnspan=2, pady=5)

        self.preview_frame = ttk.Frame(self.scrollable_frame)
        self.preview_frame.grid(row=2, column=0, columnspan=2, pady=5)

        self.text_preview = tk.Text(self.preview_frame, height=15, width=80)
        self.text_preview.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.preview_frame, command=self.text_preview.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.text_preview.config(yscrollcommand=self.scrollbar.set)

        ttk.Label(self.scrollable_frame, text="Select Font").grid(row=3, column=0, pady=5, sticky="w")
        self.font_var = tk.StringVar(self.scrollable_frame)
        self.font_var.set(self.font_styles[0])
        ttk.OptionMenu(self.scrollable_frame, self.font_var, *self.font_styles).grid(row=3, column=1, pady=5, sticky="ew")

        ttk.Label(self.scrollable_frame, text="Font Size").grid(row=4, column=0, pady=5, sticky="w")
        self.font_size_entry = ttk.Entry(self.scrollable_frame)
        self.font_size_entry.grid(row=4, column=1, pady=5, sticky="ew")
        self.font_size_entry.insert(0, "12")

        ttk.Label(self.scrollable_frame, text="Header Text").grid(row=5, column=0, pady=5, sticky="w")
        self.header_entry = ttk.Entry(self.scrollable_frame)
        self.header_entry.grid(row=5, column=1, pady=5, sticky="ew")

        ttk.Label(self.scrollable_frame, text="Footer Text").grid(row=6, column=0, pady=5, sticky="w")
        self.footer_entry = ttk.Entry(self.scrollable_frame)
        self.footer_entry.grid(row=6, column=1, pady=5, sticky="ew")

        ttk.Label(self.scrollable_frame, text="Text Alignment").grid(row=7, column=0, pady=5, sticky="w")
        self.alignment_var = tk.StringVar(self.scrollable_frame)
        self.alignment_var.set(self.alignments[0])
        ttk.OptionMenu(self.scrollable_frame, self.alignment_var, *self.alignments).grid(row=7, column=1, pady=5, sticky="ew")

        ttk.Label(self.scrollable_frame, text="Page Size").grid(row=8, column=0, pady=5, sticky="w")
        self.page_size_var = tk.StringVar(self.scrollable_frame)
        self.page_size_var.set(self.page_sizes[0])
        ttk.OptionMenu(self.scrollable_frame, self.page_size_var, *self.page_sizes).grid(row=8, column=1, pady=5, sticky="ew")

        ttk.Label(self.scrollable_frame, text="Margins (Left, Top, Right, Bottom)").grid(row=9, column=0, pady=5, sticky="w")
        self.margin_entry = ttk.Entry(self.scrollable_frame)
        self.margin_entry.grid(row=9, column=1, pady=5, sticky="ew")
        self.margin_entry.insert(0, "10,10,10,10")

        ttk.Label(self.scrollable_frame, text="Line Spacing").grid(row=10, column=0, pady=5, sticky="w")
        self.line_spacing_entry = ttk.Entry(self.scrollable_frame)
        self.line_spacing_entry.grid(row=10, column=1, pady=5, sticky="ew")
        self.line_spacing_entry.insert(0, "10")

        ttk.Label(self.scrollable_frame, text="Text Color").grid(row=11, column=0, pady=5, sticky="w")
        self.text_color_button = ttk.Button(self.scrollable_frame, text="Choose Color", command=self.choose_text_color)
        self.text_color_button.grid(row=11, column=1, pady=5, sticky="ew")

        ttk.Label(self.scrollable_frame, text="Background Color").grid(row=12, column=0, pady=5, sticky="w")
        self.bg_color_button = ttk.Button(self.scrollable_frame, text="Choose Color", command=self.choose_bg_color)
        self.bg_color_button.grid(row=12, column=1, pady=5, sticky="ew")

        self.convert_button = ttk.Button(self.scrollable_frame, text="Convert to PDF", command=self.convert_to_pdf, state="disabled")
        self.convert_button.grid(row=13, column=0, columnspan=2, pady=10)

        self.text_file_path = ""
        self.text_color = (0, 0, 0)  # Default black
        self.bg_color = (255, 255, 255)  # Default white

        # Configure column weights for responsiveness
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.columnconfigure(1, weight=3)

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

        output_file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])

        if not output_file_path:
            return

        font_style = self.font_var.get()
        font_size = int(self.font_size_entry.get())
        header_text = self.header_entry.get()
        footer_text = self.footer_entry.get()
        alignment = self.alignment_var.get()
        page_size = self.page_size_var.get()
        margins = tuple(map(int, self.margin_entry.get().split(',')))
        line_height = int(self.line_spacing_entry.get())

        pdf = PDF(orientation='P', unit='mm', format=page_size)
        pdf.add_page()
        pdf.set_margins(*margins)
        pdf.custom_header = header_text
        pdf.custom_footer = footer_text
        pdf.header_alignment = alignment
        pdf.footer_alignment = alignment
        pdf.font_style = font_style
        pdf.font_size = font_size
        pdf.text_color = self.text_color
        pdf.line_height = line_height

        with open(self.text_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                pdf.add_chapter_body(line)

        pdf.output(output_file_path)
        messagebox.showinfo("Success", f"PDF file created at {output_file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextToPDFConverter(root)
    root.mainloop()
