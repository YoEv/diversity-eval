import re
import os
import shutil
import argparse
from pathlib import Path

def parse_key_file(file_path):
    """
    Parse a key detection result file and return a dictionary mapping filenames to keys.
    
    Args:
        file_path: Path to the key detection result file
        
    Returns:
        dict: Dictionary with filename as key and detected musical key as value
    """
    results = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Skip header lines and parse results
    for line in lines:
        line = line.strip()
        if ':' in line and not line.startswith('Musical Key') and not line.startswith('='):
            # Split on the first colon to separate filename and key
            parts = line.split(': ', 1)
            if len(parts) == 2:
                filename = parts[0].strip()
                key = parts[1].strip()
                results[filename] = key
    
    return results

def normalize_key_name(key):
    """
    Normalize key names for better comparison (handle enharmonic equivalents).
    
    Args:
        key: Musical key string (e.g., "C# major", "Db major")
        
    Returns:
        str: Normalized key name
    """
    # Convert sharp/flat equivalents
    key_mappings = {
        'C#': 'Db', 'D#': 'Eb', 'F#': 'Gb', 'G#': 'Ab', 'A#': 'Bb',
        'Db': 'Db', 'Eb': 'Eb', 'Gb': 'Gb', 'Ab': 'Ab', 'Bb': 'Bb'
    }
    
    parts = key.split()
    if len(parts) == 2:
        note, mode = parts
        normalized_note = key_mappings.get(note, note)
        return f"{normalized_note} {mode}"
    
    return key

