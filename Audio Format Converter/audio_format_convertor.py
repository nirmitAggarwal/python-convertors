import os
from pydub import AudioSegment

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

def convert_audio(input_file, output_format):
    """
    Convert an audio file to a different format.
    
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
        
        # Export the audio in the new format
        print(f"Converting to '{output_format}' format...")
        audio.export(output_file, format=output_format)
        
        print(f"Successfully converted '{input_file}' to '{output_file}'")
    
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
