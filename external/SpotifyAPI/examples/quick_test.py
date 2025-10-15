#!/usr/bin/env python3
"""
Quick Test Example for Spotify API Environment
Tests the conda environment setup and basic functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from dataset_integration import SpotifyDatasetIntegration
import pandas as pd

def test_environment():
    """Test if all required packages are installed"""
    print("🧪 Testing Spotify API Environment")
    print("=" * 40)
    
    # Test package imports
    packages = {
        'pandas': 'Data manipulation',
        'numpy': 'Numerical computing', 
        'requests': 'HTTP requests',
        'spotipy': 'Spotify Web API',
        'librosa': 'Audio analysis',
        'soundfile': 'Audio I/O',
        'scipy': 'Scientific computing',
        'sklearn': 'Machine learning'
    }
    
    print("📦 Testing package imports...")
    for package, description in packages.items():
        try:
            if package == 'sklearn':
                import sklearn
            else:
                __import__(package)
            print(f"✅ {package}: {description}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
    
    print("\n🔧 Testing Spotify API integration...")
    
    # Test Spotify integration
    try:
        integration = SpotifyDatasetIntegration()
        print("✅ SpotifyDatasetIntegration initialized")
        
        # Test configuration loading
        config = integration.config
        print(f"✅ Configuration loaded: {len(config)} sections")
        
        # Test Spotify connection (if credentials are configured)
        if config.get('spotify_api', {}).get('client_id'):
            success = integration.test_spotify_connection()
            if success:
                print("✅ Spotify API connection successful")
            else:
                print("⚠️  Spotify API connection failed (check credentials)")
        else:
            print("⚠️  Spotify credentials not configured")
        
    except Exception as e:
        print(f"❌ Spotify integration error: {e}")
    
    print("\n🎵 Testing with sample data...")
    
    # Test with sample data
    try:
        sample_data = {
            'title': ['Shape of You', 'Blinding Lights'],
            'artist': ['Ed Sheeran', 'The Weeknd']
        }
        df = pd.DataFrame(sample_data)
        print(f"✅ Created sample dataset with {len(df)} tracks")
        
        # Test enrichment (without actual API calls if no credentials)
        if config.get('spotify_api', {}).get('client_id'):
            print("🔄 Testing API enrichment...")
            # This would make actual API calls
            # enriched_df = integration.enrich_with_spotify_api(df)
            print("⚠️  Skipping actual API calls in test mode")
        else:
            print("⚠️  Skipping API enrichment (no credentials)")
        
    except Exception as e:
        print(f"❌ Sample data test error: {e}")
    
    print("\n✅ Environment test completed!")
    print("\n📋 Next Steps:")
    print("1. Configure Spotify credentials in config/spotify_config.json")
    print("2. Run: python examples/spotify_preview_example.py")
    print("3. Try enriching your own datasets")

if __name__ == "__main__":
    test_environment()