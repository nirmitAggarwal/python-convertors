import os
import logging
from pydub import AudioSegment
from pydub.utils import mediainfo
from tqdm import tqdm
import argparse
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

# Configure logging
logging.basicConfig(filename='audio_converter.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def is_valid_format(format):
    valid_formats = ["mp3", "wav", "ogg", "flac", "aac"]
    return format.lower() in valid_formats

def get_metadata(input_file):
    info = mediainfo(input_file)
    metadata = {
        "title": info.get("title", "Unknown"),
        "artist": info.get("artist", "Unknown"),
        "album": info.get("album", "Unknown"),
        "year": info.get("date", "Unknown"),
    }
    return metadata

def edit_metadata_gui(metadata, parent):
    metadata_window = tk.Toplevel(parent)
    metadata_window.title("Edit Metadata")
    metadata_window.geometry("300x250")

    fields = ["Title", "Artist", "Album", "Year"]
    entries = {}

    for i, field in enumerate(fields):
        label = tk.Label(metadata_window, text=field)
        label.grid(row=i, column=0, padx=10, pady=5, sticky='e')
        entry = tk.Entry(metadata_window, width=30)
        entry.insert(0, metadata[field.lower()])
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[field.lower()] = entry

    def save_metadata():
        for field, entry in entries.items():
            metadata[field] = entry.get()
        metadata_window.destroy()

    save_button = tk.Button(metadata_window, text="Save", command=save_metadata)
    save_button.grid(row=len(fields), column=0, columnspan=2, pady=10)

    metadata_window.transient(parent)
    metadata_window.grab_set()
    parent.wait_window(metadata_window)
    
    return metadata

def detect_format(input_file):
    info = mediainfo(input_file)
    return info.get("format_name", "unknown")

def convert_audio(input_file, output_format, progress_callback=None):
    try:
        if not os.path.exists(input_file):
            print(f"Error: The file '{input_file}' does not exist.")
            return

        if not is_valid_format(output_format):
            print(f"Error: '{output_format}' is not a valid format. Valid formats are: mp3, wav, ogg, flac, aac.")
            return
        
        input_format = detect_format(input_file)
        if input_format == "unknown":
            print(f"Error: Could not detect the format of '{input_file}'.")
            return
        
        print(f"Loading audio file '{input_file}'...")
        audio = AudioSegment.from_file(input_file, format=input_format)

        file_name = os.path.splitext(input_file)[0]
        output_file = f"{file_name}.{output_format}"
        
        metadata = get_metadata(input_file)
        metadata = edit_metadata_gui(metadata, None)  # Update metadata via GUI
        
        print(f"Converting to '{output_format}' format...")
        with tqdm(total=len(audio), desc="Converting", unit="ms") as pbar:
            audio.export(output_file, format=output_format, tags=metadata, progress_callback=lambda current, total: pbar.update(current - pbar.n))
        
        print(f"Successfully converted '{input_file}' to '{output_file}' with metadata preserved.")
    
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' could not be found.")
        logging.error(f"The file '{input_file}' could not be found.")
    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred: {e}")

def batch_convert(directory, output_format):
    try:
        if not os.path.exists(directory):
            print(f"Error: The directory '{directory}' does not exist.")
            return

        tasks = []

        with ThreadPoolExecutor() as executor:
            for file_name in os.listdir(directory):
                input_file = os.path.join(directory, file_name)
                if os.path.isfile(input_file):
                    tasks.append(executor.submit(convert_audio, input_file, output_format))
            
            for task in tqdm(tasks, desc="Batch Conversion", unit="file"):
                task.result()
    
    except Exception as e:
        print(f"An error occurred during batch conversion: {e}")
        logging.error(f"An error occurred during batch conversion: {e}")

def main():
    parser = argparse.ArgumentParser(description="Audio Format Converter")
    parser.add_argument('input', type=str, help="Input file or directory")
    parser.add_argument('output_format', type=str, help="Desired output format (e.g., 'mp3', 'wav', 'ogg', 'flac', 'aac')")
    parser.add_argument('--batch', action='store_true', help="Enable batch conversion if input is a directory")
    args = parser.parse_args()

    if args.batch:
        batch_convert(args.input, args.output_format)
    else:
        convert_audio(args.input, args.output_format)

# GUI Code starts here

class AudioConverterGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Audio Format Converter")
        self.geometry("600x400")
        self.resizable(False, False)
        
        self.create_widgets()
    
    def create_widgets(self):
        self.input_label = tk.Label(self, text="Input File/Directory:")
        self.input_label.pack(pady=5)
        
        self.input_entry = tk.Entry(self, width=60)
        self.input_entry.pack(pady=5)
        
        self.browse_button = tk.Button(self, text="Browse", command=self.browse_files)
        self.browse_button.pack(pady=5)
        
        self.format_label = tk.Label(self, text="Output Format:")
        self.format_label.pack(pady=5)
        
        self.format_combobox = ttk.Combobox(self, values=["mp3", "wav", "ogg", "flac", "aac"])
        self.format_combobox.pack(pady=5)
        
        self.batch_var = tk.BooleanVar()
        self.batch_checkbox = tk.Checkbutton(self, text="Batch Conversion", variable=self.batch_var)
        self.batch_checkbox.pack(pady=5)
        
        self.edit_metadata_button = tk.Button(self, text="Edit Metadata", command=self.edit_metadata)
        self.edit_metadata_button.pack(pady=5)
        
        self.convert_button = tk.Button(self, text="Convert", command=self.start_conversion)
        self.convert_button.pack(pady=5)
        
        self.progress_label = tk.Label(self, text="Progress:")
        self.progress_label.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(self, length=400, mode='determinate')
        self.progress_bar.pack(pady=5)
        
        self.log_text = ScrolledText(self, height=10, width=70)
        self.log_text.pack(pady=5)
    
    def browse_files(self):
        input_path = filedialog.askopenfilename()
        if input_path:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, input_path)
    
    def edit_metadata(self):
        input_path = self.input_entry.get()
        if input_path and os.path.isfile(input_path):
            metadata = get_metadata(input_path)
            edited_metadata = edit_metadata_gui(metadata, self)
            self.log_text.insert(tk.END, f"Metadata edited for {input_path}: {edited_metadata}\n")
        else:
            messagebox.showerror("Error", "Please provide a valid input file to edit metadata.")
    
    def start_conversion(self):
        input_path = self.input_entry.get()
        output_format = self.format_combobox.get()
        batch_conversion = self.batch_var.get()
        
        if not input_path or not output_format:
            messagebox.showerror("Error", "Please provide an input file and select an output format.")
            return
        
        self.progress_bar['value'] = 0
        self.log_text.insert(tk.END, "Starting conversion...\n")
        
        if batch_conversion:
            self.batch_convert_gui(input_path, output_format)
        else:
            self.convert_audio_gui(input_path, output_format)
        
        messagebox.showinfo("Success", "Conversion completed successfully.")
    
    def convert_audio_gui(self, input_file, output_format):
        try:
            if not os.path.exists(input_file):
                messagebox.showerror("Error", f"The file '{input_file}' does not exist.")
                return

            if not is_valid_format(output_format):
                messagebox.showerror("Error", f"'{output_format}' is not a valid format. Valid formats are: mp3, wav, ogg, flac, aac.")
                return
            
            input_format = detect_format(input_file)
            if input_format == "unknown":
                messagebox.showerror("Error", f"Could not detect the format of '{input_file}'.")
                return
            
            self.log_text.insert(tk.END, f"Loading audio file '{input_file}'...\n")
            audio = AudioSegment.from_file(input_file, format=input_format)

            file_name = os.path.splitext(input_file)[0]
            output_file = f"{file_name}.{output_format}"
            
            metadata = get_metadata(input_file)
            metadata = edit_metadata_gui(metadata, self)  # Update metadata via GUI
            
            self.log_text.insert(tk.END, f"Converting to '{output_format}' format...\n")
            with tqdm(total=len(audio), desc="Converting", unit="ms") as pbar:
                audio.export(output_file, format=output_format, tags=metadata, progress_callback=lambda current, total: pbar.update(current - pbar.n))
            
            self.log_text.insert(tk.END, f"Successfully converted '{input_file}' to '{output_file}' with metadata preserved.\n")
        
        except FileNotFoundError:
            self.log_text.insert(tk.END, f"Error: The file '{input_file}' could not be found.\n")
            logging.error(f"The file '{input_file}' could not be found.")
        except Exception as e:
            self.log_text.insert(tk.END, f"An error occurred: {e}\n")
            logging.error(f"An error occurred: {e}")
    
    def batch_convert_gui(self, directory, output_format):
        try:
            if not os.path.exists(directory):
                messagebox.showerror("Error", f"The directory '{directory}' does not exist.")
                return

            tasks = []
            
            with ThreadPoolExecutor() as executor:
                for file_name in os.listdir(directory):
                    input_file = os.path.join(directory, file_name)
                    if os.path.isfile(input_file):
                        tasks.append(executor.submit(self.convert_audio_gui, input_file, output_format))
                
                for task in tqdm(tasks, desc="Batch Conversion", unit="file"):
                    task.result()
        
        except Exception as e:
            self.log_text.insert(tk.END, f"An error occurred during batch conversion: {e}\n")
            logging.error(f"An error occurred during batch conversion: {e}")

if __name__ == "__main__":
    app = AudioConverterGUI()
    app.mainloop()
