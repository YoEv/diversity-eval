#!/usr/bin/env python3
"""
Preview Audio Manager for Music Diversity Evaluation Pipeline
Handles downloading, organizing, and analyzing 30-second Spotify preview audio files
"""

import os
import sys
import json
import pandas as pd
import requests
import librosa
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
from urllib.parse import urlparse
import time

class PreviewAudioManager:
    """
    Manages 30-second preview audio files from Spotify
    Provides audio analysis capabilities for diversity evaluation
    """
    
    def __init__(self, datasets_dir: str = "/home/evev/diversity-eval/data/datasets"):
        self.datasets_dir = Path(datasets_dir)
        self.preview_dir = self.datasets_dir / "shared" / "preview_audio"
        self.preview_dir.mkdir(parents=True, exist_ok=True)
        
        # Audio analysis settings
        self.sample_rate = 22050
        self.hop_length = 512
        self.n_mels = 128
        
    def download_previews_from_dataframe(self, df: pd.DataFrame, 
                                       url_column: str = "spotify_preview_url",
                                       overwrite: bool = False) -> pd.DataFrame:
        """
        Download preview audio files from DataFrame containing URLs
        
        Args:
            df: DataFrame with preview URLs
            url_column: Column containing preview URLs
            overwrite: Whether to overwrite existing files
            
        Returns:
            DataFrame with local file paths added
        """
        print(f"📥 Starting download of {len(df)} preview audio files...")
        
        downloaded_files = []
        failed_downloads = []
        skipped_files = []
        
        for idx, row in df.iterrows():
            preview_url = row.get(url_column)
            
            if pd.isna(preview_url) or not preview_url:
                downloaded_files.append(None)
                continue
            
            try:
                # Generate safe filename
                track_name = str(row.get('title', row.get('name', row.get('spotify_name', f'track_{idx}')))).strip()
                artist_name = str(row.get('artist', row.get('artist_name', row.get('spotify_artist_name', 'unknown')))).strip()
                
                # Clean filename
                safe_track = "".join(c for c in track_name if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
                safe_artist = "".join(c for c in artist_name if c.isalnum() or c in (' ', '-', '_')).strip()[:30]
                
                filename = f"{safe_artist}_{safe_track}_preview.mp3"
                file_path = self.preview_dir / filename
                
                # Skip if file exists and not overwriting
                if file_path.exists() and not overwrite:
                    downloaded_files.append(str(file_path))
                    skipped_files.append(idx)
                    continue
                
                # Download the preview
                response = requests.get(preview_url, timeout=30, stream=True)
                response.raise_for_status()
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                downloaded_files.append(str(file_path))
                
                if idx % 25 == 0:
                    print(f"Downloaded {idx + 1}/{len(df)} files...")
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Failed to download preview for row {idx}: {e}")
                downloaded_files.append(None)
                failed_downloads.append(idx)
        
        # Add results to DataFrame
        df_result = df.copy()
        df_result['local_preview_path'] = downloaded_files
        df_result['preview_downloaded'] = [path is not None for path in downloaded_files]
        
        # Summary
        success_count = len([f for f in downloaded_files if f is not None])
        print(f"\n📊 Download Summary:")
        print(f"✓ Successfully downloaded: {success_count}")
        print(f"⏭️  Skipped (already exists): {len(skipped_files)}")
        print(f"❌ Failed downloads: {len(failed_downloads)}")
        print(f"📁 Files saved to: {self.preview_dir}")
        
        return df_result
    
    def extract_audio_features(self, df: pd.DataFrame, 
                             path_column: str = "local_preview_path") -> pd.DataFrame:
        """
        Extract audio features from downloaded preview files for diversity analysis
        
        Args:
            df: DataFrame with local file paths
            path_column: Column containing local file paths
            
        Returns:
            DataFrame with extracted audio features
        """
        print(f"🎵 Extracting audio features from preview files...")
        
        feature_data = []
        
        for idx, row in df.iterrows():
            file_path = row.get(path_column)
            
            if pd.isna(file_path) or not file_path or not Path(file_path).exists():
                feature_data.append({})
                continue
            
            try:
                # Load audio file
                y, sr = librosa.load(file_path, sr=self.sample_rate, duration=30)
                
                # Extract comprehensive features for diversity analysis
                features = {}
                
                # Spectral features
                features['spectral_centroid'] = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
                features['spectral_bandwidth'] = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
                features['spectral_rolloff'] = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
                features['zero_crossing_rate'] = np.mean(librosa.feature.zero_crossing_rate(y))
                
                # MFCC features (first 13 coefficients)
                mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                for i in range(13):
                    features[f'mfcc_{i+1}'] = np.mean(mfccs[i])
                
                # Chroma features
                chroma = librosa.feature.chroma(y=y, sr=sr)
                features['chroma_mean'] = np.mean(chroma)
                features['chroma_std'] = np.std(chroma)
                
                # Tempo and rhythm
                tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
                features['librosa_tempo'] = tempo
                features['beat_count'] = len(beats)
                
                # Harmonic and percussive components
                y_harmonic, y_percussive = librosa.effects.hpss(y)
                features['harmonic_energy'] = np.sum(y_harmonic**2)
                features['percussive_energy'] = np.sum(y_percussive**2)
                features['harmonic_percussive_ratio'] = features['harmonic_energy'] / (features['percussive_energy'] + 1e-8)
                
                # RMS energy
                rms = librosa.feature.rms(y=y)
                features['rms_energy'] = np.mean(rms)
                
                # Onset detection
                onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
                features['onset_rate'] = len(onset_frames) / (len(y) / sr)
                
                feature_data.append(features)
                
                if idx % 50 == 0:
                    print(f"Processed {idx + 1}/{len(df)} audio files...")
                
            except Exception as e:
                print(f"Error extracting features from {file_path}: {e}")
                feature_data.append({})
        
        # Create features DataFrame
        features_df = pd.DataFrame(feature_data)
        
        # Add prefix to distinguish from Spotify features
        features_df = features_df.add_prefix('audio_')
        
        # Combine with original DataFrame
        result_df = pd.concat([df, features_df], axis=1)
        
        feature_count = len([c for c in features_df.columns if not features_df[c].isna().all()])
        print(f"✓ Extracted {feature_count} audio features from preview files")
        
        return result_df
    
    def analyze_diversity_metrics(self, df: pd.DataFrame) -> Dict:
        """
        Analyze diversity metrics from audio features
        
        Args:
            df: DataFrame with audio features
            
        Returns:
            Dictionary with diversity analysis results
        """
        print("📊 Analyzing audio diversity metrics...")
        
        # Get audio feature columns
        audio_cols = [c for c in df.columns if c.startswith('audio_') and df[c].dtype in ['float64', 'int64']]
        spotify_cols = [c for c in df.columns if c.startswith('spotify_') and df[c].dtype in ['float64', 'int64']]
        
        analysis = {
            'total_tracks': len(df),
            'tracks_with_preview': df['preview_downloaded'].sum() if 'preview_downloaded' in df.columns else 0,
            'audio_features_extracted': len(audio_cols),
            'spotify_features_available': len(spotify_cols)
        }
        
        if audio_cols:
            # Calculate diversity metrics
            audio_data = df[audio_cols].dropna()
            
            if len(audio_data) > 0:
                # Feature variance (higher = more diverse)
                analysis['feature_variances'] = audio_data.var().to_dict()
                
                # Feature ranges
                analysis['feature_ranges'] = (audio_data.max() - audio_data.min()).to_dict()
                
                # Correlation analysis
                correlation_matrix = audio_data.corr()
                analysis['avg_correlation'] = correlation_matrix.abs().mean().mean()
                
                # Diversity score (based on variance and low correlation)
                variance_score = audio_data.var().mean()
                correlation_penalty = analysis['avg_correlation']
                analysis['diversity_score'] = variance_score * (1 - correlation_penalty)
        
        return analysis
    
    def generate_diversity_report(self, df: pd.DataFrame, output_path: str = None) -> str:
        """
        Generate a comprehensive diversity analysis report
        
        Args:
            df: DataFrame with audio features
            output_path: Path to save the report
            
        Returns:
            Report content as string
        """
        analysis = self.analyze_diversity_metrics(df)
        
        report = f"""
# Music Diversity Analysis Report
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Dataset Overview
- Total tracks: {analysis['total_tracks']}
- Tracks with preview audio: {analysis['tracks_with_preview']}
- Audio features extracted: {analysis['audio_features_extracted']}
- Spotify features available: {analysis['spotify_features_available']}

## Diversity Metrics
"""
        
        if 'diversity_score' in analysis:
            report += f"- Overall diversity score: {analysis['diversity_score']:.4f}\n"
            report += f"- Average feature correlation: {analysis['avg_correlation']:.4f}\n"
            
            # Top diverse features
            if 'feature_variances' in analysis:
                variances = analysis['feature_variances']
                top_diverse = sorted(variances.items(), key=lambda x: x[1], reverse=True)[:5]
                
                report += "\n### Most Diverse Features (by variance):\n"
                for feature, variance in top_diverse:
                    report += f"- {feature}: {variance:.4f}\n"
        
        # Spotify feature analysis if available
        spotify_cols = [c for c in df.columns if c.startswith('spotify_') and df[c].dtype in ['float64', 'int64']]
        if spotify_cols:
            spotify_data = df[spotify_cols].dropna()
            if len(spotify_data) > 0:
                report += "\n### Spotify Feature Summary:\n"
                for col in ['spotify_danceability', 'spotify_energy', 'spotify_valence', 'spotify_tempo']:
                    if col in spotify_data.columns:
                        mean_val = spotify_data[col].mean()
                        std_val = spotify_data[col].std()
                        report += f"- {col}: mean={mean_val:.3f}, std={std_val:.3f}\n"
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(report)
            print(f"📄 Report saved to: {output_path}")
        
        return report

def main():
    parser = argparse.ArgumentParser(description="Preview Audio Manager for Music Diversity Evaluation")
    parser.add_argument("command", choices=["download", "extract", "analyze", "report"], 
                       help="Command to execute")
    parser.add_argument("--input", "-i", required=True, help="Input CSV file with track data")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--url-column", default="spotify_preview_url", 
                       help="Column name containing preview URLs")
    parser.add_argument("--overwrite", action="store_true", 
                       help="Overwrite existing files")
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = PreviewAudioManager()
    
    # Load input data
    df = pd.read_csv(args.input)
    print(f"Loaded {len(df)} tracks from {args.input}")
    
    if args.command == "download":
        result_df = manager.download_previews_from_dataframe(df, args.url_column, args.overwrite)
        output_path = args.output or args.input.replace('.csv', '_with_previews.csv')
        result_df.to_csv(output_path, index=False)
        print(f"Results saved to: {output_path}")
        
    elif args.command == "extract":
        result_df = manager.extract_audio_features(df)
        output_path = args.output or args.input.replace('.csv', '_with_audio_features.csv')
        result_df.to_csv(output_path, index=False)
        print(f"Results saved to: {output_path}")
        
    elif args.command == "analyze":
        analysis = manager.analyze_diversity_metrics(df)
        print(json.dumps(analysis, indent=2))
        
    elif args.command == "report":
        report = manager.generate_diversity_report(df, args.output)
        if not args.output:
            print(report)

if __name__ == "__main__":
    main()