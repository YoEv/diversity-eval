import os
import subprocess
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

def cut_audio_file(input_file, output_dir, cut_length=15):

    input_path = Path(input_file)
    output_filename = f"{input_path.stem}_15s{input_path.suffix}"
    output_path = os.path.join(output_dir, output_filename)

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Use FFmpeg to cut the audio file to 15 seconds
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_file,
        "-t", str(cut_length),
        "-c:a", "copy",  # Copy audio codec to avoid re-encoding
        "-y",  # Overwrite output file if it exists
        output_path
    ]

    subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print(f"✓ Cut: {input_path.name} -> {output_filename} (15s)")
    return True

def batch_cut_shutter_dataset(input_dir="Shutter_Solo_Dataset", output_dir="Shutter_Solo_Dataset_15s", threads=4):
    supported_formats = ('.wav', '.m4a', '.mp3', '.flac', '.ogg', '.aac', '.mp4', '.wma')

    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist")
        return

    audio_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(supported_formats):
                audio_files.append(os.path.join(root, file))

    if not audio_files:
        print(f"Error: No supported audio files found in {input_dir}")
        return

    print(f"Found {len(audio_files)} audio files in {input_dir}")
    print(f"Cutting all files to 15 seconds...")

    # Process files in parallel
    with ThreadPoolExecutor(max_workers=threads) as executor:
        results = list(executor.map(
            lambda f: cut_audio_file(f, output_dir, 15),
            audio_files
        ))

    success_count = sum(results)
    print(f"\nCutting complete: {success_count}/{len(audio_files)} files successfully cut to 15s")
    print(f"Output directory: {output_dir}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Cut all audio files in Shutter_Solo_Dataset to 15 seconds')
    parser.add_argument('--input', default='Shutter_Solo_Dataset', 
                        help='Input directory containing audio files (default: Shutter_Solo_Dataset)')
    parser.add_argument('--output', default='Shutter_Solo_Dataset_15s', 
                        help='Output directory for cut audio files (default: Shutter_Solo_Dataset_15s)')
    parser.add_argument('--threads', type=int, default=4, 
                        help='Number of parallel processing threads (default: 4)')

    args = parser.parse_args()

    subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print(f"Input directory: {args.input}")
    print(f"Output directory: {args.output}")
    print("Starting audio cutting process...\n")

    # Run the batch cutting
    batch_cut_shutter_dataset(args.input, args.output, args.threads)

if __name__ == "__main__":
    main()