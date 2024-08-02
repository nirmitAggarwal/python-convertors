import os
import logging
from tkinter import *
from tkinter import filedialog, messagebox
from moviepy.editor import VideoFileClip
from tqdm import tqdm

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

def convert_video(input_file, output_formats, start_time=None, end_time=None):
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
                new_clip.write_videofile(output_file)
            
            logging.info(f"Successfully converted '{input_file}' to '{output_file}'")
            messagebox.showinfo("Success", f"Successfully converted '{input_file}' to '{output_file}'")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

def browse_file():
    filename = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov *.wmv *.flv *.mkv")])
    input_file_var.set(filename)

def start_conversion():
    input_file = input_file_var.get()
    output_formats = output_formats_var.get().split()
    start_time = float(start_time_var.get()) if start_time_var.get() else None
    end_time = float(end_time_var.get()) if end_time_var.get() else None
    
    convert_video(input_file, output_formats, start_time, end_time)

def create_gui():
    root = Tk()
    root.title("Video Format Converter")

    Label(root, text="Input File:").grid(row=0, column=0, padx=10, pady=10)
    Entry(root, textvariable=input_file_var, width=50).grid(row=0, column=1, padx=10, pady=10)
    Button(root, text="Browse", command=browse_file).grid(row=0, column=2, padx=10, pady=10)

    Label(root, text="Output Formats (space-separated):").grid(row=1, column=0, padx=10, pady=10)
    Entry(root, textvariable=output_formats_var, width=50).grid(row=1, column=1, padx=10, pady=10)

    Label(root, text="Start Time (seconds):").grid(row=2, column=0, padx=10, pady=10)
    Entry(root, textvariable=start_time_var, width=50).grid(row=2, column=1, padx=10, pady=10)

    Label(root, text="End Time (seconds):").grid(row=3, column=0, padx=10, pady=10)
    Entry(root, textvariable=end_time_var, width=50).grid(row=3, column=1, padx=10, pady=10)

    Button(root, text="Convert", command=start_conversion).grid(row=4, column=1, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    input_file_var = StringVar()
    output_formats_var = StringVar()
    start_time_var = StringVar()
    end_time_var = StringVar()
    
    create_gui()
