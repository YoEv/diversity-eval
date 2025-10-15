#!/usr/bin/env python3
"""
全面的Spotify预览URL测试
测试不同地区、不同类型的歌曲和不同的API端点
"""

import json
import requests
import base64
import os
import time
from datetime import datetime

def load_config():
    """加载Spotify配置"""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'spotify_config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def get_access_token(client_id, client_secret):
    """获取访问令牌"""
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print(f"❌ 获取访问令牌失败: {response.status_code}")
        return None

def test_markets_comprehensive(access_token):
    """测试所有主要市场的预览URL可用性"""
    print("🌍 测试不同市场的预览URL可用性")
    print("=" * 60)
    
    # 扩展的市场列表
    markets = [
        "AD", "AE", "AG", "AL", "AM", "AO", "AR", "AT", "AU", "AZ",
        "BA", "BB", "BD", "BE", "BF", "BG", "BH", "BI", "BJ", "BN",
        "BO", "BR", "BS", "BT", "BW", "BY", "BZ", "CA", "CD", "CG",
        "CH", "CI", "CL", "CM", "CO", "CR", "CV", "CW", "CY", "CZ",
        "DE", "DJ", "DK", "DM", "DO", "DZ", "EC", "EE", "EG", "ES",
        "FI", "FJ", "FM", "FR", "GA", "GB", "GD", "GE", "GH", "GM",
        "GN", "GQ", "GR", "GT", "GW", "GY", "HK", "HN", "HR", "HT",
        "HU", "ID", "IE", "IL", "IN", "IQ", "IS", "IT", "JM", "JO",
        "JP", "KE", "KG", "KH", "KI", "KM", "KN", "KR", "KW", "KZ",
        "LA", "LB", "LC", "LI", "LK", "LR", "LS", "LT", "LU", "LV",
        "LY", "MA", "MC", "MD", "ME", "MG", "MH", "MK", "ML", "MN",
        "MO", "MR", "MT", "MU", "MV", "MW", "MX", "MY", "MZ", "NA",
        "NE", "NG", "NI", "NL", "NO", "NP", "NR", "NZ", "OM", "PA",
        "PE", "PG", "PH", "PK", "PL", "PS", "PT", "PW", "PY", "QA",
        "RO", "RS", "RW", "SA", "SB", "SC", "SE", "SG", "SI", "SK",
        "SL", "SM", "SN", "SR", "ST", "SV", "SZ", "TD", "TG", "TH",
        "TJ", "TL", "TN", "TO", "TR", "TT", "TV", "TW", "TZ", "UA",
        "UG", "US", "UY", "UZ", "VC", "VE", "VN", "VU", "WS", "XK",
        "ZA", "ZM", "ZW"
    ]
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # 测试一些知名歌曲
    test_tracks = [
        "4iV5W9uYEdYUVa79Axb7Rh",  # Never Gonna Give You Up - Rick Astley
        "7qiZfU4dY1lWllzX7mPBI3",  # Shape of You - Ed Sheeran
        "6habFhsOp2NvshLv26DqMb",  # Blinding Lights - The Weeknd
        "11dFghVXANMlKmJXsNCbNl",  # Watermelon Sugar - Harry Styles
        "0VjIjW4GlULA7QjNiNhNKN",  # Levitating - Dua Lipa
    ]
    
    results = {}
    
    for i, market in enumerate(markets):
        if i % 20 == 0:  # 每20个市场显示一次进度
            print(f"📊 测试进度: {i}/{len(markets)} 市场")
        
        market_results = {"total": 0, "with_preview": 0, "tracks": []}
        
        # 测试单个歌曲
        track_id = test_tracks[0]  # 使用第一首歌曲作为测试
        url = f"https://api.spotify.com/v1/tracks/{track_id}?market={market}"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                track_data = response.json()
                preview_url = track_data.get('preview_url')
                
                market_results["total"] = 1
                if preview_url:
                    market_results["with_preview"] = 1
                    market_results["tracks"].append({
                        "name": track_data.get('name'),
                        "artist": track_data.get('artists', [{}])[0].get('name'),
                        "preview_url": preview_url
                    })
                
                results[market] = market_results
                
                if preview_url:
                    print(f"🎉 市场 {market}: 找到预览URL!")
                    print(f"   歌曲: {track_data.get('name')} - {track_data.get('artists', [{}])[0].get('name')}")
                    print(f"   预览: {preview_url}")
                    print()
            
            time.sleep(0.1)  # 避免请求过快
            
        except Exception as e:
            print(f"❌ 市场 {market} 测试失败: {e}")
    
    # 总结结果
    print("\n📊 市场测试总结:")
    successful_markets = [market for market, data in results.items() if data["with_preview"] > 0]
    
    if successful_markets:
        print(f"✅ 找到预览URL的市场 ({len(successful_markets)}):")
        for market in successful_markets:
            print(f"   {market}")
    else:
        print("❌ 没有任何市场找到预览URL")
    
    return results

