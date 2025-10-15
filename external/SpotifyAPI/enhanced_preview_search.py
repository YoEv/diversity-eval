#!/usr/bin/env python3
"""
增强的预览音频搜索和下载
使用多种策略查找带有预览URL的歌曲
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import requests
import json
from pathlib import Path
import time
import os

def load_config():
    """加载配置"""
    config_path = Path(__file__).parent / "config" / "spotify_config.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def init_spotify_client(config):
    """初始化Spotify客户端"""
    client_id = config["spotify_api"]["client_id"]
    client_secret = config["spotify_api"]["client_secret"]
    
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def search_with_preview(sp, query, limit=10):
    """搜索带有预览URL的歌曲"""
    try:
        results = sp.search(q=query, type='track', limit=limit)
        tracks_with_preview = []
        
        for track in results['tracks']['items']:
            if track['preview_url']:
                tracks_with_preview.append({
                    'id': track['id'],
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'preview_url': track['preview_url'],
                    'popularity': track['popularity'],
                    'album': track['album']['name'],
                    'release_date': track['album']['release_date'],
                    'duration_ms': track['duration_ms']
                })
        
        return tracks_with_preview
    except Exception as e:
        print(f"搜索失败: {e}")
        return []

def clean_filename(filename):
    """清理文件名，移除不合法字符"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def download_preview(url, filename):
    """下载预览音频"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        return True
    except Exception as e:
        print(f"下载失败: {e}")
        return False

def main():
    """主函数"""
    print("🎵 增强预览音频搜索和下载")
    print("=" * 50)
    
    try:
        # 加载配置和初始化客户端
        config = load_config()
        sp = init_spotify_client(config)
        
        # 创建输出目录
        output_dir = Path(__file__).parent / "data" / "preview_audio"
        output_dir.mkdir(exist_ok=True)
        
        # 搜索策略 - 使用更具体的查询来增加找到预览的机会
        search_queries = [
            "year:2020-2023 pop",
            "year:2019-2022 rock", 
            "year:2018-2023 electronic",
            "year:2020-2023 hip hop",
            "year:2019-2023 indie",
            "year:2021-2023 dance",
            "year:2020-2023 alternative",
            "year:2019-2022 R&B"
        ]
        
        all_tracks = []
        
        print("🔍 搜索带有预览URL的歌曲...")
        for query in search_queries:
            print(f"搜索: {query}")
            tracks = search_with_preview(sp, query, limit=10)
            print(f"  找到 {len(tracks)} 首带预览的歌曲")
            all_tracks.extend(tracks)
            time.sleep(1)  # 避免API限制
        
        # 去重
        unique_tracks = {}
        for track in all_tracks:
            if track['id'] not in unique_tracks:
                unique_tracks[track['id']] = track
        
        print(f"\n找到 {len(unique_tracks)} 首独特的带预览URL的歌曲")
        
        if len(unique_tracks) == 0:
            print("❌ 没有找到带预览URL的歌曲")
            print("💡 建议:")
            print("   1. 检查Spotify API权限")
            print("   2. 尝试不同的搜索关键词")
            print("   3. 某些地区的预览可能受限")
            return
        
        # 下载预览音频
        print("\n📥 下载预览音频...")
        downloaded = 0
        
        for track_id, track in list(unique_tracks.items())[:20]:  # 限制下载数量
            # 清理文件名
            artist_clean = clean_filename(track['artist'])
            name_clean = clean_filename(track['name'])
            filename = output_dir / f"{artist_clean}_{name_clean}.mp3"
            
            print(f"下载: {track['name']} - {track['artist']}")
            
            if download_preview(track['preview_url'], filename):
                downloaded += 1
                print(f"  ✅ 成功")
            else:
                print(f"  ❌ 失败")
            
            time.sleep(0.5)  # 避免过快请求
        
        print(f"\n🎉 下载完成! 成功下载 {downloaded} 个预览音频文件")
        print(f"文件保存在: {output_dir}")
        
        # 保存歌曲信息到CSV
        df = pd.DataFrame(list(unique_tracks.values()))
        csv_path = output_dir.parent / "enhanced_preview_dataset.csv"
        df.to_csv(csv_path, index=False)
        print(f"歌曲信息保存到: {csv_path}")
        
        # 显示统计信息
        print(f"\n📊 统计信息:")
        print(f"   总搜索结果: {len(all_tracks)}")
        print(f"   独特歌曲: {len(unique_tracks)}")
        print(f"   成功下载: {downloaded}")
        print(f"   平均流行度: {df['popularity'].mean():.1f}")
        
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()