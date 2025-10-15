#!/usr/bin/env python3
"""
简化的MR-MT3测试脚本
用于快速测试Shutter_Solo_Dataset_15s和BJ_Opera_Vocal数据集
"""

import os
import subprocess
import sys
from datetime import datetime

def run_mr_mt3_test(dataset_name, input_dir, output_dir):
    """运行MR-MT3测试"""
    print(f"\n🎼 开始处理数据集: {dataset_name}")
    print(f"📂 输入目录: {input_dir}")
    print(f"📁 输出目录: {output_dir}")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 构建命令
    cmd = [
        "python", "test_mr_mt3.py",
        "--input_dir", input_dir,
        "--output_dir", output_dir
    ]
    
    try:
        # 运行命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {dataset_name} 处理成功")
            print(result.stdout)
        else:
            print(f"❌ {dataset_name} 处理失败")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ 运行错误: {e}")
    
    print(f"⏰ 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """主函数 - 测试多个数据集"""
    
    # 检查当前目录
    if not os.path.basename(os.getcwd()) == "diversity-eval":
        print("❌ 请在diversity-eval目录下运行此脚本")
        sys.exit(1)
    
    # 定义测试数据集
    datasets = [
        {
            "name": "Shutter_Solo_15s",
            "input_dir": "Shutter_Solo_Dataset_15s",
            "output_dir": "mr_mt3_output/shutter_solo_15s"
        },
        {
            "name": "BJ_Opera_Vocal",
            "input_dir": "BJ_Opera_Vocal", 
            "output_dir": "mr_mt3_output/bj_opera_vocal"
        },
        {
            "name": "Shutter_Songs",
            "input_dir": "Shutter_Songs",
            "output_dir": "mr_mt3_output/shutter_songs"
        }
    ]
    
    print("🎼 MR-MT3 批量测试工具")
    print("=" * 50)
    
    # 逐个处理数据集
    for dataset in datasets:
        if os.path.exists(dataset["input_dir"]):
            run_mr_mt3_test(
                dataset["name"],
                dataset["input_dir"], 
                dataset["output_dir"]
            )
        else:
            print(f"⚠️  跳过不存在的数据集: {dataset['input_dir']}")
    
    print("\n🎉 所有测试完成!")

if __name__ == "__main__":
    main()