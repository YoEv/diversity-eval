#!/usr/bin/env python3
"""
修复预览音频问题
分析为什么预览URL为空并提供解决方案
"""

import pandas as pd
import requests
import json
import os
from pathlib import Path

def analyze_preview_issue():
    """分析预览音频问题"""
    print("🔍 分析预览音频问题...")
    
    # 加载数据集
    dataset_path = Path(__file__).parent / "data" / "no_audio_features_output" / "spotify_dataset_no_audio_features.csv"
    df = pd.read_csv(dataset_path)
    
    print(f"📊 数据集信息:")
    print(f"  总歌曲数: {len(df)}")
    print(f"  有Spotify ID的歌曲: {df['spotify_id'].notna().sum()}")
    print(f"  有预览URL的歌曲: {df['preview_url'].notna().sum()}")
    
    # 检查预览URL字段
    print(f"\n🔍 预览URL字段分析:")
    for idx, row in df.iterrows():
        preview_url = row['preview_url']
        print(f"  {row['spotify_name']}: {preview_url if pd.notna(preview_url) else '无预览URL'}")
    
    return df

def test_direct_spotify_api():
    """直接测试Spotify API获取预览URL"""
    print("\n🧪 直接测试Spotify API...")
    
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        
        # 加载配置
        config_path = Path(__file__).parent / "config" / "spotify_config.json"
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
        
        # 测试几首歌
        test_songs = [
            ("Shape of You", "Ed Sheeran"),
            ("Blinding Lights", "The Weeknd"),
            ("Watermelon Sugar", "Harry Styles")
        ]
        
        print("🎵 测试歌曲预览URL获取:")
        for song, artist in test_songs:
            try:
                results = sp.search(q=f"track:{song} artist:{artist}", type='track', limit=1)
                if results['tracks']['items']:
                    track = results['tracks']['items'][0]
                    preview_url = track.get('preview_url')
                    print(f"  {song} - {artist}: {'有预览' if preview_url else '无预览'}")
                else:
                    print(f"  {song} - {artist}: 未找到")
            except Exception as e:
                print(f"  {song} - {artist}: 错误 - {e}")
        
        return True
        
    except ImportError:
        print("❌ spotipy未安装")
        return False
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

def create_enhanced_preview_script():
    """创建增强的预览音频获取脚本"""
    print("\n🔧 创建增强的预览音频获取脚本...")
    
    script_content = '''#!/usr/bin/env python3
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
                    'popularity': track['popularity']
                })
        
        return tracks_with_preview
    except Exception as e:
        print(f"搜索失败: {e}")
        return []

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
    
    # 加载配置和初始化客户端
    config = load_config()
    sp = init_spotify_client(config)
    
    # 创建输出目录
    output_dir = Path(__file__).parent / "data" / "preview_audio"
    output_dir.mkdir(exist_ok=True)
    
    # 搜索策略
    search_queries = [
        "year:2020-2023 pop",
        "year:2019-2022 rock", 
        "year:2018-2023 electronic",
        "year:2020-2023 hip hop",
        "year:2019-2023 indie"
    ]
    
    all_tracks = []
    
    print("🔍 搜索带有预览URL的歌曲...")
    for query in search_queries:
        print(f"搜索: {query}")
        tracks = search_with_preview(sp, query, limit=5)
        all_tracks.extend(tracks)
        time.sleep(1)  # 避免API限制
    
    # 去重
    unique_tracks = {}
    for track in all_tracks:
        if track['id'] not in unique_tracks:
            unique_tracks[track['id']] = track
    
    print(f"\\n找到 {len(unique_tracks)} 首独特的带预览URL的歌曲")
    
    # 下载预览音频
    print("\\n📥 下载预览音频...")
    downloaded = 0
    
    for track_id, track in unique_tracks.items():
        filename = output_dir / f"{track['artist']}_{track['name']}.mp3"
        # 清理文件名
        filename = output_dir / f"{track['artist'].replace('/', '_')}_{track['name'].replace('/', '_')}.mp3"
        
        print(f"下载: {track['name']} - {track['artist']}")
        
        if download_preview(track['preview_url'], filename):
            downloaded += 1
            print(f"  ✅ 成功")
        else:
            print(f"  ❌ 失败")
        
        time.sleep(0.5)  # 避免过快请求
    
    print(f"\\n🎉 下载完成! 成功下载 {downloaded} 个预览音频文件")
    print(f"文件保存在: {output_dir}")

if __name__ == "__main__":
    main()
'''
    
    # 保存脚本
    script_path = Path(__file__).parent / "examples" / "enhanced_preview_search.py"
    script_path.parent.mkdir(exist_ok=True)
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # 设置执行权限
    os.chmod(script_path, 0o755)
    
    print(f"✅ 增强搜索脚本已创建: {script_path}")

def main():
    """主函数"""
    print("🔧 预览音频问题修复工具")
    print("=" * 50)
    
    # 1. 分析当前数据集的预览URL问题
    df = analyze_preview_issue()
    
    # 2. 直接测试Spotify API
    api_works = test_direct_spotify_api()
    
    # 3. 创建增强的预览搜索脚本
    if api_works:
        create_enhanced_preview_script()
        
        print("\n💡 解决方案:")
        print("1. 原始歌曲可能没有预览URL（Spotify政策限制）")
        print("2. 某些地区的预览可能受限")
        print("3. 使用增强搜索脚本查找更多带预览的歌曲")
        print("\n📝 下一步:")
        print("- 运行: python examples/enhanced_preview_search.py")
        print("- 这将搜索并下载更多带预览URL的歌曲")
    else:
        print("\n❌ API连接有问题，请检查配置")

if __name__ == "__main__":
    main()