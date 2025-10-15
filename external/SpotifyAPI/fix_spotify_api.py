#!/usr/bin/env python3
"""
Spotify API修复脚本
解决常见的API权限和配置问题
"""

import sys
import os
import json
import time
from pathlib import Path

# 添加脚本路径
sys.path.append(str(Path(__file__).parent / "scripts"))

def fix_config_file():
    """修复配置文件"""
    print("🔧 修复配置文件...")
    
    config_dir = Path(__file__).parent / "config"
    config_path = config_dir / "spotify_config.json"
    template_path = config_dir / "spotify_config_template.json"
    
    if not config_path.exists() and template_path.exists():
        import shutil
        shutil.copy(template_path, config_path)
        print("✅ 已创建spotify_config.json")
    
    # 更新配置以提高成功率
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # 调整API设置以提高成功率
        config["api_settings"] = {
            "rate_limit_delay": 0.5,  # 增加延迟
            "batch_size": 10,         # 减少批次大小
            "max_retries": 5,         # 增加重试次数
            "timeout": 30             # 增加超时时间
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ 已优化API设置")
        return config
    
    return None

def create_robust_dataset_script():
    """创建更稳健的数据集获取脚本"""
    print("🔧 创建稳健的数据集获取脚本...")
    
    script_content = '''#!/usr/bin/env python3
"""
稳健的Spotify数据集获取脚本
包含错误处理和重试机制
"""

import sys
import os
import pandas as pd
import time
from pathlib import Path

# 添加脚本路径
sys.path.append(str(Path(__file__).parent.parent / "scripts"))

from dataset_integration import SpotifyDatasetIntegration

def create_simple_dataset():
    """创建简单的测试数据集"""
    print("🎵 创建简单测试数据集...")
    
    # 使用知名度高的歌曲，更容易获取数据
    sample_tracks = [
        {"title": "Shape of You", "artist": "Ed Sheeran"},
        {"title": "Blinding Lights", "artist": "The Weeknd"},
        {"title": "Watermelon Sugar", "artist": "Harry Styles"},
        {"title": "Levitating", "artist": "Dua Lipa"},
        {"title": "Good 4 U", "artist": "Olivia Rodrigo"}
    ]
    
    df = pd.DataFrame(sample_tracks)
    print(f"✅ 创建了包含 {len(df)} 首歌曲的测试数据集")
    return df

def robust_spotify_enrichment(df):
    """稳健的Spotify数据丰富"""
    print("\\n🔄 使用稳健模式丰富数据集...")
    
    try:
        # 初始化Spotify集成
        integration = SpotifyDatasetIntegration()
        
        # 测试连接
        if not integration.test_spotify_connection():
            print("❌ Spotify连接测试失败")
            return df
        
        print("✅ Spotify连接正常")
        
        # 使用保守的设置丰富数据集
        enriched_df = integration.enrich_with_spotify_api(
            df, 
            download_previews=True,
            batch_size=1,    # 一次处理一首歌
            delay=1.0        # 1秒延迟
        )
        
        return enriched_df
        
    except Exception as e:
        print(f"❌ 数据丰富过程出错: {e}")
        import traceback
        traceback.print_exc()
        return df

def main():
    print("🎵 稳健的Spotify数据集获取")
    print("=" * 50)
    
    # 设置输出目录
    output_dir = Path(__file__).parent.parent / "data" / "robust_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 1. 创建简单数据集
        df = create_simple_dataset()
        
        # 2. 稳健的Spotify数据丰富
        enriched_df = robust_spotify_enrichment(df)
        
        # 3. 保存结果
        output_file = output_dir / "robust_dataset.csv"
        enriched_df.to_csv(output_file, index=False)
        print(f"\\n💾 数据集已保存到: {output_file}")
        
        # 4. 显示统计信息
        spotify_success = enriched_df['spotify_id'].notna().sum() if 'spotify_id' in enriched_df.columns else 0
        preview_success = enriched_df['local_preview_path'].notna().sum() if 'local_preview_path' in enriched_df.columns else 0
        
        print(f"\\n📋 处理结果:")
        print(f"  - 总歌曲数: {len(df)}")
        print(f"  - 成功获取Spotify数据: {spotify_success}")
        print(f"  - 成功下载预览音频: {preview_success}")
        
        if spotify_success > 0:
            print("\\n✅ 部分或全部数据获取成功！")
        else:
            print("\\n⚠️  未能获取Spotify数据，请检查API配置")
        
    except Exception as e:
        print(f"❌ 处理过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
'''
    
    script_path = Path(__file__).parent / "examples" / "robust_dataset_example.py"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # 使脚本可执行
    os.chmod(script_path, 0o755)
    print(f"✅ 已创建稳健数据集脚本: {script_path}")

def main():
    print("🔧 Spotify API修复工具")
    print("=" * 50)
    
    # 1. 修复配置文件
    config = fix_config_file()
    
    # 2. 创建稳健的数据集脚本
    create_robust_dataset_script()
    
    print("\\n✅ 修复完成！")
    print("\\n📋 后续步骤:")
    print("1. 运行诊断脚本: python diagnose_spotify_issues.py")
    print("2. 测试稳健脚本: python examples/robust_dataset_example.py")
    print("3. 如果仍有问题，请检查Spotify应用设置")

if __name__ == "__main__":
    main()