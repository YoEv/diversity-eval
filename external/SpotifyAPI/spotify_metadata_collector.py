
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
