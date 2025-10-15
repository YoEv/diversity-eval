#!/usr/bin/env python3
"""
处理自定义数据集的脚本
支持CSV文件输入，自动获取Spotify数据
"""

import argparse
import pandas as pd
import sys
from pathlib import Path

# 添加脚本路径
sys.path.append(str(Path(__file__).parent))

from dataset_integration import SpotifyDatasetIntegration

def load_dataset(file_path, title_column=None, artist_column=None):
    """加载数据集"""
    print(f"📂 加载数据集: {file_path}")
    
    try:
        df = pd.read_csv(file_path)
        print(f"✅ 成功加载 {len(df)} 行数据")
        
        # 自动检测列名
        if not title_column:
            possible_title_cols = ['title', 'song', 'track', 'name', 'song_name', 'track_name']
            for col in possible_title_cols:
                if col in df.columns:
                    title_column = col
                    break
        
        if not artist_column:
            possible_artist_cols = ['artist', 'singer', 'performer', 'artist_name']
            for col in possible_artist_cols:
                if col in df.columns:
                    artist_column = col
                    break
        
        if not title_column or not artist_column:
            print("❌ 无法自动检测歌曲标题和艺术家列")
            print(f"可用列: {list(df.columns)}")
            print("请使用 --title-column 和 --artist-column 参数指定")
            return None, None, None
        
        print(f"✅ 检测到列: 标题='{title_column}', 艺术家='{artist_column}'")
        return df, title_column, artist_column
        
    except Exception as e:
        print(f"❌ 加载数据集失败: {e}")
        return None, None, None

def process_dataset(input_file, output_file=None, title_column=None, artist_column=None, 
                   download_previews=True, batch_size=20):
    """处理数据集"""
    
    # 加载数据集
    df, title_col, artist_col = load_dataset(input_file, title_column, artist_column)
    if df is None:
        return False
    
    # 标准化列名
    if title_col != 'title':
        df['title'] = df[title_col]
    if artist_col != 'artist':
        df['artist'] = df[artist_col]
    
    # 初始化Spotify集成
    print("\n🔄 初始化Spotify API集成...")
    integration = SpotifyDatasetIntegration()
    
    # 测试连接
    if not integration.test_spotify_connection():
        print("❌ Spotify API连接失败")
        return False
    
    # 处理数据集
    print(f"\n🎵 开始处理 {len(df)} 首歌曲...")
    enriched_df = integration.enrich_with_spotify_api(
        df,
        download_previews=download_previews,
        batch_size=batch_size,
        delay=0.1
    )
    
    # 保存结果
    if not output_file:
        input_path = Path(input_file)
        output_file = input_path.parent / f"{input_path.stem}_enriched.csv"
    
    enriched_df.to_csv(output_file, index=False)
    print(f"\n💾 结果已保存到: {output_file}")
    
    # 统计信息
    spotify_success = enriched_df['spotify_id'].notna().sum()
    preview_success = enriched_df['local_preview_path'].notna().sum() if 'local_preview_path' in enriched_df.columns else 0
    
    print(f"\n📊 处理结果统计:")
    print(f"  - 总歌曲数: {len(df)}")
    print(f"  - 成功获取Spotify数据: {spotify_success} ({spotify_success/len(df)*100:.1f}%)")
    print(f"  - 成功下载预览音频: {preview_success} ({preview_success/len(df)*100:.1f}%)")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="处理自定义音乐数据集")
    parser.add_argument("input", help="输入CSV文件路径")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("--title-column", help="歌曲标题列名")
    parser.add_argument("--artist-column", help="艺术家列名")
    parser.add_argument("--no-preview", action="store_true", help="不下载预览音频")
    parser.add_argument("--batch-size", type=int, default=20, help="批处理大小")
    
    args = parser.parse_args()
    
    success = process_dataset(
        input_file=args.input,
        output_file=args.output,
        title_column=args.title_column,
        artist_column=args.artist_column,
        download_previews=not args.no_preview,
        batch_size=args.batch_size
    )
    
    if success:
        print("\n✅ 数据集处理完成！")
    else:
        print("\n❌ 数据集处理失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()