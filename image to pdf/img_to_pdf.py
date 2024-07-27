import os
from tkinter import Tk, Button, filedialog, messagebox, PhotoImage
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

        # Treeview for displaying images
        self.tree = ttk.Treeview(self, columns=('Path'), show='tree')
        self.tree.pack(pady=10, fill='both', expand=True)
        self.tree.bind("<ButtonRelease-1>", self.on_item_select)

        self.tree.tag_configure('image', image=None)
        self.tree.bind('<B1-Motion>', self.drag_motion)
        self.tree.bind('<ButtonRelease-1>', self.drop_item)

        # Image references to avoid garbage collection
        self.image_refs = []

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
        self.image_refs.append(tk_img)  # keep a reference!
        self.tree.insert('', 'end', text=os.path.basename(file_path), values=(file_path,), tags=('image',))
        self.tree.tag_configure('image', image=tk_img)

    def drag_motion(self, event):
        self.tree.update_idletasks()
        item = self.tree.identify('item', event.x, event.y)
        self.tree.selection_set(item)

    def drop_item(self, event):
        item = self.tree.selection()[0]
        target = self.tree.identify_row(event.y)
        if target and target != item:
            items = self.tree.get_children()
            item_idx = items.index(item)
            target_idx = items.index(target)
            self.tree.move(item, '', target_idx if item_idx < target_idx else target_idx+1)
            self.update_image_order()

    def update_image_order(self):
        items = self.tree.get_children()
        self.images = [self.tree.item(item, 'values')[0] for item in items]

    def on_item_select(self, event):
        self.update_image_order()

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
            for idx, file_path in enumerate(self.images):
                img = Image.open(file_path)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                image_objects.append(img)

            image_objects[0].save(pdf_path, save_all=True, append_images=image_objects[1:])
            messagebox.showinfo("Success", f"Images have been successfully converted to {pdf_path}")

    def clear_list(self):
        self.images = []
        self.tree.delete(*self.tree.get_children())
        self.image_refs.clear()

# Initialize the GUI application
app = ImageToPDFApp()
app.mainloop()
