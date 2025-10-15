#!/usr/bin/env python3
"""
批量F0音频合成运行脚本
自动检查JSON文件并运行合成
"""

import os
import subprocess
import time

def check_json_files():
    """
    检查所有JSON结果文件的状态
    """
    json_files = [
        'libf0_yin_results.json',
        'libf0_swipe_results.json', 
        'libf0_salience_results.json'
    ]
    
    print("检查JSON结果文件状态...")
    print("=" * 50)
    
    existing_files = []
    for file_path in json_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✓ {file_path} (大小: {file_size:,} 字节)")
            existing_files.append(file_path)
        else:
            print(f"✗ {file_path} (不存在)")
    
    return existing_files

def run_synthesis(existing_files):
    """
    运行音频合成
    """
    if not existing_files:
        print("\n没有找到任何JSON文件，无法进行合成。")
        return
    
    print(f"\n找到 {len(existing_files)} 个JSON文件，开始合成...")
    print("=" * 50)
    
    # 运行谐波合成（推荐）
    print("\n1. 运行谐波合成（推荐，声音更自然）...")
    cmd_harmonic = [
        'python', 'batch_f0_to_audio.py',
        '--input_files'] + existing_files + [
        '--method', 'harmonic',
        '--output_dir', 'synthesized_audio'
    ]
    
    try:
        result = subprocess.run(cmd_harmonic, capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ 谐波合成完成")
        else:
            print(f"✗ 谐波合成失败: {result.stderr}")
    except Exception as e:
        print(f"✗ 运行谐波合成时出错: {e}")
    
    # 运行正弦波合成
    print("\n2. 运行正弦波合成（简单，文件较小）...")
    cmd_sine = [
        'python', 'batch_f0_to_audio.py',
        '--input_files'] + existing_files + [
        '--method', 'sine',
        '--output_dir', 'synthesized_audio'
    ]
    
    try:
        result = subprocess.run(cmd_sine, capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ 正弦波合成完成")
        else:
            print(f"✗ 正弦波合成失败: {result.stderr}")
    except Exception as e:
        print(f"✗ 运行正弦波合成时出错: {e}")

def show_results():
    """
    显示合成结果
    """
    print("\n检查合成结果...")
    print("=" * 50)
    
    output_dirs = [
        'synthesized_audio/harmonic_synthesized_audio',
        'synthesized_audio/sine_synthesized_audio'
    ]
    
    for output_dir in output_dirs:
        if os.path.exists(output_dir):
            files = [f for f in os.listdir(output_dir) if f.endswith('.wav')]
            print(f"\n{output_dir}:")
            print(f"  生成了 {len(files)} 个音频文件")
            if files:
                for file in sorted(files)[:5]:  # 显示前5个文件
                    file_path = os.path.join(output_dir, file)
                    file_size = os.path.getsize(file_path)
                    print(f"  - {file} ({file_size:,} 字节)")
                if len(files) > 5:
                    print(f"  ... 还有 {len(files) - 5} 个文件")
        else:
            print(f"\n{output_dir}: 目录不存在")

def main():
    print("F0音频合成批处理脚本")
    print("=" * 50)
    
    # 检查JSON文件
    existing_files = check_json_files()
    
    if not existing_files:
        print("\n提示: 请先运行以下命令生成JSON结果文件:")
        print("python libf0_melody_extraction.py --method yin --dataset_path Shutter_Solo_Dataset_15s")
        print("python libf0_melody_extraction.py --method swipe --dataset_path Shutter_Solo_Dataset_15s")
        print("python libf0_melody_extraction.py --method salience --dataset_path Shutter_Solo_Dataset_15s")
        return
    
    # 运行合成
    run_synthesis(existing_files)
    
    # 显示结果
    show_results()
    
    print("\n完成! 您可以在 synthesized_audio/ 目录中找到生成的音频文件。")
    print("\n使用说明:")
    print("- harmonic_synthesized_audio/: 谐波合成音频（推荐，声音更自然）")
    print("- sine_synthesized_audio/: 正弦波合成音频（简单，文件较小）")

if __name__ == '__main__':
    main()