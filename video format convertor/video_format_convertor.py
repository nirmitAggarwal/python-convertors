import os
import sys
import logging
import argparse
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
    except Exception as e:
        logging.error(f"An error occurred: {e}")

def parse_args():
    parser = argparse.ArgumentParser(description="Video Format Converter")
    parser.add_argument("input_file", help="Path to the input video file")
    parser.add_argument("output_formats", nargs='+', help="Desired output formats (e.g., mp4 avi mov)")
    parser.add_argument("--start", type=float, help="Start time for conversion (in seconds)", default=None)
    parser.add_argument("--end", type=float, help="End time for conversion (in seconds)", default=None)
    return parser.parse_args()

def main():
    args = parse_args()
    
    convert_video(args.input_file, args.output_formats, args.start, args.end)

if __name__ == "__main__":
    main()
