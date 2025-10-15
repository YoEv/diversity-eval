#!/usr/bin/env python3
"""
直接测试Spotify API端点
验证预览URL获取方法
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
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

def get_access_token(config):
    """获取访问令牌"""
    client_id = config["spotify_api"]["client_id"]
    client_secret = config["spotify_api"]["client_secret"]
    
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    
    token_info = client_credentials_manager.get_access_token()
    return token_info['access_token']

def test_direct_api_calls(access_token):
    """直接测试API调用"""
    print("🌐 直接测试API端点...")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # 测试你提到的track ID
    test_track_id = "3AhXZa8sUQht0UEdBJgpGc"
    
    print(f"\n🎵 测试歌曲ID: {test_track_id}")
    
    # 1. 测试获取单个歌曲信息
    print("1. 测试获取单个歌曲信息...")
    track_url = f"https://api.spotify.com/v1/tracks/{test_track_id}"
    response = requests.get(track_url, headers=headers)
    
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        track_data = response.json()
        print(f"   歌曲名: {track_data['name']}")
        print(f"   艺术家: {track_data['artists'][0]['name']}")
        print(f"   预览URL: {track_data.get('preview_url', 'None')}")
        print(f"   流行度: {track_data.get('popularity', 'None')}")
        
        if track_data.get('preview_url'):
            print("   ✅ 找到预览URL!")
            return track_data
        else:
            print("   ❌ 没有预览URL")
    else:
        print(f"   ❌ 请求失败: {response.text}")
    
    # 2. 测试音频特征API
    print("\n2. 测试音频特征API...")
    audio_features_url = f"https://api.spotify.com/v1/audio-features/{test_track_id}"
    response = requests.get(audio_features_url, headers=headers)
    
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        audio_data = response.json()
        print(f"   ✅ 音频特征获取成功")
        print(f"   能量: {audio_data.get('energy', 'None')}")
        print(f"   舞蹈性: {audio_data.get('danceability', 'None')}")
    else:
        print(f"   ❌ 音频特征获取失败: {response.text}")
    
    return None

def test_artist_top_tracks(sp, access_token):
    """测试艺术家热门歌曲API"""
    print("\n🎤 测试艺术家热门歌曲...")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # 搜索一个艺术家
    results = sp.search(q="Ed Sheeran", type='artist', limit=1)
    if results['artists']['items']:
        artist = results['artists']['items'][0]
        artist_id = artist['id']
        
        print(f"艺术家: {artist['name']} (ID: {artist_id})")
        
        # 使用API获取热门歌曲
        top_tracks_url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=US"
        response = requests.get(top_tracks_url, headers=headers)
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            tracks = data['tracks']
            
            print(f"找到 {len(tracks)} 首热门歌曲:")
            tracks_with_preview = []
            
            for i, track in enumerate(tracks[:5]):  # 只显示前5首
                preview_url = track.get('preview_url')
                print(f"  {i+1}. {track['name']} - 预览: {'有' if preview_url else '无'}")
                
                if preview_url:
                    tracks_with_preview.append(track)
            
            return tracks_with_preview
        else:
            print(f"❌ 获取热门歌曲失败: {response.text}")
    
    return []

def test_album_tracks(sp, access_token):
    """测试专辑歌曲API"""
    print("\n💿 测试专辑歌曲...")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # 搜索一个专辑
    results = sp.search(q="÷ Ed Sheeran", type='album', limit=1)
    if results['albums']['items']:
        album = results['albums']['items'][0]
        album_id = album['id']
        
        print(f"专辑: {album['name']} by {album['artists'][0]['name']}")
        
        # 使用API获取专辑歌曲
        album_tracks_url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
        response = requests.get(album_tracks_url, headers=headers)
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            tracks = data['items']
            
            print(f"专辑包含 {len(tracks)} 首歌曲:")
            tracks_with_preview = []
            
            # 获取每首歌的完整信息（包含预览URL）
            for i, track in enumerate(tracks[:5]):  # 只测试前5首
                track_url = f"https://api.spotify.com/v1/tracks/{track['id']}"
                track_response = requests.get(track_url, headers=headers)
                
                if track_response.status_code == 200:
                    full_track = track_response.json()
                    preview_url = full_track.get('preview_url')
                    print(f"  {i+1}. {full_track['name']} - 预览: {'有' if preview_url else '无'}")
                    
                    if preview_url:
                        tracks_with_preview.append(full_track)
                
                time.sleep(0.2)  # 避免API限制
            
            return tracks_with_preview
        else:
            print(f"❌ 获取专辑歌曲失败: {response.text}")
    
    return []

def test_multiple_tracks(access_token):
    """测试批量获取歌曲信息"""
    print("\n📦 测试批量获取歌曲...")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # 测试多个歌曲ID
    track_ids = [
        "3AhXZa8sUQht0UEdBJgpGc",  # 你提供的ID
        "4VqPOruhp5EdPBeR92t6lQ",  # Uptown Funk
        "0VjIjW4GlULA4LGvWeEY5u",  # Blinding Lights
        "6DCZcSspjsKoFjzjrWoCdn",  # God's Plan
        "2takcwOaAZWiXQijPHIx7B"   # Time After Time
    ]
    
    # 批量获取
    ids_param = ",".join(track_ids)
    tracks_url = f"https://api.spotify.com/v1/tracks?ids={ids_param}"
    response = requests.get(tracks_url, headers=headers)
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        tracks = data['tracks']
        
        print(f"批量获取 {len(tracks)} 首歌曲:")
        tracks_with_preview = []
        
        for i, track in enumerate(tracks):
            if track:  # 有些ID可能无效
                preview_url = track.get('preview_url')
                print(f"  {i+1}. {track['name']} - {track['artists'][0]['name']}")
                print(f"      预览: {'有' if preview_url else '无'}")
                
                if preview_url:
                    tracks_with_preview.append(track)
                    print(f"      预览URL: {preview_url[:50]}...")
        
        return tracks_with_preview
    else:
        print(f"❌ 批量获取失败: {response.text}")
    
    return []

def download_and_test_preview(track):
    """下载并测试预览音频"""
    print(f"\n📥 测试下载预览: {track['name']}")
    
    preview_url = track['preview_url']
    
    try:
        response = requests.get(preview_url, timeout=30)
        response.raise_for_status()
        
        # 保存到临时文件
        output_dir = Path(__file__).parent / "data" / "preview_audio"
        output_dir.mkdir(exist_ok=True)
        
        filename = output_dir / f"test_{track['name'].replace(' ', '_')[:20]}.mp3"
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        file_size = len(response.content)
        print(f"✅ 下载成功!")
        print(f"   文件大小: {file_size} bytes")
        print(f"   保存位置: {filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return False

def main():
    """主函数"""
    print("🔍 Spotify API端点测试")
    print("=" * 40)
    
    try:
        # 加载配置
        config = load_config()
        sp = init_spotify_client(config)
        access_token = get_access_token(config)
        
        print("✅ API连接成功")
        
        # 测试各种API端点
        all_tracks_with_preview = []
        
        # 1. 直接API调用
        track = test_direct_api_calls(access_token)
        if track:
            all_tracks_with_preview.append(track)
        
        # 2. 艺术家热门歌曲
        artist_tracks = test_artist_top_tracks(sp, access_token)
        all_tracks_with_preview.extend(artist_tracks)
        
        # 3. 专辑歌曲
        album_tracks = test_album_tracks(sp, access_token)
        all_tracks_with_preview.extend(album_tracks)
        
        # 4. 批量获取
        multiple_tracks = test_multiple_tracks(access_token)
        all_tracks_with_preview.extend(multiple_tracks)
        
        # 总结结果
        print(f"\n📊 测试总结:")
        print(f"找到 {len(all_tracks_with_preview)} 首带预览URL的歌曲")
        
        if all_tracks_with_preview:
            print("\n🎵 带预览URL的歌曲:")
            for i, track in enumerate(all_tracks_with_preview[:5]):
                print(f"  {i+1}. {track['name']} - {track['artists'][0]['name']}")
            
            # 测试下载第一首
            if all_tracks_with_preview:
                download_and_test_preview(all_tracks_with_preview[0])
        else:
            print("\n❌ 没有找到任何带预览URL的歌曲")
            print("💡 这可能表明:")
            print("   1. 地区限制 - 你的地区可能不支持预览")
            print("   2. API权限问题")
            print("   3. Spotify政策变化")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()