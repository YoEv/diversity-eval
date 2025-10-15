#!/usr/bin/env python3

import os
import sys
from key_distribution_analysis import (
    parse_key_file, 
    calculate_key_distribution, 
    calculate_entropy,
    calculate_kl_divergence,
    calculate_overlapping_area,
    calculate_rare_key_activation,
    plot_key_distributions
)
import matplotlib.pyplot as plt
import numpy as np

def run_uniform_comparisons():
    # Create uniform distribution file first
    print("Creating uniform distribution file...")
    exec(open('create_uniform_distribution.py').read())
    
    # Parse uniform distribution
    uniform_keys = parse_key_file("uniform_distri.txt", file_type="gen")
    uniform_dist = calculate_key_distribution(uniform_keys)
    
    # Files to compare against
    comparison_files = [
        "BJ_Segments_keys_madmom.txt",
        "BJ_Segments_1st_keys_madmom.txt", 
        "Shutter_keys_total_agreement_files.txt",
        "gen_melody_keys_topk250_1st_madmom.txt",
        "gen_melody_keys_topk250_2nd_madmom.txt",
        "gen_melody_keys_topk250_3rd_madmom.txt"
    ]
    
    # Create results directory
    os.makedirs("uniform_comparison_results", exist_ok=True)
    
    print(f"\nUniform distribution created with {len(uniform_keys)} pieces")
    print("\nStarting comparisons...\n")
    
    for comparison_file in comparison_files:
        if not os.path.exists(comparison_file):
            print(f"Warning: {comparison_file} not found, skipping...")
            continue
            
        try:
            print(f"=== Comparing uniform distribution with {comparison_file} ===")
            
            # Parse comparison file
            base_name = os.path.splitext(comparison_file)[0]
            if "total_agreement" in comparison_file:
                comp_keys = parse_key_file(comparison_file, file_type="real")
            else:
                comp_keys = parse_key_file(comparison_file, file_type="gen")
            comp_dist = calculate_key_distribution(comp_keys)
            
            print(f"Dataset: {len(comp_keys)} keys")
            
            # Calculate metrics
            comp_entropy = calculate_entropy(comp_dist)
            kl_div = calculate_kl_divergence(uniform_dist, comp_dist)
            overlap_area = calculate_overlapping_area(uniform_dist, comp_dist)
            rare_keys_uniform_rate, rare_keys_uniform_list = calculate_rare_key_activation(uniform_dist)
            rare_keys_comp_rate, rare_keys_comp_list = calculate_rare_key_activation(comp_dist)
            
            # Create visualization
            output_path = f"uniform_comparison_results/{base_name}_vs_uniform.png"
            plot_key_distributions(uniform_dist, comp_dist, output_path)
            
            # Save detailed results
            results_text = f"""Comparison: Uniform Distribution vs {os.path.basename(comparison_file)}
{'=' * 80}

Dataset Statistics:
- Uniform Distribution: {len(uniform_keys)} pieces
- {os.path.basename(comparison_file)}: {len(comp_keys)} pieces

Key Distribution Metrics:
- Uniform Entropy: {calculate_entropy(uniform_dist):.4f}
- Dataset Entropy: {comp_entropy:.4f}
- KL Divergence (Uniform → Dataset): {kl_div:.4f}
- Overlapping Area: {overlap_area:.4f}
- Rare Keys (Uniform): {rare_keys_uniform_rate:.4f}
- Rare Keys (Dataset): {rare_keys_comp_rate:.4f}

Interpretation:
- Higher entropy indicates more uniform key distribution
- Lower KL divergence indicates similarity to uniform distribution
- Higher overlapping area indicates better coverage similarity
- Lower rare key rate indicates better key diversity
"""
            
            with open(f"uniform_comparison_results/{base_name}_vs_uniform_results.txt", 'w') as f:
                f.write(results_text)
                
            print(f"Results saved to uniform_comparison_results/{base_name}_vs_uniform_results.txt")
            print(f"Visualization saved to {output_path}")
            
            # Print key metrics
            print(f"Entropy: {comp_entropy:.4f} (Uniform: {calculate_entropy(uniform_dist):.4f})")
            print(f"KL Divergence: {kl_div:.4f}")
            print(f"Overlapping Area: {overlap_area:.4f}")
            
        except Exception as e:
            print(f"Error processing {comparison_file}: {e}")
            continue
    
    print("\nAll comparisons completed. Results saved in uniform_comparison_results/ directory.")

if __name__ == "__main__":
    run_uniform_comparisons()