def copy_agreement_files(source_dir, output_dir, agreed_files_with_keys, agreement_list_file):
    """
    Copy files with total agreement to a new folder and create a list file.
    
    Args:
        source_dir: Directory containing the original audio files
        output_dir: Directory to copy agreed files to
        agreed_files_with_keys: List of tuples (filename, detected_key) that have agreement
        agreement_list_file: Path to save the list of agreed files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    copied_files = []
    not_found_files = []
    
    print(f"\nCopying {len(agreed_files_with_keys)} files with total agreement to {output_dir}...")
    
    for filename, detected_key in agreed_files_with_keys:
        # Check if filename already has an extension
        if any(filename.endswith(ext) for ext in ['.wav', '.mp3', '.flac', '.m4a', '.ogg', '.aac']):
            # Filename already includes extension, use it directly
            potential_path = os.path.join(source_dir, filename)
            if os.path.exists(potential_path):
                source_file = potential_path
            else:
                source_file = None
        else:
            # Find the source file (check common audio extensions)
            source_file = None
            audio_extensions = ['.wav', '.mp3', '.flac', '.m4a', '.ogg', '.aac']
            
            for ext in audio_extensions:
                potential_path = os.path.join(source_dir, filename + ext)
                if os.path.exists(potential_path):
                    source_file = potential_path
                    break
        
        if source_file:
            # Copy file to output directory
            dest_file = os.path.join(output_dir, os.path.basename(source_file))
            try:
                shutil.copy2(source_file, dest_file)
                copied_files.append((os.path.basename(source_file), detected_key))
                print(f"✓ Copied: {os.path.basename(source_file)} (Key: {detected_key})")
            except Exception as e:
                print(f"✗ Failed to copy {os.path.basename(source_file)}: {e}")
        else:
            not_found_files.append((filename, detected_key))
            print(f"✗ Source file not found: {filename}")
    
    # Create agreement list file
    with open(agreement_list_file, 'w', encoding='utf-8') as f:
        f.write("Files with Total Agreement (Exact + Enharmonic Matches)\n")
        f.write("=" * 55 + "\n\n")
        f.write(f"Total files with agreement: {len(agreed_files_with_keys)}\n")
        f.write(f"Successfully copied: {len(copied_files)}\n")
        f.write(f"Not found: {len(not_found_files)}\n\n")
        
        f.write("Successfully copied files with detected keys:\n")
        f.write("-" * 50 + "\n")
        for file, key in sorted(copied_files):
            f.write(f"{file}: {key}\n")
        
        if not_found_files:
            f.write("\nFiles not found in source directory:\n")
            f.write("-" * 40 + "\n")
            for file, key in sorted(not_found_files):
                f.write(f"{file}: {key}\n")
    
    print(f"\nCopy operation complete:")
    print(f"- Successfully copied: {len(copied_files)} files")
    print(f"- Not found: {len(not_found_files)} files")
    print(f"- Agreement list saved to: {agreement_list_file}")
    
    return copied_files, not_found_files

def compare_key_results(librosa_file, madmom_file, output_file=None):
    """
    Compare key detection results from librosa and madmom.
    
    Args:
        librosa_file: Path to librosa results file
        madmom_file: Path to madmom results file
        output_file: Optional path to save detailed comparison results
    """
    print("Parsing key detection results...")
    
    # Parse both files
    librosa_results = parse_key_file(librosa_file)
    madmom_results = parse_key_file(madmom_file)
    
    print(f"Librosa results: {len(librosa_results)} files")
    print(f"Madmom results: {len(madmom_results)} files")
    
    # Find common files
    common_files = set(librosa_results.keys()) & set(madmom_results.keys())
    print(f"Common files: {len(common_files)}")
    
    # Compare results
    exact_matches = 0
    enharmonic_matches = 0
    differences = []
    agreed_files_with_keys = []  # Files with total agreement (exact + enharmonic) and their keys
    
    for filename in sorted(common_files):
        librosa_key = librosa_results[filename]
        madmom_key = madmom_results[filename]
        
        if librosa_key == madmom_key:
            exact_matches += 1
            agreed_files_with_keys.append((filename, librosa_key))
        elif normalize_key_name(librosa_key) == normalize_key_name(madmom_key):
            enharmonic_matches += 1
            # Use librosa key as the agreed key (could also use madmom_key)
            agreed_files_with_keys.append((filename, librosa_key))
        else:
            differences.append({
                'filename': filename,
                'librosa': librosa_key,
                'madmom': madmom_key
            })
    
    # Print summary
    print("\n" + "=" * 60)
    print("KEY DETECTION COMPARISON RESULTS")
    print("=" * 60)
    print(f"Total files compared: {len(common_files)}")
    print(f"Exact matches: {exact_matches} ({exact_matches/len(common_files)*100:.1f}%)")
    print(f"Enharmonic matches: {enharmonic_matches} ({enharmonic_matches/len(common_files)*100:.1f}%)")
    print(f"Different keys: {len(differences)} ({len(differences)/len(common_files)*100:.1f}%)")
    
    total_matches = exact_matches + enharmonic_matches
    print(f"Total agreement: {total_matches} ({total_matches/len(common_files)*100:.1f}%)")
    
    # Show differences
    if differences:
        print(f"\nFILES WITH DIFFERENT KEY DETECTIONS ({len(differences)} files):")
        print("-" * 80)
        print(f"{'Filename':<50} {'Librosa':<15} {'Madmom':<15}")
        print("-" * 80)
        
        for diff in differences[:190]:  # Show first 20 differences
            filename = diff['filename'][:47] + '...' if len(diff['filename']) > 50 else diff['filename']
            print(f"{filename:<50} {diff['librosa']:<15} {diff['madmom']:<15}")
        
        if len(differences) > 190:
            print(f"... and {len(differences) - 190} more differences")
    
    # Save detailed results if requested
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Key Detection Comparison Results\n")
            f.write("=" * 35 + "\n\n")
            f.write(f"Total files compared: {len(common_files)}\n")
            f.write(f"Exact matches: {exact_matches} ({exact_matches/len(common_files)*100:.1f}%)\n")
            f.write(f"Enharmonic matches: {enharmonic_matches} ({enharmonic_matches/len(common_files)*100:.1f}%)\n")
            f.write(f"Different keys: {len(differences)} ({len(differences)/len(common_files)*100:.1f}%)\n")
            f.write(f"Total agreement: {total_matches} ({total_matches/len(common_files)*100:.1f}%)\n\n")
            
            if differences:
                f.write("Files with different key detections:\n")
                f.write("-" * 80 + "\n")
                for diff in differences:
                    f.write(f"{diff['filename']}: Librosa={diff['librosa']}, Madmom={diff['madmom']}\n")
        
        print(f"\nDetailed results saved to: {output_file}")
    
    return {
        'total_files': len(common_files),
        'exact_matches': exact_matches,
        'enharmonic_matches': enharmonic_matches,
        'differences': len(differences),
        'agreement_rate': total_matches / len(common_files) * 100,
        'agreed_files_with_keys': agreed_files_with_keys
    }

def main():
    parser = argparse.ArgumentParser(description='Compare key detection results from librosa and madmom')
    parser.add_argument('--librosa', default='Shutter_Solo_keys_librosa.txt',
                        help='Path to librosa results file (default: Shutter_Solo_keys_librosa.txt)')
    parser.add_argument('--madmom', default='Shutter_Solo_keys_madmom.txt',
                        help='Path to madmom results file (default: Shutter_Solo_keys_madmom.txt)')
    parser.add_argument('--output', default='key_comparison_results.txt',
                        help='Path to save detailed comparison results (default: key_comparison_results.txt)')
    parser.add_argument('--source-dir', default='Shutter_Solo_Dataset_15s',
                        help='Source directory containing audio files (default: Shutter_Solo_Dataset_15s)')
    parser.add_argument('--copy-agreed', action='store_true',
                        help='Copy files with total agreement to a new folder')
    parser.add_argument('--agreed-dir', default='Agreed_Keys_Dataset',
                        help='Directory to copy agreed files to (default: Agreed_Keys_Dataset)')
    parser.add_argument('--agreed-list', default='total_agreement_files.txt',
                        help='File to save list of agreed files (default: total_agreement_files.txt)')
    
    args = parser.parse_args()
    
    # Check if files exist
    if not Path(args.librosa).exists():
        print(f"Error: {args.librosa} not found")
        return
    
    if not Path(args.madmom).exists():
        print(f"Error: {args.madmom} not found")
        return
    
    # Compare results
    results = compare_key_results(args.librosa, args.madmom, args.output)
    
    print(f"\nSummary: {results['differences']} out of {results['total_files']} files have different key detections")
    print(f"Agreement rate: {results['agreement_rate']:.1f}%")
    
    # Copy agreed files if requested
    if args.copy_agreed:
        if not Path(args.source_dir).exists():
            print(f"Error: Source directory {args.source_dir} not found")
            return
        
        copy_agreement_files(args.source_dir, args.agreed_dir, 
                           results['agreed_files_with_keys'], args.agreed_list)

if __name__ == "__main__":
    main()