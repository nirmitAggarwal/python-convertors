import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import xml.etree.ElementTree as ET

class JsonToXmlConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON to XML Converter")
        self.root.geometry("600x400")

        self.label = tk.Label(root, text="JSON to XML Converter", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.open_button = tk.Button(root, text="Open JSON File", command=self.open_json)
        self.open_button.pack(pady=5)

        self.preview_button = tk.Button(root, text="Preview JSON Data", command=self.preview_json, state=tk.DISABLED)
        self.preview_button.pack(pady=5)

        self.convert_button = tk.Button(root, text="Convert to XML", command=self.convert_to_xml, state=tk.DISABLED)
        self.convert_button.pack(pady=5)

        self.progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress.pack(pady=20)

        self.json_data = None

    def open_json(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r") as file:
                    self.json_data = json.load(file)
                messagebox.showinfo("Success", "JSON file loaded successfully!")
                self.preview_button.config(state=tk.NORMAL)
                self.convert_button.config(state=tk.NORMAL)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load JSON file: {e}")

    def dict_to_element(self, tag, d):
        """Convert a dictionary to an XML Element."""
        elem = ET.Element(tag)
        if isinstance(d, dict):
            for key, val in d.items():
                child_elem = None
                if isinstance(val, dict):
                    child_elem = self.dict_to_element(key, val)
                elif isinstance(val, list):
                    child_elem = ET.Element(key)
                    for i, item in enumerate(val):
                        list_elem = self.dict_to_element(f"{key}_{i}", item)
                        child_elem.append(list_elem)
                else:
                    child_elem = ET.Element(key)
                    child_elem.text = str(val)
                if child_elem is not None:
                    elem.append(child_elem)
        return elem

    def preview_json(self):
        if self.json_data:
            preview_window = tk.Toplevel(self.root)
            preview_window.title("JSON Data Preview")
            preview_window.geometry("500x300")
            
            text_area = tk.Text(preview_window, wrap=tk.WORD)
            text_area.pack(expand=True, fill=tk.BOTH)
            text_area.insert(tk.END, json.dumps(self.json_data, indent=4))
            text_area.config(state=tk.DISABLED)

    def convert_to_xml(self):
        if self.json_data:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xml",
                filetypes=[("XML Files", "*.xml"), ("All Files", "*.*")]
            )
            if save_path:
                try:
                    self.progress['value'] = 0
                    self.root.update_idletasks()

                    root_element = self.dict_to_element('root', self.json_data)
                    tree = ET.ElementTree(root_element)
                    tree.write(save_path, encoding='utf-8', xml_declaration=True)
                    
                    self.progress['value'] = 100
                    self.root.update_idletasks()
                    messagebox.showinfo("Success", "XML file saved successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save XML file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = JsonToXmlConverter(root)
    root.mainloop()
