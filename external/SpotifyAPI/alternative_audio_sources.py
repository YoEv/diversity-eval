#!/usr/bin/env python3
"""
替代音频源获取脚本
由于Spotify preview_url已被弃用，提供其他音频数据源的解决方案
"""

import json
import requests
import os
import time
from datetime import datetime

def load_config():
    """加载配置"""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'spotify_config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def create_metadata_dataset():
    """创建基于Spotify元数据的数据集（不包含音频）"""
    print("📊 创建Spotify元数据数据集")
    print("=" * 50)
    
    # 这里可以使用Spotify API获取歌曲的元数据
    # 包括音频特征、流派、艺术家信息等
    # 虽然没有预览音频，但可以用于分析音乐多样性
    
    metadata_features = [
        "danceability", "energy", "key", "loudness", "mode",
        "speechiness", "acousticness", "instrumentalness",
        "liveness", "valence", "tempo", "duration_ms"
    ]
    
    print("✅ 可以获取的Spotify元数据特征:")
    for feature in metadata_features:
        print(f"   • {feature}")
    
    print("\n💡 用途:")
    print("   • 音乐多样性分析")
    print("   • 推荐系统训练")
    print("   • 音乐特征研究")
    
    return metadata_features

def suggest_alternative_audio_sources():
    """建议替代的音频数据源"""
    print("\n🎵 替代音频数据源建议")
    print("=" * 50)
    
    alternatives = {
        "免费音频数据集": [
            {
                "name": "Free Music Archive (FMA)",
                "description": "大型免费音乐数据集，包含多种流派",
                "url": "https://github.com/mdeff/fma",
                "size": "~1000小时音频",
                "license": "Creative Commons"
            },
            {
                "name": "Million Song Dataset",
                "description": "百万歌曲的音频特征数据",
                "url": "http://millionsongdataset.com/",
                "size": "1M songs metadata",
                "license": "研究用途"
            },
            {
                "name": "GTZAN Dataset",
                "description": "音乐流派分类数据集",
                "url": "http://marsyas.info/downloads/datasets.html",
                "size": "1000首歌曲，10个流派",
                "license": "研究用途"
            }
        ],
        "API服务": [
            {
                "name": "YouTube Music API",
                "description": "可能提供音频预览",
                "url": "https://developers.google.com/youtube/v3",
                "note": "需要检查ToS"
            },
            {
                "name": "SoundCloud API",
                "description": "部分歌曲有预览",
                "url": "https://developers.soundcloud.com/",
                "note": "有免费tier"
            },
            {
                "name": "Last.fm API",
                "description": "音乐元数据和推荐",
                "url": "https://www.last.fm/api",
                "note": "主要是元数据"
            }
        ],
        "音乐生成": [
            {
                "name": "MusicGen (Meta)",
                "description": "AI音乐生成模型",
                "url": "https://github.com/facebookresearch/musicgen",
                "note": "可生成多样化音乐样本"
            },
            {
                "name": "Jukebox (OpenAI)",
                "description": "神经网络音乐生成",
                "url": "https://github.com/openai/jukebox",
                "note": "高质量音乐生成"
            }
        ]
    }
    
    for category, sources in alternatives.items():
        print(f"\n📂 {category}:")
        for source in sources:
            print(f"   🎯 {source['name']}")
            print(f"      描述: {source['description']}")
            if 'url' in source:
                print(f"      链接: {source['url']}")
            if 'size' in source:
                print(f"      规模: {source['size']}")
            if 'license' in source:
                print(f"      许可: {source['license']}")
            if 'note' in source:
                print(f"      备注: {source['note']}")
            print()
    
    return alternatives

