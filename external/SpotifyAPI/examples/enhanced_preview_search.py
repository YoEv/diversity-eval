#!/usr/bin/env python3
"""
增强的预览音频获取脚本
使用多种策略获取预览音频
"""

import sys
import os
import pandas as pd
import requests
import json
import time
from pathlib import Path

def enhanced_preview_search():
    """增强的预览音频搜索"""
    print("🎵 增强的预览音频搜索")
    print("=" * 50)
    
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        
        # 加载配置
        config_path = Path(__file__).parent.parent / "config" / "spotify_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        client_id = config["spotify_api"]["client_id"]
        client_secret = config["spotify_api"]["client_secret"]
        
        # 初始化客户端
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        # 测试多种搜索策略
        test_songs = [
            {"title": "Shape of You", "artist": "Ed Sheeran"},
            {"title": "Blinding Lights", "artist": "The Weeknd"},
            {"title": "Watermelon Sugar", "artist": "Harry Styles"},
            {"title": "Levitating", "artist": "Dua Lipa"},
            {"title": "Good 4 U", "artist": "Olivia Rodrigo"}
        ]
        
        results = []
        
        for song in test_songs:
            print(f"\n🔍 搜索: {song['title']} - {song['artist']}")
            
            # 策略1: 精确搜索
            query1 = f"track:\"{song['title']}\" artist:\"{song['artist']}\""
            print(f"  策略1 (精确): {query1}")
            
            try:
                search_results = sp.search(q=query1, type='track', limit=5)
                tracks = search_results['tracks']['items']
                
                if tracks:
                    for i, track in enumerate(tracks):
                        preview_url = track.get('preview_url')
                        print(f"    结果{i+1}: {track['name']} - {track['artists'][0]['name']}")
                        print(f"    预览URL: {preview_url if preview_url else '无'}")
                        
                        if preview_url:
                            results.append({
                                'original_title': song['title'],
                                'original_artist': song['artist'],
                                'spotify_name': track['name'],
                                'spotify_artist': track['artists'][0]['name'],
                                'spotify_id': track['id'],
                                'preview_url': preview_url,
                                'popularity': track['popularity'],
                                'album': track['album']['name'],
                                'release_date': track['album']['release_date']
                            })
                            break
                else:
                    print("    无结果")
                
                # 如果精确搜索没有预览，尝试模糊搜索
                if not tracks or not any(t.get('preview_url') for t in tracks):
                    query2 = f"{song['title']} {song['artist']}"
                    print(f"  策略2 (模糊): {query2}")
                    
                    search_results2 = sp.search(q=query2, type='track', limit=10)
                    tracks2 = search_results2['tracks']['items']
                    
                    for track in tracks2:
                        if track.get('preview_url'):
                            print(f"    找到预览: {track['name']} - {track['artists'][0]['name']}")
                            results.append({
                                'original_title': song['title'],
                                'original_artist': song['artist'],
                                'spotify_name': track['name'],
                                'spotify_artist': track['artists'][0]['name'],
                                'spotify_id': track['id'],
                                'preview_url': track['preview_url'],
                                'popularity': track['popularity'],
                                'album': track['album']['name'],
                                'release_date': track['album']['release_date']
                            })
                            break
                
                time.sleep(0.5)  # 避免API限制
                
            except Exception as e:
                print(f"    搜索错误: {e}")
        
        # 保存结果
        if results:
            df = pd.DataFrame(results)
            output_dir = Path(__file__).parent.parent / "data" / "enhanced_preview_output"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = output_dir / "songs_with_previews.csv"
            df.to_csv(output_file, index=False)
            print(f"\n💾 找到预览的歌曲已保存到: {output_file}")
            
            # 下载预览音频
            download_previews(df, output_dir)
        else:
            print("\n⚠️  未找到任何有预览的歌曲")
        
    except Exception as e:
        print(f"❌ 增强搜索失败: {e}")

def download_previews(df, output_dir):
    """下载预览音频"""
    print("\n📥 下载预览音频...")
    
    preview_dir = output_dir / "preview_audio"
    preview_dir.mkdir(parents=True, exist_ok=True)
    
    downloaded_count = 0
    
    for idx, row in df.iterrows():
        if pd.notna(row['preview_url']) and row['preview_url']:
            try:
                print(f"  下载: {row['spotify_name']}")
                response = requests.get(row['preview_url'], timeout=30)
                
                if response.status_code == 200:
                    filename = f"{row['spotify_id']}_preview.mp3"
                    filepath = preview_dir / filename
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    downloaded_count += 1
                    print(f"    ✅ 成功")
                else:
                    print(f"    ❌ HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ 错误: {e}")
    
    print(f"\n✅ 成功下载 {downloaded_count} 个预览音频文件")

def main():
    enhanced_preview_search()

if __name__ == "__main__":
    main()
