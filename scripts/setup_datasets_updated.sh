#!/bin/bash

# Updated Dataset Setup Script for Music Diversity Evaluation Pipeline
# Sets up MusicOSet, Million Song Dataset, and Spotify Tracks Dataset
# with proper Spotify Web API integration

set -e

echo "🎵 Setting up Music Datasets with Spotify Web API Integration"
echo "=============================================================="

# Define paths
PROJECT_ROOT="/home/evev/diversity-eval"
DATASETS_DIR="$PROJECT_ROOT/data/datasets"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"

# Create directory structure
echo "📁 Creating dataset directory structure..."
mkdir -p "$DATASETS_DIR"/{musicoset,million_song,spotify_tracks,config,downloads,shared}

# Create subdirectories for Million Song Dataset
mkdir -p "$DATASETS_DIR/million_song"/{beatles,uspop,cal500,cal10k}

# Create shared resources directory
mkdir -p "$DATASETS_DIR/shared"/{audio_features,metadata,processed}

echo "✅ Directory structure created"

# Create updated Spotify configuration template
echo "🔧 Creating Spotify API configuration template..."
cat > "$DATASETS_DIR/config/spotify_config_template.json" << 'EOF'
{
  "spotify_api": {
    "client_id": "YOUR_SPOTIFY_CLIENT_ID",
    "client_secret": "YOUR_SPOTIFY_CLIENT_SECRET",
    "description": "Get these from https://developer.spotify.com/dashboard"
  },
  "api_settings": {
    "rate_limit_delay": 0.1,
    "batch_size": 50,
    "max_retries": 3,
    "timeout": 10
  },
  "feature_extraction": {
    "include_audio_features": true,
    "include_artist_info": true,
    "include_album_info": true,
    "include_popularity": true
  }
}
EOF

# Create environment configuration
echo "🌍 Creating environment configuration..."
cat > "$DATASETS_DIR/config/environment.json" << 'EOF'
{
  "datasets": {
    "musicoset": {
      "source": "https://zenodo.org/record/4778563",
      "files": [
        "musicoset.sql",
        "musicoset_metadata.zip",
        "musicoset_popularity.zip",
        "musicoset_songfeatures.zip"
      ],
      "description": "Enhanced music dataset with popularity-based classification"
    },
    "million_song": {
      "source": "http://millionsongdataset.com/",
      "subsets": ["beatles", "uspop", "cal500", "cal10k"],
      "description": "Million Song Dataset subsets"
    },
    "spotify_tracks": {
      "source": "https://www.kaggle.com/datasets/lehaknarnauli/spotify-datasets",
      "description": "Spotify tracks dataset from Kaggle"
    }
  },
  "requirements": {
    "python_packages": [
      "spotipy>=2.22.1",
      "pandas>=1.3.0",
      "sqlite3",
      "h5py",
      "requests"
    ]
  }
}
EOF

# Create updated download instructions
echo "📋 Creating comprehensive download instructions..."
cat > "$DATASETS_DIR/DOWNLOAD_INSTRUCTIONS.md" << 'EOF'
# Music Datasets Download Instructions

## 🎯 Overview
This guide helps you download and set up three major music datasets for the diversity evaluation pipeline.

## 🔑 Spotify Developer Setup (Required)

### Step 1: Create Spotify Developer Account
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account (create one if needed)
3. Click "Create App"

### Step 2: Configure Your App
- **App Name**: `Music Diversity Evaluation`
- **App Description**: `Research tool for music diversity analysis`
- **Website**: `http://localhost` (or your website)
- **Redirect URI**: `http://localhost:8080/callback`

### Step 3: Get API Credentials
1. After creating the app, click on it in your dashboard
2. Click "Settings"
3. Copy your **Client ID** and **Client Secret**
4. Keep these secure - never share them publicly!

### Step 4: Configure the Integration
```bash
# Copy the template and edit with your credentials
cp data/datasets/config/spotify_config_template.json data/datasets/config/spotify_config.json

# Edit the file with your credentials
nano data/datasets/config/spotify_config.json
```

## 📦 Dataset Downloads

