#!/usr/bin/env python3
"""
下载GTZAN音乐流派分类数据集
使用kagglehub下载数据集到data/input/GTZAN_Dataset目录
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def install_kagglehub():
    """检查kagglehub是否可用，不在脚本内安装以避免配额问题"""
    print("🔧 检查kagglehub...")
    try:
        import kagglehub
        print("✅ kagglehub已安装")
        return True
    except ImportError:
        print("❌ 未检测到kagglehub。请使用当前解释器手动安装：")
        print(f"   {sys.executable} -m pip install --cache-dir=$HOME/scratch/.cache kagglehub")
        return False

def download_gtzan_dataset(target_dir):
    """下载GTZAN数据集到可用空间（优先使用scratch）"""
    print("🎵 开始下载GTZAN数据集...")
    print("=" * 50)

    cache_root = Path.home() / "scratch" / ".cache"
    tmp_root = Path.home() / "scratch" / "tmp"
    try:
        cache_root.mkdir(parents=True, exist_ok=True)
        tmp_root.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault("XDG_CACHE_HOME", str(cache_root))
        os.environ.setdefault("XDG_CONFIG_HOME", str(cache_root / "config"))
        os.environ.setdefault("XDG_DATA_HOME", str(cache_root / "data"))
        os.environ.setdefault("TMPDIR", str(tmp_root))
    except Exception:
        pass

    # 确保kagglehub已安装
    if not install_kagglehub():
        return None

    try:
        import kagglehub
        print("📥 正在从Kaggle下载GTZAN数据集...")
        print("⏳ 这可能需要几分钟时间，请耐心等待...")
        path = kagglehub.dataset_download("andradaolteanu/gtzan-dataset-music-genre-classification")
        print("✅ 数据集下载完成!")
        print(f"📁 下载路径: {path}")
        return path
    except Exception as e:
        print(f"❌ kagglehub 下载失败: {e}")
        kaggle_cli = shutil.which("kaggle")
        if kaggle_cli:
            try:
                target_dir = Path(target_dir)
                target_dir.mkdir(parents=True, exist_ok=True)
                os.environ.setdefault("KAGGLE_CONFIG_DIR", str(Path.home() / "scratch" / ".kaggle"))
                subprocess.check_call([
                    kaggle_cli, "datasets", "download",
                    "-d", "andradaolteanu/gtzan-dataset-music-genre-classification",
                    "-p", str(target_dir),
                    "-unzip",
                ])
                print(f"✅ Kaggle CLI 下载完成: {target_dir}")
                return str(target_dir)
            except Exception as e2:
                print(f"❌ Kaggle CLI 下载失败: {e2}")
                return None
        else:
            print("⚠️ 未检测到 kaggle CLI。请在计算节点配置好 ~/.kaggle/token 后再试，或手动下载到 scratch。")
            return None

def organize_dataset(download_path, target_dir):
    """整理数据集到目标目录"""
    print("\n🗂️  整理数据集...")
    print("=" * 50)

    target_dir = Path(target_dir)
    print(f"📂 目标目录: {target_dir}")
    target_dir.mkdir(parents=True, exist_ok=True)

    download_path = Path(download_path)
    
    try:
        print("📋 复制文件...")
        
        # 查找下载的文件
        if download_path.is_dir():
            # 复制整个目录内容
            for item in download_path.iterdir():
                if item.is_dir():
                    shutil.copytree(item, target_dir / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, target_dir / item.name)
        else:
            print(f"⚠️  下载路径不是目录: {download_path}")
            return False
        
        print("✅ 数据集整理完成!")
        
        # 显示目录结构
        print("\n📊 数据集结构:")
        for root, dirs, files in os.walk(target_dir):
            level = root.replace(str(target_dir), '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files[:5]:  # 只显示前5个文件
                print(f"{subindent}{file}")
            if len(files) > 5:
                print(f"{subindent}... 还有 {len(files) - 5} 个文件")
        
        return True
        
    except Exception as e:
        print(f"❌ 整理数据集失败: {e}")
        return False

def analyze_dataset(target_dir):
    """分析数据集内容"""
    print("\n📊 分析GTZAN数据集...")
    print("=" * 50)
    
    target_dir = Path(target_dir)
    
    if not target_dir.exists():
        print("❌ 数据集目录不存在")
        return
    
    # 统计文件
    audio_files = []
    genres = set()
    
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.wav', '.mp3', '.au')):
                audio_files.append(os.path.join(root, file))
                # 尝试从路径中提取流派信息
                path_parts = Path(root).parts
                for part in path_parts:
                    if part in ['blues', 'classical', 'country', 'disco', 'hiphop', 
                               'jazz', 'metal', 'pop', 'reggae', 'rock']:
                        genres.add(part)
    
    print(f"🎵 总音频文件数: {len(audio_files)}")
    print(f"🎭 音乐流派数: {len(genres)}")
    
    if genres:
        print("🎼 包含的流派:")
        for genre in sorted(genres):
            genre_files = [f for f in audio_files if genre in f]
            print(f"   • {genre}: {len(genre_files)} 首")
    
    # 检查文件格式
    formats = {}
    for file in audio_files:
        ext = Path(file).suffix.lower()
        formats[ext] = formats.get(ext, 0) + 1
    
    print("\n📁 文件格式分布:")
    for fmt, count in formats.items():
        print(f"   • {fmt}: {count} 个文件")
    
    return {
        "total_files": len(audio_files),
        "genres": list(genres),
        "formats": formats,
        "sample_files": audio_files[:5]
    }

def create_dataset_info(target_dir):
    """创建数据集信息文件"""
    print("\n📄 创建数据集信息文件...")

    target_dir = Path(target_dir)

    info = {
        "dataset_name": "GTZAN Music Genre Classification Dataset",
        "source": "Kaggle - andradaolteanu/gtzan-dataset-music-genre-classification",
        "description": "音乐流派分类数据集，包含10个流派，每个流派100首歌曲",
        "genres": ["blues", "classical", "country", "disco", "hiphop", 
                   "jazz", "metal", "pop", "reggae", "rock"],
        "total_tracks": 1000,
        "track_length": "30秒",
        "sample_rate": "22050 Hz",
        "format": "WAV",
        "use_cases": [
            "音乐流派分类",
            "音频特征提取",
            "音乐多样性分析",
            "机器学习训练"
        ],
        "download_date": None,
        "local_path": str(target_dir)
    }
    
    # 保存信息文件
    import json
    from datetime import datetime
    
    info["download_date"] = datetime.now().isoformat()
    
    info_file = target_dir / "dataset_info.json"
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 数据集信息已保存到: {info_file}")
    
    return info

def main():
    print("🎵 GTZAN音乐流派数据集下载器")
    print("=" * 60)
    print("📋 这个脚本将数据集保存到scratch目录: ~/scratch/datasets/GTZAN_Dataset")
    print()

    scratch_base = Path.home() / "scratch" / "datasets"
    target_dir = scratch_base / "GTZAN_Dataset"

    download_path = download_gtzan_dataset(target_dir)
    if not download_path:
        print("❌ 数据集下载失败，程序退出")
        return False

    if not organize_dataset(download_path, target_dir):
        print("❌ 数据集整理失败")
        return False

    analysis = analyze_dataset(target_dir)
    info = create_dataset_info(target_dir)

    print("\n🎉 GTZAN数据集下载和设置完成!")
    print("=" * 60)
    print(f"📁 数据集位置: {target_dir}")
    print(f"🎵 音频文件数: {analysis['total_files']}")
    print(f"🎭 音乐流派数: {len(analysis['genres'])}")
    print()
    print("💡 接下来你可以:")
    print("   1. 使用这个数据集进行音乐多样性分析")
    print("   2. 提取音频特征")
    print("   3. 训练音乐分类模型")
    print("   4. 与现有的BJ Opera数据集进行对比分析")

    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ 脚本执行成功!")
        else:
            print("\n❌ 脚本执行失败!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  用户中断了下载过程")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生未预期的错误: {e}")
        sys.exit(1)