#!/usr/bin/env python3
"""
分析Spotify数据集
提供多样性分析和数据可视化
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json

def load_dataset():
    """加载数据集"""
    print("📊 加载Spotify数据集...")
    
    dataset_path = Path(__file__).parent / "data" / "no_audio_features_output" / "spotify_dataset_no_audio_features.csv"
    
    if not dataset_path.exists():
        print(f"❌ 数据集文件不存在: {dataset_path}")
        return None
    
    df = pd.read_csv(dataset_path)
    print(f"✅ 成功加载数据集，包含 {len(df)} 首歌曲")
    return df

def analyze_basic_stats(df):
    """分析基本统计信息"""
    print("\n📈 基本统计分析")
    print("=" * 50)
    
    # 数据完整性
    print("📋 数据完整性:")
    for col in df.columns:
        non_null_count = df[col].notna().sum()
        percentage = (non_null_count / len(df)) * 100
        print(f"  {col}: {non_null_count}/{len(df)} ({percentage:.1f}%)")
    
    # 数值字段统计
    numeric_cols = ['popularity', 'duration_ms', 'artist_popularity', 'artist_followers']
    available_numeric_cols = [col for col in numeric_cols if col in df.columns and df[col].notna().any()]
    
    if available_numeric_cols:
        print(f"\n📊 数值字段统计:")
        for col in available_numeric_cols:
            data = df[col].dropna()
            if len(data) > 0:
                print(f"  {col}:")
                print(f"    平均值: {data.mean():.2f}")
                print(f"    中位数: {data.median():.2f}")
                print(f"    最小值: {data.min()}")
                print(f"    最大值: {data.max()}")
                print(f"    标准差: {data.std():.2f}")

def analyze_diversity(df):
    """分析音乐多样性"""
    print("\n🎵 音乐多样性分析")
    print("=" * 50)
    
    # 流行度多样性
    if 'popularity' in df.columns and df['popularity'].notna().any():
        popularity_data = df['popularity'].dropna()
        popularity_std = popularity_data.std()
        popularity_range = popularity_data.max() - popularity_data.min()
        
        print(f"🔥 流行度多样性:")
        print(f"  标准差: {popularity_std:.2f}")
        print(f"  范围: {popularity_range}")
        print(f"  变异系数: {popularity_std / popularity_data.mean():.3f}")
        
        # 流行度分类
        def categorize_popularity(pop):
            if pop >= 80: return "非常流行"
            elif pop >= 60: return "流行"
            elif pop >= 40: return "中等"
            elif pop >= 20: return "小众"
            else: return "非常小众"
        
        df['popularity_category'] = df['popularity'].apply(categorize_popularity)
        pop_dist = df['popularity_category'].value_counts()
        print(f"  流行度分布:")
        for category, count in pop_dist.items():
            print(f"    {category}: {count} 首")
    
    # 发行年份多样性
    if 'release_date' in df.columns and df['release_date'].notna().any():
        df['release_year'] = pd.to_datetime(df['release_date']).dt.year
        year_data = df['release_year'].dropna()
        year_range = year_data.max() - year_data.min()
        
        print(f"\n📅 发行年份多样性:")
        print(f"  年份范围: {year_data.min()} - {year_data.max()} ({year_range} 年)")
        print(f"  年份分布:")
        for year, count in year_data.value_counts().sort_index().items():
            print(f"    {year}: {count} 首")
    
    # 歌曲时长多样性
    if 'duration_ms' in df.columns and df['duration_ms'].notna().any():
        duration_data = df['duration_ms'].dropna() / 1000  # 转换为秒
        duration_std = duration_data.std()
        
        print(f"\n⏱️  歌曲时长多样性:")
        print(f"  平均时长: {duration_data.mean():.1f} 秒 ({duration_data.mean()/60:.1f} 分钟)")
        print(f"  时长标准差: {duration_std:.1f} 秒")
        print(f"  最短: {duration_data.min():.1f} 秒")
        print(f"  最长: {duration_data.max():.1f} 秒")
        
        # 时长分类
        def categorize_duration(duration_sec):
            if duration_sec < 120: return "短歌 (<2分钟)"
            elif duration_sec < 180: return "中短 (2-3分钟)"
            elif duration_sec < 240: return "标准 (3-4分钟)"
            elif duration_sec < 300: return "中长 (4-5分钟)"
            else: return "长歌 (>5分钟)"
        
        df['duration_category'] = duration_data.apply(categorize_duration)
        duration_dist = df['duration_category'].value_counts()
        print(f"  时长分布:")
        for category, count in duration_dist.items():
            print(f"    {category}: {count} 首")
    
    # 艺术家多样性
    if 'artist_genres' in df.columns and df['artist_genres'].notna().any():
        print(f"\n🎨 艺术家类型多样性:")
        genres_data = df['artist_genres'].dropna()
        unique_artists = df['spotify_artist'].nunique()
        print(f"  独特艺术家数量: {unique_artists}")
        
        # 提取所有类型
        all_genres = []
        for genres_str in genres_data:
            if genres_str and isinstance(genres_str, str):
                genres = [g.strip() for g in genres_str.split(',')]
                all_genres.extend(genres)
        
        if all_genres:
            genre_counts = pd.Series(all_genres).value_counts()
            print(f"  发现的音乐类型: {len(genre_counts)}")
            print(f"  主要类型:")
            for genre, count in genre_counts.head(10).items():
                print(f"    {genre}: {count} 次")

def create_visualizations(df):
    """创建可视化图表"""
    print("\n📊 创建可视化图表...")
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'SimHei', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 创建输出目录
    viz_dir = Path(__file__).parent / "data" / "visualizations"
    viz_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. 流行度分布
    if 'popularity' in df.columns and df['popularity'].notna().any():
        plt.figure(figsize=(10, 6))
        plt.subplot(2, 2, 1)
        df['popularity'].dropna().hist(bins=10, alpha=0.7, color='skyblue')
        plt.title('Popularity Distribution')
        plt.xlabel('Popularity Score')
        plt.ylabel('Number of Songs')
        
        # 2. 发行年份分布
        if 'release_year' in df.columns:
            plt.subplot(2, 2, 2)
            df['release_year'].dropna().value_counts().sort_index().plot(kind='bar', color='lightgreen')
            plt.title('Release Year Distribution')
            plt.xlabel('Year')
            plt.ylabel('Number of Songs')
            plt.xticks(rotation=45)
        
        # 3. 歌曲时长分布
        if 'duration_ms' in df.columns and df['duration_ms'].notna().any():
            plt.subplot(2, 2, 3)
            duration_min = df['duration_ms'].dropna() / 60000  # 转换为分钟
            duration_min.hist(bins=10, alpha=0.7, color='orange')
            plt.title('Song Duration Distribution')
            plt.xlabel('Duration (minutes)')
            plt.ylabel('Number of Songs')
        
        # 4. 艺术家粉丝数分布
        if 'artist_followers' in df.columns and df['artist_followers'].notna().any():
            plt.subplot(2, 2, 4)
            followers_millions = df['artist_followers'].dropna() / 1000000  # 转换为百万
            followers_millions.hist(bins=10, alpha=0.7, color='pink')
            plt.title('Artist Followers Distribution')
            plt.xlabel('Followers (millions)')
            plt.ylabel('Number of Artists')
        
        plt.tight_layout()
        viz_path = viz_dir / "spotify_dataset_analysis.png"
        plt.savefig(viz_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ 可视化图表已保存到: {viz_path}")

def generate_diversity_report(df):
    """生成多样性报告"""
    print("\n📝 生成多样性报告...")
    
    report = {
        "dataset_summary": {
            "total_songs": len(df),
            "unique_artists": df['spotify_artist'].nunique() if 'spotify_artist' in df.columns else 0,
            "data_completeness": {}
        },
        "diversity_metrics": {},
        "recommendations": []
    }
    
    # 数据完整性
    for col in df.columns:
        non_null_count = df[col].notna().sum()
        percentage = (non_null_count / len(df)) * 100
        report["dataset_summary"]["data_completeness"][col] = {
            "count": int(non_null_count),
            "percentage": round(percentage, 1)
        }
    
    # 多样性指标
    if 'popularity' in df.columns and df['popularity'].notna().any():
        pop_data = df['popularity'].dropna()
        report["diversity_metrics"]["popularity"] = {
            "mean": round(pop_data.mean(), 2),
            "std": round(pop_data.std(), 2),
            "range": int(pop_data.max() - pop_data.min()),
            "coefficient_of_variation": round(pop_data.std() / pop_data.mean(), 3)
        }
    
    if 'duration_ms' in df.columns and df['duration_ms'].notna().any():
        duration_data = df['duration_ms'].dropna() / 1000
        report["diversity_metrics"]["duration"] = {
            "mean_seconds": round(duration_data.mean(), 1),
            "std_seconds": round(duration_data.std(), 1),
            "range_seconds": round(duration_data.max() - duration_data.min(), 1)
        }
    
    if 'release_year' in df.columns and df['release_year'].notna().any():
        year_data = df['release_year'].dropna()
        report["diversity_metrics"]["release_year"] = {
            "earliest": int(year_data.min()),
            "latest": int(year_data.max()),
            "span_years": int(year_data.max() - year_data.min())
        }
    
    # 建议
    if report["diversity_metrics"].get("popularity", {}).get("std", 0) < 10:
        report["recommendations"].append("流行度多样性较低，建议添加更多不同流行度的歌曲")
    
    if report["diversity_metrics"].get("release_year", {}).get("span_years", 0) < 10:
        report["recommendations"].append("发行年份跨度较小，建议添加不同年代的歌曲")
    
    if report["dataset_summary"]["unique_artists"] < len(df) * 0.8:
        report["recommendations"].append("艺术家多样性良好，有重复艺术家")
    
    # 保存报告
    report_dir = Path(__file__).parent / "data" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_path = report_dir / "diversity_analysis_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 多样性报告已保存到: {report_path}")
    return report

def main():
    print("🎵 Spotify数据集分析工具")
    print("=" * 50)
    
    # 1. 加载数据集
    df = load_dataset()
    if df is None:
        return
    
    # 2. 基本统计分析
    analyze_basic_stats(df)
    
    # 3. 多样性分析
    analyze_diversity(df)
    
    # 4. 创建可视化
    try:
        create_visualizations(df)
    except Exception as e:
        print(f"⚠️  可视化创建失败: {e}")
    
    # 5. 生成报告
    report = generate_diversity_report(df)
    
    print("\n" + "=" * 50)
    print("✅ 分析完成！")
    print("\n📋 主要发现:")
    print(f"  - 数据集包含 {len(df)} 首歌曲")
    print(f"  - 独特艺术家: {df['spotify_artist'].nunique()} 位")
    
    if 'popularity' in df.columns and df['popularity'].notna().any():
        pop_data = df['popularity'].dropna()
        print(f"  - 平均流行度: {pop_data.mean():.1f}")
        print(f"  - 流行度多样性: {pop_data.std():.1f} (标准差)")
    
    if 'release_year' in df.columns and df['release_year'].notna().any():
        year_data = df['release_year'].dropna()
        print(f"  - 年份跨度: {year_data.min()}-{year_data.max()}")
    
    print("\n💡 建议:")
    for rec in report.get("recommendations", []):
        print(f"  - {rec}")
    
    if not report.get("recommendations"):
        print("  - 数据集多样性良好！")

if __name__ == "__main__":
    main()