def test_different_track_types(access_token):
    """测试不同类型的歌曲"""
    print("\n🎵 测试不同类型的歌曲")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # 不同类型的歌曲测试
    track_categories = {
        "经典老歌": [
            "4iV5W9uYEdYUVa79Axb7Rh",  # Never Gonna Give You Up - Rick Astley
            "5ChkMS8OtdzJeqyybCc9R5",  # Bohemian Rhapsody - Queen
            "32OlwWuMpZ6b0aN2RZOeMS",  # Sweet Child O' Mine - Guns N' Roses
        ],
        "最新热门": [
            "6habFhsOp2NvshLv26DqMb",  # Blinding Lights - The Weeknd
            "11dFghVXANMlKmJXsNCbNl",  # Watermelon Sugar - Harry Styles
            "0VjIjW4GlULA7QjNiNhNKN",  # Levitating - Dua Lipa
        ],
        "独立音乐": [
            "2plbrEY59IikOBgBGLjaoe",  # Somebody Else - The 1975
            "3CRDbSG3x5Y4y4eMKwKmKR",  # Mr. Brightside - The Killers
            "0e7ipj03S05BNilyu5bRzt",  # Pumped Up Kicks - Foster the People
        ],
        "电子音乐": [
            "4uLU6hMCjMI75M1A2tKUQC",  # Titanium - David Guetta ft. Sia
            "0KKkJNfGyhkQ5aFogxQAPU",  # Clarity - Zedd ft. Foxes
            "5ygDXis42ncn6kYG14lEZG",  # Wake Me Up - Avicii
        ]
    }
    
    results = {}
    
    for category, track_ids in track_categories.items():
        print(f"\n🎼 测试类别: {category}")
        category_results = {"total": 0, "with_preview": 0, "tracks": []}
        
        for track_id in track_ids:
            url = f"https://api.spotify.com/v1/tracks/{track_id}?market=US"
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    track_data = response.json()
                    preview_url = track_data.get('preview_url')
                    name = track_data.get('name', 'Unknown')
                    artist = track_data.get('artists', [{}])[0].get('name', 'Unknown')
                    
                    category_results["total"] += 1
                    
                    if preview_url:
                        category_results["with_preview"] += 1
                        category_results["tracks"].append({
                            "name": name,
                            "artist": artist,
                            "preview_url": preview_url
                        })
                        print(f"   ✅ {name} - {artist}: 有预览")
                    else:
                        print(f"   ❌ {name} - {artist}: 无预览")
                
                time.sleep(0.2)
                
            except Exception as e:
                print(f"   ❌ 测试歌曲 {track_id} 失败: {e}")
        
        results[category] = category_results
        print(f"   📊 {category}: {category_results['with_preview']}/{category_results['total']} 有预览")
    
    return results

