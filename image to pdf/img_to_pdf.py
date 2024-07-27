import os
from tkinter import Tk, Button, Listbox, MULTIPLE, filedialog, messagebox
from PIL import Image

def browse_images():
    file_paths = filedialog.askopenfilenames(
        title="Select Images",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
    )
    for file_path in file_paths:
        images_listbox.insert('end', file_path)

def convert_to_pdf():
    image_files = list(images_listbox.get(0, 'end'))
    if not image_files:
        messagebox.showwarning("No Images Selected", "Please select images to convert.")
        return
    
    pdf_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF file", "*.pdf")],
        title="Save PDF As"
    )
    
    if pdf_path:
        image_objects = []
        for file in image_files:
            img = Image.open(file)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            image_objects.append(img)
        
        image_objects[0].save(pdf_path, save_all=True, append_images=image_objects[1:])
        messagebox.showinfo("Success", f"Images have been successfully converted to {pdf_path}")

def clear_list():
    images_listbox.delete(0, 'end')

# Initialize the GUI application
app = Tk()
app.title("Image to PDF Converter")
app.geometry("400x300")

# Add buttons and listbox to the GUI
browse_button = Button(app, text="Browse Images", command=browse_images)
browse_button.pack(pady=10)

clear_button = Button(app, text="Clear List", command=clear_list)
clear_button.pack(pady=10)

images_listbox = Listbox(app, selectmode=MULTIPLE)
images_listbox.pack(pady=10, fill='both', expand=True)

convert_button = Button(app, text="Convert", command=convert_to_pdf)
convert_button.pack(pady=10)

# Run the GUI event loop
app.mainloop()
