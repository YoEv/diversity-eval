import librosa
import numpy as np
import os
import argparse
from pathlib import Path

def estimate_key(audio_file):
    """
    Estimate the musical key of an audio file using librosa.
    Returns the estimated key as a string.
    """
    try:
        # Load audio file
        y, sr = librosa.load(audio_file)
        
        # Extract chroma features
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        
        # Average chroma across time
        chroma_mean = np.mean(chroma, axis=1)
        
        # Define key profiles (major and minor)
        # Krumhansl-Schmuckler key profiles
        major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        
        # Note names
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Calculate correlation with each key
        correlations = []
        
        for i in range(12):
            # Rotate profiles to match different keys
            major_rotated = np.roll(major_profile, i)
            minor_rotated = np.roll(minor_profile, i)
            
            # Calculate correlation
            major_corr = np.corrcoef(chroma_mean, major_rotated)[0, 1]
            minor_corr = np.corrcoef(chroma_mean, minor_rotated)[0, 1]
            
            correlations.append((notes[i] + ' major', major_corr))
            correlations.append((notes[i] + ' minor', minor_corr))
        
        # Find the key with highest correlation
        best_key = max(correlations, key=lambda x: x[1])
        
        return best_key[0]
        
    except Exception as e:
        return f"Error: {str(e)}"

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
    
    # Write results to output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Musical Key Detection Results (Librosa)\n")
            f.write("=" * 30 + "\n\n")
            for result in results:
                f.write(result + "\n")
        
        print(f"\nResults saved to '{output_file}'")
        print(f"Processed {len(results)} files successfully.")
        
    except Exception as e:
        print(f"Error writing to output file: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Detect musical keys of audio files in a folder using librosa"
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Path to the folder containing music files'
    )
    
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Path to the output text file where results will be saved'
    )
    
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Search for audio files recursively in subfolders (default: True)'
    )
    
    args = parser.parse_args()
    
    print(f"Music folder: {args.input}")
    print(f"Output file: {args.output}")
    print("Starting key detection...\n")
    
    process_music_folder(args.input, args.output)

if __name__ == "__main__":
    main()