import os
from tkinter import Tk, Canvas, filedialog, messagebox, PhotoImage, Scrollbar, HORIZONTAL, Frame, Label
from tkinter import ttk
from tkinter.font import Font
from PIL import Image, ImageTk

class ImageToPDFApp(Tk):
    def __init__(self):
        super().__init__()
        self.title("Image to PDF Converter")
        self.geometry("900x650")
        self.configure(bg='#1e1e1e')

        self.images = []
        self.image_objects = []
        self.selected_image = None

        # Styling
        style = ttk.Style(self)
        style.theme_use('clam')

        style.configure('TButton', font=('Arial', 12, 'bold'), borderwidth=0, focusthickness=3, focuscolor='none')
        style.configure('TFrame', background='#1e1e1e')
        style.configure('TLabel', background='#1e1e1e', foreground='white', font=('Arial', 14, 'bold'))
        style.map('TButton', foreground=[('pressed', 'white'), ('active', '#ffffff')],
                  background=[('pressed', '#3a3a3a'), ('active', '#3a3a3a')])

        # Custom Font
        custom_font = Font(family="Arial", size=12, weight="bold")

        # Heading
        heading = Label(self, text="Image to PDF Converter", font=('Arial', 24, 'bold'), fg='#ffffff', bg='#1e1e1e')
        heading.pack(pady=20)

        # Frame for buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        # Browse Button
        browse_button = ttk.Button(button_frame, text="Browse Images", command=self.browse_images, style='TButton')
        browse_button.grid(row=0, column=0, padx=10)

        # Convert Button
        convert_button = ttk.Button(button_frame, text="Convert", command=self.convert_to_pdf, style='TButton')
        convert_button.grid(row=0, column=1, padx=10)

        # Clear Button
        clear_button = ttk.Button(button_frame, text="Clear List", command=self.clear_list, style='TButton')
        clear_button.grid(row=0, column=2, padx=10)

        # Up Button
        up_button = ttk.Button(button_frame, text="Move Up", command=self.move_up, style='TButton')
        up_button.grid(row=0, column=3, padx=10)

        # Down Button
        down_button = ttk.Button(button_frame, text="Move Down", command=self.move_down, style='TButton')
        down_button.grid(row=0, column=4, padx=10)

        # Frame for canvas and scrollbar
        canvas_frame = Frame(self, bg='#1e1e1e')
        canvas_frame.pack(fill='both', expand=True)

        # Horizontal Scrollbar
        h_scrollbar = Scrollbar(canvas_frame, orient=HORIZONTAL)
        h_scrollbar.pack(side='bottom', fill='x')

        # Canvas for displaying images
        self.canvas = Canvas(canvas_frame, bg='#2e2e2e', highlightthickness=0, xscrollcommand=h_scrollbar.set)
        self.canvas.pack(pady=10, fill='both', expand=True)
        h_scrollbar.config(command=self.canvas.xview)

        self.canvas.bind("<ButtonPress-1>", self.on_image_press)

    def browse_images(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        for file_path in file_paths:
            if file_path not in self.images:
                self.images.append(file_path)
                self.display_image(file_path)

    def display_image(self, file_path):
        img = Image.open(file_path)
        img.thumbnail((100, 100))
        tk_img = ImageTk.PhotoImage(img)
        x = len(self.image_objects) * 120 + 10
        item = self.canvas.create_image(x, 30, anchor='nw', image=tk_img)
        index = self.canvas.create_text(x + 50, 140, text=str(len(self.image_objects) + 1), fill='white', font=('Arial', 10, 'bold'))
        self.image_objects.append((item, tk_img, file_path, index))
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_image_press(self, event):
        closest_item = self.canvas.find_closest(event.x, event.y)[0]
        for obj in self.image_objects:
            if obj[0] == closest_item:
                self.selected_image = obj
                break

    def move_up(self):
        if self.selected_image:
            idx = self.image_objects.index(self.selected_image)
            if idx > 0:
                self.image_objects[idx], self.image_objects[idx - 1] = self.image_objects[idx - 1], self.image_objects[idx]
                self.reorder_images()

    def move_down(self):
        if self.selected_image:
            idx = self.image_objects.index(self.selected_image)
            if idx < len(self.image_objects) - 1:
                self.image_objects[idx], self.image_objects[idx + 1] = self.image_objects[idx + 1], self.image_objects[idx]
                self.reorder_images()

    def reorder_images(self):
        for idx, (item, tk_img, _, index) in enumerate(self.image_objects):
            x = idx * 120 + 10
            self.canvas.coords(item, x, 30)
            self.canvas.coords(index, x + 50, 140)
            self.canvas.itemconfig(index, text=str(idx + 1))
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def convert_to_pdf(self):
        if not self.image_objects:
            messagebox.showwarning("No Images Selected", "Please select images to convert.")
            return

        pdf_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF file", "*.pdf")],
            title="Save PDF As"
        )

        if pdf_path:
            image_objects = []
            for _, _, file_path, _ in self.image_objects:
                img = Image.open(file_path)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                image_objects.append(img)

            image_objects[0].save(pdf_path, save_all=True, append_images=image_objects[1:])
            messagebox.showinfo("Success", f"Images have been successfully converted to {pdf_path}")

    def clear_list(self):
        self.images = []
        self.image_objects = []
        self.canvas.delete("all")
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

# Initialize the GUI application
app = ImageToPDFApp()
app.mainloop()
