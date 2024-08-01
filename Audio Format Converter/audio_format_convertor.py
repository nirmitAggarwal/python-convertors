import os
from pydub import AudioSegment
from pydub.utils import mediainfo
from tqdm import tqdm

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
        
        # Load the audio file
        print(f"Loading audio file '{input_file}'...")
        audio = AudioSegment.from_file(input_file)

        # Extract the file name without extension
        file_name = os.path.splitext(input_file)[0]
        
        # Define the output file name
        output_file = f"{file_name}.{output_format}"
        
        # Extract metadata
        metadata = get_metadata(input_file)
        
        # Export the audio in the new format with metadata
        print(f"Converting to '{output_format}' format...")
        with tqdm(total=len(audio), desc="Converting", unit="ms") as pbar:
            audio.export(output_file, format=output_format, tags=metadata, progress_callback=lambda current, total: pbar.update(current - pbar.n))
        
        print(f"Successfully converted '{input_file}' to '{output_file}' with metadata preserved.")
    
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' could not be found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    """
    Main function to handle user input and perform the conversion.
    
    Returns:
    - None
    """
    # Get user input for the input file and output format
    input_file = input("Enter the path to the input audio file: ")
    output_format = input("Enter the desired output format (e.g., 'mp3', 'wav', 'ogg', 'flac', 'aac'): ")
    
    # Perform the conversion
    convert_audio(input_file, output_format)

# Example usage
if __name__ == "__main__":
    main()
