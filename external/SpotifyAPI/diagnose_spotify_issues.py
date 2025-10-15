#!/usr/bin/env python3
"""
Spotify API问题诊断脚本
帮助识别和解决API权限和配置问题
"""

import sys
import os
import json
import requests
from pathlib import Path

# 添加脚本路径
sys.path.append(str(Path(__file__).parent / "scripts"))

def check_config():
    """检查配置文件"""
    print("🔍 检查Spotify配置...")
    
    config_dir = Path(__file__).parent / "config"
    config_path = config_dir / "spotify_config.json"
    template_path = config_dir / "spotify_config_template.json"
    
    if not config_path.exists():
        if template_path.exists():
            print("⚠️  spotify_config.json不存在，正在从模板创建...")
            import shutil
            shutil.copy(template_path, config_path)
            print("✅ 已创建spotify_config.json")
        else:
            print("❌ 配置文件不存在")
            return None
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    client_id = config.get("spotify_api", {}).get("client_id")
    client_secret = config.get("spotify_api", {}).get("client_secret")
    
    if not client_id or not client_secret:
        print("❌ API凭据未配置")
        return None
    
    print(f"✅ 配置文件存在，Client ID: {client_id[:8]}...")
    return config

def test_spotify_auth(config):
    """测试Spotify认证"""
    print("\n🔐 测试Spotify API认证...")
    
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        
        client_id = config["spotify_api"]["client_id"]
        client_secret = config["spotify_api"]["client_secret"]
        
        # 创建认证管理器
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        
        # 创建Spotify客户端
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        # 测试基本搜索
        print("🔍 测试基本搜索...")
        result = sp.search(q="test", type="track", limit=1)
        print("✅ 基本搜索成功")
        
        # 测试获取特定歌曲信息
        print("🔍 测试获取歌曲信息...")
        if result['tracks']['items']:
            track_id = result['tracks']['items'][0]['id']
            track_info = sp.track(track_id)
            print(f"✅ 获取歌曲信息成功: {track_info['name']}")
            
            # 测试音频特征
            print("🔍 测试音频特征获取...")
            try:
                audio_features = sp.audio_features([track_id])
                if audio_features and audio_features[0]:
                    print("✅ 音频特征获取成功")
                    return True, track_id
                else:
                    print("⚠️  音频特征返回空值")
                    return False, track_id
            except Exception as e:
                print(f"❌ 音频特征获取失败: {e}")
                return False, track_id
        
        return True, None
        
    except ImportError:
        print("❌ spotipy库未安装")
        return False, None
    except Exception as e:
        print(f"❌ 认证失败: {e}")
        return False, None

def test_direct_api_call(config, track_id):
    """直接测试API调用"""
    print(f"\n🌐 直接测试API调用 (Track ID: {track_id})...")
    
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        
        client_id = config["spotify_api"]["client_id"]
        client_secret = config["spotify_api"]["client_secret"]
        
        # 获取访问令牌
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        
        token_info = client_credentials_manager.get_access_token()
        access_token = token_info['access_token']
        
        # 直接调用API
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # 测试音频特征API
        url = f"https://api.spotify.com/v1/audio-features/{track_id}"
        response = requests.get(url, headers=headers)
        
        print(f"API响应状态码: {response.status_code}")
        print(f"API响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ 直接API调用成功")
            data = response.json()
            print(f"音频特征数据: {list(data.keys())}")
            return True
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 直接API调用异常: {e}")
        return False

def check_app_permissions():
    """检查应用权限设置"""
    print("\n📋 检查Spotify应用权限...")
    print("请确认您的Spotify应用设置:")
    print("1. 登录 https://developer.spotify.com/dashboard")
    print("2. 选择您的应用")
    print("3. 检查以下设置:")
    print("   - App Status: 应该是 'In Development' 或 'Live'")
    print("   - Users and Access: 确保您的账户在用户列表中")
    print("   - Settings > Basic Information: 确认Client ID和Secret正确")
    print("4. 如果是新应用，可能需要等待几分钟才能生效")

def suggest_solutions():
    """建议解决方案"""
    print("\n💡 可能的解决方案:")
    print("1. 检查Spotify应用状态和权限")
    print("2. 确认Client ID和Client Secret正确")
    print("3. 检查网络连接")
    print("4. 尝试创建新的Spotify应用")
    print("5. 检查是否有API使用限制")
    print("6. 等待几分钟后重试（新应用可能需要时间生效）")

def main():
    print("🔧 Spotify API问题诊断工具")
    print("=" * 50)
    
    # 1. 检查配置
    config = check_config()
    if not config:
        print("❌ 配置检查失败，请先配置API凭据")
        return
    
    # 2. 测试认证
    auth_success, track_id = test_spotify_auth(config)
    
    if auth_success and track_id:
        # 3. 测试直接API调用
        api_success = test_direct_api_call(config, track_id)
        
        if not api_success:
            check_app_permissions()
            suggest_solutions()
    else:
        check_app_permissions()
        suggest_solutions()
    
    print("\n" + "=" * 50)
    print("诊断完成")

if __name__ == "__main__":
    main()