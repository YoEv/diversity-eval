#!/usr/bin/env python3
"""
Spotify预览URL问题诊断和修复脚本
专门解决预览音频获取问题
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

def test_popular_songs_preview(sp):
    """测试热门歌曲的预览URL可用性"""
    print("🎵 测试热门歌曲预览URL...")
    
    # 知名歌曲列表
    popular_songs = [
        ("Shape of You", "Ed Sheeran"),
        ("Blinding Lights", "The Weeknd"),
        ("Watermelon Sugar", "Harry Styles"),
        ("Bad Guy", "Billie Eilish"),
        ("Someone You Loved", "Lewis Capaldi"),
        ("Sunflower", "Post Malone"),
        ("Old Town Road", "Lil Nas X"),
        ("Señorita", "Shawn Mendes"),
        ("Thank U, Next", "Ariana Grande"),
        ("Circles", "Post Malone")
    ]
    
    preview_count = 0
    total_count = 0
    
    for song, artist in popular_songs:
        try:
            results = sp.search(q=f'track:"{song}" artist:"{artist}"', type='track', limit=1)
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                preview_url = track.get('preview_url')
                total_count += 1
                
                if preview_url:
                    preview_count += 1
                    print(f"  ✅ {song} - {artist}: 有预览")
                else:
                    print(f"  ❌ {song} - {artist}: 无预览")
            else:
                print(f"  🔍 {song} - {artist}: 未找到")
                
        except Exception as e:
            print(f"  ❌ {song} - {artist}: 搜索失败 - {e}")
        
        time.sleep(0.5)  # 避免API限制
    
    print(f"\n📊 预览URL统计: {preview_count}/{total_count} ({preview_count/total_count*100:.1f}%)")
    return preview_count > 0

def test_different_search_strategies(sp):
    """测试不同的搜索策略"""
    print("\n🔍 测试不同搜索策略...")
    
    strategies = [
        ("简单流行音乐", "pop"),
        ("最新热门", "year:2023"),
        ("流行+高人气", "pop popularity:>80"),
        ("摇滚音乐", "rock"),
        ("电子音乐", "electronic"),
        ("嘻哈音乐", "hip hop"),
        ("独立音乐", "indie"),
        ("舞曲", "dance"),
        ("R&B", "R&B"),
        ("乡村音乐", "country")
    ]
    
    total_with_preview = 0
    
    for name, query in strategies:
        try:
            results = sp.search(q=query, type='track', limit=20)
            tracks_with_preview = [t for t in results['tracks']['items'] if t.get('preview_url')]
            
            print(f"  {name}: {len(tracks_with_preview)}/20 首有预览")
            total_with_preview += len(tracks_with_preview)
            
            # 显示几个有预览的例子
            if tracks_with_preview:
                for track in tracks_with_preview[:2]:
                    print(f"    - {track['name']} by {track['artists'][0]['name']}")
                    
        except Exception as e:
            print(f"  {name}: 搜索失败 - {e}")
        
        time.sleep(0.5)
    
    print(f"\n📊 总计找到 {total_with_preview} 首带预览的歌曲")
    return total_with_preview > 0

def test_regional_availability(sp):
    """测试地区可用性"""
    print("\n🌍 测试地区可用性...")
    
    try:
        # 搜索一些国际热门歌曲
        results = sp.search(q="track:Despacito artist:Luis Fonsi", type='track', limit=1)
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            available_markets = track.get('available_markets', [])
            preview_url = track.get('preview_url')
            
            print(f"  歌曲: {track['name']}")
            print(f"  可用市场数量: {len(available_markets)}")
            print(f"  预览URL: {'有' if preview_url else '无'}")
            
            # 检查一些主要市场
            major_markets = ['US', 'GB', 'CA', 'AU', 'DE', 'FR', 'JP', 'CN']
            available_major = [m for m in major_markets if m in available_markets]
            print(f"  主要市场可用: {available_major}")
            
    except Exception as e:
        print(f"  地区测试失败: {e}")

def create_improved_search_script():
    """创建改进的搜索脚本"""
    print("\n🔧 创建改进的预览搜索脚本...")
    
    script_content = '''#!/usr/bin/env python3
"""
改进的预览音频搜索脚本
使用更广泛的搜索策略和更好的错误处理
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

def search_with_multiple_strategies(sp, limit_per_strategy=10):
    """使用多种策略搜索"""
    print("🔍 使用多种策略搜索带预览的歌曲...")
    
    # 更广泛的搜索策略
    strategies = [
        "pop",
        "rock", 
        "electronic",
        "hip hop",
        "indie",
        "dance",
        "alternative",
        "R&B",
        "country",
        "jazz",
        "year:2020-2024",
        "year:2018-2022",
        "popularity:>70",
        "popularity:>50",
        "genre:pop",
        "genre:rock",
        "artist:Taylor Swift",
        "artist:Ed Sheeran",
        "artist:The Weeknd",
        "artist:Billie Eilish"
    ]
    
    all_tracks = []
    
    for strategy in strategies:
        try:
            print(f"  搜索策略: {strategy}")
            results = sp.search(q=strategy, type='track', limit=limit_per_strategy)
            
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
                        'search_strategy': strategy
                    })
            
            print(f"    找到 {len(tracks_with_preview)} 首带预览的歌曲")
            all_tracks.extend(tracks_with_preview)
            
        except Exception as e:
            print(f"    策略 {strategy} 失败: {e}")
        
        time.sleep(0.3)  # 避免API限制
    
    return all_tracks

