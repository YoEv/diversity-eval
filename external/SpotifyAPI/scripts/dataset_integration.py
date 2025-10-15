#!/usr/bin/env python3
"""
Spotify API Dataset Integration for Music Diversity Evaluation Pipeline
Supports MusicOSet, Million Song Dataset, and Spotify Tracks Dataset
with 30-second preview audio download capabilities
"""

import os
import sys
import json
import pandas as pd
import sqlite3
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse

class SpotifyDatasetIntegration:
    """
    Spotify API Dataset Integration for Music Diversity Evaluation Pipeline
    Optimized for conda environment 'spotifyapi'
    """
    
    def __init__(self, spotify_dir: str = "/home/evev/diversity-eval/external/SpotifyAPI"):
        self.spotify_dir = Path(spotify_dir)
        self.config_dir = self.spotify_dir / "config"
        self.data_dir = self.spotify_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load configuration from JSON file"""
        config_path = self.config_dir / "spotify_config.json"
        template_path = self.config_dir / "spotify_config_template.json"
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        elif template_path.exists():
            print(f"⚠️  Using template config. Please copy to spotify_config.json and configure your credentials.")
            with open(template_path, 'r') as f:
                return json.load(f)
        else:
            print(f"❌ No config file found. Please create {config_path}")
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            "spotify_api": {"client_id": "", "client_secret": ""},
            "api_settings": {"rate_limit_delay": 0.1, "batch_size": 50, "max_retries": 3, "timeout": 10},
            "feature_extraction": {"include_audio_features": True, "include_artist_info": True, "include_album_info": True, "include_popularity": True},
            "preview_audio": {"download_enabled": True, "audio_format": "mp3", "quality": "preview", "timeout": 30}
        }
    
    def _init_spotify_client(self):
        """Initialize Spotify client with proper error handling"""
        try:
            import spotipy
            from spotipy.oauth2 import SpotifyClientCredentials
            
            config = self.config.get("spotify_api", {})
            client_id = config.get("client_id")
            client_secret = config.get("client_secret")
            
            if not client_id or not client_secret:
                raise ValueError("Spotify API credentials not configured. Please edit config/spotify_config.json")
            
            # Use Client Credentials Flow for server-to-server authentication
            client_credentials_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
            
            sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
            
            # Test the connection
            sp.search(q="test", type="track", limit=1)
            print("✅ Spotify API connection successful")
            
            return sp
            
        except ImportError:
            raise ImportError("spotipy library not installed. Activate 'spotifyapi' environment and run: pip install spotipy")
        except Exception as e:
            raise Exception(f"Failed to initialize Spotify client: {e}")

    def test_spotify_connection(self) -> bool:
        """Test Spotify API connection"""
        try:
            sp = self._init_spotify_client()
            result = sp.search(q="test", type="track", limit=1)
            print("✅ Spotify API test successful")
            return True
        except Exception as e:
            print(f"❌ Spotify API test failed: {e}")
            return False

    def enrich_with_spotify_api(self, df: pd.DataFrame, id_column: str = "id", 
                               batch_size: int = 50, delay: float = 0.1, 
                               download_previews: bool = True) -> pd.DataFrame:
        """
        Enhanced Spotify API enrichment with preview audio download
        
        Args:
            df: DataFrame with Spotify IDs or track names
            id_column: Column name containing Spotify IDs or track identifiers
            batch_size: Number of tracks to process in each batch
            delay: Delay between API calls to respect rate limits
            download_previews: Whether to download 30s preview audio files
            
        Returns:
            Enriched DataFrame with audio features and preview files
        """
        try:
            sp = self._init_spotify_client()
            enriched_data = []
            
            print(f"🎵 Enriching {len(df)} tracks with Spotify API data...")
            
            for idx, row in df.iterrows():
                if idx % 100 == 0:
                    print(f"Processing row {idx}/{len(df)} ({idx/len(df)*100:.1f}%)")
                
                row_dict = row.to_dict()
                
                try:
                    # Add delay to respect rate limits
                    if idx > 0 and idx % batch_size == 0:
                        time.sleep(delay)
                    
                    spotify_id = None
                    
                    # Check if we have a Spotify ID
                    if pd.notna(row.get(id_column)):
                        potential_id = str(row[id_column])
                        # Spotify IDs are 22 characters long
                        if len(potential_id) == 22 and potential_id.isalnum():
                            spotify_id = potential_id
                    
                    # If no direct ID, try to search by track and artist
                    if not spotify_id and 'artist' in row_dict and 'title' in row_dict:
                        artist = str(row_dict['artist']).strip()
                        title = str(row_dict['title']).strip()
                        
                        if artist and title and artist != 'Unknown' and title != 'Unknown':
                            # Clean search query
                            query = f'track:"{title}" artist:"{artist}"'
                            
                            try:
                                results = sp.search(q=query, type='track', limit=1)
                                
                                if results['tracks']['items']:
                                    track = results['tracks']['items'][0]
                                    spotify_id = track['id']
                                    
                                    # Add comprehensive track metadata
                                    row_dict['spotify_id'] = spotify_id
                                    row_dict['spotify_name'] = track.get('name')
                                    row_dict['spotify_popularity'] = track.get('popularity', 0)
                                    row_dict['spotify_preview_url'] = track.get('preview_url')
                                    row_dict['spotify_external_url'] = track.get('external_urls', {}).get('spotify')
                                    row_dict['spotify_duration_ms'] = track.get('duration_ms')
                                    row_dict['spotify_explicit'] = track.get('explicit', False)
                                    
                                    # Add album info
                                    if 'album' in track:
                                        album = track['album']
                                        row_dict['spotify_album_name'] = album.get('name')
                                        row_dict['spotify_album_release_date'] = album.get('release_date')
                                        row_dict['spotify_album_type'] = album.get('album_type')
                                    
                                    # Add artist info
                                    if 'artists' in track and track['artists']:
                                        main_artist = track['artists'][0]
                                        row_dict['spotify_artist_id'] = main_artist.get('id')
                                        row_dict['spotify_artist_name'] = main_artist.get('name')
                                        
                            except Exception as search_error:
                                print(f"Search error for '{title}' by '{artist}': {search_error}")
                    
                    # Get comprehensive audio features if we have a Spotify ID
                    if spotify_id:
                        try:
                            # Audio features
                            features = sp.audio_features([spotify_id])[0]
                            
                            if features:
                                # Add all audio features with spotify_ prefix
                                audio_features = {
                                    'danceability', 'energy', 'key', 'loudness', 'mode',
                                    'speechiness', 'acousticness', 'instrumentalness',
                                    'liveness', 'valence', 'tempo', 'duration_ms',
                                    'time_signature'
                                }
                                
                                for feature in audio_features:
                                    if feature in features and features[feature] is not None:
                                        row_dict[f'spotify_{feature}'] = features[feature]
                                
                                # Add derived features for diversity analysis
                                if 'tempo' in features and features['tempo']:
                                    tempo = features['tempo']
                                    row_dict['spotify_tempo_category'] = self._categorize_tempo(tempo)
                                
                                if 'key' in features and features['key'] is not None:
                                    row_dict['spotify_key_name'] = self._key_to_name(features['key'])
                                
                                if 'mode' in features and features['mode'] is not None:
                                    row_dict['spotify_mode_name'] = 'Major' if features['mode'] == 1 else 'Minor'
                                
                                # Energy and valence categories for diversity analysis
                                if 'energy' in features and features['energy'] is not None:
                                    energy = features['energy']
                                    row_dict['spotify_energy_category'] = 'Low' if energy < 0.3 else 'Medium' if energy < 0.7 else 'High'
                                
                                if 'valence' in features and features['valence'] is not None:
                                    valence = features['valence']
                                    row_dict['spotify_mood_category'] = 'Sad' if valence < 0.3 else 'Neutral' if valence < 0.7 else 'Happy'
                                        
                        except Exception as features_error:
                            print(f"Audio features error for ID {spotify_id}: {features_error}")
                
                except Exception as e:
                    print(f"Error enriching row {idx}: {e}")
                
                enriched_data.append(row_dict)
            
            result_df = pd.DataFrame(enriched_data)
            spotify_columns = [c for c in result_df.columns if c.startswith('spotify_')]
            print(f"✅ Enrichment complete. Added {len(spotify_columns)} Spotify features")
            
            # Download preview audio if requested
            if download_previews and 'spotify_preview_url' in result_df.columns:
                print("📥 Starting preview audio download...")
                result_df = self.download_preview_audio(result_df)
            
            return result_df
            
        except Exception as e:
            print(f"❌ Error with Spotify API enrichment: {e}")
            return df

    def download_preview_audio(self, df: pd.DataFrame, 
                             url_column: str = "spotify_preview_url") -> pd.DataFrame:
        """
        Download 30-second preview audio files from Spotify
        
        Args:
            df: DataFrame containing preview URLs
            url_column: Column name containing preview URLs
            
        Returns:
            DataFrame with local file paths added
        """
        output_dir = self.data_dir / "preview_audio"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        config = self.config.get("preview_audio", {})
        timeout = config.get("timeout", 30)
        
        print(f"📥 Downloading preview audio to: {output_dir}")
        
        downloaded_files = []
        failed_downloads = []
        
        for idx, row in df.iterrows():
            preview_url = row.get(url_column)
            
            if pd.isna(preview_url) or not preview_url:
                downloaded_files.append(None)
                continue
            
            try:
                # Generate filename from track info
                track_name = str(row.get('title', row.get('name', row.get('spotify_name', f'track_{idx}')))).strip()
                artist_name = str(row.get('artist', row.get('artist_name', row.get('spotify_artist_name', 'unknown')))).strip()
                
                # Clean filename
                safe_track = "".join(c for c in track_name if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
                safe_artist = "".join(c for c in artist_name if c.isalnum() or c in (' ', '-', '_')).strip()[:30]
                
                filename = f"{safe_artist}_{safe_track}_preview.mp3"
                file_path = output_dir / filename
                
                # Skip if file already exists
                if file_path.exists():
                    downloaded_files.append(str(file_path))
                    continue
                
                # Download the preview
                response = requests.get(preview_url, timeout=timeout, stream=True)
                response.raise_for_status()
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                downloaded_files.append(str(file_path))
                
                if idx % 50 == 0:
                    print(f"Downloaded {idx + 1}/{len(df)} preview files...")
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Failed to download preview for row {idx}: {e}")
                downloaded_files.append(None)
                failed_downloads.append(idx)
        
        # Add local file paths to DataFrame
        df_copy = df.copy()
        df_copy['local_preview_path'] = downloaded_files
        
        success_count = len([f for f in downloaded_files if f is not None])
        print(f"✅ Downloaded {success_count}/{len(df)} preview audio files")
        
        if failed_downloads:
            print(f"⚠️  Failed downloads: {len(failed_downloads)} files")
        
        return df_copy

    def _categorize_tempo(self, tempo: float) -> str:
        """Categorize tempo into musical terms"""
        if tempo < 60:
            return "Largo"
        elif tempo < 76:
            return "Adagio"
        elif tempo < 108:
            return "Andante"
        elif tempo < 120:
            return "Moderato"
        elif tempo < 168:
            return "Allegro"
        elif tempo < 200:
            return "Presto"
        else:
            return "Prestissimo"
    
    def _key_to_name(self, key: int) -> str:
        """Convert Spotify key number to key name"""
        key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        if 0 <= key <= 11:
            return key_names[key]
        return 'Unknown'

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Spotify Dataset Integration")
    parser.add_argument("command", choices=["test", "enrich", "download"], 
                       help="Command to execute")
    parser.add_argument("--input", "-i", help="Input CSV file")
    parser.add_argument("--output", "-o", help="Output CSV file")
    
    args = parser.parse_args()
    
    # Initialize integration
    integration = SpotifyDatasetIntegration()
    
    if args.command == "test":
        integration.test_spotify_connection()
        
    elif args.command == "enrich":
        if not args.input:
            print("❌ Input file required for enrich command")
            return
        
        df = pd.read_csv(args.input)
        result_df = integration.enrich_with_spotify_api(df)
        
        output_path = args.output or args.input.replace('.csv', '_enriched.csv')
        result_df.to_csv(output_path, index=False)
        print(f"💾 Results saved to: {output_path}")

if __name__ == "__main__":
    main()