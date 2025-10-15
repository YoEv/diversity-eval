#!/usr/bin/env python3
"""
Simple test script to verify Spotify API environment
"""

def test_imports():
    """Test all required package imports"""
    print("🧪 Testing package imports...")
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ numpy imported successfully")
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ requests imported successfully")
    except ImportError as e:
        print(f"❌ requests import failed: {e}")
        return False
    
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        print("✅ spotipy imported successfully")
    except ImportError as e:
        print(f"❌ spotipy import failed: {e}")
        return False
    
    try:
        import librosa
        print("✅ librosa imported successfully")
    except ImportError as e:
        print(f"❌ librosa import failed: {e}")
        return False
    
    try:
        import soundfile
        print("✅ soundfile imported successfully")
    except ImportError as e:
        print(f"❌ soundfile import failed: {e}")
        return False
    
    try:
        import h5py
        print("✅ h5py imported successfully")
    except ImportError as e:
        print(f"❌ h5py import failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality"""
    print("\n🔧 Testing basic functionality...")
    
    try:
        import pandas as pd
        import numpy as np
        
        # Test pandas
        df = pd.DataFrame({'test': [1, 2, 3]})
        print(f"✅ pandas DataFrame created: {len(df)} rows")
        
        # Test numpy
        arr = np.array([1, 2, 3])
        print(f"✅ numpy array created: {arr.shape}")
        
        # Test spotipy client creation (without credentials)
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        print("✅ spotipy client classes accessible")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def main():
    print("🎵 Spotify API Environment Test")
    print("=" * 40)
    
    # Test imports
    imports_ok = test_imports()
    
    if not imports_ok:
        print("\n❌ Import tests failed!")
        return False
    
    # Test basic functionality
    functionality_ok = test_basic_functionality()
    
    if not functionality_ok:
        print("\n❌ Functionality tests failed!")
        return False
    
    print("\n✅ All tests passed!")
    print("\n📋 Environment is ready for Spotify API integration!")
    print("\n🚀 Next steps:")
    print("1. Configure Spotify credentials in config/spotify_config.json")
    print("2. Run examples/quick_test.py")
    print("3. Start using the Spotify API integration!")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)