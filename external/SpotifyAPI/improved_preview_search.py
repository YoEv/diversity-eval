#!/usr/bin/env python3
"""
改进的预览音频搜索脚本
使用更广泛的搜索策略
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import requests
import json
from pathlib import Path
import time

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

def search_popular_artists(sp):
    """搜索知名艺术家的歌曲"""
    print("🎤 搜索知名艺术家的歌曲...")
    
    popular_artists = [
        "Taylor Swift", "Ed Sheeran", "The Weeknd", "Billie Eilish",
        "Post Malone", "Ariana Grande", "Drake", "Justin Bieber",
        "Dua Lipa", "Harry Styles", "Olivia Rodrigo", "Bad Bunny"
    ]
    
    all_tracks = []
    
    for artist in popular_artists:
        try:
            print(f"  搜索: {artist}")
            results = sp.search(q=f'artist:"{artist}"', type='track', limit=20)
            
            tracks_with_preview = []
            for track in results['tracks']['items']:
                if track.get('preview_url'):
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
            
            print(f"    找到 {len(tracks_with_preview)} 首带预览的歌曲")
            all_tracks.extend(tracks_with_preview)
            
        except Exception as e:
            print(f"    {artist}: 搜索失败 - {e}")
        
        time.sleep(0.5)
    
    return all_tracks

def search_by_genres(sp):
    """按音乐类型搜索"""
    print("\n🎵 按音乐类型搜索...")
    
    genres = ["pop", "rock", "hip-hop", "electronic", "indie", "country", "R&B", "jazz"]
    all_tracks = []
    
    for genre in genres:
        try:
            print(f"  搜索: {genre}")
            results = sp.search(q=genre, type='track', limit=20)
            
            tracks_with_preview = []
            for track in results['tracks']['items']:
                if track.get('preview_url'):
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
            
            print(f"    找到 {len(tracks_with_preview)} 首带预览的歌曲")
            all_tracks.extend(tracks_with_preview)
            
        except Exception as e:
            print(f"    {genre}: 搜索失败 - {e}")
        
        time.sleep(0.5)
    
    return all_tracks

def search_trending_playlists(sp):
    """搜索热门播放列表中的歌曲"""
    print("\n📋 搜索热门播放列表...")
    
    try:
        # 搜索一些热门播放列表
        playlists = sp.search(q="Today's Top Hits", type='playlist', limit=1)
        
        if playlists['playlists']['items']:
            playlist = playlists['playlists']['items'][0]
            print(f"  找到播放列表: {playlist['name']}")
            
            # 获取播放列表中的歌曲
            tracks = sp.playlist_tracks(playlist['id'], limit=50)
            
            tracks_with_preview = []
            for item in tracks['items']:
                if item['track'] and item['track'].get('preview_url'):
                    track = item['track']
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
            
            print(f"    找到 {len(tracks_with_preview)} 首带预览的歌曲")
            return tracks_with_preview
            
    except Exception as e:
        print(f"    播放列表搜索失败: {e}")
    
    return []

def clean_filename(filename):
    """清理文件名"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename[:100]

def download_preview(url, filename):
    """下载预览音频"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        return True
    except Exception as e:
        return False

def main():
    """主函数"""
    print("🎵 改进的预览音频搜索")
    print("=" * 40)
    
    try:
        # 加载配置和初始化客户端
        config = load_config()
        sp = init_spotify_client(config)
        
        print("✅ Spotify API连接成功")
        
        # 创建输出目录
        output_dir = Path(__file__).parent / "data" / "preview_audio"
        output_dir.mkdir(exist_ok=True)
        
        # 使用多种搜索策略
        all_tracks = []
        
        # 1. 搜索知名艺术家
        artist_tracks = search_popular_artists(sp)
        all_tracks.extend(artist_tracks)
        
        # 2. 按类型搜索
        genre_tracks = search_by_genres(sp)
        all_tracks.extend(genre_tracks)
        
        # 3. 搜索热门播放列表
        playlist_tracks = search_trending_playlists(sp)
        all_tracks.extend(playlist_tracks)
        
        # 去重
        unique_tracks = {}
        for track in all_tracks:
            if track['id'] not in unique_tracks:
                unique_tracks[track['id']] = track
        
        print(f"\n📊 搜索结果:")
        print(f"  总搜索结果: {len(all_tracks)}")
        print(f"  独特歌曲: {len(unique_tracks)}")
        
        if len(unique_tracks) == 0:
            print("\n❌ 没有找到带预览URL的歌曲")
            print("💡 这可能是由于:")
            print("   1. 地区限制 - Spotify在某些地区不提供预览")
            print("   2. API政策变化")
            print("   3. 网络连接问题")
            return
        
        # 按流行度排序
        sorted_tracks = sorted(unique_tracks.values(), key=lambda x: x['popularity'], reverse=True)
        
        # 下载前20首
        print(f"\n📥 下载前 {min(20, len(sorted_tracks))} 首歌曲的预览...")
        downloaded = 0
        
        for i, track in enumerate(sorted_tracks[:20]):
            artist_clean = clean_filename(track['artist'])
            name_clean = clean_filename(track['name'])
            filename = output_dir / f"{i+1:02d}_{artist_clean}_{name_clean}.mp3"
            
            print(f"  {i+1:2d}. {track['name']} - {track['artist']} (流行度: {track['popularity']})")
            
            if download_preview(track['preview_url'], filename):
                downloaded += 1
                print(f"      ✅ 下载成功")
            else:
                print(f"      ❌ 下载失败")
            
            time.sleep(0.5)
        
        print(f"\n🎉 下载完成!")
        print(f"  成功下载: {downloaded} 个预览音频文件")
        print(f"  文件保存在: {output_dir}")
        
        # 保存数据集
        if len(sorted_tracks) > 0:
            df = pd.DataFrame(sorted_tracks)
            csv_path = output_dir.parent / "improved_preview_dataset.csv"
            df.to_csv(csv_path, index=False)
            print(f"  数据集保存到: {csv_path}")
            
            print(f"\n📊 数据集统计:")
            print(f"  歌曲数量: {len(df)}")
            print(f"  平均流行度: {df['popularity'].mean():.1f}")
            print(f"  独特艺术家: {df['artist'].nunique()}")
        
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()