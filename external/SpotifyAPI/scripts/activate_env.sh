#!/bin/bash

# Spotify API Environment Activation Script
# Convenient script to activate the spotifyapi conda environment

echo "🐍 Activating Spotify API Environment..."

# Source conda
source $(conda info --base)/etc/profile.d/conda.sh

# Activate environment
conda activate spotifyapi

# Check if activation was successful
if [[ "$CONDA_DEFAULT_ENV" == "spotifyapi" ]]; then
    echo "✅ Successfully activated 'spotifyapi' environment"
    echo ""
    echo "📦 Installed packages:"
    conda list | grep -E "(pandas|numpy|spotipy|librosa|requests)"
    echo ""
    echo "🎵 Ready to use Spotify API!"
    echo ""
    echo "💡 Quick commands:"
    echo "  - Test environment: python examples/quick_test.py"
    echo "  - Test Spotify API: python scripts/dataset_integration.py test"
    echo "  - Deactivate: conda deactivate"
else
    echo "❌ Failed to activate 'spotifyapi' environment"
    echo "Please run: conda create -n spotifyapi python=3.9"
fi