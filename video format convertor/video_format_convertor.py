import os
import sys
from moviepy.editor import VideoFileClip

def convert_video(input_file, output_format):
    try:
        # Check if the input file exists
        if not os.path.exists(input_file):
            print(f"Error: The file '{input_file}' does not exist.")
            return
        
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
