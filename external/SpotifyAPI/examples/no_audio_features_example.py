#!/usr/bin/env python3
"""
不依赖音频特征的Spotify数据集获取脚本
专门解决音频特征权限问题
"""

import sys
import os
import pandas as pd
import time
from pathlib import Path

# 添加脚本路径
sys.path.append(str(Path(__file__).parent.parent / "scripts"))

def create_test_dataset():
    """创建测试数据集"""
    print("🎵 创建测试数据集...")
    
    sample_tracks = [
        {"title": "Shape of You", "artist": "Ed Sheeran"},
        {"title": "Blinding Lights", "artist": "The Weeknd"},
        {"title": "Watermelon Sugar", "artist": "Harry Styles"},
        {"title": "Levitating", "artist": "Dua Lipa"},
        {"title": "Good 4 U", "artist": "Olivia Rodrigo"}
    ]
    
    df = pd.DataFrame(sample_tracks)
    print(f"✅ 创建了包含 {len(df)} 首歌曲的测试数据集")
    return df

def enrich_without_audio_features(df):
    """不使用音频特征的数据丰富"""
    print("\n🔄 获取基本Spotify数据（不包含音频特征）...")
    
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        import json
        
        # 加载配置
        config_path = Path(__file__).parent.parent / "config" / "spotify_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        client_id = config["spotify_api"]["client_id"]
        client_secret = config["spotify_api"]["client_secret"]
        
        # 初始化Spotify客户端
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        enriched_data = []
        
        for idx, row in df.iterrows():
            print(f"处理 {idx+1}/{len(df)}: {row['title']} - {row['artist']}")
            
            try:
                # 搜索歌曲
                query = f"track:{row['title']} artist:{row['artist']}"
                results = sp.search(q=query, type='track', limit=1)
                
                if results['tracks']['items']:
                    track = results['tracks']['items'][0]
                    
                    # 获取基本信息（不包含音频特征）
                    track_data = {
                        'original_title': row['title'],
                        'original_artist': row['artist'],
                        'spotify_id': track['id'],
                        'spotify_name': track['name'],
                        'spotify_artist': ', '.join([artist['name'] for artist in track['artists']]),
                        'album_name': track['album']['name'],
                        'release_date': track['album']['release_date'],
                        'popularity': track['popularity'],
                        'duration_ms': track['duration_ms'],
                        'explicit': track['explicit'],
                        'preview_url': track['preview_url'],
                        'external_urls': track['external_urls']['spotify']
                    }
                    
                    # 获取艺术家详细信息
                    if track['artists']:
                        artist_id = track['artists'][0]['id']
                        artist_info = sp.artist(artist_id)
                        track_data.update({
                            'artist_genres': ', '.join(artist_info['genres']),
                            'artist_popularity': artist_info['popularity'],
                            'artist_followers': artist_info['followers']['total']
                        })
                    
                    enriched_data.append(track_data)
                    print(f"  ✅ 成功获取数据")
                    
                else:
                    # 未找到匹配的歌曲
                    track_data = {
                        'original_title': row['title'],
                        'original_artist': row['artist'],
                        'spotify_id': None,
                        'spotify_name': None,
                        'spotify_artist': None,
                        'album_name': None,
                        'release_date': None,
                        'popularity': None,
                        'duration_ms': None,
                        'explicit': None,
                        'preview_url': None,
                        'external_urls': None,
                        'artist_genres': None,
                        'artist_popularity': None,
                        'artist_followers': None
                    }
                    enriched_data.append(track_data)
                    print(f"  ⚠️  未找到匹配的歌曲")
                
                # 添加延迟避免API限制
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  ❌ 处理失败: {e}")
                # 添加空数据
                track_data = {
                    'original_title': row['title'],
                    'original_artist': row['artist'],
                    'spotify_id': None,
                    'spotify_name': None,
                    'spotify_artist': None,
                    'album_name': None,
                    'release_date': None,
                    'popularity': None,
                    'duration_ms': None,
                    'explicit': None,
                    'preview_url': None,
                    'external_urls': None,
                    'artist_genres': None,
                    'artist_popularity': None,
                    'artist_followers': None
                }
                enriched_data.append(track_data)
        
        enriched_df = pd.DataFrame(enriched_data)
        return enriched_df
        
    except Exception as e:
        print(f"❌ 数据丰富过程出错: {e}")
        return df

def download_preview_audio(df):
    """下载预览音频"""
    print("\n📥 下载预览音频...")
    
    if 'preview_url' not in df.columns:
        print("⚠️  没有预览URL数据")
        return df
    
    preview_dir = Path(__file__).parent.parent / "data" / "preview_audio"
    preview_dir.mkdir(parents=True, exist_ok=True)
    
    downloaded_files = []
    
    for idx, row in df.iterrows():
        if pd.notna(row['preview_url']) and row['preview_url']:
            try:
                # 下载预览音频
                response = requests.get(row['preview_url'], timeout=30)
                if response.status_code == 200:
                    filename = f"{row['spotify_id']}_preview.mp3"
                    filepath = preview_dir / filename
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    downloaded_files.append(str(filepath))
                    print(f"  ✅ 下载成功: {row['spotify_name']}")
                else:
                    downloaded_files.append(None)
                    print(f"  ❌ 下载失败: {row['spotify_name']}")
            except Exception as e:
                downloaded_files.append(None)
                print(f"  ❌ 下载异常: {row['spotify_name']} - {e}")
        else:
            downloaded_files.append(None)
            print(f"  ⚠️  无预览URL: {row['spotify_name'] if pd.notna(row['spotify_name']) else row['original_title']}")
    
    df['local_preview_path'] = downloaded_files
    print(f"\n✅ 成功下载 {len([f for f in downloaded_files if f])} 个预览音频文件")
    
    return df

def main():
    print("🎵 不依赖音频特征的Spotify数据集获取")
    print("=" * 50)
    
    # 设置输出目录
    output_dir = Path(__file__).parent.parent / "data" / "no_audio_features_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 1. 创建测试数据集
        df = create_test_dataset()
        
        # 2. 获取基本Spotify数据（不包含音频特征）
        enriched_df = enrich_without_audio_features(df)
        
        # 3. 下载预览音频
        final_df = download_preview_audio(enriched_df)
        
        # 4. 保存结果
        output_file = output_dir / "spotify_dataset_no_audio_features.csv"
        final_df.to_csv(output_file, index=False)
        print(f"\n💾 数据集已保存到: {output_file}")
        
        # 5. 显示统计信息
        spotify_success = final_df['spotify_id'].notna().sum()
        preview_success = final_df['local_preview_path'].notna().sum()
        
        print(f"\n📋 处理结果:")
        print(f"  - 总歌曲数: {len(df)}")
        print(f"  - 成功获取Spotify数据: {spotify_success}")
        print(f"  - 成功下载预览音频: {preview_success}")
        print(f"  - 获取的数据字段: {list(final_df.columns)}")
        
        if spotify_success > 0:
            print("\n✅ 数据获取成功！虽然没有音频特征，但获取了其他有用信息")
            print("\n📊 可用的分析维度:")
            print("  - 流行度分析")
            print("  - 艺术家类型分析") 
            print("  - 发行年份分析")
            print("  - 歌曲时长分析")
            print("  - 预览音频分析（如果有下载成功的）")
        else:
            print("\n⚠️  未能获取Spotify数据，请检查API配置")
        
    except Exception as e:
        print(f"❌ 处理过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
