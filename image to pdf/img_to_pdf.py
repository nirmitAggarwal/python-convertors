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
        img_label = Button(self.image_frame, image=tk_img, text=os.path.basename(file_path), compound='top')
        img_label.image = tk_img  # keep a reference!
        img_label.pack(side='left', padx=5, pady=5)
        self.image_objects.append((img_label, file_path))

    def start_drag(self, event):
        widget = event.widget.winfo_containing(event.x_root, event.y_root)
        if widget in [item[0] for item in self.image_objects]:
            self.dragged_widget = widget
            self.drag_start_index = self.image_objects.index(next(item for item in self.image_objects if item[0] == widget))
            self.drag_start = event.x, event.y

    def on_drag_motion(self, event):
        if hasattr(self, 'drag_start'):
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            self.dragged_widget.place(x=event.x_root + dx, y=event.y_root + dy, anchor='center')

    def on_drop(self, event):
        if hasattr(self, 'drag_start'):
            drop_widget = event.widget.winfo_containing(event.x_root, event.y_root)
            drop_index = self.image_objects.index(next(item for item in self.image_objects if item[0] == drop_widget))
            self.image_objects[self.drag_start_index], self.image_objects[drop_index] = self.image_objects[drop_index], self.image_objects[self.drag_start_index]
            for index, (widget, path) in enumerate(self.image_objects):
                widget.pack_forget()
                widget.pack(side='left', padx=5, pady=5)
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
            for idx, (widget, file_path) in enumerate(self.image_objects):
                img = Image.open(file_path)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                image_objects.append(img)

            image_objects[0].save(pdf_path, save_all=True, append_images=image_objects[1:])
            messagebox.showinfo("Success", f"Images have been successfully converted to {pdf_path}")

    def clear_list(self):
        self.images = []
        self.image_objects = []
        for widget in self.image_frame.winfo_children():
            widget.destroy()

# Initialize the GUI application
app = ImageToPDFApp()
app.mainloop()
