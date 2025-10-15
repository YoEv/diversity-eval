#!/usr/bin/env python3
"""
Install missing packages for Spotify API analysis
"""

import subprocess
import sys
import importlib

def check_package(package_name):
    """Check if a package is installed"""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def install_package(package_name, use_conda=True):
    """Install a package using conda or pip"""
    if use_conda:
        cmd = f"conda install {package_name} -c conda-forge -y"
    else:
        cmd = f"pip install {package_name}"
    
    print(f"Installing {package_name}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        print(f"✓ Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {package_name} with conda, trying pip...")
        if use_conda:
            return install_package(package_name, use_conda=False)
        else:
            print(f"Error: {e.stderr}")
            return False

def main():
    """Main function to check and install missing packages"""
    print("=== Checking and Installing Missing Packages ===")
    
    # List of required packages
    required_packages = [
        ('seaborn', 'seaborn'),
        ('matplotlib', 'matplotlib'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('scipy', 'scipy'),
        ('sklearn', 'scikit-learn'),
        ('librosa', 'librosa'),
        ('spotipy', 'spotipy'),
    ]
    
    missing_packages = []
    
    # Check which packages are missing
    for import_name, install_name in required_packages:
        if not check_package(import_name):
            missing_packages.append((import_name, install_name))
            print(f"✗ Missing: {import_name}")
        else:
            print(f"✓ Found: {import_name}")
    
    # Install missing packages
    if missing_packages:
        print(f"\nInstalling {len(missing_packages)} missing packages...")
        for import_name, install_name in missing_packages:
            install_package(install_name)
    else:
        print("\n✓ All required packages are already installed!")
    
    # Test imports
    print("\n=== Testing Imports ===")
    test_imports = [
        'pandas',
        'numpy', 
        'matplotlib.pyplot',
        'seaborn',
        'scipy',
        'sklearn',
        'librosa',
        'spotipy'
    ]
    
    all_good = True
    for module in test_imports:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            all_good = False
    
    if all_good:
        print("\n🎉 All packages are working correctly!")
        print("You can now run: python analyze_spotify_dataset.py")
    else:
        print("\n⚠️  Some packages still have issues. Please check the errors above.")

if __name__ == "__main__":
    main()