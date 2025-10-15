import madmom
import numpy as np
import os
import argparse
from pathlib import Path

def estimate_key(audio_file):
    """
    Estimate the musical key of an audio file using madmom.
    Returns the estimated key as a string.
    """
    # Use madmom's CNN key recognition processor
    proc = madmom.features.key.CNNKeyRecognitionProcessor()
    
    # Load and process the audio file
    key_predictions = proc(audio_file)
    
    # Convert predictions to human-readable key label
    estimated_key = madmom.features.key.key_prediction_to_label(key_predictions)
    
    return estimated_key
        

def process_music_folder(music_folder, output_file):
    """
    Process all audio files in a folder and detect their keys.
    Save results to a text file.
    """
    # Supported audio formats
    audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma'}
    
    results = []
    music_path = Path(music_folder)
    
    if not music_path.exists():
        print(f"Error: Music folder '{music_folder}' does not exist.")
        return
    
    # Find all audio files
    audio_files = []
    for file_path in music_path.rglob('*'):
        if file_path.suffix.lower() in audio_extensions:
            audio_files.append(file_path)
    
    if not audio_files:
        print(f"No audio files found in '{music_folder}'.")
        return
    
    print(f"Found {len(audio_files)} audio files. Processing...")
    
    # Process each audio file
    for i, audio_file in enumerate(audio_files, 1):
        print(f"Processing {i}/{len(audio_files)}: {audio_file.name}")
        
        key = estimate_key(str(audio_file))
        relative_path = audio_file.relative_to(music_path)
        results.append(f"{relative_path}: {key}")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Musical Key Detection Results (Madmom)\n")
        f.write("=" * 35 + "\n\n")
        for result in results:
            f.write(result + "\n")
    
    print(f"\nResults saved to '{output_file}'")
    print(f"Processed {len(results)} files successfully.")


def main():
    parser = argparse.ArgumentParser(description="Detect musical keys of audio files in a folder using madmom")
    parser.add_argument('-i', '--input', required=True, help='Path to the folder containing music files')
    parser.add_argument('-o', '--output', required=True, help='Path to the output text file where results will be saved')
    parser.add_argument('--recursive', '-r', action='store_true', help='Search for audio files recursively in subfolders (default: True)')
    args = parser.parse_args()
    
    print(f"Music folder: {args.input}")
    print(f"Output file: {args.output}")
    print("Starting key detection with Madmom...\n")

    process_music_folder(args.input, args.output)

if __name__ == "__main__":
    main()