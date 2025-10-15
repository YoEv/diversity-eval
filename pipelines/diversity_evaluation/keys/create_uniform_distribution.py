#!/usr/bin/env python3

def create_uniform_distribution_file():
    """Create a uniform distribution file with 120 pieces, 5 per key"""
    
    # Standard 24 major and minor keys (avoiding enharmonic duplicates)
    all_keys = [
        'C major', 'C minor', 
        'C# major', 'C# minor',
        'D major', 'D minor', 
        'Eb major', 'Eb minor',
        'E major', 'E minor', 
        'F major', 'F minor', 
        'F# major', 'F# minor',
        'G major', 'G minor', 
        'Ab major', 'Ab minor',
        'A major', 'A minor', 
        'Bb major', 'Bb minor',
        'B major', 'B minor'
    ]
    
    # Verify we have exactly 24 keys
    assert len(all_keys) == 24, f"Expected 24 keys, got {len(all_keys)}"
    
    with open('uniform_distri.txt', 'w', encoding='utf-8') as f:
        f.write("Musical Key Detection Results (Uniform Distribution)\n")
        f.write("=====================================================\n")
        f.write("\n")
        
        # Create 5 pieces for each key
        for i, key in enumerate(all_keys):
            for j in range(1, 6):  # 5 pieces per key
                piece_number = i * 5 + j
                filename = f"uniform_piece_{piece_number:03d}.wav"
                f.write(f"{filename}: {key}\n")
    
    print(f"Created uniform_distri.txt with {24 * 5} pieces (5 per key for 24 keys)")
    print(f"Keys used: {len(all_keys)} unique keys")
    
    # Verify the output
    with open('uniform_distri.txt', 'r') as f:
        lines = [line.strip() for line in f if ':' in line]
        keys_in_file = [line.split(': ')[1] for line in lines]
        unique_keys = set(keys_in_file)
        
    print(f"Verification: {len(lines)} total pieces, {len(unique_keys)} unique keys")
    print(f"Unique keys: {sorted(unique_keys)}")

if __name__ == "__main__":
    create_uniform_distribution_file()