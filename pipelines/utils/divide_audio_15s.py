import os
import subprocess
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json
import tempfile

def find_continuous_vocal_segments(input_file, min_db_threshold=-12, segment_length=15, min_silence_duration=0.5, max_gap_duration=2.0):
    """
    Find continuous segments where audio stays above the dB threshold for at least segment_length seconds.
    Gaps of max_gap_duration seconds or less are considered continuous.
    Returns list of valid segments as (start_time, end_time) tuples.
    """
    # Use FFmpeg silencedetect to find silence segments
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_file,
        "-af", f"silencedetect=noise={min_db_threshold}dB:d={min_silence_duration}",
        "-f", "null",
        "-"
    ]
    
    try:
        result = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        stderr_output = result.stderr.decode('utf-8')
        
        # Parse silence detection output
        silence_starts = []
        silence_ends = []
        
        for line in stderr_output.split('\n'):
            if 'silence_start:' in line:
                start_time = float(line.split('silence_start: ')[1].split()[0])
                silence_starts.append(start_time)
            elif 'silence_end:' in line:
                end_time = float(line.split('silence_end: ')[1].split()[0])
                silence_ends.append(end_time)
        
        # Get total duration
        duration_cmd = [
            "ffprobe",
            "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "csv=p=0",
            input_file
        ]
        duration_result = subprocess.run(duration_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        total_duration = float(duration_result.stdout.decode('utf-8').strip())
        
        # Build continuous vocal segments (non-silent segments)
        vocal_segments = []
        current_start = 0.0
        
        # Handle case where silence detection found segments
        for i in range(len(silence_starts)):
            if silence_starts[i] > current_start:
                vocal_segments.append((current_start, silence_starts[i]))
            
            if i < len(silence_ends):
                current_start = silence_ends[i]
        
        # Add final segment if there's audio after last silence
        if current_start < total_duration:
            vocal_segments.append((current_start, total_duration))
        
        # Merge segments separated by gaps of max_gap_duration or less
        merged_segments = []
        if vocal_segments:
            current_segment = vocal_segments[0]
            
            for next_segment in vocal_segments[1:]:
                gap_duration = next_segment[0] - current_segment[1]
                
                # If gap is small enough, merge the segments
                if gap_duration <= max_gap_duration:
                    current_segment = (current_segment[0], next_segment[1])
                else:
                    # Gap is too large, finalize current segment and start new one
                    merged_segments.append(current_segment)
                    current_segment = next_segment
            
            # Add the last segment
            merged_segments.append(current_segment)
        
        # Filter segments that are at least segment_length seconds long
        valid_segments = []
        for start, end in merged_segments:
            segment_duration = end - start
            if segment_duration >= segment_length:
                # Calculate how many complete segment_length chunks we can extract
                num_chunks = int(segment_duration // segment_length)
                for i in range(num_chunks):
                    chunk_start = start + (i * segment_length)
                    chunk_end = chunk_start + segment_length
                    valid_segments.append((chunk_start, chunk_end))
        
        return valid_segments, total_duration
        
    except subprocess.CalledProcessError as e:
        print(f"Error analyzing audio {input_file}: {e}")
        return [], 0.0

def extract_15s_segments(input_file, output_dir, segment_length=15):
    """
    Extract continuous 15-second segments with vocal content above -12dB threshold.
    Preserves musical coherence by keeping original timing.
    """
    input_path = Path(input_file)
    base_name = input_path.stem
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Find continuous vocal segments
    valid_segments, total_duration = find_continuous_vocal_segments(input_file, segment_length=segment_length)
    
    if not valid_segments:
        print(f"⚠ No continuous {segment_length}s vocal segments found in {input_path.name}")
        return 0
    
    print(f"🎵 {input_path.name}: Found {len(valid_segments)} continuous {segment_length}s segments")
    
    segments_created = 0
    for i, (start_time, end_time) in enumerate(valid_segments):
        output_filename = f"{base_name}_{i+1:03d}_15s.wav"
        output_path = os.path.join(output_dir, output_filename)
        
        # Extract the segment using FFmpeg
        extract_cmd = [
            "ffmpeg",
            "-i", input_file,
            "-ss", str(start_time),
            "-t", str(segment_length),
            "-c:a", "copy",  # Copy audio codec to avoid re-encoding
            "-y",  # Overwrite output file if it exists
            output_path
        ]
        
        try:
            subprocess.run(extract_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            segments_created += 1
            print(f"  ✓ Created: {output_filename} (from {start_time:.1f}s-{end_time:.1f}s)")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Failed to create segment {i+1}: {e}")
    
    return segments_created

def batch_divide_bj_opera_dataset(input_dir="BJ_Opera_Vocal", output_dir="BJ_Opera_Vocal_15s", threads=4):
    """
    Process all audio files in BJ_Opera_Vocal dataset.
    """
    supported_formats = ('.wav', '.WAV', '.m4a', '.mp3', '.flac', '.ogg', '.aac', '.mp4', '.wma')
    
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist")
        return
    
    audio_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(tuple(fmt.lower() for fmt in supported_formats)):
                audio_files.append(os.path.join(root, file))
    
    if not audio_files:
        print(f"Error: No supported audio files found in {input_dir}")
        return
    
    print(f"Found {len(audio_files)} audio files in {input_dir}")
    print(f"Extracting continuous 15s vocal segments (>-12dB)...\n")
    
    # Process files in parallel
    def process_file(file_path):
        try:
            return extract_15s_segments(file_path, output_dir)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return 0
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        results = list(executor.map(process_file, audio_files))
    
    total_segments = sum(results)
    successful_files = sum(1 for r in results if r > 0)
    
    print(f"\n🎵 Processing complete:")
    print(f"   Files processed: {successful_files}/{len(audio_files)}")
    print(f"   Total 15s segments created: {total_segments}")
    print(f"   Output directory: {output_dir}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Extract continuous 15-second vocal segments from BJ Opera audio files'
    )
    parser.add_argument('--input', default='BJ_Opera_Vocal',
                        help='Input directory containing audio files (default: BJ_Opera_Vocal)')
    parser.add_argument('--output', default='BJ_Opera_Vocal_15s',
                        help='Output directory for segmented audio files (default: BJ_Opera_Vocal_15s)')
    parser.add_argument('--threads', type=int, default=4,
                        help='Number of parallel processing threads (default: 4)')
    parser.add_argument('--db-threshold', type=float, default=-12.0,
                        help='Minimum dB threshold for vocal content (default: -12.0)')
    
    args = parser.parse_args()
    
    # Check if FFmpeg is available
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["ffprobe", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: FFmpeg and FFprobe are required but not found in PATH")
        return
    
    print(f"Input directory: {args.input}")
    print(f"Output directory: {args.output}")
    print(f"dB threshold: {args.db_threshold}dB")
    print(f"Threads: {args.threads}")
    print("Starting continuous segment extraction...\n")
    
    # Run the batch processing
    batch_divide_bj_opera_dataset(args.input, args.output, args.threads)

if __name__ == "__main__":
    main()