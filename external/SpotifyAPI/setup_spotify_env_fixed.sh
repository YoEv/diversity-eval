#!/bin/bash

# Fixed Spotify API Environment Setup Script
# Handles package dependencies step by step

set -e

echo "🎵 Setting up Spotify API Environment (Fixed)"
echo "============================================="

# Define paths
SPOTIFY_DIR="/home/evev/diversity-eval/external/SpotifyAPI"
PROJECT_ROOT="/home/evev/diversity-eval"

# Create directory structure
echo "📁 Creating SpotifyAPI directory structure..."
mkdir -p "$SPOTIFY_DIR"/{config,scripts,examples,docs,data/preview_audio}

echo "✅ Directory structure created"

# Remove existing environment if it exists
echo "🧹 Cleaning up existing environment..."
if conda env list | grep -q "spotifyapi"; then
    echo "Removing existing 'spotifyapi' environment..."
    conda env remove -n spotifyapi -y
fi

# Create conda environment with basic packages first
echo "🐍 Creating conda environment 'spotifyapi' with basic packages..."
conda create -n spotifyapi python=3.9 -y

echo "✅ Basic conda environment created"

# Activate environment and install packages step by step
echo "📦 Installing packages in spotifyapi environment..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate spotifyapi

# Install core scientific packages via conda (more stable)
echo "Installing core scientific packages..."
conda install -c conda-forge pandas numpy scipy scikit-learn -y

# Install requests
echo "Installing requests..."
conda install -c conda-forge requests -y

# Install audio processing packages via pip (more reliable for these packages)
echo "Installing audio processing packages via pip..."
pip install librosa>=0.9.0
pip install soundfile>=0.10.0
pip install numba>=0.56.0

# Install Spotify API package
echo "Installing Spotify API package..."
pip install spotipy>=2.20.0

# Install additional packages for data processing
echo "Installing additional packages..."
pip install h5py>=3.1.0

# Verify installation with safer version checking
echo "🧪 Verifying installation..."
python -c "
import pandas as pd
import numpy as np
import requests
import spotipy
import librosa
import soundfile
import h5py
import pkg_resources

print('✅ All packages imported successfully!')
print('Versions:')
print(f'  pandas: {pd.__version__}')
print(f'  numpy: {np.__version__}')

# Safe version checking for packages that might not have __version__
try:
    print(f'  spotipy: {pkg_resources.get_distribution(\"spotipy\").version}')
except:
    print('  spotipy: installed (version check failed)')

try:
    print(f'  librosa: {librosa.__version__}')
except:
    print('  librosa: installed (version check failed)')

try:
    print(f'  soundfile: {soundfile.__version__}')
except:
    print('  soundfile: installed (version check failed)')

print('\\n🎵 Testing Spotify API import...')
from spotipy.oauth2 import SpotifyClientCredentials
print('✅ Spotify API components imported successfully!')
"

echo "✅ All packages installed and verified successfully"

# Create environment info file
echo "📄 Creating environment information..."
cat > "$SPOTIFY_DIR/environment_info.txt" << EOF
# Spotify API Environment Information
Environment Name: spotifyapi
Python Version: 3.9
Created: $(date)

## Installed Packages:
- pandas (data manipulation)
- numpy (numerical computing)
- requests (HTTP requests)
- spotipy (Spotify Web API)
- librosa (audio analysis)
- soundfile (audio I/O)
- h5py (HDF5 data format)
- scipy (scientific computing)
- scikit-learn (machine learning)
- numba (JIT compilation for librosa)

## Activation Command:
conda activate spotifyapi

## Deactivation Command:
conda deactivate
EOF

echo "✅ Environment setup complete!"
echo ""
echo "🚀 Next Steps:"
echo "1. Activate environment: conda activate spotifyapi"
echo "2. Configure Spotify credentials in: $SPOTIFY_DIR/config/"
echo "3. Run examples in: $SPOTIFY_DIR/examples/"
echo ""
echo "🧪 Test the environment:"
echo "   conda activate spotifyapi"
echo "   python $SPOTIFY_DIR/examples/quick_test.py"