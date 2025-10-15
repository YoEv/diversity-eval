#!/usr/bin/env python3
"""
直接测试Spotify API调用
使用curl和requests来验证API访问
"""

import json
import requests
import subprocess
import base64
import os

def load_config():
    """加载Spotify配置"""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'spotify_config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def get_access_token_direct(client_id, client_secret):
    """直接获取访问令牌"""
    print("🔑 获取访问令牌...")
    
    # 编码客户端凭据
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    # 请求访问令牌
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get('access_token')
        print(f"✅ 成功获取访问令牌: {access_token[:20]}...")
        return access_token
    else:
        print(f"❌ 获取访问令牌失败: {response.status_code}")
        print(response.text)
        return None

def test_curl_api(access_token):
    """使用curl测试API"""
    print("\n🌐 使用curl测试API...")
    
    # 测试获取多首歌曲的信息
    track_ids = "7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B"
    url = f"https://api.spotify.com/v1/tracks?market=US&ids={track_ids}"
    
    curl_command = [
        "curl",
        "--request", "GET",
        "--url", url,
        "--header", f"Authorization: Bearer {access_token}",
        "--silent"
    ]
    
    try:
        result = subprocess.run(curl_command, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            response_data = json.loads(result.stdout)
            print("✅ curl请求成功")
            
            tracks = response_data.get('tracks', [])
            print(f"📊 获取到 {len(tracks)} 首歌曲:")
            
            preview_count = 0
            for i, track in enumerate(tracks, 1):
                if track:
                    name = track.get('name', 'Unknown')
                    artists = ', '.join([artist['name'] for artist in track.get('artists', [])])
                    preview_url = track.get('preview_url')
                    popularity = track.get('popularity', 0)
                    
                    print(f"   {i}. {name} - {artists}")
                    print(f"      流行度: {popularity}")
                    if preview_url:
                        print(f"      ✅ 预览URL: {preview_url}")
                        preview_count += 1
                    else:
                        print(f"      ❌ 无预览URL")
                    print()
            
            print(f"📈 找到 {preview_count} 首带预览URL的歌曲")
            return preview_count > 0
            
        else:
            print(f"❌ curl请求失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ curl请求超时")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        print(f"响应内容: {result.stdout}")
        return False
    except Exception as e:
        print(f"❌ curl测试出错: {e}")
        return False

def test_requests_api(access_token):
    """使用requests测试API"""
    print("\n🐍 使用requests测试API...")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # 测试不同市场
    markets = ["US", "GB", "DE", "ES", "FR", "CA", "AU"]
    
    for market in markets:
        print(f"\n🌍 测试市场: {market}")
        
        # 测试一些知名歌曲
        track_ids = "7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B"
        url = f"https://api.spotify.com/v1/tracks?market={market}&ids={track_ids}"
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                tracks = data.get('tracks', [])
                
                preview_count = 0
                for track in tracks:
                    if track and track.get('preview_url'):
                        preview_count += 1
                
                print(f"   状态: ✅ 成功 (找到 {preview_count} 个预览)")
                
                if preview_count > 0:
                    print(f"   🎉 在市场 {market} 找到预览URL!")
                    for i, track in enumerate(tracks, 1):
                        if track and track.get('preview_url'):
                            print(f"      {i}. {track.get('name')} - {track.get('preview_url')}")
                    return True
                    
            else:
                print(f"   状态: ❌ 失败 ({response.status_code})")
                
        except Exception as e:
            print(f"   状态: ❌ 错误 ({e})")
    
    return False

def test_search_api(access_token):
    """测试搜索API"""
    print("\n🔍 测试搜索API...")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # 测试不同的搜索查询
    search_queries = [
        "track:despacito artist:luis fonsi",
        "track:shape of you artist:ed sheeran",
        "track:blinding lights artist:the weeknd",
        "year:2023 genre:pop",
        "year:2022 genre:indie"
    ]
    
    for query in search_queries:
        print(f"\n🎵 搜索: {query}")
        
        url = f"https://api.spotify.com/v1/search?q={query}&type=track&market=US&limit=10"
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                tracks = data.get('tracks', {}).get('items', [])
                
                preview_count = 0
                for track in tracks:
                    if track.get('preview_url'):
                        preview_count += 1
                
                print(f"   找到 {len(tracks)} 首歌曲，{preview_count} 个有预览")
                
                if preview_count > 0:
                    print("   🎉 找到带预览的歌曲:")
                    for track in tracks:
                        if track.get('preview_url'):
                            name = track.get('name')
                            artists = ', '.join([artist['name'] for artist in track.get('artists', [])])
                            preview_url = track.get('preview_url')
                            print(f"      • {name} - {artists}")
                            print(f"        预览: {preview_url}")
                    return True
                    
            else:
                print(f"   ❌ 搜索失败: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 搜索错误: {e}")
    
    return False

def main():
    print("🎵 Spotify API直接测试")
    print("=" * 50)
    
    # 加载配置
    config = load_config()
    client_id = config['spotify_api']['client_id']
    client_secret = config['spotify_api']['client_secret']
    
    # 获取访问令牌
    access_token = get_access_token_direct(client_id, client_secret)
    
    if not access_token:
        print("❌ 无法获取访问令牌，测试终止")
        return
    
    # 测试不同的API调用方法
    results = []
    
    # 1. 测试curl
    print("\n" + "=" * 50)
    curl_success = test_curl_api(access_token)
    results.append(("curl API测试", curl_success))
    
    # 2. 测试requests with different markets
    print("\n" + "=" * 50)
    requests_success = test_requests_api(access_token)
    results.append(("requests API测试", requests_success))
    
    # 3. 测试搜索API
    print("\n" + "=" * 50)
    search_success = test_search_api(access_token)
    results.append(("搜索API测试", search_success))
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试总结:")
    for test_name, success in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"   {test_name}: {status}")
    
    if not any(success for _, success in results):
        print("\n💡 所有测试都没有找到预览URL，可能的原因:")
        print("   1. 地区限制 - 你的地区不支持预览音频")
        print("   2. Spotify政策变化 - 预览功能可能被限制")
        print("   3. 应用权限问题 - 需要检查开发者控制台设置")
        print("   4. 网络问题 - 检查网络连接")
    else:
        print("\n🎉 找到了预览URL! 问题可能在于搜索策略或特定歌曲的限制。")

if __name__ == "__main__":
    main()