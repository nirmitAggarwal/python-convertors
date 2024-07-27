import os
from tkinter import Tk, Button, Canvas, filedialog, messagebox, PhotoImage
from tkinter import ttk
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD

class ImageToPDFApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Image to PDF Converter")
        self.geometry("600x600")

        self.images = []
        self.image_ids = []

        # Browse Button
        browse_button = Button(self, text="Browse Images", command=self.browse_images)
        browse_button.pack(pady=10)

        # Convert Button
        convert_button = Button(self, text="Convert", command=self.convert_to_pdf)
        convert_button.pack(pady=10)

        # Clear Button
        clear_button = Button(self, text="Clear List", command=self.clear_list)
        clear_button.pack(pady=10)

        # Canvas for displaying images
        self.canvas = Canvas(self, bg='white')
        self.canvas.pack(pady=10, fill='both', expand=True)

        # Progress Bar
        self.progress_bar = ttk.Progressbar(self, orient='horizontal', mode='determinate')
        self.progress_bar.pack(pady=10, fill='x', expand=True)

        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_drop)

        self.canvas.drop_target_register(DND_FILES)
        self.canvas.dnd_bind('<<Drop>>', self.drop)

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
        self.image_ids.append(self.canvas.create_image(10, 10, anchor='nw', image=tk_img))
        self.canvas.image = tk_img
        self.canvas.update_idletasks()

    def start_drag(self, event):
        self.drag_start = event.x, event.y
        item = self.canvas.find_closest(event.x, event.y)[0]
        self.canvas.itemconfig(item, outline='red', width=2)

    def on_drag_motion(self, event):
        if hasattr(self, 'drag_start'):
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            self.canvas.move(self.canvas.find_closest(self.drag_start[0], self.drag_start[1])[0], dx, dy)
            self.drag_start = event.x, event.y

    def on_drop(self, event):
        item = self.canvas.find_closest(event.x, event.y)[0]
        self.canvas.itemconfig(item, outline='', width=1)

    def drop(self, event):
        data = event.data.split()
        for item in data:
            if item not in self.images:
                self.images.append(item)
                self.display_image(item)

    def convert_to_pdf(self):
        if not self.images:
            messagebox.showwarning("No Images Selected", "Please select images to convert.")
            return
        
        pdf_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF file", "*.pdf")],
            title="Save PDF As"
        )
        
        if pdf_path:
            image_objects = []
            self.progress_bar['maximum'] = len(self.images)
            for idx, file in enumerate(self.images):
                img = Image.open(file)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                image_objects.append(img)
                self.progress_bar['value'] = idx + 1
                self.update_idletasks()

            image_objects[0].save(pdf_path, save_all=True, append_images=image_objects[1:])
            messagebox.showinfo("Success", f"Images have been successfully converted to {pdf_path}")
            self.progress_bar['value'] = 0

    def clear_list(self):
        self.images = []
        self.image_ids = []
        self.canvas.delete("all")

# Initialize the GUI application
app = ImageToPDFApp()
app.mainloop()
