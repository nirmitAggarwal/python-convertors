import os
import logging
from pydub import AudioSegment
from pydub.utils import mediainfo
from tqdm import tqdm
import argparse
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Menu
from tkinter.scrolledtext import ScrolledText
import simpleaudio as sa
import time

# Configure logging
logging.basicConfig(filename='audio_converter.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def is_valid_format(format):
    valid_formats = ["mp3", "wav", "ogg", "flac", "aac", "wma", "m4a"]
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

def convert_audio(input_file, output_format, bitrate=None, channels=None, sample_rate=None, progress_callback=None):
    try:
        if not os.path.exists(input_file):
            print(f"Error: The file '{input_file}' does not exist.")
            return

        if not is_valid_format(output_format):
            print(f"Error: '{output_format}' is not a valid format. Valid formats are: mp3, wav, ogg, flac, aac, wma, m4a.")
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

        params = {}
        if bitrate:
            params["bitrate"] = bitrate
        if channels:
            params["channels"] = channels
        if sample_rate:
            params["sample_rate"] = sample_rate
        
        print(f"Converting to '{output_format}' format...")
        with tqdm(total=len(audio), desc="Converting", unit="ms") as pbar:
            audio.export(output_file, format=output_format, tags=metadata, parameters=params, progress_callback=lambda current, total: pbar.update(current - pbar.n))
        
        print(f"Successfully converted '{input_file}' to '{output_file}' with metadata and parameters preserved.")
    
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' could not be found.")
        logging.error(f"The file '{input_file}' could not be found.")
    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred: {e}")

def batch_convert(directory, output_format, bitrate=None, channels=None, sample_rate=None, progress_bar=None, progress_label=None):
    try:
        if not os.path.exists(directory):
            print(f"Error: The directory '{directory}' does not exist.")
            return

        tasks = []
        start_time = time.time()

        with ThreadPoolExecutor() as executor:
            for file_name in os.listdir(directory):
                input_file = os.path.join(directory, file_name)
                if os.path.isfile(input_file):
                    tasks.append(executor.submit(convert_audio, input_file, output_format, bitrate, channels, sample_rate))
            
            for task in tqdm(tasks, desc="Batch Conversion", unit="file"):
                task.result()
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        progress_label.config(text=f"Batch conversion completed in {elapsed_time:.2f} seconds.")
        progress_bar['value'] = 100
    
    except Exception as e:
        print(f"An error occurred during batch conversion: {e}")
        logging.error(f"An error occurred during batch conversion: {e}")

def preview_audio(file_path):
    try:
        wave_obj = sa.WaveObject.from_wave_file(file_path)
        play_obj = wave_obj.play()
        play_obj.wait_done()
    except Exception as e:
        print(f"An error occurred during audio preview: {e}")
        logging.error(f"An error occurred during audio preview: {e}")

# GUI Code starts here

class AudioConverterGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Audio Format Converter")
        self.geometry("800x600")
        self.resizable(False, False)
        
        self.create_widgets()
    
    def create_widgets(self):
        self.create_menu()
        
        self.input_label = tk.Label(self, text="Input File/Directory:")
        self.input_label.pack(pady=5)
        
        self.input_entry = tk.Entry(self, width=60)
        self.input_entry.pack(pady=5)
        
        self.browse_button = tk.Button(self, text="Browse", command=self.browse_files)
        self.browse_button.pack(pady=5)
        
        self.format_label = tk.Label(self, text="Output Format:")
        self.format_label.pack(pady=5)
        
        self.format_combobox = ttk.Combobox(self, values=["mp3", "wav", "ogg", "flac", "aac", "wma", "m4a"])
        self.format_combobox.pack(pady=5)
        
        self.batch_var = tk.BooleanVar()
        self.batch_checkbox = tk.Checkbutton(self, text="Batch Conversion", variable=self.batch_var)
        self.batch_checkbox.pack(pady=5)

        self.bitrate_label = tk.Label(self, text="Bitrate (e.g., 192k):")
        self.bitrate_label.pack(pady=5)
        
        self.bitrate_entry = tk.Entry(self, width=20)
        self.bitrate_entry.pack(pady=5)
        
        self.channels_label = tk.Label(self, text="Channels (e.g., 1 or 2):")
        self.channels_label.pack(pady=5)
        
        self.channels_entry = tk.Entry(self, width=20)
        self.channels_entry.pack(pady=5)
        
        self.sample_rate_label = tk.Label(self, text="Sample Rate (e.g., 44100):")
        self.sample_rate_label.pack(pady=5)
        
        self.sample_rate_entry = tk.Entry(self, width=20)
        self.sample_rate_entry.pack(pady=5)
        
        self.edit_metadata_button = tk.Button(self, text="Edit Metadata", command=self.edit_metadata)
        self.edit_metadata_button.pack(pady=5)

        self.preview_button = tk.Button(self, text="Preview Audio", command=self.preview_audio)
        self.preview_button.pack(pady=5)
        
        self.convert_button = tk.Button(self, text="Convert", command=self.start_conversion)
        self.convert_button.pack(pady=5)
        
        self.progress_label = tk.Label(self, text="Progress:")
        self.progress_label.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(self, length=400, mode='determinate')
        self.progress_bar.pack(pady=5)
        
        self.log_text = ScrolledText(self, height=10, width=70)
        self.log_text.pack(pady=5)
        
        self.input_entry.drop_target_register(tk.DND_FILES)
        self.input_entry.dnd_bind('<<Drop>>', self.drop_files)

    def create_menu(self):
        menu_bar = Menu(self)

        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self.browse_files)
        file_menu.add_command(label="Save As", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        settings_menu = Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="Preferences", command=self.open_preferences)
        settings_menu.add_command(label="Language", command=self.change_language)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)
        
        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menu_bar)

    def open_preferences(self):
        messagebox.showinfo("Preferences", "Preferences window coming soon.")

    def change_language(self):
        messagebox.showinfo("Language", "Language selection coming soon.")

    def show_about(self):
        messagebox.showinfo("About", "Audio Format Converter v1.0\nCreated by Nirmit Aggarwal")

    def browse_files(self):
        file_path = filedialog.askopenfilename(title="Select a File", filetypes=(("Audio Files", "*.mp3;*.wav;*.ogg;*.flac;*.aac;*.wma;*.m4a"), ("All Files", "*.*")))
        self.input_entry.insert(0, file_path)
    
    def save_as(self):
        save_path = filedialog.asksaveasfilename(title="Save File As", defaultextension=".txt", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
        with open(save_path, 'w') as file:
            file.write(self.log_text.get("1.0", tk.END))
        messagebox.showinfo("Save As", f"Log saved to {save_path}")

    def drop_files(self, event):
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, event.data)
    
    def edit_metadata(self):
        input_path = self.input_entry.get()
        if not input_path:
            messagebox.showerror("Error", "Please select an input file first.")
            return
        metadata = get_metadata(input_path)
        edit_metadata_gui(metadata, self)

    def preview_audio(self):
        input_path = self.input_entry.get()
        if not input_path:
            messagebox.showerror("Error", "Please select an input file first.")
            return
        preview_audio(input_path)
    
    def start_conversion(self):
        input_path = self.input_entry.get()
        output_format = self.format_combobox.get()
        batch_mode = self.batch_var.get()
        bitrate = self.bitrate_entry.get()
        channels = self.channels_entry.get()
        sample_rate = self.sample_rate_entry.get()

        if not input_path or not output_format:
            messagebox.showerror("Error", "Please provide both input file and output format.")
            return
        
        self.progress_bar["value"] = 0
        self.log_text.insert(tk.END, "Starting conversion...\n")
        
        if batch_mode:
            self.batch_convert_gui(input_path, output_format, bitrate, channels, sample_rate)
        else:
            self.convert_audio_gui(input_path, output_format, bitrate, channels, sample_rate)
    
    def convert_audio_gui(self, input_file, output_format, bitrate=None, channels=None, sample_rate=None):
        try:
            if not os.path.exists(input_file):
                self.log_text.insert(tk.END, f"Error: The file '{input_file}' does not exist.\n")
                logging.error(f"The file '{input_file}' does not exist.")
                return

            if not is_valid_format(output_format):
                self.log_text.insert(tk.END, f"Error: '{output_format}' is not a valid format.\n")
                logging.error(f"'{output_format}' is not a valid format.")
                return
            
            input_format = detect_format(input_file)
            if input_format == "unknown":
                self.log_text.insert(tk.END, f"Error: Could not detect the format of '{input_file}'.\n")
                logging.error(f"Could not detect the format of '{input_file}'.")
                return
            
            self.log_text.insert(tk.END, f"Loading audio file '{input_file}'...\n")
            audio = AudioSegment.from_file(input_file, format=input_format)

            file_name = os.path.splitext(input_file)[0]
            output_file = f"{file_name}.{output_format}"
            
            metadata = get_metadata(input_file)
            metadata = edit_metadata_gui(metadata, self)  # Update metadata via GUI

            params = {}
            if bitrate:
                params["bitrate"] = bitrate
            if channels:
                params["channels"] = channels
            if sample_rate:
                params["sample_rate"] = sample_rate
            
            self.log_text.insert(tk.END, f"Converting to '{output_format}' format...\n")
            with tqdm(total=len(audio), desc="Converting", unit="ms") as pbar:
                audio.export(output_file, format=output_format, tags=metadata, parameters=params, progress_callback=lambda current, total: pbar.update(current - pbar.n))
            
            self.log_text.insert(tk.END, f"Successfully converted '{input_file}' to '{output_file}' with metadata and parameters preserved.\n")
        
        except FileNotFoundError:
            self.log_text.insert(tk.END, f"Error: The file '{input_file}' could not be found.\n")
            logging.error(f"The file '{input_file}' could not be found.")
        except Exception as e:
            self.log_text.insert(tk.END, f"An error occurred: {e}\n")
            logging.error(f"An error occurred: {e}")
    
    def batch_convert_gui(self, directory, output_format, bitrate=None, channels=None, sample_rate=None):
        try:
            if not os.path.exists(directory):
                messagebox.showerror("Error", f"The directory '{directory}' does not exist.")
                return

            tasks = []
            start_time = time.time()

            with ThreadPoolExecutor() as executor:
                for file_name in os.listdir(directory):
                    input_file = os.path.join(directory, file_name)
                    if os.path.isfile(input_file):
                        tasks.append(executor.submit(self.convert_audio_gui, input_file, output_format, bitrate, channels, sample_rate))
                
                for task in tqdm(tasks, desc="Batch Conversion", unit="file"):
                    task.result()
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            self.progress_label.config(text=f"Batch conversion completed in {elapsed_time:.2f} seconds.")
            self.progress_bar['value'] = 100
        
        except Exception as e:
            self.log_text.insert(tk.END, f"An error occurred during batch conversion: {e}\n")
            logging.error(f"An error occurred during batch conversion: {e}")

if __name__ == "__main__":
    app = AudioConverterGUI()
    app.mainloop()
