#!/usr/bin/env python3
"""
Example: Using Spotify 30-second Preview Audio for Music Diversity Analysis
Demonstrates the complete workflow from API enrichment to audio feature extraction
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pipelines.utils.dataset_integration import DatasetIntegration
from pipelines.utils.preview_audio_manager import PreviewAudioManager
import pandas as pd

def main():
    print("🎵 Spotify Preview Audio Diversity Analysis Example")
    print("=" * 60)
    
    # Initialize components
    dataset_integration = DatasetIntegration()
    preview_manager = PreviewAudioManager()
    
    # Example 1: Load a small sample dataset
    print("\n1. Creating sample dataset...")
    sample_data = {
        'title': ['Shape of You', 'Blinding Lights', 'Watermelon Sugar', 'Levitating', 'Good 4 U'],
        'artist': ['Ed Sheeran', 'The Weeknd', 'Harry Styles', 'Dua Lipa', 'Olivia Rodrigo']
    }
    df = pd.DataFrame(sample_data)
    print(f"Created sample dataset with {len(df)} tracks")
    
    # Example 2: Enrich with Spotify API (includes preview URLs)
    print("\n2. Enriching with Spotify API data...")
    try:
        enriched_df = dataset_integration.enrich_with_spotify_api(
            df, 
            download_previews=True  # This will download 30s previews
        )
        
        # Show what we got
        spotify_cols = [c for c in enriched_df.columns if c.startswith('spotify_')]
        print(f"✓ Added {len(spotify_cols)} Spotify features")
        
        # Check preview URLs
        preview_count = enriched_df['spotify_preview_url'].notna().sum()
        print(f"✓ Found {preview_count} preview URLs")
        
        # Check downloaded files
        if 'local_preview_path' in enriched_df.columns:
            downloaded_count = enriched_df['local_preview_path'].notna().sum()
            print(f"✓ Downloaded {downloaded_count} preview audio files")
        
    except Exception as e:
        print(f"❌ Error with Spotify API: {e}")
        print("Make sure you have configured your Spotify credentials!")
        return
    
    # Example 3: Extract audio features from preview files
    print("\n3. Extracting audio features from preview files...")
    try:
        if 'local_preview_path' in enriched_df.columns:
            featured_df = preview_manager.extract_audio_features(enriched_df)
            
            audio_cols = [c for c in featured_df.columns if c.startswith('audio_')]
            print(f"✓ Extracted {len(audio_cols)} audio features")
            
            # Show some example features
            print("\nExample audio features:")
            for col in audio_cols[:5]:
                if not featured_df[col].isna().all():
                    mean_val = featured_df[col].mean()
                    print(f"  {col}: {mean_val:.4f}")
        else:
            print("⚠️  No preview files to analyze")
            featured_df = enriched_df
            
    except Exception as e:
        print(f"❌ Error extracting audio features: {e}")
        featured_df = enriched_df
    
    # Example 4: Analyze diversity
    print("\n4. Analyzing music diversity...")
    try:
        analysis = preview_manager.analyze_diversity_metrics(featured_df)
        
        print(f"📊 Diversity Analysis Results:")
        print(f"  Total tracks: {analysis['total_tracks']}")
        print(f"  Tracks with preview: {analysis['tracks_with_preview']}")
        
        if 'diversity_score' in analysis:
            print(f"  Diversity score: {analysis['diversity_score']:.4f}")
            print(f"  Average correlation: {analysis['avg_correlation']:.4f}")
        
    except Exception as e:
        print(f"❌ Error in diversity analysis: {e}")
    
    # Example 5: Generate report
    print("\n5. Generating diversity report...")
    try:
        report = preview_manager.generate_diversity_report(featured_df)
        print("📄 Diversity Report Generated!")
        
        # Save results
        output_path = "/home/evev/diversity-eval/data/results/spotify_preview_example.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        featured_df.to_csv(output_path, index=False)
        print(f"💾 Results saved to: {output_path}")
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
    
    print("\n✅ Example completed!")
    print("\nNext steps:")
    print("1. Configure your Spotify API credentials in data/datasets/config/spotify_config.json")
    print("2. Try with larger datasets like MusicOSet or Million Song Dataset")
    print("3. Use the extracted features for diversity evaluation in your pipeline")

if __name__ == "__main__":
    main()