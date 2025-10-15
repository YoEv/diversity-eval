#!/usr/bin/env python3
"""
小众艺术家预览音频搜索脚本
专门搜索独立音乐人和小众艺术家的歌曲
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import requests
import json
from pathlib import Path
import time
import random

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

def search_indie_artists(sp):
    """搜索独立音乐人"""
    print("🎸 搜索独立音乐人...")
    
    # 小众和独立艺术家
    indie_artists = [
        "Phoebe Bridgers", "Clairo", "Boy Pablo", "Rex Orange County",
        "Mac DeMarco", "Tame Impala", "The 1975", "Arctic Monkeys",
        "Vampire Weekend", "Foster the People", "MGMT", "Two Door Cinema Club",
        "Phoenix", "Passion Pit", "Empire of the Sun", "Cut Copy",
        "Grimes", "FKA twigs", "James Blake", "Bon Iver",
        "Sufjan Stevens", "Fleet Foxes", "Animal Collective", "Beach House",
        "Alvvays", "Japanese Breakfast", "Snail Mail", "Soccer Mommy",
        "Mitski", "Lorde", "Lana Del Rey", "Mazzy Star"
    ]
    
    all_tracks = []
    
    for artist in indie_artists:
        try:
            print(f"  搜索: {artist}")
            results = sp.search(q=f'artist:"{artist}"', type='track', limit=15)
            
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
                        'duration_ms': track['duration_ms'],
                        'category': 'indie_artist'
                    })
            
            print(f"    找到 {len(tracks_with_preview)} 首带预览的歌曲")
            all_tracks.extend(tracks_with_preview)
            
        except Exception as e:
            print(f"    {artist}: 搜索失败 - {e}")
        
        time.sleep(0.3)
    
    return all_tracks

def search_underground_genres(sp):
    """搜索地下音乐类型"""
    print("\n🎵 搜索地下音乐类型...")
    
    underground_genres = [
        "lo-fi", "bedroom pop", "dream pop", "shoegaze", "post-punk",
        "indie folk", "indie rock", "indie pop", "chillwave", "synthwave",
        "vaporwave", "ambient", "experimental", "noise pop", "garage rock",
        "psych rock", "math rock", "emo", "slowcore", "sadcore"
    ]
    
    all_tracks = []
    
    for genre in underground_genres:
        try:
            print(f"  搜索: {genre}")
            results = sp.search(q=f'genre:"{genre}"', type='track', limit=15)
            
            tracks_with_preview = []
            for track in results['tracks']['items']:
                if track.get('preview_url') and track['popularity'] < 70:  # 过滤掉太热门的
                    tracks_with_preview.append({
                        'id': track['id'],
                        'name': track['name'],
                        'artist': track['artists'][0]['name'],
                        'preview_url': track['preview_url'],
                        'popularity': track['popularity'],
                        'album': track['album']['name'],
                        'release_date': track['album']['release_date'],
                        'duration_ms': track['duration_ms'],
                        'category': f'underground_{genre}'
                    })
            
            print(f"    找到 {len(tracks_with_preview)} 首带预览的歌曲")
            all_tracks.extend(tracks_with_preview)
            
        except Exception as e:
            print(f"    {genre}: 搜索失败 - {e}")
        
        time.sleep(0.3)
    
    return all_tracks

def search_new_releases(sp):
    """搜索新发布的音乐"""
    print("\n🆕 搜索新发布的音乐...")
    
    try:
        # 获取新发布的专辑
        new_releases = sp.new_releases(limit=20)
        all_tracks = []
        
        for album in new_releases['albums']['items']:
            try:
                print(f"  检查专辑: {album['name']} - {album['artists'][0]['name']}")
                
                # 获取专辑中的歌曲
                tracks = sp.album_tracks(album['id'], limit=10)
                
                tracks_with_preview = []
                for track in tracks['items']:
                    # 获取完整的歌曲信息（包含预览URL）
                    full_track = sp.track(track['id'])
                    if full_track.get('preview_url'):
                        tracks_with_preview.append({
                            'id': full_track['id'],
                            'name': full_track['name'],
                            'artist': full_track['artists'][0]['name'],
                            'preview_url': full_track['preview_url'],
                            'popularity': full_track['popularity'],
                            'album': full_track['album']['name'],
                            'release_date': full_track['album']['release_date'],
                            'duration_ms': full_track['duration_ms'],
                            'category': 'new_release'
                        })
                
                print(f"    找到 {len(tracks_with_preview)} 首带预览的歌曲")
                all_tracks.extend(tracks_with_preview)
                
            except Exception as e:
                print(f"    专辑处理失败: {e}")
            
            time.sleep(0.5)
        
        return all_tracks
        
    except Exception as e:
        print(f"  新发布音乐搜索失败: {e}")
        return []

def search_low_popularity_tracks(sp):
    """搜索低流行度歌曲"""
    print("\n📉 搜索低流行度歌曲...")
    
    # 使用一些通用关键词，但限制流行度
    keywords = [
        "acoustic", "cover", "demo", "live", "session", "unplugged",
        "remix", "instrumental", "piano", "guitar", "vocals", "original"
    ]
    
    all_tracks = []
    
    for keyword in keywords:
        try:
            print(f"  搜索: {keyword}")
            results = sp.search(q=keyword, type='track', limit=20)
            
            tracks_with_preview = []
            for track in results['tracks']['items']:
                # 只选择流行度较低的歌曲
                if track.get('preview_url') and track['popularity'] < 50:
                    tracks_with_preview.append({
                        'id': track['id'],
                        'name': track['name'],
                        'artist': track['artists'][0]['name'],
                        'preview_url': track['preview_url'],
                        'popularity': track['popularity'],
                        'album': track['album']['name'],
                        'release_date': track['album']['release_date'],
                        'duration_ms': track['duration_ms'],
                        'category': f'low_popularity_{keyword}'
                    })
            
            print(f"    找到 {len(tracks_with_preview)} 首带预览的歌曲")
            all_tracks.extend(tracks_with_preview)
            
        except Exception as e:
            print(f"    {keyword}: 搜索失败 - {e}")
        
        time.sleep(0.3)
    
    return all_tracks

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
    print("🎵 小众艺术家预览音频搜索")
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
        
        # 1. 搜索独立艺术家
        indie_tracks = search_indie_artists(sp)
        all_tracks.extend(indie_tracks)
        
        # 2. 搜索地下音乐类型
        underground_tracks = search_underground_genres(sp)
        all_tracks.extend(underground_tracks)
        
        # 3. 搜索新发布的音乐
        new_tracks = search_new_releases(sp)
        all_tracks.extend(new_tracks)
        
        # 4. 搜索低流行度歌曲
        low_pop_tracks = search_low_popularity_tracks(sp)
        all_tracks.extend(low_pop_tracks)
        
        # 去重
        unique_tracks = {}
        for track in all_tracks:
            if track['id'] not in unique_tracks:
                unique_tracks[track['id']] = track
        
        print(f"\n📊 搜索结果:")
        print(f"  总搜索结果: {len(all_tracks)}")
        print(f"  独特歌曲: {len(unique_tracks)}")
        
        if len(unique_tracks) == 0:
            print("\n❌ 仍然没有找到带预览URL的歌曲")
            print("💡 这可能表明:")
            print("   1. 你所在的地区Spotify不提供预览URL")
            print("   2. API应用可能需要特殊权限")
            print("   3. 网络连接问题")
            return
        
        # 按流行度排序（优先选择中等流行度的）
        sorted_tracks = sorted(unique_tracks.values(), key=lambda x: abs(x['popularity'] - 30))
        
        # 显示找到的歌曲类别统计
        categories = {}
        for track in sorted_tracks:
            cat = track['category'].split('_')[0]
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\n📈 按类别统计:")
        for cat, count in categories.items():
            print(f"  {cat}: {count} 首")
        
        # 下载前25首
        download_count = min(25, len(sorted_tracks))
        print(f"\n📥 下载前 {download_count} 首歌曲的预览...")
        downloaded = 0
        
        for i, track in enumerate(sorted_tracks[:download_count]):
            artist_clean = clean_filename(track['artist'])
            name_clean = clean_filename(track['name'])
            filename = output_dir / f"{i+1:02d}_{artist_clean}_{name_clean}.mp3"
            
            print(f"  {i+1:2d}. {track['name']} - {track['artist']}")
            print(f"      流行度: {track['popularity']}, 类别: {track['category']}")
            
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
            csv_path = output_dir.parent / "indie_preview_dataset.csv"
            df.to_csv(csv_path, index=False)
            print(f"  数据集保存到: {csv_path}")
            
            print(f"\n📊 数据集统计:")
            print(f"  歌曲数量: {len(df)}")
            print(f"  平均流行度: {df['popularity'].mean():.1f}")
            print(f"  流行度范围: {df['popularity'].min()} - {df['popularity'].max()}")
            print(f"  独特艺术家: {df['artist'].nunique()}")
            print(f"  最早发行: {df['release_date'].min()}")
            print(f"  最新发行: {df['release_date'].max()}")
        
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()