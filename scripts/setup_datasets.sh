#!/bin/bash

# Realistic Dataset Setup Script
# Handles actual download and setup of music datasets

set -e

echo "Setting up music datasets for diversity evaluation..."

# Create datasets directory structure
DATASETS_DIR="/home/evev/diversity-eval/data/datasets"
mkdir -p "$DATASETS_DIR"

# Create subdirectories
mkdir -p "$DATASETS_DIR/musicoset"
mkdir -p "$DATASETS_DIR/million_song"
mkdir -p "$DATASETS_DIR/spotify_tracks"
mkdir -p "$DATASETS_DIR/config"
mkdir -p "$DATASETS_DIR/downloads"

echo "Created dataset directories"

# Create Spotify API configuration template
cat > "$DATASETS_DIR/config/spotify_config_template.json" << 'EOF'
{
    "spotify_api": {
        "client_id": "YOUR_SPOTIFY_CLIENT_ID_HERE",
        "client_secret": "YOUR_SPOTIFY_CLIENT_SECRET_HERE",
        "note": "Get these from https://developer.spotify.com/dashboard/"
    },
    "datasets": {
        "musicoset": {
            "enabled": true,
            "source": "zenodo",
            "download_url": "https://zenodo.org/records/4904639",
            "files": [
                "musicoset.sql",
                "musicoset_metadata.zip", 
                "musicoset_popularity.zip",
                "musicoset_songfeatures.zip",
                "additional.zip"
            ]
        },
        "million_song": {
            "enabled": true,
            "source": "manual",
            "info_url": "http://millionsongdataset.com/pages/additional-datasets/",
            "subsets": ["beatles", "uspop", "cal500", "cal10k"]
        },
        "spotify_tracks": {
            "enabled": true,
            "source": "kaggle",
            "dataset_id": "maharshipandya/-spotify-tracks-dataset",
            "requires_kaggle": true
        }
    }
}
EOF

# Create download instructions
cat > "$DATASETS_DIR/DOWNLOAD_INSTRUCTIONS.md" << 'EOF'
# Dataset Download Instructions

## 1. Spotify Developer Setup (Required for API access)

### Step 1: Create Spotify Developer Account
1. Go to https://developer.spotify.com/dashboard/
2. Log in with your Spotify account (create one if needed)
3. Accept the Developer Terms of Service

### Step 2: Create an App
1. Click "Create app" button
2. Fill in the form:
   - App name: "Music Diversity Evaluation"
   - App description: "Research project for music diversity analysis"
   - Website: http://localhost (or your website)
   - Redirect URIs: http://localhost:8888/callback
   - APIs used: Web API
3. Accept terms and click "Save"

### Step 3: Get Credentials
1. Click on your newly created app
2. Click "Settings"
3. Copy the "Client ID"
4. Click "View client secret" and copy the "Client Secret"
5. Update `config/spotify_config.json` with these values

## 2. Dataset Downloads

### MusicOSet (Automatic Download Available)
```bash
# Run the download script
./download_musicoset.sh
```

### Million Song Dataset (Manual Download Required)
1. Visit: http://millionsongdataset.com/pages/additional-datasets/
2. Choose datasets to download:
   - Beatles: Click "DATASET" link
   - USPOP: Click "DATASET" link  
   - CAL500: Click "DATASET" link
   - CAL10k: Click "DATASET" link
3. Extract files to respective subdirectories in `million_song/`

### Spotify Tracks Dataset (Kaggle)
```bash
# Install Kaggle CLI
pip install kaggle

# Setup Kaggle credentials
# 1. Go to https://www.kaggle.com/settings
# 2. Create new API token (downloads kaggle.json)
# 3. Place kaggle.json in ~/.kaggle/

# Download dataset
kaggle datasets download -d maharshipandya/-spotify-tracks-dataset
unzip -d spotify_tracks/ spotify-tracks-dataset.zip
```

## 3. Verify Setup
```bash
python verify_datasets.py
```
EOF

# Create MusicOSet download script
cat > "$DATASETS_DIR/download_musicoset.sh" << 'EOF'
#!/bin/bash

