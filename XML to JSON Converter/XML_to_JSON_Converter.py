import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import xml.etree.ElementTree as ET
import json

class XmlToJsonConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("XML to JSON Converter")
        self.root.geometry("600x400")

        self.label = tk.Label(root, text="XML to JSON Converter", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.open_button = tk.Button(root, text="Open XML File", command=self.open_xml)
        self.open_button.pack(pady=5)

        self.preview_button = tk.Button(root, text="Preview XML Data", command=self.preview_xml, state=tk.DISABLED)
        self.preview_button.pack(pady=5)

        self.convert_button = tk.Button(root, text="Convert to JSON", command=self.convert_to_json, state=tk.DISABLED)
        self.convert_button.pack(pady=5)

        self.progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress.pack(pady=20)

        self.xml_data = None

    def open_xml(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("XML Files", "*.xml"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                tree = ET.parse(file_path)
                self.xml_data = self.element_to_dict(tree.getroot())
                messagebox.showinfo("Success", "XML file loaded successfully!")
                self.preview_button.config(state=tk.NORMAL)
                self.convert_button.config(state=tk.NORMAL)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load XML file: {e}")

    def element_to_dict(self, element):
        """Convert an XML element to a dictionary."""
        def parse_element(el):
            d = {}
            for child in el:
                if len(child) > 0:
                    d[child.tag] = parse_element(child)
                else:
                    d[child.tag] = child.text
            return d

        return {element.tag: parse_element(element)}

    def preview_xml(self):
        if self.xml_data:
            preview_window = tk.Toplevel(self.root)
            preview_window.title("XML Data Preview")
            preview_window.geometry("500x300")
            
            text_area = tk.Text(preview_window, wrap=tk.WORD)
            text_area.pack(expand=True, fill=tk.BOTH)
            text_area.insert(tk.END, json.dumps(self.xml_data, indent=4))
            text_area.config(state=tk.DISABLED)

    def convert_to_json(self):
        if self.xml_data:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
            )
            if save_path:
                try:
                    self.progress['value'] = 0
                    self.root.update_idletasks()

                    with open(save_path, "w") as json_file:
                        json.dump(self.xml_data, json_file, indent=4)
                        self.progress['value'] = 100
                        self.root.update_idletasks()
                        messagebox.showinfo("Success", "JSON file saved successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save JSON file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = XmlToJsonConverter(root)
    root.mainloop()
