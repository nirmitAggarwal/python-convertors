import os
import sys
from moviepy.editor import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

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
            "resolution": f"{width}x{height}"
        }
        return metadata
    except Exception as e:
        print(f"Error retrieving metadata: {e}")
        return None

def convert_video(input_file, output_format):
    try:
        # Check if the input file exists
        if not os.path.exists(input_file):
            print(f"Error: The file '{input_file}' does not exist.")
            return
        
        # Check if the output format is valid
        if not is_valid_format(output_format):
            print(f"Error: '{output_format}' is not a valid format. Valid formats are: mp4, avi, mov, wmv, flv, mkv.")
            return
        
        # Retrieve and print metadata
        metadata = get_metadata(input_file)
        if metadata:
            print("Video Metadata:")
            for key, value in metadata.items():
                print(f"  {key}: {value}")
        
        # Load the video file
        clip = VideoFileClip(input_file)
        
        # Determine the output file name
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}.{output_format}"
        
        # Write the video to the output file
        clip.write_videofile(output_file)
        
        print(f"Successfully converted '{input_file}' to '{output_file}'")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python video_format_converter.py <input_file> <output_format>")
        return
    
    input_file = sys.argv[1]
    output_format = sys.argv[2]
    
    convert_video(input_file, output_format)

if __name__ == "__main__":
    main()
