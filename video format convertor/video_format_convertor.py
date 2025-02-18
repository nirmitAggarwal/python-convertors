import os
import logging
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from moviepy.editor import VideoFileClip
from moviepy.video.fx import resize
from tqdm import tqdm
import threading
from PIL import Image, ImageTk

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_valid_format(format):
    valid_formats = ["mp4", "avi", "mov", "wmv", "flv", "mkv"]
    return format.lower() in valid_formats

def get_metadata(input_file):
    try:
        clip = VideoFileClip(input_file)
        duration = clip.duration
        fps = clip.fps
        width, height = clip.size
        metadata = {
            "duration": duration,
            "fps": fps,
            "resolution": f"{width}x{height}",
            "audio_codec": clip.audio.codec if clip.audio else 'None',
            "video_codec": clip.codec if hasattr(clip, 'codec') else 'Unknown'
        }
        return metadata
    except Exception as e:
        logging.error(f"Error retrieving metadata: {e}")
        return None

def get_resolution_from_string(resolution_str):
    try:
        width, height = map(int, resolution_str.lower().split('x'))
        return (width, height)
    except ValueError:
        return None

def convert_video(input_file, output_formats, start_time=None, end_time=None, video_bitrate=None, audio_bitrate=None, resolution=None, aspect_ratio=None):
    try:
        # Check if the input file exists
        if not os.path.exists(input_file):
            logging.error(f"The file '{input_file}' does not exist.")
            return
        
        # Check if the output formats are valid
        for format in output_formats:
            if not is_valid_format(format):
                logging.error(f"'{format}' is not a valid format. Valid formats are: mp4, avi, mov, wmv, flv, mkv.")
                return
        
        # Retrieve and print metadata
        metadata = get_metadata(input_file)
        if metadata:
            logging.info("Video Metadata:")
            for key, value in metadata.items():
                logging.info(f"  {key}: {value}")
        
        # Load the video file
        clip = VideoFileClip(input_file)
        
        # Trim the video if start and end times are provided
        if start_time is not None and end_time is not None:
            clip = clip.subclip(start_time, end_time)
        
        # Resize video if resolution is provided
        if resolution:
            width, height = resolution
            clip = resize(clip, newsize=(width, height))
        
        # Convert to each output format
        for output_format in output_formats:
            # Determine the output file name
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}.{output_format}"
            
            # Progress bar
            duration = clip.duration
            with tqdm(total=duration, desc=f"Converting to {output_format}", unit="s") as pbar:
                def update_progress(get_frame, t):
                    pbar.update(t - pbar.n)
                    return get_frame(t)
                new_clip = clip.fl(update_progress, apply_to=["mask", "audio"])
                
                # Write the video to the output file
                new_clip.write_videofile(
                    output_file,
                    bitrate=video_bitrate,
                    audio_bitrate=audio_bitrate
                )
            
            logging.info(f"Successfully converted '{input_file}' to '{output_file}'")
            messagebox.showinfo("Success", f"Successfully converted '{input_file}' to '{output_file}'")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

def browse_files():
    filenames = filedialog.askopenfilenames(filetypes=[("Video files", "*.mp4 *.avi *.mov *.wmv *.flv *.mkv")])
    if filenames:
        for filename in filenames:
            input_files_listbox.insert(tk.END, filename)
            input_files.append(filename)

def preview_video():
    selected_file = input_files_listbox.get(tk.ACTIVE)
    if selected_file:
        metadata = get_metadata(selected_file)
        if metadata:
            preview_label.config(text=f"Duration: {metadata['duration']}s\nFPS: {metadata['fps']}\nResolution: {metadata['resolution']}\nAudio Codec: {metadata['audio_codec']}\nVideo Codec: {metadata['video_codec']}")
            clip = VideoFileClip(selected_file)
            clip.preview()

def start_conversion():
    output_formats = output_formats_var.get().split()
    start_time = float(start_time_var.get()) if start_time_var.get() else None
    end_time = float(end_time_var.get()) if end_time_var.get() else None
    video_bitrate = video_bitrate_var.get() if video_bitrate_var.get() else None
    audio_bitrate = audio_bitrate_var.get() if audio_bitrate_var.get() else None
    resolution_str = resolution_var.get() if resolution_var.get() else None
    aspect_ratio = aspect_ratio_var.get() if aspect_ratio_var.get() else None

    resolution = get_resolution_from_string(resolution_str) if resolution_str else None

    def convert_files():
        for input_file in input_files:
            convert_video(input_file, output_formats, start_time, end_time, video_bitrate, audio_bitrate, resolution, aspect_ratio)

    conversion_thread = threading.Thread(target=convert_files)
    conversion_thread.start()

