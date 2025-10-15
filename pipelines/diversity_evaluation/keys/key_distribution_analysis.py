import re
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
import math
from scipy.stats import entropy
import argparse
import os


def parse_key_file(file_path, file_type="real"):
    """
    Parse key detection results from file.
    
    Args:
        file_path: Path to the key file
        file_type: "real" for total_agreement_files.txt, "gen" for gen_keys_madmon.txt
    
    Returns:
        List of detected keys
    """
    keys = []
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    if file_type == "real":
        # Parse total_agreement_files.txt format - support both .mp3 and .wav files
        for line in lines:
            if (".mp3:" in line or ".wav:" in line) and ("minor" in line or "major" in line):
                # Extract key from "filename.mp3: Key" or "filename.wav: Key"
                match = re.search(r': ([A-G][#b]? (?:major|minor))', line)
                if match:
                    keys.append(match.group(1))
    else:
        # Parse gen_keys_madmon.txt format - support both .mp3 and .wav files
        for line in lines:
            if (".mp3:" in line or ".wav:" in line) and ("minor" in line or "major" in line):
                # Extract key from "filename.mp3: Key" or "filename.wav: Key"
                match = re.search(r': ([A-G][#b]? (?:major|minor))', line)
                if match:
                    keys.append(match.group(1))
    
    return keys

def normalize_key_name(key):
    """
    Normalize key names to handle enharmonic equivalents.
    """
    # Convert sharps to flats for consistency
    key_mapping = {
        'C# major': 'Db major', 'C# minor': 'C# minor',
        'D# major': 'Eb major', 'D# minor': 'Eb minor', 
        'F# major': 'F# major', 'F# minor': 'F# minor',
        'G# major': 'Ab major', 'G# minor': 'Ab minor',
        'A# major': 'Bb major', 'A# minor': 'Bb minor'
    }
    return key_mapping.get(key, key)

def get_all_possible_keys():
    """
    Get all 24 possible major and minor keys.
    """
    notes = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
    keys = []
    for note in notes:
        keys.append(f"{note} major")
        keys.append(f"{note} minor")
    return keys

def calculate_key_distribution(keys):
    """
    Calculate the probability distribution of keys.
    """
    all_keys = get_all_possible_keys()
    key_counts = Counter([normalize_key_name(key) for key in keys])
    total_count = len(keys)
    
    # Create probability distribution for all 24 keys
    distribution = {}
    for key in all_keys:
        normalized_key = normalize_key_name(key)
        distribution[normalized_key] = key_counts.get(normalized_key, 0) / total_count
    
    return distribution

def calculate_entropy(distribution):
    """
    Calculate Shannon entropy of key distribution.
    H = -Σ p_i * log2(p_i)
    """
    probs = [p for p in distribution.values() if p > 0]
    return -sum(p * math.log2(p) for p in probs)

def calculate_kl_divergence(real_dist, gen_dist):
    """
    Calculate KL divergence: D_KL(P_real || P_gen)
    """
    kl_div = 0
    for key in real_dist:
        p_real = real_dist[key]
        p_gen = gen_dist[key]
        
        if p_real > 0:
            # Add small epsilon to avoid log(0)
            p_gen_safe = max(p_gen, 1e-10)
            kl_div += p_real * math.log2(p_real / p_gen_safe)
    
    return kl_div

def calculate_overlapping_area(real_dist, gen_dist):
    """
    Calculate overlapping area between two distributions.
    """
    overlap = 0
    for key in real_dist:
        overlap += min(real_dist[key], gen_dist[key])
    return overlap

def calculate_rare_key_activation(distribution, threshold=0.05):
    """
    Calculate rare key activation rate.
    Rare keys are those with probability < threshold.
    """
    rare_keys = [key for key, prob in distribution.items() if prob < threshold and prob > 0]
    total_keys_used = sum(1 for prob in distribution.values() if prob > 0)
    
    if total_keys_used == 0:
        return 0, rare_keys
    
    rare_activation_rate = len(rare_keys) / total_keys_used
    return rare_activation_rate, rare_keys