# Download MusicOSet from Zenodo
echo "Downloading MusicOSet dataset from Zenodo..."

MUSICOSET_DIR="./musicoset"
DOWNLOAD_DIR="./downloads"

# Create directories
mkdir -p "$MUSICOSET_DIR"
mkdir -p "$DOWNLOAD_DIR"

# Zenodo download URLs
BASE_URL="https://zenodo.org/records/4904639/files"

FILES=(
    "musicoset.sql"
    "musicoset_metadata.zip"
    "musicoset_popularity.zip" 
    "musicoset_songfeatures.zip"
    "additional.zip"
)

echo "Downloading MusicOSet files..."
for file in "${FILES[@]}"; do
    echo "Downloading $file..."
    wget -P "$DOWNLOAD_DIR" "$BASE_URL/$file" || {
        echo "Failed to download $file"
        echo "You may need to download manually from: https://zenodo.org/records/4904639"
    }
done

# Extract zip files
echo "Extracting files..."
cd "$DOWNLOAD_DIR"
for zipfile in *.zip; do
    if [ -f "$zipfile" ]; then
        echo "Extracting $zipfile..."
        unzip -o "$zipfile" -d "../$MUSICOSET_DIR/"
    fi
done

# Move SQL file
if [ -f "musicoset.sql" ]; then
    mv "musicoset.sql" "../$MUSICOSET_DIR/"
fi

cd ..
echo "MusicOSet download completed!"
echo "Files are in: $MUSICOSET_DIR"
EOF

chmod +x "$DATASETS_DIR/download_musicoset.sh"

# Create dataset verification script
cat > "$DATASETS_DIR/verify_datasets.py" << 'EOF'
#!/usr/bin/env python3
"""
Verify dataset setup and Spotify API configuration
"""

import json
import os
import sys
from pathlib import Path

def check_spotify_config():
    """Check if Spotify API is configured"""
    config_path = Path("config/spotify_config.json")
    
    if not config_path.exists():
        print("❌ Spotify config not found")
        print("   Copy config/spotify_config_template.json to config/spotify_config.json")
        print("   and fill in your Spotify API credentials")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        client_id = config.get('spotify_api', {}).get('client_id', '')
        client_secret = config.get('spotify_api', {}).get('client_secret', '')
        
        if 'YOUR_SPOTIFY' in client_id or 'YOUR_SPOTIFY' in client_secret:
            print("❌ Spotify API credentials not configured")
            print("   Update config/spotify_config.json with your actual credentials")
            return False
        
        print("✅ Spotify API configuration found")
        return True
        
    except Exception as e:
        print(f"❌ Error reading Spotify config: {e}")
        return False

def check_musicoset():
    """Check MusicOSet dataset"""
    musicoset_dir = Path("musicoset")
    
    if not musicoset_dir.exists():
        print("❌ MusicOSet directory not found")
        print("   Run: ./download_musicoset.sh")
        return False
    
    expected_files = ["musicoset.sql"]
    found_files = []
    
    for file in expected_files:
        if (musicoset_dir / file).exists():
            found_files.append(file)
    
    if found_files:
        print(f"✅ MusicOSet found ({len(found_files)} files)")
        return True
    else:
        print("❌ MusicOSet files not found")
        print("   Run: ./download_musicoset.sh")
        return False

def check_million_song():
    """Check Million Song Dataset"""
    msd_dir = Path("million_song")
    
    if not msd_dir.exists():
        print("❌ Million Song Dataset directory not found")
        print("   Create directory and download manually from:")
        print("   http://millionsongdataset.com/pages/additional-datasets/")
        return False
    
    subsets = ["beatles", "uspop", "cal500", "cal10k"]
    found_subsets = []
    
    for subset in subsets:
        if (msd_dir / subset).exists() and list((msd_dir / subset).glob("*")):
            found_subsets.append(subset)
    
    if found_subsets:
        print(f"✅ Million Song Dataset found ({len(found_subsets)} subsets: {', '.join(found_subsets)})")
        return True
    else:
        print("❌ Million Song Dataset subsets not found")
        print("   Download manually from: http://millionsongdataset.com/pages/additional-datasets/")
        return False

