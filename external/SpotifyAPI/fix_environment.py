#!/usr/bin/env python3
"""
Fix Spotify API environment dependencies
"""

import subprocess
import sys
import os

def run_command(cmd, check=True):
    """Run a shell command and return the result"""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        if result.stdout:
            print(result.stdout)
        if result.stderr and check:
            print(f"Warning: {result.stderr}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e.stderr}")
        return e

def fix_environment():
    """Fix the Spotify API environment"""
    print("=== Fixing Spotify API Environment ===")
    
    # Check if we're in the spotifyapi environment
    current_env = os.environ.get('CONDA_DEFAULT_ENV', '')
    if current_env == 'spotifyapi':
        print("Currently in spotifyapi environment. Please run:")
        print("conda deactivate")
        print("Then run this script again.")
        return False
    
    # Remove existing environment
    print("\n1. Removing existing spotifyapi environment...")
    run_command("conda env remove -n spotifyapi", check=False)
    
    # Create new environment
    print("\n2. Creating new spotifyapi environment...")
    result = run_command("conda env create -f environment.yml")
    
    if result.returncode != 0:
        print("Failed to create environment. Trying alternative approach...")
        
        # Create environment manually
        print("\n3. Creating environment manually...")
        run_command("conda create -n spotifyapi python=3.9 -y")
        
        # Install packages one by one
        packages = [
            "numpy=1.24.3",
            "pandas=1.5.3", 
            "scipy=1.10.1",
            "matplotlib=3.7.1",
            "requests",
            "scikit-learn",
            "librosa"
        ]
        
        for package in packages:
            print(f"Installing {package}...")
            run_command(f"conda install -n spotifyapi {package} -c conda-forge -y")
        
        # Install pip packages
        pip_packages = [
            "spotipy>=2.20.0",
            "h5py>=3.1.0", 
            "soundfile>=0.10.0",
            "numba>=0.56.0"
        ]
        
        for package in pip_packages:
            print(f"Installing {package} with pip...")
            run_command(f"conda run -n spotifyapi pip install {package}")
    
    print("\n=== Environment Setup Complete ===")
    print("To activate the environment, run:")
    print("conda activate spotifyapi")
    print("\nThen test with:")
    print("python analyze_spotify_dataset.py")
    
    return True

if __name__ == "__main__":
    fix_environment()