def plot_key_distributions(real_dist, gen_dist, output_path=None):
    """
    Plot comparison of real vs generated key distributions.
    """
    keys = list(real_dist.keys())
    real_probs = [real_dist[key] for key in keys]
    gen_probs = [gen_dist[key] for key in keys]
    
    x = np.arange(len(keys))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(15, 8))
    bars1 = ax.bar(x - width/2, real_probs, width, label='Real Music', alpha=0.8)
    bars2 = ax.bar(x + width/2, gen_probs, width, label='Generated Music', alpha=0.8)
    
    ax.set_xlabel('Musical Keys')
    ax.set_ylabel('Probability')
    ax.set_title('Key Distribution Comparison: Real vs Generated Music')
    ax.set_xticks(x)
    ax.set_xticklabels(keys, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {output_path}")
    else:
        plt.show()

def analyze_key_distributions(real_file, gen_file, output_dir="analysis_results"):
    """
    Perform comprehensive analysis of key distributions.
    """
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Parse key files
    print("Parsing key files...")
    real_keys = parse_key_file(real_file, "real")
    gen_keys = parse_key_file(gen_file, "gen")
    
    print(f"Real music keys found: {len(real_keys)}")
    print(f"Generated music keys found: {len(gen_keys)}")
    
    # Calculate distributions
    real_dist = calculate_key_distribution(real_keys)
    gen_dist = calculate_key_distribution(gen_keys)
    
    # Calculate metrics
    print("\n" + "="*60)
    print("KEY DISTRIBUTION ANALYSIS RESULTS")
    print("="*60)
    
    # 1. Total Real Keys - ratio
    total_real_keys = len(real_keys)
    unique_real_keys = len([k for k, v in real_dist.items() if v > 0])
    real_key_ratio = unique_real_keys / 24
    print(f"\n1. Total Real Keys Ratio:")
    print(f"   - Total files: {total_real_keys}")
    print(f"   - Unique keys used: {unique_real_keys}/24")
    print(f"   - Total keys ratio: {real_key_ratio:.3f}")
    
    # Show percentage of each key across all real songs
    print(f"\n   Key Distribution (% of {total_real_keys} songs):")
    for key in sorted(real_dist.keys()):
        percentage = real_dist[key] * 100
        if percentage > 0:
            print(f"   - {key}: {percentage:.1f}%")
    
    # 2. Total Gen Keys - ratio  
    total_gen_keys = len(gen_keys)
    unique_gen_keys = len([k for k, v in gen_dist.items() if v > 0])
    gen_key_ratio = unique_gen_keys / 24
    print(f"\n2. Total Generated Keys Ratio:")
    print(f"   - Total files: {total_gen_keys}")
    print(f"   - Unique keys used: {unique_gen_keys}/24")
    print(f"   - Total keys ratio: {gen_key_ratio:.3f}")
    
    # Show percentage of each key across all generated songs
    print(f"\n   Key Distribution (% of {total_gen_keys} songs):")
    for key in sorted(gen_dist.keys()):
        percentage = gen_dist[key] * 100
        if percentage > 0:
            print(f"   - {key}: {percentage:.1f}%")
    
    # 3. Distribution Entropy
    real_entropy = calculate_entropy(real_dist)
    gen_entropy = calculate_entropy(gen_dist)
    max_entropy = math.log2(24)  # ≈ 4.58
    
    print(f"\n3. Distribution Entropy (Diversity):")
    print(f"   - Real music entropy: {real_entropy:.3f}")
    print(f"   - Generated music entropy: {gen_entropy:.3f}")
    print(f"   - Maximum possible entropy: {max_entropy:.3f}")
    print(f"   - Real diversity ratio: {real_entropy/max_entropy:.3f}")
    print(f"   - Generated diversity ratio: {gen_entropy/max_entropy:.3f}")
    
    # 4. KL Divergence
    kl_divergence = calculate_kl_divergence(real_dist, gen_dist)
    print(f"\n4. KL Divergence D_KL(P_real || P_gen):")
    print(f"   - KL divergence: {kl_divergence:.3f}")
    print(f"   - Lower values indicate better match to real distribution")
    
    # 5. Overlapping Area
    overlap = calculate_overlapping_area(real_dist, gen_dist)
    print(f"\n5. Overlapping Area:")
    print(f"   - Overlap coefficient: {overlap:.3f}")
    print(f"   - Higher values indicate better distribution match")
    
    # 6. Rare Key Activation
    real_rare_rate, real_rare_keys = calculate_rare_key_activation(real_dist)
    gen_rare_rate, gen_rare_keys = calculate_rare_key_activation(gen_dist)
    
    print(f"\n6. Rare Key Activation (p < 0.05):")
    print(f"   - Real music rare key rate: {real_rare_rate:.3f}")
    print(f"   - Generated music rare key rate: {gen_rare_rate:.3f}")
    print(f"   - Real rare keys: {real_rare_keys[:5]}{'...' if len(real_rare_keys) > 5 else ''}")
    print(f"   - Generated rare keys: {gen_rare_keys[:5]}{'...' if len(gen_rare_keys) > 5 else ''}")
    
    # Generate detailed report
    report_path = os.path.join(output_dir, "key_analysis_report.txt")
    with open(report_path, 'w') as f:
        f.write("KEY DISTRIBUTION ANALYSIS REPORT\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Analysis Date: {__import__('datetime').datetime.now()}\n")
        f.write(f"Real Music File: {real_file}\n")
        f.write(f"Generated Music File: {gen_file}\n\n")
        
        f.write("METRICS SUMMARY:\n")
        f.write("-" * 20 + "\n")
        f.write(f"Total Real Keys: {total_real_keys} (Coverage: {unique_real_keys/24:.3f})\n")
        f.write(f"Total Gen Keys: {total_gen_keys} (Coverage: {unique_gen_keys/24:.3f})\n")
        f.write(f"Real Entropy: {real_entropy:.3f} (Diversity: {real_entropy/max_entropy:.3f})\n")
        f.write(f"Gen Entropy: {gen_entropy:.3f} (Diversity: {gen_entropy/max_entropy:.3f})\n")
        f.write(f"KL Divergence: {kl_divergence:.3f}\n")
        f.write(f"Overlapping Area: {overlap:.3f}\n")
        f.write(f"Real Rare Key Rate: {real_rare_rate:.3f}\n")
        f.write(f"Gen Rare Key Rate: {gen_rare_rate:.3f}\n\n")
        
        f.write("DETAILED DISTRIBUTIONS:\n")
        f.write("-" * 25 + "\n")
        f.write(f"{'Key':<12} {'Real':<8} {'Generated':<10} {'Difference':<10}\n")
        f.write("-" * 45 + "\n")
        
        for key in sorted(real_dist.keys()):
            real_prob = real_dist[key]
            gen_prob = gen_dist[key]
            diff = abs(real_prob - gen_prob)
            f.write(f"{key:<12} {real_prob:<8.3f} {gen_prob:<10.3f} {diff:<10.3f}\n")
    
    print(f"\nDetailed report saved to: {report_path}")
    
    # Generate visualization
    plot_path = os.path.join(output_dir, "key_distribution_comparison.png")
    plot_key_distributions(real_dist, gen_dist, plot_path)
    
    return {
        'total_real_keys': total_real_keys,
        'total_gen_keys': total_gen_keys,
        'real_entropy': real_entropy,
        'gen_entropy': gen_entropy,
        'kl_divergence': kl_divergence,
        'overlapping_area': overlap,
        'real_rare_rate': real_rare_rate,
        'gen_rare_rate': gen_rare_rate,
        'real_distribution': real_dist,
        'gen_distribution': gen_dist
    }

def main():
    parser = argparse.ArgumentParser(description='Analyze key distributions between real and generated music')
    parser.add_argument('--real-file', default='total_agreement_files.txt',
                       help='Path to real music keys file (default: total_agreement_files.txt)')
    parser.add_argument('--gen-file', default='gen_melody_keys_topk250_madmom.txt', 
                       help='Path to generated music keys file (default: gen_keys_madmon.txt)')
    parser.add_argument('--output-dir', default='analysis_results_melody_topk250',
                       help='Output directory for results (default: analysis_results)')
    
    args = parser.parse_args()
    
    results = analyze_key_distributions(args.real_file, args.gen_file, args.output_dir)
    print("\nAnalysis completed successfully!")

if __name__ == "__main__":
    main()