def create_spotify_metadata_collector():
    """创建Spotify元数据收集器"""
    print("\n🔧 创建Spotify元数据收集器")
    print("=" * 50)
    
    collector_code = '''
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import json

def collect_spotify_metadata(search_queries, limit_per_query=50):
    """
    收集Spotify歌曲元数据（不包含音频）
    """
    # 初始化Spotify客户端
    client_credentials_manager = SpotifyClientCredentials(
        client_id="your_client_id",
        client_secret="your_client_secret"
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    all_tracks = []
    
    for query in search_queries:
        print(f"搜索: {query}")
        
        # 搜索歌曲
        results = sp.search(q=query, type='track', limit=limit_per_query)
        tracks = results['tracks']['items']
        
        for track in tracks:
            track_id = track['id']
            
            # 获取音频特征
            try:
                audio_features = sp.audio_features([track_id])[0]
                if audio_features:
                    track_data = {
                        'id': track_id,
                        'name': track['name'],
                        'artist': ', '.join([artist['name'] for artist in track['artists']]),
                        'album': track['album']['name'],
                        'popularity': track['popularity'],
                        'duration_ms': track['duration_ms'],
                        'explicit': track['explicit'],
                        'release_date': track['album']['release_date'],
                        # 音频特征
                        'danceability': audio_features['danceability'],
                        'energy': audio_features['energy'],
                        'key': audio_features['key'],
                        'loudness': audio_features['loudness'],
                        'mode': audio_features['mode'],
                        'speechiness': audio_features['speechiness'],
                        'acousticness': audio_features['acousticness'],
                        'instrumentalness': audio_features['instrumentalness'],
                        'liveness': audio_features['liveness'],
                        'valence': audio_features['valence'],
                        'tempo': audio_features['tempo'],
                        'time_signature': audio_features['time_signature']
                    }
                    all_tracks.append(track_data)
            except Exception as e:
                print(f"获取音频特征失败: {e}")
    
    return pd.DataFrame(all_tracks)

# 使用示例
search_queries = [
    "genre:pop year:2020-2024",
    "genre:rock year:2020-2024", 
    "genre:electronic year:2020-2024",
    "genre:hip-hop year:2020-2024",
    "genre:indie year:2020-2024"
]

df = collect_spotify_metadata(search_queries)
df.to_csv('spotify_metadata_dataset.csv', index=False)
print(f"收集了 {len(df)} 首歌曲的元数据")
'''
    
    # 保存收集器代码
    with open('spotify_metadata_collector.py', 'w', encoding='utf-8') as f:
        f.write(collector_code)
    
    print("✅ 已创建 spotify_metadata_collector.py")
    print("💡 这个脚本可以收集歌曲的音频特征和元数据")
    print("   虽然没有音频文件，但可以用于多样性分析")

def suggest_workflow():
    """建议新的工作流程"""
    print("\n🔄 建议的新工作流程")
    print("=" * 50)
    
    workflow = [
        {
            "step": 1,
            "title": "收集Spotify元数据",
            "description": "使用Spotify API收集歌曲的音频特征和元数据",
            "output": "包含音频特征的CSV文件"
        },
        {
            "step": 2,
            "title": "下载免费音频数据集",
            "description": "从FMA或其他免费数据集获取实际音频文件",
            "output": "音频文件 + 元数据"
        },
        {
            "step": 3,
            "title": "特征匹配",
            "description": "根据音频特征匹配Spotify数据和免费数据集",
            "output": "匹配的音频-元数据对"
        },
        {
            "step": 4,
            "title": "多样性分析",
            "description": "基于音频特征进行多样性评估",
            "output": "多样性评估报告"
        }
    ]
    
    for step_info in workflow:
        print(f"📋 步骤 {step_info['step']}: {step_info['title']}")
        print(f"   描述: {step_info['description']}")
        print(f"   输出: {step_info['output']}")
        print()
    
    return workflow

def main():
    print("🎵 Spotify预览URL替代方案")
    print("=" * 60)
    print("🚨 由于Spotify已弃用preview_url功能，提供以下替代方案:")
    print()
    
    # 1. 创建元数据数据集说明
    metadata_features = create_metadata_dataset()
    
    # 2. 建议替代音频源
    alternatives = suggest_alternative_audio_sources()
    
    # 3. 创建元数据收集器
    create_spotify_metadata_collector()
    
    # 4. 建议新工作流程
    workflow = suggest_workflow()
    
    # 5. 总结建议
    print("\n💡 最终建议:")
    print("=" * 50)
    print("1. 🎯 短期方案: 使用Spotify API收集音频特征数据")
    print("   • 可以进行基于特征的多样性分析")
    print("   • 不需要实际音频文件")
    print()
    print("2. 🎯 中期方案: 结合免费音频数据集")
    print("   • 下载FMA等免费数据集")
    print("   • 基于特征匹配进行分析")
    print()
    print("3. 🎯 长期方案: 探索其他API或生成模型")
    print("   • YouTube Music API")
    print("   • 音乐生成模型")
    print()
    
    # 保存完整报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "issue": "Spotify preview_url deprecated",
        "metadata_features": metadata_features,
        "alternatives": alternatives,
        "workflow": workflow
    }
    
    with open('spotify_alternatives_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("📄 完整报告已保存到: spotify_alternatives_report.json")

if __name__ == "__main__":
    main()