def check_spotify_tracks():
    """Check Spotify Tracks Dataset"""
    spotify_dir = Path("spotify_tracks")
    
    if not spotify_dir.exists():
        print("❌ Spotify Tracks directory not found")
        print("   Download from Kaggle:")
        print("   kaggle datasets download -d maharshipandya/-spotify-tracks-dataset")
        return False
    
    csv_files = list(spotify_dir.glob("*.csv"))
    
    if csv_files:
        print(f"✅ Spotify Tracks Dataset found ({len(csv_files)} CSV files)")
        return True
    else:
        print("❌ Spotify Tracks CSV files not found")
        print("   Download and extract from Kaggle")
        return False

def test_spotify_api():
    """Test Spotify API connection"""
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        
        config_path = Path("config/spotify_config.json")
        if not config_path.exists():
            print("❌ Cannot test Spotify API - config not found")
            return False
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        client_credentials_manager = SpotifyClientCredentials(
            client_id=config['spotify_api']['client_id'],
            client_secret=config['spotify_api']['client_secret']
        )
        
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        # Test API call
        results = sp.search(q='test', type='track', limit=1)
        
        if results and 'tracks' in results:
            print("✅ Spotify API connection successful")
            return True
        else:
            print("❌ Spotify API test failed")
            return False
            
    except ImportError:
        print("⚠️  Spotipy not installed - run: pip install spotipy")
        return False
    except Exception as e:
        print(f"❌ Spotify API error: {e}")
        print("   Check your client_id and client_secret")
        return False

def main():
    print("Dataset Setup Verification")
    print("=" * 40)
    
    checks = [
        ("Spotify Configuration", check_spotify_config),
        ("MusicOSet Dataset", check_musicoset),
        ("Million Song Dataset", check_million_song),
        ("Spotify Tracks Dataset", check_spotify_tracks),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\nChecking {name}...")
        results.append(check_func())
    
    print(f"\nTesting Spotify API...")
    api_result = test_spotify_api()
    
    print("\n" + "=" * 40)
    print("Summary:")
    passed = sum(results)
    total = len(results)
    print(f"Dataset checks: {passed}/{total} passed")
    
    if api_result:
        print("Spotify API: ✅ Working")
    else:
        print("Spotify API: ❌ Not working")
    
    if passed == total and api_result:
        print("\n🎉 All checks passed! You're ready to use the datasets.")
    else:
        print("\n⚠️  Some issues found. Please follow the instructions above.")

if __name__ == "__main__":
    main()
EOF

chmod +x "$DATASETS_DIR/verify_datasets.py"

# Create requirements file
cat > "$DATASETS_DIR/requirements.txt" << 'EOF'
spotipy>=2.22.1
pandas>=1.5.0
requests>=2.28.0
kaggle>=1.5.12
numpy>=1.21.0
matplotlib>=3.5.0
seaborn>=0.11.0
sqlalchemy>=1.4.0
EOF

echo ""
echo "Dataset setup structure created!"
echo ""
echo "📁 Directory structure:"
echo "  data/datasets/"
echo "  ├── config/                     # Configuration files"
echo "  ├── musicoset/                  # MusicOSet dataset"
echo "  ├── million_song/               # Million Song Dataset"
echo "  ├── spotify_tracks/             # Spotify Tracks Dataset"
echo "  ├── downloads/                  # Temporary download files"
echo "  ├── download_musicoset.sh       # MusicOSet downloader"
echo "  ├── verify_datasets.py          # Setup verification"
echo "  ├── DOWNLOAD_INSTRUCTIONS.md   # Detailed instructions"
echo "  └── requirements.txt            # Python dependencies"
echo ""
echo "🚀 Next steps:"
echo "1. cd data/datasets"
echo "2. Read DOWNLOAD_INSTRUCTIONS.md"
echo "3. Setup Spotify Developer account"
echo "4. Download datasets"
echo "5. Run: python verify_datasets.py"