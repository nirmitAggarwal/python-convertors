import os
from tkinter import Tk, Button, Canvas, filedialog, messagebox, PhotoImage, Frame
from PIL import Image, ImageTk

class ImageToPDFApp(Tk):
    def __init__(self):
        super().__init__()
        self.title("Image to PDF Converter")
        self.geometry("800x600")

        self.images = []
        self.image_objects = []

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

        self.canvas.bind("<ButtonPress-1>", self.on_image_press)
        self.canvas.bind("<B1-Motion>", self.on_image_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_image_release)

        self.drag_data = {"x": 0, "y": 0, "item": None}

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
        x = len(self.image_objects) * 110 + 10
        item = self.canvas.create_image(x, 10, anchor='nw', image=tk_img)
        self.image_objects.append((item, tk_img, file_path))

    def on_image_press(self, event):
        item = self.canvas.find_closest(event.x, event.y)[0]
        self.drag_data["item"] = item
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_image_motion(self, event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.canvas.move(self.drag_data["item"], dx, dy)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_image_release(self, event):
        items = self.canvas.find_overlapping(event.x, event.y, event.x+1, event.y+1)
        if len(items) > 1:
            item1_idx = self.get_image_index(self.drag_data["item"])
            item2_idx = self.get_image_index(items[0])
            self.image_objects[item1_idx], self.image_objects[item2_idx] = self.image_objects[item2_idx], self.image_objects[item1_idx]
            self.reorder_images()
        self.drag_data["item"] = None

    def get_image_index(self, item):
        for idx, (img_item, _, _) in enumerate(self.image_objects):
            if img_item == item:
                return idx
        return None

    def reorder_images(self):
        for idx, (item, tk_img, _) in enumerate(self.image_objects):
            x = idx * 110 + 10
            self.canvas.coords(item, x, 10)

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
            for _, _, file_path in self.image_objects:
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

# Initialize the GUI application
app = ImageToPDFApp()
app.mainloop()
