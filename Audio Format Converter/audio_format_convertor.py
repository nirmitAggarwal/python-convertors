import os
import logging
from pydub import AudioSegment
from pydub.utils import mediainfo
from tqdm import tqdm
import argparse
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(filename='audio_converter.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def is_valid_format(format):
    """
    Check if the provided format is valid.
    
    Args:
    - format (str): The format to check.
    
    Returns:
    - bool: True if format is valid, False otherwise.
    """
    valid_formats = ["mp3", "wav", "ogg", "flac", "aac"]
    return format.lower() in valid_formats

def get_metadata(input_file):
    """
    Extract metadata from the audio file.
    
    Args:
    - input_file (str): Path to the input audio file.
    
    Returns:
    - dict: Metadata of the audio file.
    """
    info = mediainfo(input_file)
    metadata = {
        "title": info.get("title", "Unknown"),
        "artist": info.get("artist", "Unknown"),
        "album": info.get("album", "Unknown"),
        "year": info.get("date", "Unknown"),
    }
    return metadata

def edit_metadata(metadata):
    """
    Edit metadata fields.
    
    Args:
    - metadata (dict): The metadata to edit.
    
    Returns:
    - dict: The edited metadata.
    """
    print("Current metadata:")
    for key, value in metadata.items():
        print(f"{key.capitalize()}: {value}")
    
    print("\nEnter new values for the metadata fields (leave blank to keep current value):")
    for key in metadata:
        new_value = input(f"{key.capitalize()}: ").strip()
        if new_value:
            metadata[key] = new_value
    
    return metadata

def detect_format(input_file):
    """
    Detect the format of the input audio file.
    
    Args:
    - input_file (str): Path to the input audio file.
    
    Returns:
    - str: Detected format of the audio file.
    """
    info = mediainfo(input_file)
    return info.get("format_name", "unknown")

def convert_audio(input_file, output_format):
    """
    Convert an audio file to a different format while preserving metadata and showing progress.
    
    Args:
    - input_file (str): Path to the input audio file.
    - output_format (str): Desired output format (e.g., 'mp3', 'wav').
    
    Returns:
    - None
    """
    try:
        # Check if the input file exists
        if not os.path.exists(input_file):
            print(f"Error: The file '{input_file}' does not exist.")
            return

        # Check if the output format is valid
        if not is_valid_format(output_format):
            print(f"Error: '{output_format}' is not a valid format. Valid formats are: mp3, wav, ogg, flac, aac.")
            return
        
        # Detect input format
        input_format = detect_format(input_file)
        if input_format == "unknown":
            print(f"Error: Could not detect the format of '{input_file}'.")
            return
        
        # Load the audio file
        print(f"Loading audio file '{input_file}'...")
        audio = AudioSegment.from_file(input_file, format=input_format)

        # Extract the file name without extension
        file_name = os.path.splitext(input_file)[0]
        
        # Define the output file name
        output_file = f"{file_name}.{output_format}"
        
        # Extract and edit metadata
        metadata = get_metadata(input_file)
        metadata = edit_metadata(metadata)
        
        # Export the audio in the new format with metadata
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
    """
    Convert all audio files in a directory to a different format using multithreading.
    
    Args:
    - directory (str): Path to the directory containing audio files.
    - output_format (str): Desired output format (e.g., 'mp3', 'wav').
    
    Returns:
    - None
    """
    try:
        # Check if the directory exists
        if not os.path.exists(directory):
            print(f"Error: The directory '{directory}' does not exist.")
            return

        # Create a list to store future tasks
        tasks = []

        with ThreadPoolExecutor() as executor:
            # Iterate through all files in the directory
            for file_name in os.listdir(directory):
                input_file = os.path.join(directory, file_name)
                if os.path.isfile(input_file):
                    # Submit each conversion task to the thread pool executor
                    tasks.append(executor.submit(convert_audio, input_file, output_format))
            
            # Wait for all tasks to complete
            for task in tqdm(tasks, desc="Batch Conversion", unit="file"):
                task.result()
    
    except Exception as e:
        print(f"An error occurred during batch conversion: {e}")
        logging.error(f"An error occurred during batch conversion: {e}")

def main():
    """
    Main function to handle user input and perform the conversion.
    
    Returns:
    - None
    """
    parser = argparse.ArgumentParser(description="Audio Format Converter")
    parser.add_argument('input', type=str, help="Input file or directory")
    parser.add_argument('output_format', type=str, help="Desired output format (e.g., 'mp3', 'wav', 'ogg', 'flac', 'aac')")
    parser.add_argument('--batch', action='store_true', help="Enable batch conversion if input is a directory")
    args = parser.parse_args()

    if args.batch:
        batch_convert(args.input, args.output_format)
    else:
        convert_audio(args.input, args.output_format)

# Example usage
if __name__ == "__main__":
    main()

# Additional utility functions and classes

def get_audio_length(input_file):
    """
    Get the length of the audio file in milliseconds.
    
    Args:
    - input_file (str): Path to the input audio file.
    
    Returns:
    - int: Length of the audio file in milliseconds.
    """
    audio = AudioSegment.from_file(input_file)
    return len(audio)

class AudioConverter:
    """
    A class to handle audio conversion tasks.
    """
    
    def __init__(self, input_file, output_format):
        self.input_file = input_file
        self.output_format = output_format
    
    def convert(self):
        convert_audio(self.input_file, self.output_format)
    
    def get_length(self):
        return get_audio_length(self.input_file)
    
    def get_metadata(self):
        return get_metadata(self.input_file)
    
    def edit_metadata(self):
        return edit_metadata(self.get_metadata())
