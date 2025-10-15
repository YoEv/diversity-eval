# Spotify API Environment for Music Diversity Evaluation

This directory contains a dedicated Spotify API environment for the music diversity evaluation pipeline.

## 🚀 Quick Setup

### 1. Create Conda Environment

```bash
# Option A: Using environment.yml (recommended)
conda env create -f environment.yml

# Option B: Using setup script
bash setup_spotify_env.sh

# Option C: Manual setup
conda create -n spotifyapi python=3.9
conda activate spotifyapi
pip install -r requirements.txt
```

### 2. Configure Spotify API Credentials

1. Visit [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Copy Client ID and Client Secret
4. Configure credentials:

```bash
cp config/spotify_config_template.json config/spotify_config.json
# Edit config/spotify_config.json with your credentials
```

### 3. Test Setup

```bash
conda activate spotifyapi
python examples/quick_test.py
```

## 📁 Directory Structure