def test_search_strategies(access_token):
    """测试不同的搜索策略"""
    print("\n🔍 测试不同的搜索策略")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    search_strategies = [
        ("新发布音乐", "year:2024", "US"),
        ("去年音乐", "year:2023", "US"),
        ("流行音乐", "genre:pop", "US"),
        ("摇滚音乐", "genre:rock", "US"),
        ("电子音乐", "genre:electronic", "US"),
        ("嘻哈音乐", "genre:hip-hop", "US"),
        ("独立音乐", "genre:indie", "US"),
        ("低流行度", "year:2020-2024", "US"),  # 搜索最近但可能不太热门的歌曲
    ]
    
    results = {}
    
    for strategy_name, query, market in search_strategies:
        print(f"\n🎯 策略: {strategy_name} (查询: {query})")
        
        url = f"https://api.spotify.com/v1/search?q={query}&type=track&market={market}&limit=20"
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                tracks = data.get('tracks', {}).get('items', [])
                
                strategy_results = {"total": len(tracks), "with_preview": 0, "tracks": []}
                
                for track in tracks:
                    if track.get('preview_url'):
                        strategy_results["with_preview"] += 1
                        strategy_results["tracks"].append({
                            "name": track.get('name'),
                            "artist": ', '.join([artist['name'] for artist in track.get('artists', [])]),
                            "preview_url": track.get('preview_url'),
                            "popularity": track.get('popularity', 0)
                        })
                
                results[strategy_name] = strategy_results
                
                print(f"   📊 找到 {len(tracks)} 首歌曲，{strategy_results['with_preview']} 首有预览")
                
                if strategy_results["with_preview"] > 0:
                    print("   🎉 找到预览的歌曲:")
                    for track in strategy_results["tracks"][:3]:  # 只显示前3首
                        print(f"      • {track['name']} - {track['artist']} (流行度: {track['popularity']})")
                
            else:
                print(f"   ❌ 搜索失败: {response.status_code}")
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   ❌ 搜索错误: {e}")
    
    return results

def main():
    print("🎵 Spotify预览URL全面测试")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 加载配置
    config = load_config()
    client_id = config['spotify_api']['client_id']
    client_secret = config['spotify_api']['client_secret']
    
    # 获取访问令牌
    access_token = get_access_token(client_id, client_secret)
    
    if not access_token:
        print("❌ 无法获取访问令牌，测试终止")
        return
    
    print(f"✅ 成功获取访问令牌: {access_token[:20]}...")
    
    all_results = {}
    
    # 1. 测试不同类型的歌曲
    track_results = test_different_track_types(access_token)
    all_results["track_types"] = track_results
    
    # 2. 测试搜索策略
    search_results = test_search_strategies(access_token)
    all_results["search_strategies"] = search_results
    
    # 3. 如果前面都没找到预览，测试所有市场（这会比较慢）
    # 修复TypeError: 正确计算总预览数
    total_previews = 0
    for category_data in track_results.values():
        if isinstance(category_data, dict) and "with_preview" in category_data:
            total_previews += category_data.get("with_preview", 0)
    
    for strategy_data in search_results.values():
        if isinstance(strategy_data, dict) and "with_preview" in strategy_data:
            total_previews += strategy_data.get("with_preview", 0)
    
    if total_previews == 0:
        print("\n⚠️  前面的测试都没找到预览URL，开始测试所有市场...")
        print("这可能需要几分钟时间...")
        market_results = test_markets_comprehensive(access_token)
        all_results["markets"] = market_results
    
    # 最终总结
    print("\n" + "=" * 60)
    print("📊 最终测试总结")
    print("=" * 60)
    
    total_found = 0
    for category, results in all_results.items():
        if isinstance(results, dict):
            for subcategory, data in results.items():
                if isinstance(data, dict) and "with_preview" in data:
                    found = data["with_preview"]
                    total = data["total"]
                    total_found += found
                    print(f"{category} - {subcategory}: {found}/{total} 有预览")
    
    if total_found > 0:
        print(f"\n🎉 总共找到 {total_found} 首带预览URL的歌曲!")
        print("💡 建议使用找到预览的类别和策略来构建数据集。")
    else:
        print("\n❌ 没有找到任何预览URL")
        print("\n💡 根据最新信息，这是正常的!")
        print("🚨 Spotify已经弃用了preview_url功能:")
        print("   • 新应用无法使用preview_url")
        print("   • 开发模式的应用也被限制")
        print("   • 只有一些老的生产应用可能还有访问权限")
        print("\n🔄 替代方案:")
        print("   1. 使用其他音乐API (如YouTube Music, SoundCloud)")
        print("   2. 使用音乐生成模型创建样本")
        print("   3. 使用现有的音频数据集")
        print("   4. 申请Spotify的新嵌入方法")
    
    # 保存结果
    results_file = "comprehensive_preview_test_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 详细结果已保存到: {results_file}")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()