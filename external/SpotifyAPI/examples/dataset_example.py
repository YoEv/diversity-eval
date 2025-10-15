#!/usr/bin/env python3
"""
Spotify数据集获取示例
演示如何获取和分析音乐数据集
"""

import sys
import os
import pandas as pd
from pathlib import Path

# 添加脚本路径
sys.path.append(str(Path(__file__).parent.parent / "scripts"))

from dataset_integration import SpotifyDatasetIntegration

def create_sample_dataset():
    """创建示例数据集"""
    print("🎵 创建示例数据集...")
    
    # 流行歌曲示例
    sample_tracks = [
        {"title": "Shape of You", "artist": "Ed Sheeran"},
        {"title": "Blinding Lights", "artist": "The Weeknd"},
        {"title": "Watermelon Sugar", "artist": "Harry Styles"},
        {"title": "Levitating", "artist": "Dua Lipa"},
        {"title": "Good 4 U", "artist": "Olivia Rodrigo"},
        {"title": "Stay", "artist": "The Kid LAROI"},
        {"title": "Industry Baby", "artist": "Lil Nas X"},
        {"title": "Heat Waves", "artist": "Glass Animals"},
        {"title": "Bad Habits", "artist": "Ed Sheeran"},
        {"title": "Peaches", "artist": "Justin Bieber"},
        # 添加一些不同风格的歌曲
        {"title": "Bohemian Rhapsody", "artist": "Queen"},
        {"title": "Hotel California", "artist": "Eagles"},
        {"title": "Smells Like Teen Spirit", "artist": "Nirvana"},
        {"title": "Billie Jean", "artist": "Michael Jackson"},
        {"title": "Sweet Child O' Mine", "artist": "Guns N' Roses"},
        {"title": "Imagine", "artist": "John Lennon"},
        {"title": "Like a Rolling Stone", "artist": "Bob Dylan"},
        {"title": "Purple Haze", "artist": "Jimi Hendrix"},
        {"title": "What's Going On", "artist": "Marvin Gaye"},
        {"title": "Respect", "artist": "Aretha Franklin"}
    ]
    
    df = pd.DataFrame(sample_tracks)
    print(f"✅ 创建了包含 {len(df)} 首歌曲的示例数据集")
    return df

def enrich_dataset_with_spotify(df):
    """使用Spotify API丰富数据集"""
    print("\n🔄 使用Spotify API丰富数据集...")
    
    # 初始化Spotify集成
    integration = SpotifyDatasetIntegration()
    
    # 丰富数据集（包括下载预览音频）
    enriched_df = integration.enrich_with_spotify_api(
        df, 
        download_previews=True,
        batch_size=10,  # 较小的批次大小以避免API限制
        delay=0.2       # 稍长的延迟
    )
    
    return enriched_df

def analyze_diversity(df):
    """分析音乐多样性"""
    print("\n📊 分析音乐多样性...")
    
    # 检查可用的Spotify特征
    spotify_features = [col for col in df.columns if col.startswith('spotify_')]
    print(f"可用的Spotify特征: {len(spotify_features)} 个")
    
    if not spotify_features:
        print("❌ 没有找到Spotify特征数据")
        return
    
    # 音频特征分析
    audio_features = ['spotify_danceability', 'spotify_energy', 'spotify_valence', 
                     'spotify_acousticness', 'spotify_instrumentalness', 'spotify_tempo']
    
    available_features = [f for f in audio_features if f in df.columns]
    
    if available_features:
        print(f"\n🎶 音频特征统计 ({len(available_features)} 个特征):")
        for feature in available_features:
            if df[feature].notna().any():
                mean_val = df[feature].mean()
                std_val = df[feature].std()
                print(f"  {feature.replace('spotify_', '')}: 平均值={mean_val:.3f}, 标准差={std_val:.3f}")
    
    # 流派多样性分析
    if 'spotify_key_name' in df.columns:
        key_distribution = df['spotify_key_name'].value_counts()
        print(f"\n🎼 音调分布:")
        for key, count in key_distribution.head().items():
            print(f"  {key}: {count} 首歌曲")
    
    # 情感分析
    if 'spotify_mood_category' in df.columns:
        mood_distribution = df['spotify_mood_category'].value_counts()
        print(f"\n😊 情感分布:")
        for mood, count in mood_distribution.items():
            print(f"  {mood}: {count} 首歌曲")
    
    # 能量分析
    if 'spotify_energy_category' in df.columns:
        energy_distribution = df['spotify_energy_category'].value_counts()
        print(f"\n⚡ 能量分布:")
        for energy, count in energy_distribution.items():
            print(f"  {energy}: {count} 首歌曲")

def save_results(df, output_dir):
    """保存结果"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 保存完整数据集
    full_output = output_path / "enriched_dataset.csv"
    df.to_csv(full_output, index=False)
    print(f"\n💾 完整数据集已保存到: {full_output}")
    
    # 保存仅包含Spotify特征的数据
    spotify_columns = ['title', 'artist'] + [col for col in df.columns if col.startswith('spotify_')]
    if len(spotify_columns) > 2:
        spotify_df = df[spotify_columns]
        spotify_output = output_path / "spotify_features.csv"
        spotify_df.to_csv(spotify_output, index=False)
        print(f"💾 Spotify特征数据已保存到: {spotify_output}")
    
    # 保存预览音频文件列表
    if 'local_preview_path' in df.columns:
        preview_files = df[df['local_preview_path'].notna()]['local_preview_path'].tolist()
        if preview_files:
            preview_list = output_path / "preview_audio_files.txt"
            with open(preview_list, 'w') as f:
                for file_path in preview_files:
                    f.write(f"{file_path}\n")
            print(f"💾 预览音频文件列表已保存到: {preview_list}")
            print(f"📥 成功下载了 {len(preview_files)} 个预览音频文件")

def main():
    print("🎵 Spotify数据集获取和分析示例")
    print("=" * 50)
    
    # 设置输出目录
    output_dir = Path(__file__).parent.parent / "data" / "example_output"
    
    try:
        # 1. 创建示例数据集
        df = create_sample_dataset()
        
        # 2. 使用Spotify API丰富数据集
        enriched_df = enrich_dataset_with_spotify(df)
        
        # 3. 分析多样性
        analyze_diversity(enriched_df)
        
        # 4. 保存结果
        save_results(enriched_df, output_dir)
        
        print("\n✅ 数据集获取和分析完成！")
        print(f"\n📋 结果摘要:")
        print(f"  - 原始歌曲数量: {len(df)}")
        print(f"  - 成功获取Spotify数据的歌曲: {enriched_df['spotify_id'].notna().sum()}")
        print(f"  - 可用预览音频: {enriched_df['local_preview_path'].notna().sum()}")
        print(f"  - 输出目录: {output_dir}")
        
    except Exception as e:
        print(f"❌ 处理过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()