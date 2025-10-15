#!/usr/bin/env python3
"""
Dataset Integration for Music Diversity Evaluation Pipeline
Integrates MusicOSet, Million Song Dataset, and Spotify Tracks Dataset
Updated with proper Spotify Web API usage
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

class DatasetIntegration:
    """
    Enhanced Dataset Integration for Music Diversity Evaluation Pipeline
    Supports MusicOSet, Million Song Dataset, and Spotify Tracks Dataset
    with 30-second preview audio download capabilities
    """
    
    def __init__(self, datasets_dir: str = "/home/evev/diversity-eval/data/datasets"):
        self.datasets_dir = Path(datasets_dir)
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load configuration from JSON file"""
        config_path = self.datasets_dir / "config" / "spotify_config.json"
        
        if not config_path.exists():
            print(f"⚠️  Config file not found at {config_path}")
            print("Using template config. Please set up your Spotify credentials.")
            return {
                "spotify_api": {"client_id": "", "client_secret": ""},
                "api_settings": {"rate_limit_delay": 0.1, "batch_size": 50, "max_retries": 3, "timeout": 10},
                "feature_extraction": {"include_audio_features": True, "include_artist_info": True, "include_album_info": True, "include_popularity": True},
                "preview_audio": {"download_enabled": True, "audio_format": "mp3", "quality": "preview", "timeout": 30}
            }
        
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def _init_spotify_client(self):
        """Initialize Spotify client with proper error handling"""
        try:
            import spotipy
            from spotipy.oauth2 import SpotifyClientCredentials
            
            config = self.config.get("spotify_api", {})
            client_id = config.get("client_id")
            client_secret = config.get("client_secret")
            
            if not client_id or not client_secret:
                raise ValueError("Spotify API credentials not configured")
            
            # Use Client Credentials Flow for server-to-server authentication
            client_credentials_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
            
            sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
            
            # Test the connection
            sp.search(q="test", type="track", limit=1)
            print("✓ Spotify API connection successful")
            
            return sp
            
        except ImportError:
            raise ImportError("spotipy library not installed. Run: pip install spotipy")
        except Exception as e:
            raise Exception(f"Failed to initialize Spotify client: {e}")
    
    def get_musicoset_data(self, table: str = "songs") -> pd.DataFrame:
        """
        Load MusicOSet dataset from SQL database
        
        Args:
            table: Table name to load (songs, artists, albums, etc.)
            
        Returns:
            DataFrame with MusicOSet data
        """
        sql_file = self.datasets_dir / "musicoset" / "musicoset.sql"
        
        if not sql_file.exists():
            raise FileNotFoundError(f"MusicOSet SQL file not found at {sql_file}")
        
        # Create temporary SQLite database from SQL file
        db_path = self.datasets_dir / "musicoset" / "musicoset.db"
        
        if not db_path.exists():
            print("Creating SQLite database from SQL file...")
            self._create_sqlite_from_sql(sql_file, db_path)
        
        # Load data from SQLite
        conn = sqlite3.connect(db_path)
        
        try:
            # Get available tables
            tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
            available_tables = pd.read_sql_query(tables_query, conn)['name'].tolist()
            
            if table not in available_tables:
                print(f"Available tables: {available_tables}")
                raise ValueError(f"Table '{table}' not found in database")
            
            # Load the requested table
            query = f"SELECT * FROM {table}"
            df = pd.read_sql_query(query, conn)
            
            return df
            
        finally:
            conn.close()
    
    def _create_sqlite_from_sql(self, sql_file: Path, db_path: Path):
        """Create SQLite database from SQL dump file"""
        try:
            conn = sqlite3.connect(db_path)
            
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Execute SQL commands
            conn.executescript(sql_content)
            conn.close()
            
            print(f"SQLite database created at {db_path}")
            
        except Exception as e:
            print(f"Error creating SQLite database: {e}")
            if db_path.exists():
                db_path.unlink()  # Remove incomplete database
            raise
    
    def get_million_song_data(self, subset: str = "uspop") -> pd.DataFrame:
        """
        Load Million Song Dataset subset
        
        Args:
            subset: Subset name (beatles, uspop, cal500, cal10k)
            
        Returns:
            DataFrame with Million Song data
        """
        subset_dir = self.datasets_dir / "million_song" / subset
        
        if not subset_dir.exists():
            raise FileNotFoundError(f"Million Song {subset} subset not found at {subset_dir}")
        
        # Look for HDF5 or CSV files
        h5_files = list(subset_dir.glob("*.h5"))
        csv_files = list(subset_dir.glob("*.csv"))
        
        if h5_files:
            # Load HDF5 file (typical for Million Song Dataset)
            try:
                import h5py
                h5_file = h5_files[0]
                
                # This is a simplified loader - actual structure depends on the specific dataset
                data = []
                with h5py.File(h5_file, 'r') as f:
                    # Extract basic metadata (structure varies by subset)
                    if 'metadata' in f:
                        metadata = f['metadata']
                        # Process metadata structure
                        pass
                
                return pd.DataFrame(data)
                
            except ImportError:
                print("h5py not installed. Run: pip install h5py")
                return pd.DataFrame()
                
        elif csv_files:
            # Load CSV file
            return pd.read_csv(csv_files[0])
        
        else:
            raise FileNotFoundError(f"No data files found in {subset_dir}")
    
    def get_spotify_tracks_data(self) -> pd.DataFrame:
        """
        Load Spotify Tracks Dataset from Kaggle
        
        Returns:
            DataFrame with Spotify tracks data
        """
        spotify_dir = self.datasets_dir / "spotify_tracks"
        
        if not spotify_dir.exists():
            raise FileNotFoundError(f"Spotify tracks directory not found at {spotify_dir}")
        
        # Look for CSV files
        csv_files = list(spotify_dir.glob("*.csv"))
        
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {spotify_dir}")
        
        # Load the main dataset file
        main_file = None
        for csv_file in csv_files:
            if 'track' in csv_file.name.lower() or 'spotify' in csv_file.name.lower():
                main_file = csv_file
                break
        
        if main_file is None:
            main_file = csv_files[0]  # Use first CSV file
        
        print(f"Loading Spotify dataset from: {main_file}")
        return pd.read_csv(main_file)
    
    def download_preview_audio(self, df: pd.DataFrame, output_dir: str = None, 
                             url_column: str = "spotify_preview_url") -> pd.DataFrame:
        """
        Download 30-second preview audio files from Spotify
        
        Args:
            df: DataFrame containing preview URLs
            output_dir: Directory to save audio files
            url_column: Column name containing preview URLs
            
        Returns:
            DataFrame with local file paths added
        """
        if output_dir is None:
            output_dir = self.datasets_dir / "shared" / "preview_audio"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        config = self.config.get("preview_audio", {})
        timeout = config.get("timeout", 30)
        
        print(f"📥 Downloading preview audio to: {output_path}")
        
        downloaded_files = []
        failed_downloads = []
        
        for idx, row in df.iterrows():
            preview_url = row.get(url_column)
            
            if pd.isna(preview_url) or not preview_url:
                downloaded_files.append(None)
                continue
            
            try:
                # Generate filename from track info
                track_name = str(row.get('title', row.get('name', f'track_{idx}'))).strip()
                artist_name = str(row.get('artist', row.get('artist_name', 'unknown'))).strip()
                
                # Clean filename
                safe_track = "".join(c for c in track_name if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_artist = "".join(c for c in artist_name if c.isalnum() or c in (' ', '-', '_')).strip()
                
                filename = f"{safe_artist}_{safe_track}_preview.mp3"
                file_path = output_path / filename
                
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
        print(f"✓ Downloaded {success_count}/{len(df)} preview audio files")
        
        if failed_downloads:
            print(f"⚠️  Failed downloads: {len(failed_downloads)} files")
        
        return df_copy

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
                                    row_dict['spotify_track_number'] = track.get('track_number')
                                    row_dict['spotify_disc_number'] = track.get('disc_number')
                                    
                                    # Add album info
                                    if 'album' in track:
                                        album = track['album']
                                        row_dict['spotify_album_name'] = album.get('name')
                                        row_dict['spotify_album_release_date'] = album.get('release_date')
                                        row_dict['spotify_album_type'] = album.get('album_type')
                                        row_dict['spotify_album_total_tracks'] = album.get('total_tracks')
                                        
                                        # Album images
                                        if 'images' in album and album['images']:
                                            row_dict['spotify_album_image_url'] = album['images'][0].get('url')
                                    
                                    # Add artist info
                                    if 'artists' in track and track['artists']:
                                        main_artist = track['artists'][0]
                                        row_dict['spotify_artist_id'] = main_artist.get('id')
                                        row_dict['spotify_artist_name'] = main_artist.get('name')
                                        
                                        # All artists
                                        all_artists = [artist['name'] for artist in track['artists']]
                                        row_dict['spotify_all_artists'] = ', '.join(all_artists)
                                        
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
                                    row_dict['spotify_tempo_bpm_rounded'] = round(tempo)
                                
                                if 'key' in features and features['key'] is not None:
                                    row_dict['spotify_key_name'] = self._key_to_name(features['key'])
                                
                                if 'mode' in features and features['mode'] is not None:
                                    row_dict['spotify_mode_name'] = 'Major' if features['mode'] == 1 else 'Minor'
                                
                                # Energy and valence categories for diversity analysis
                                if 'energy' in features and features['energy'] is not None:
                                    energy = features['energy']
                                    if energy < 0.3:
                                        row_dict['spotify_energy_category'] = 'Low'
                                    elif energy < 0.7:
                                        row_dict['spotify_energy_category'] = 'Medium'
                                    else:
                                        row_dict['spotify_energy_category'] = 'High'
                                
                                if 'valence' in features and features['valence'] is not None:
                                    valence = features['valence']
                                    if valence < 0.3:
                                        row_dict['spotify_mood_category'] = 'Sad'
                                    elif valence < 0.7:
                                        row_dict['spotify_mood_category'] = 'Neutral'
                                    else:
                                        row_dict['spotify_mood_category'] = 'Happy'
                                
                                # Danceability categories
                                if 'danceability' in features and features['danceability'] is not None:
                                    danceability = features['danceability']
                                    if danceability < 0.3:
                                        row_dict['spotify_danceability_category'] = 'Low'
                                    elif danceability < 0.7:
                                        row_dict['spotify_danceability_category'] = 'Medium'
                                    else:
                                        row_dict['spotify_danceability_category'] = 'High'
                                        
                        except Exception as features_error:
                            print(f"Audio features error for ID {spotify_id}: {features_error}")
                
                except Exception as e:
                    print(f"Error enriching row {idx}: {e}")
                
                enriched_data.append(row_dict)
            
            result_df = pd.DataFrame(enriched_data)
            spotify_columns = [c for c in result_df.columns if c.startswith('spotify_')]
            print(f"✓ Enrichment complete. Added {len(spotify_columns)} Spotify features")
            
            # Download preview audio if requested
            if download_previews and 'spotify_preview_url' in result_df.columns:
                print("📥 Starting preview audio download...")
                result_df = self.download_preview_audio(result_df)
            
            return result_df
            
        except Exception as e:
            print(f"Error with Spotify API enrichment: {e}")
            return df
    
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
    
    def get_spotify_artist_info(self, artist_ids: List[str]) -> pd.DataFrame:
        """
        Get detailed artist information from Spotify API
        
        Args:
            artist_ids: List of Spotify artist IDs
            
        Returns:
            DataFrame with artist information
        """
        try:
            sp = self._init_spotify_client()
            artist_data = []
            
            # Process in batches of 50 (Spotify API limit)
            batch_size = 50
            for i in range(0, len(artist_ids), batch_size):
                batch = artist_ids[i:i + batch_size]
                
                try:
                    artists = sp.artists(batch)
                    
                    for artist in artists['artists']:
                        if artist:  # Check if artist data is not None
                            artist_info = {
                                'artist_id': artist['id'],
                                'artist_name': artist['name'],
                                'artist_popularity': artist.get('popularity', 0),
                                'artist_followers': artist.get('followers', {}).get('total', 0),
                                'artist_genres': ', '.join(artist.get('genres', [])),
                                'artist_external_url': artist.get('external_urls', {}).get('spotify')
                            }
                            artist_data.append(artist_info)
                    
                    # Rate limiting
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"Error fetching artist batch {i//batch_size + 1}: {e}")
            
            return pd.DataFrame(artist_data)
            
        except Exception as e:
            print(f"Error fetching artist information: {e}")
            return pd.DataFrame()
    
    def prepare_for_pipeline(self, dataset_name: str, **kwargs) -> Dict:
        """
        Prepare dataset for use in diversity evaluation pipeline
        
        Args:
            dataset_name: Name of dataset (musicoset, million_song, spotify_tracks)
            **kwargs: Additional arguments for dataset loading
            
        Returns:
            Dictionary with prepared data and metadata
        """
        print(f"Preparing {dataset_name} dataset...")
        
        if dataset_name == "musicoset":
            df = self.get_musicoset_data(**kwargs)
        elif dataset_name == "million_song":
            df = self.get_million_song_data(**kwargs)
        elif dataset_name == "spotify_tracks":
            df = self.get_spotify_tracks_data(**kwargs)
        else:
            raise ValueError(f"Unknown dataset: {dataset_name}")
        
        print(f"Loaded {len(df)} records")
        
        # Standardize column names for pipeline compatibility
        standardized_df = self.standardize_columns(df)
        
        # Prepare metadata
        metadata = {
            'dataset_name': dataset_name,
            'total_tracks': len(standardized_df),
            'columns': list(standardized_df.columns),
            'has_audio_features': any('audio_' in col or 'spotify_' in col for col in standardized_df.columns),
            'has_spotify_ids': 'spotify_id' in standardized_df.columns,
            'sample_data': standardized_df.head(3).to_dict('records') if len(standardized_df) > 0 else []
        }
        
        return {
            'data': standardized_df,
            'metadata': metadata
        }
    
    def standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names across different datasets
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with standardized columns
        """
        # Define column mapping for standardization
        column_mapping = {
            # Common variations for track name
            'track_name': 'title',
            'song_name': 'title',
            'track_title': 'title',
            'song_title': 'title',
            'name': 'title',
            
            # Common variations for artist
            'artist_name': 'artist',
            'track_artist': 'artist',
            'artists': 'artist',
            
            # Audio features (keep spotify_ prefix if exists)
            'danceability': 'audio_danceability',
            'energy': 'audio_energy',
            'valence': 'audio_valence',
            'tempo': 'audio_tempo',
            'loudness': 'audio_loudness',
            'speechiness': 'audio_speechiness',
            'acousticness': 'audio_acousticness',
            'instrumentalness': 'audio_instrumentalness',
            'liveness': 'audio_liveness',
            
            # Other common fields
            'release_date': 'year',
            'album_name': 'album',
            'genre': 'genres',
        }
        
        # Create a copy to avoid modifying original
        df_standardized = df.copy()
        
        # Rename columns
        df_standardized = df_standardized.rename(columns=column_mapping)
        
        # Ensure required columns exist
        required_columns = ['title', 'artist']
        for col in required_columns:
            if col not in df_standardized.columns:
                df_standardized[col] = 'Unknown'
        
        return df_standardized
    
    def export_for_analysis(self, dataset_name: str, output_path: str, enrich_spotify: bool = False, **kwargs):
        """
        Export dataset in format suitable for diversity analysis
        
        Args:
            dataset_name: Name of dataset to export
            output_path: Path to save exported data
            enrich_spotify: Whether to enrich with Spotify API data
            **kwargs: Additional arguments for dataset loading
        """
        prepared_data = self.prepare_for_pipeline(dataset_name, **kwargs)
        df = prepared_data['data']
        
        # Enrich with Spotify API if requested
        if enrich_spotify:
            print("Enriching with Spotify API data...")
            df = self.enrich_with_spotify_api(df)
        
        # Save data
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        df.to_csv(output_path, index=False)
        
        # Update metadata
        prepared_data['metadata']['enriched_with_spotify'] = enrich_spotify
        prepared_data['metadata']['exported_records'] = len(df)
        
        # Save metadata
        metadata_path = output_path.with_suffix('.json')
        with open(metadata_path, 'w') as f:
            json.dump(prepared_data['metadata'], f, indent=2)
        
        print(f"Dataset exported to {output_path}")
        print(f"Metadata saved to {metadata_path}")
        print(f"Total records: {len(df)}")

def main():
    """Main function for command-line usage"""
    if len(sys.argv) < 2:
        print("Usage: python dataset_integration.py <command> [args...]")
        print("Commands:")
        print("  prepare <dataset_name> - Prepare dataset for pipeline")
        print("  export <dataset_name> <output_path> [--enrich] - Export dataset")
        print("  info <dataset_name> - Show dataset information")
        print("  test-spotify - Test Spotify API connection")
        print("  list - List available datasets")
        return
    
    integration = DatasetIntegration()
    command = sys.argv[1]
    
    if command == "list":
        print("Available datasets:")
        print("  - musicoset: MusicOSet dataset from Zenodo")
        print("  - million_song: Million Song Dataset subsets")
        print("  - spotify_tracks: Spotify Tracks Dataset from Kaggle")
        
    elif command == "test-spotify":
        try:
            sp = integration._init_spotify_client()
            print("✓ Spotify API connection successful!")
            
            # Test search
            results = sp.search(q='The Beatles', type='artist', limit=1)
            if results['artists']['items']:
                artist = results['artists']['items'][0]
                print(f"✓ Search test successful: Found {artist['name']}")
            
        except Exception as e:
            print(f"✗ Spotify API connection failed: {e}")
        
    elif command == "prepare":
        if len(sys.argv) < 3:
            print("Usage: python dataset_integration.py prepare <dataset_name>")
            return
        
        dataset_name = sys.argv[2]
        try:
            result = integration.prepare_for_pipeline(dataset_name)
            print(f"Dataset {dataset_name} prepared successfully:")
            print(f"  Total tracks: {result['metadata']['total_tracks']}")
            print(f"  Columns: {len(result['metadata']['columns'])}")
            print(f"  Has audio features: {result['metadata']['has_audio_features']}")
        except Exception as e:
            print(f"Error preparing dataset: {e}")
        
    elif command == "export":
        if len(sys.argv) < 4:
            print("Usage: python dataset_integration.py export <dataset_name> <output_path> [--enrich]")
            return
        
        dataset_name = sys.argv[2]
        output_path = sys.argv[3]
        enrich = "--enrich" in sys.argv
        
        try:
            integration.export_for_analysis(dataset_name, output_path, enrich_spotify=enrich)
        except Exception as e:
            print(f"Error exporting dataset: {e}")
        
    elif command == "info":
        if len(sys.argv) < 3:
            print("Usage: python dataset_integration.py info <dataset_name>")
            return
        
        dataset_name = sys.argv[2]
        try:
            result = integration.prepare_for_pipeline(dataset_name)
            print(f"Dataset Information: {dataset_name}")
            print("=" * 40)
            for key, value in result['metadata'].items():
                if key != 'sample_data':
                    print(f"{key}: {value}")
        except Exception as e:
            print(f"Error getting dataset info: {e}")

if __name__ == "__main__":
    main()