def clean_filename(filename):
    """清理文件名"""
    invalid_chars = '<>:"/\\\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename[:100]  # 限制文件名长度

def download_preview(url, filename):
    """下载预览音频"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        return True
    except Exception as e:
        print(f"    下载失败: {e}")
        return False

def main():
    """主函数"""
    print("🎵 改进的预览音频搜索和下载")
    print("=" * 50)
    
    try:
        # 加载配置和初始化客户端
        config = load_config()
        sp = init_spotify_client(config)
        
        # 创建输出目录
        output_dir = Path(__file__).parent / "data" / "preview_audio"
        output_dir.mkdir(exist_ok=True)
        
        # 搜索带预览的歌曲
        all_tracks = search_with_multiple_strategies(sp, limit_per_strategy=15)
        
        # 去重
        unique_tracks = {}
        for track in all_tracks:
            if track['id'] not in unique_tracks:
                unique_tracks[track['id']] = track
        
        print(f"\\n📊 搜索结果:")
        print(f"  总搜索结果: {len(all_tracks)}")
        print(f"  独特歌曲: {len(unique_tracks)}")
        
        if len(unique_tracks) == 0:
            print("❌ 没有找到带预览URL的歌曲")
            print("💡 可能的原因:")
            print("   1. 地区限制 - 某些地区的预览可能不可用")
            print("   2. API权限问题")
            print("   3. Spotify政策变化")
            return
        
        # 按流行度排序，优先下载热门歌曲
        sorted_tracks = sorted(unique_tracks.values(), key=lambda x: x['popularity'], reverse=True)
        
        # 下载预览音频
        print(f"\\n📥 开始下载前 {min(20, len(sorted_tracks))} 首歌曲的预览...")
        downloaded = 0
        
        for i, track in enumerate(sorted_tracks[:20]):
            # 清理文件名
            artist_clean = clean_filename(track['artist'])
            name_clean = clean_filename(track['name'])
            filename = output_dir / f"{i+1:02d}_{artist_clean}_{name_clean}.mp3"
            
            print(f"  {i+1:2d}. {track['name']} - {track['artist']} (流行度: {track['popularity']})")
            
            if download_preview(track['preview_url'], filename):
                downloaded += 1
                print(f"      ✅ 下载成功")
            else:
                print(f"      ❌ 下载失败")
            
            time.sleep(0.5)  # 避免过快请求
        
        print(f"\\n🎉 下载完成!")
        print(f"  成功下载: {downloaded} 个预览音频文件")
        print(f"  文件保存在: {output_dir}")
        
        # 保存歌曲信息到CSV
        df = pd.DataFrame(sorted_tracks)
        csv_path = output_dir.parent / "improved_preview_dataset.csv"
        df.to_csv(csv_path, index=False)
        print(f"  歌曲信息保存到: {csv_path}")
        
        # 显示统计信息
        if len(df) > 0:
            print(f"\\n📊 数据集统计:")
            print(f"  歌曲数量: {len(df)}")
            print(f"  平均流行度: {df['popularity'].mean():.1f}")
            print(f"  流行度范围: {df['popularity'].min()} - {df['popularity'].max()}")
            print(f"  发行年份范围: {df['release_date'].min()[:4]} - {df['release_date'].max()[:4]}")
            print(f"  独特艺术家: {df['artist'].nunique()}")
        
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
'''
    
    script_path = Path(__file__).parent / "improved_preview_search.py"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # 设置执行权限
    import os
    os.chmod(script_path, 0o755)
    
    print(f"✅ 改进的搜索脚本已创建: {script_path}")
    return script_path

def main():
    """主诊断函数"""
    print("🔍 Spotify预览URL问题诊断")
    print("=" * 50)
    
    try:
        # 加载配置和初始化客户端
        config = load_config()
        sp = init_spotify_client(config)
        
        print("✅ Spotify API连接成功")
        
        # 运行各种测试
        has_preview_popular = test_popular_songs_preview(sp)
        has_preview_search = test_different_search_strategies(sp)
        test_regional_availability(sp)
        
        # 总结和建议
        print("\n" + "=" * 50)
        print("📋 诊断总结:")
        
        if has_preview_popular or has_preview_search:
            print("✅ 找到了一些带预览URL的歌曲")
            print("💡 建议: 使用改进的搜索策略")
            
            # 创建改进的搜索脚本
            script_path = create_improved_search_script()
            print(f"\\n🚀 运行改进的搜索脚本:")
            print(f"   python {script_path}")
            
        else:
            print("❌ 没有找到任何带预览URL的歌曲")
            print("💡 可能的原因和解决方案:")
            print("   1. 地区限制 - 尝试使用VPN或不同的网络")
            print("   2. Spotify政策变化 - 预览可能在某些地区不可用")
            print("   3. API应用设置 - 检查开发者控制台的应用状态")
            print("   4. 账户限制 - 确保开发者账户状态正常")
        
    except Exception as e:
        print(f"❌ 诊断失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()