def create_gui():
    global output_formats_var, start_time_var, end_time_var, video_bitrate_var, audio_bitrate_var, resolution_var, aspect_ratio_var
    global input_files_listbox, preview_label, input_files

    root = tk.Tk()
    root.title("Video Format Converter")

    input_files = []

    output_formats_var = tk.StringVar()
    start_time_var = tk.StringVar()
    end_time_var = tk.StringVar()
    video_bitrate_var = tk.StringVar()
    audio_bitrate_var = tk.StringVar()
    resolution_var = tk.StringVar()
    aspect_ratio_var = tk.StringVar()

    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    ttk.Label(main_frame, text="Input Files:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
    browse_button = ttk.Button(main_frame, text="Browse", command=browse_files)
    browse_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

    input_files_listbox = tk.Listbox(main_frame, height=5)
    input_files_listbox.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=(tk.W, tk.E))

    ttk.Label(main_frame, text="Output Formats (space-separated):").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
    output_formats_entry = ttk.Entry(main_frame, textvariable=output_formats_var, width=50)
    output_formats_entry.grid(row=2, column=1, padx=10, pady=10, sticky=(tk.W, tk.E))

    ttk.Label(main_frame, text="Start Time (seconds):").grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
    start_time_entry = ttk.Entry(main_frame, textvariable=start_time_var, width=50)
    start_time_entry.grid(row=3, column=1, padx=10, pady=10, sticky=(tk.W, tk.E))

    ttk.Label(main_frame, text="End Time (seconds):").grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
    end_time_entry = ttk.Entry(main_frame, textvariable=end_time_var, width=50)
    end_time_entry.grid(row=4, column=1, padx=10, pady=10, sticky=(tk.W, tk.E))

    ttk.Label(main_frame, text="Video Bitrate (e.g., 500k, 1M):").grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)
    video_bitrate_entry = ttk.Entry(main_frame, textvariable=video_bitrate_var, width=50)
    video_bitrate_entry.grid(row=5, column=1, padx=10, pady=10, sticky=(tk.W, tk.E))

    ttk.Label(main_frame, text="Audio Bitrate (e.g., 128k):").grid(row=6, column=0, padx=10, pady=10, sticky=tk.W)
    audio_bitrate_entry = ttk.Entry(main_frame, textvariable=audio_bitrate_var, width=50)
    audio_bitrate_entry.grid(row=6, column=1, padx=10, pady=10, sticky=(tk.W, tk.E))

    ttk.Label(main_frame, text="Resolution (widthxheight):").grid(row=7, column=0, padx=10, pady=10, sticky=tk.W)
    resolution_entry = ttk.Entry(main_frame, textvariable=resolution_var, width=50)
    resolution_entry.grid(row=7, column=1, padx=10, pady=10, sticky=(tk.W, tk.E))

    ttk.Label(main_frame, text="Aspect Ratio (e.g., 16:9, 4:3):").grid(row=8, column=0, padx=10, pady=10, sticky=tk.W)
    aspect_ratio_entry = ttk.Entry(main_frame, textvariable=aspect_ratio_var, width=50)
    aspect_ratio_entry.grid(row=8, column=1, padx=10, pady=10, sticky=(tk.W, tk.E))

    preview_button = ttk.Button(main_frame, text="Preview", command=preview_video)
    preview_button.grid(row=9, column=0, padx=10, pady=10, sticky=tk.W)
    convert_button = ttk.Button(main_frame, text="Convert", command=start_conversion)
    convert_button.grid(row=9, column=1, padx=10, pady=10, sticky=(tk.W, tk.E))

    preview_label = ttk.Label(main_frame, text="Video Metadata:")
    preview_label.grid(row=10, column=0, columnspan=2, padx=10, pady=10, sticky=(tk.W, tk.E))

    root.mainloop()

if __name__ == "__main__":
    create_gui()
