import os
from tkinter import Tk, Button, Canvas, filedialog, messagebox, Frame, PhotoImage
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk

class ImageToPDFApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Image to PDF Converter")
        self.geometry("800x600")

        self.images = []
        self.image_ids = []
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

        # Frame to hold the images
        self.image_frame = Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.image_frame, anchor='nw')

        # Scrollbars
        self.h_scroll = ttk.Scrollbar(self, orient='horizontal', command=self.canvas.xview)
        self.h_scroll.pack(fill='x', side='bottom')
        self.v_scroll = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.v_scroll.pack(fill='y', side='right')

        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.image_frame.bind("<Button-1>", self.start_drag)
        self.image_frame.bind("<B1-Motion>", self.on_drag_motion)
        self.image_frame.bind("<ButtonRelease-1>", self.on_drop)

    def on_canvas_resize(self, event):
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

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
        image_id = self.canvas.create_image(10, 10, anchor='nw', image=tk_img)
        self.image_frame.update_idletasks()
        self.image_ids.append(image_id)
        self.image_objects.append((tk_img, file_path))

    def start_drag(self, event):
        self.drag_start = event.x, event.y
        self.dragged_item = self.canvas.find_closest(event.x, event.y)[0]
        self.dragged_index = self.image_ids.index(self.dragged_item)

    def on_drag_motion(self, event):
        if hasattr(self, 'drag_start'):
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            self.canvas.move(self.dragged_item, dx, dy)
            self.drag_start = event.x, event.y

    def on_drop(self, event):
        if hasattr(self, 'drag_start'):
            end_index = self.canvas.find_closest(event.x, event.y)[0]
            end_index = self.image_ids.index(end_index)
            if self.dragged_index != end_index:
                # Swap images in the list
                self.image_ids[self.dragged_index], self.image_ids[end_index] = self.image_ids[end_index], self.image_ids[self.dragged_index]
                self.image_objects[self.dragged_index], self.image_objects[end_index] = self.image_objects[end_index], self.image_objects[self.dragged_index]
            self.canvas.update_idletasks()
            self.drag_start = None

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
            self.progress_bar['maximum'] = len(self.image_objects)
            for idx, (tk_img, file_path) in enumerate(self.image_objects):
                img = Image.open(file_path)
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
        self.image_objects = []
        self.canvas.delete("all")

# Initialize the GUI application
app = ImageToPDFApp()
app.mainloop()
