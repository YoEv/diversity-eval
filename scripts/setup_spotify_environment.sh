#!/bin/bash

# Complete Spotify API Environment Setup (Fixed)
# Creates conda environment and organizes all files

set -e

echo "🎵 Setting up Complete Spotify API Environment (Fixed)"
echo "====================================================="

PROJECT_ROOT="/home/evev/diversity-eval"
SPOTIFY_DIR="$PROJECT_ROOT/external/SpotifyAPI"

# Create directory structure
echo "📁 Creating SpotifyAPI directory structure..."
mkdir -p "$SPOTIFY_DIR"/{config,scripts,examples,docs,data/preview_audio}

# Run the fixed environment setup
echo "🐍 Running fixed environment setup..."
cd "$SPOTIFY_DIR"

# Use the fixed setup script
bash setup_spotify_env_fixed.sh

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x "$SPOTIFY_DIR/scripts/activate_env.sh" 2>/dev/null || true
chmod +x "$SPOTIFY_DIR/setup_spotify_env_fixed.sh"

# Test the environment
echo "🧪 Testing environment setup..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate spotifyapi

python -c "
try:
    import pandas as pd
    import numpy as np
    import requests
    import spotipy
    import librosa
    import soundfile
    print('✅ All core packages imported successfully')
    print('Environment is ready for Spotify API integration!')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

conda deactivate

echo ""
echo "✅ Spotify API Environment Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Activate environment:"
echo "   conda activate spotifyapi"
echo ""
echo "2. Configure Spotify credentials:"
echo "   cd $SPOTIFY_DIR"
echo "   cp config/spotify_config_template.json config/spotify_config.json"
echo "   # Edit config/spotify_config.json with your Spotify app credentials"
echo ""
echo "3. Test the setup:"
echo "   python examples/quick_test.py"
echo ""
echo "4. Run example:"
echo "   python examples/spotify_preview_example.py"
echo ""
echo "🎯 Environment Location: $SPOTIFY_DIR"
echo "🐍 Environment Name: spotifyapi"
echo ""
echo "💡 If you encounter any issues, check the logs above or run:"
echo "   conda activate spotifyapi"
echo "   python -c 'import librosa, soundfile, spotipy; print(\"All packages working!\")'"