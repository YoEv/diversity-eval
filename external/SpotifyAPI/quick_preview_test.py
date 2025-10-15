#!/usr/bin/env python3
"""
快速预览URL测试脚本
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
from pathlib import Path

def main():
    print("🔍 快速预览URL测试")
    print("=" * 30)
    
    try:
        # 加载配置
        config_path = Path(__file__).parent / "config" / "spotify_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # 初始化客户端
        client_id = config["spotify_api"]["client_id"]
        client_secret = config["spotify_api"]["client_secret"]
        
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        print("✅ Spotify API连接成功")
        
        # 测试知名歌曲
        test_songs = [
            "Shape of You Ed Sheeran",
            "Blinding Lights The Weeknd", 
            "Bad Guy Billie Eilish",
            "Watermelon Sugar Harry Styles",
            "Circles Post Malone"
        ]
        
        print("\n🎵 测试知名歌曲预览:")
        preview_found = 0
        
        for song in test_songs:
            try:
                results = sp.search(q=song, type='track', limit=1)
                if results['tracks']['items']:
                    track = results['tracks']['items'][0]
                    preview_url = track.get('preview_url')
                    
                    if preview_url:
                        preview_found += 1
                        print(f"  ✅ {track['name']} - {track['artists'][0]['name']}: 有预览")
                    else:
                        print(f"  ❌ {track['name']} - {track['artists'][0]['name']}: 无预览")
                else:
                    print(f"  🔍 {song}: 未找到")
            except Exception as e:
                print(f"  ❌ {song}: 错误 - {e}")
        
        print(f"\n📊 结果: {preview_found}/{len(test_songs)} 首歌有预览")
        
        # 测试简单搜索
        print("\n🔍 测试简单搜索:")
        simple_queries = ["pop", "rock", "Taylor Swift", "Ed Sheeran"]
        
        for query in simple_queries:
            try:
                results = sp.search(q=query, type='track', limit=10)
                with_preview = [t for t in results['tracks']['items'] if t.get('preview_url')]
                print(f"  {query}: {len(with_preview)}/10 首有预览")
                
                if with_preview:
                    print(f"    例如: {with_preview[0]['name']} - {with_preview[0]['artists'][0]['name']}")
                    
            except Exception as e:
                print(f"  {query}: 错误 - {e}")
        
        if preview_found == 0:
            print("\n❌ 没有找到任何预览URL")
            print("💡 可能的原因:")
            print("   1. 地区限制")
            print("   2. Spotify政策变化") 
            print("   3. 网络问题")
        else:
            print(f"\n✅ 找到了 {preview_found} 个预览URL")
            print("💡 建议使用更广泛的搜索策略")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()