### 1. MusicOSet Dataset
**Source**: [Zenodo - MusicOSet](https://zenodo.org/record/4778563)

**Automatic Download**:
```bash
cd data/datasets/downloads
bash ../../../scripts/download_musicoset_updated.sh
```

**Manual Download**:
1. Visit the Zenodo link above
2. Download these files to `data/datasets/musicoset/`:
   - `musicoset.sql` (main database)
   - `musicoset_metadata.zip`
   - `musicoset_popularity.zip`
   - `musicoset_songfeatures.zip`

### 2. Million Song Dataset
**Source**: [Million Song Dataset](http://millionsongdataset.com/)

**Available Subsets**:
- **Beatles**: [Download](http://millionsongdataset.com/sites/default/files/AdditionalFiles/beatles.zip)
- **US Pop**: [Download](http://millionsongdataset.com/sites/default/files/AdditionalFiles/uspop.zip)
- **CAL500**: [Download](http://millionsongdataset.com/sites/default/files/AdditionalFiles/cal500.zip)
- **CAL10K**: [Download](http://millionsongdataset.com/sites/default/files/AdditionalFiles/cal10k.zip)

Extract each subset to its respective directory:
```bash
# Example for Beatles subset
unzip beatles.zip -d data/datasets/million_song/beatles/
```

### 3. Spotify Tracks Dataset
**Source**: [Kaggle - Spotify Datasets](https://www.kaggle.com/datasets/lehaknarnauli/spotify-datasets)

**Download Steps**:
1. Create a Kaggle account if you don't have one
2. Install Kaggle CLI: `pip install kaggle`
3. Set up Kaggle API credentials (see [Kaggle API docs](https://github.com/Kaggle/kaggle-api))
4. Download the dataset:
```bash
cd data/datasets/spotify_tracks
kaggle datasets download -d lehaknarnauli/spotify-datasets
unzip spotify-datasets.zip
```

## 🔍 Verification

After downloading, verify your setup:
```bash
# Test Spotify API connection
python pipelines/utils/dataset_integration.py test-spotify

# Check dataset availability
python pipelines/utils/dataset_integration.py list

# Get dataset info
python pipelines/utils/dataset_integration.py info musicoset
```

## 🚨 Troubleshooting

### Spotify API Issues
- **401 Unauthorized**: Check your Client ID and Client Secret
- **Rate Limiting**: The integration includes automatic rate limiting
- **Connection Timeout**: Check your internet connection

### Dataset Issues
- **File Not Found**: Ensure files are in the correct directories
- **Permission Errors**: Check file permissions with `chmod 644`
- **Corrupted Downloads**: Re-download the files

### Python Dependencies
```bash
# Install required packages
pip install spotipy pandas h5py requests

# For conda users
conda install -c conda-forge spotipy pandas h5py requests
```

## 📊 Usage Examples

### Basic Dataset Loading
```python
from pipelines.utils.dataset_integration import DatasetIntegration

# Initialize
integration = DatasetIntegration()

# Load datasets
musicoset = integration.get_musicoset_data()
spotify_tracks = integration.get_spotify_tracks_data()

# Enrich with Spotify API
enriched = integration.enrich_with_spotify_api(musicoset)
```

### Export for Analysis
```bash
# Export with Spotify enrichment
python pipelines/utils/dataset_integration.py export musicoset output/musicoset_enriched.csv --enrich
```

## 🔒 Data Privacy & Ethics

- **Spotify API**: Only accesses public track metadata and audio features
- **Rate Limiting**: Respects Spotify's API rate limits
- **Data Storage**: No personal user data is collected or stored
- **Research Use**: Ensure compliance with your institution's research ethics guidelines

## 📈 Next Steps

1. Complete the Spotify Developer setup
2. Download at least one dataset to test
3. Run the verification commands
4. Explore the integration features
5. Start your diversity analysis!

For additional help, check the main README or create an issue in the repository.
EOF

# Create updated MusicOSet download script
echo "⬇️ Creating MusicOSet download script..."
cat > "$SCRIPTS_DIR/download_musicoset_updated.sh" << 'EOF'
#!/bin/bash

# Download MusicOSet dataset from Zenodo
# Updated with better error handling and verification

set -e

DATASETS_DIR="/home/evev/diversity-eval/data/datasets"
MUSICOSET_DIR="$DATASETS_DIR/musicoset"
DOWNLOAD_DIR="$DATASETS_DIR/downloads"

echo "🎵 Downloading MusicOSet Dataset from Zenodo"
echo "============================================="

# Create directories
mkdir -p "$MUSICOSET_DIR" "$DOWNLOAD_DIR"

# Zenodo record URL
ZENODO_BASE="https://zenodo.org/record/4778563/files"

# Files to download
declare -A FILES=(
    ["musicoset.sql"]="Main database file"
    ["musicoset_metadata.zip"]="Metadata archive"
    ["musicoset_popularity.zip"]="Popularity data"
    ["musicoset_songfeatures.zip"]="Song features"
    ["additional.zip"]="Additional data"
)

# Download function
download_file() {
    local filename="$1"
    local description="$2"
    local url="$ZENODO_BASE/$filename"
    local output_path="$DOWNLOAD_DIR/$filename"
    
    echo "📥 Downloading $filename ($description)..."
    
    if [ -f "$output_path" ]; then
        echo "   ✓ File already exists, skipping"
        return 0
    fi
    
    if curl -L -o "$output_path" "$url"; then
        echo "   ✓ Downloaded successfully"
        
        # Verify file size (basic check)
        if [ -s "$output_path" ]; then
            echo "   ✓ File verification passed"
        else
            echo "   ✗ File appears to be empty"
            rm -f "$output_path"
            return 1
        fi
    else
        echo "   ✗ Download failed"
        return 1
    fi
}

# Download all files
echo "Starting downloads..."
for filename in "${!FILES[@]}"; do
    description="${FILES[$filename]}"
    if ! download_file "$filename" "$description"; then
        echo "❌ Failed to download $filename"
        exit 1
    fi
done

# Extract and organize files
echo "📦 Extracting and organizing files..."

# Move SQL file directly
if [ -f "$DOWNLOAD_DIR/musicoset.sql" ]; then
    mv "$DOWNLOAD_DIR/musicoset.sql" "$MUSICOSET_DIR/"
    echo "   ✓ Moved musicoset.sql"
fi

# Extract zip files
for zipfile in "$DOWNLOAD_DIR"/*.zip; do
    if [ -f "$zipfile" ]; then
        echo "   📂 Extracting $(basename "$zipfile")..."
        unzip -q "$zipfile" -d "$MUSICOSET_DIR/"
        echo "   ✓ Extracted $(basename "$zipfile")"
    fi
done

# Verify the main database file
if [ -f "$MUSICOSET_DIR/musicoset.sql" ]; then
    echo "✅ MusicOSet dataset downloaded and organized successfully!"
    echo "📊 Dataset location: $MUSICOSET_DIR"
    echo "📈 You can now use the dataset with the integration script"
else
    echo "❌ Main database file not found. Please check the download."
    exit 1
fi

# Clean up download directory (optional)
read -p "🗑️  Remove downloaded zip files? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f "$DOWNLOAD_DIR"/*.zip
    echo "   ✓ Cleaned up download files"
fi

echo "🎉 MusicOSet setup complete!"
EOF

chmod +x "$SCRIPTS_DIR/download_musicoset_updated.sh"

# Create updated verification script
echo "🔍 Creating verification script..."
cat > "$DATASETS_DIR/verify_setup.py" << 'EOF'
#!/usr/bin/env python3
"""
Comprehensive verification script for music datasets setup
Tests Spotify API connection, dataset availability, and integration functionality
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from pipelines.utils.dataset_integration import DatasetIntegration

def check_spotify_config():
    """Check Spotify API configuration"""
    print("🔑 Checking Spotify API Configuration...")
    
    config_path = Path("/home/evev/diversity-eval/data/datasets/config/spotify_config.json")
    
    if not config_path.exists():
        print("   ❌ spotify_config.json not found")
        print("   💡 Copy spotify_config_template.json and add your credentials")
        return False
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        if 'spotify_api' not in config:
            print("   ❌ spotify_api section missing from config")
            return False
        
        api_config = config['spotify_api']
        
        if api_config.get('client_id') == 'YOUR_SPOTIFY_CLIENT_ID':
            print("   ❌ Client ID not configured (still using template value)")
            return False
        
        if api_config.get('client_secret') == 'YOUR_SPOTIFY_CLIENT_SECRET':
            print("   ❌ Client Secret not configured (still using template value)")
            return False
        
        print("   ✅ Configuration file looks good")
        return True
        
    except Exception as e:
        print(f"   ❌ Error reading config: {e}")
        return False

def test_spotify_connection():
    """Test Spotify API connection"""
    print("🌐 Testing Spotify API Connection...")
    
    try:
        integration = DatasetIntegration()
        sp = integration._init_spotify_client()
        
        # Test search
        results = sp.search(q='test', type='track', limit=1)
        print("   ✅ API connection successful")
        
        # Test audio features
        if results['tracks']['items']:
            track_id = results['tracks']['items'][0]['id']
            features = sp.audio_features([track_id])
            if features and features[0]:
                print("   ✅ Audio features access working")
            else:
                print("   ⚠️  Audio features access limited")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False

def check_datasets():
    """Check dataset availability"""
    print("📊 Checking Dataset Availability...")
    
    datasets_dir = Path("/home/evev/diversity-eval/data/datasets")
    results = {}
    
    # Check MusicOSet
    musicoset_sql = datasets_dir / "musicoset" / "musicoset.sql"
    if musicoset_sql.exists():
        print("   ✅ MusicOSet: SQL file found")
        results['musicoset'] = True
    else:
        print("   ❌ MusicOSet: SQL file not found")
        results['musicoset'] = False
    
    # Check Million Song Dataset
    million_song_dir = datasets_dir / "million_song"
    subsets_found = []
    for subset in ['beatles', 'uspop', 'cal500', 'cal10k']:
        subset_dir = million_song_dir / subset
        if subset_dir.exists() and any(subset_dir.iterdir()):
            subsets_found.append(subset)
    
    if subsets_found:
        print(f"   ✅ Million Song Dataset: {len(subsets_found)} subsets found ({', '.join(subsets_found)})")
        results['million_song'] = True
    else:
        print("   ❌ Million Song Dataset: No subsets found")
        results['million_song'] = False
    
    # Check Spotify Tracks
    spotify_dir = datasets_dir / "spotify_tracks"
    csv_files = list(spotify_dir.glob("*.csv")) if spotify_dir.exists() else []
    if csv_files:
        print(f"   ✅ Spotify Tracks: {len(csv_files)} CSV files found")
        results['spotify_tracks'] = True
    else:
        print("   ❌ Spotify Tracks: No CSV files found")
        results['spotify_tracks'] = False
    
    return results

def test_integration():
    """Test dataset integration functionality"""
    print("🔧 Testing Integration Functionality...")
    
    try:
        integration = DatasetIntegration()
        
        # Test configuration loading
        config = integration.load_config()
        if config:
            print("   ✅ Configuration loading works")
        else:
            print("   ⚠️  Configuration loading returned empty config")
        
        # Test dataset listing
        print("   📋 Available datasets:")
        
        # Try to load each dataset
        datasets_to_test = ['musicoset', 'spotify_tracks']
        
        for dataset_name in datasets_to_test:
            try:
                result = integration.prepare_for_pipeline(dataset_name)
                total_tracks = result['metadata']['total_tracks']
                print(f"      ✅ {dataset_name}: {total_tracks} tracks loaded")
            except Exception as e:
                print(f"      ❌ {dataset_name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        return False

def main():
    """Main verification function"""
    print("🎵 Music Datasets Setup Verification")
    print("=" * 50)
    
    all_checks = []
    
    # Run all checks
    all_checks.append(check_spotify_config())
    all_checks.append(test_spotify_connection())
    
    dataset_results = check_datasets()
    all_checks.append(any(dataset_results.values()))
    
    all_checks.append(test_integration())
    
    # Summary
    print("\n📋 Verification Summary")
    print("=" * 30)
    
    if all(all_checks):
        print("🎉 All checks passed! Your setup is ready for use.")
        print("\n🚀 Next steps:")
        print("   1. Try loading a dataset: python pipelines/utils/dataset_integration.py info musicoset")
        print("   2. Export enriched data: python pipelines/utils/dataset_integration.py export musicoset output.csv --enrich")
        print("   3. Start your diversity analysis!")
    else:
        print("⚠️  Some checks failed. Please review the issues above.")
        print("\n🔧 Common fixes:")
        print("   1. Configure Spotify API credentials in spotify_config.json")
        print("   2. Download datasets using the provided scripts")
        print("   3. Install required Python packages: pip install spotipy pandas h5py")
    
    return all(all_checks)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
EOF

chmod +x "$DATASETS_DIR/verify_setup.py"

# Create updated requirements file
echo "📦 Creating requirements file..."
cat > "$DATASETS_DIR/requirements.txt" << 'EOF'
# Music Datasets Integration Requirements
# Updated with proper Spotify Web API support

# Core data processing
pandas>=1.3.0
numpy>=1.20.0

# Spotify Web API
spotipy>=2.22.1

# Database support
sqlite3  # Usually included with Python

# HDF5 support for Million Song Dataset
h5py>=3.1.0

# HTTP requests
requests>=2.25.0

# Optional: Progress bars
tqdm>=4.60.0

# Optional: Data visualization
matplotlib>=3.3.0
seaborn>=0.11.0

# Optional: Advanced audio analysis
librosa>=0.8.0
EOF

# Update the main integration script permissions
chmod +x "$PROJECT_ROOT/pipelines/utils/dataset_integration.py"

echo "✅ Updated dataset setup complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Configure Spotify API:"
echo "   - Visit: https://developer.spotify.com/dashboard"
echo "   - Create an app and get Client ID & Secret"
echo "   - Edit: $DATASETS_DIR/config/spotify_config.json"
echo ""
echo "2. Download datasets:"
echo "   - MusicOSet: bash $SCRIPTS_DIR/download_musicoset_updated.sh"
echo "   - Million Song: Follow instructions in DOWNLOAD_INSTRUCTIONS.md"
echo "   - Spotify Tracks: Use Kaggle CLI as described in instructions"
echo ""
echo "3. Verify setup:"
echo "   python $DATASETS_DIR/verify_setup.py"
echo ""
echo "4. Test integration:"
echo "   python $PROJECT_ROOT/pipelines/utils/dataset_integration.py test-spotify"
echo ""
echo "📖 Full documentation: $DATASETS_DIR/DOWNLOAD_INSTRUCTIONS.md"