#!/usr/bin/env python3
"""
MR-MT3 音频转MIDI测试脚本
基于MR-MT3项目的test.py，适配diversity-eval目录结构
"""

import os
import sys
import argparse
import glob
from pathlib import Path

# 添加MR-MT3路径到系统路径
MR_MT3_PATH = "../MR-MT3"
sys.path.insert(0, MR_MT3_PATH)

try:
    # 导入MR-MT3相关模块
    import torch
    import librosa
    import numpy as np
    from datetime import datetime
    
    # 尝试导入MR-MT3的核心模块
    # 这些导入可能需要根据实际的MR-MT3代码结构调整
    from models import MrMt3Model  # 假设的模型类名
    from utils import audio_to_midi, load_pretrained_model
    
except ImportError as e:
    print(f"❌ 导入MR-MT3模块失败: {e}")
    print("请确保:")
    print("1. MR-MT3文件夹与diversity-eval在同一目录下")
    print("2. 已安装所有必要的依赖")
    print("3. 已激活mr-mt3 conda环境")
    sys.exit(1)

def transcribe_audio_to_midi(audio_file, model, output_dir):
    """
    将单个音频文件转写为MIDI
    
    Args:
        audio_file: 音频文件路径
        model: 预训练的MR-MT3模型
        output_dir: 输出目录
    
    Returns:
        str: 生成的MIDI文件路径
    """
    try:
        print(f"🎵 处理音频: {os.path.basename(audio_file)}")
        
        # 加载音频 (MR-MT3通常使用16kHz采样率)
        audio, sr = librosa.load(audio_file, sr=16000)
        print(f"📊 音频信息: 长度={len(audio)/sr:.2f}秒, 采样率={sr}Hz")
        
        # 使用MR-MT3模型进行转写
        # 这里的具体实现需要根据MR-MT3的实际API调整
        with torch.no_grad():
            midi_data = model.transcribe(audio, sr)
        
        # 保存MIDI文件
        audio_name = Path(audio_file).stem
        midi_file = os.path.join(output_dir, f"{audio_name}.mid")
        
        # 保存MIDI数据 (具体方法需要根据MR-MT3的输出格式调整)
        midi_data.write(midi_file)
        
        print(f"✅ MIDI已保存: {midi_file}")
        return midi_file
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        return None

def batch_transcribe(input_dir, output_dir, model_path=None):
    """
    批量处理音频目录
    
    Args:
        input_dir: 输入音频目录
        output_dir: 输出MIDI目录
        model_path: 预训练模型路径
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 加载预训练模型
    if model_path is None:
        model_path = os.path.join(MR_MT3_PATH, "pretrained", "mr_mt3_model.ckpt")
    
    print(f"🔄 加载模型: {model_path}")
    try:
        model = load_pretrained_model(model_path)
        print("✅ 模型加载成功")
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return
    
    # 查找音频文件
    audio_extensions = ['*.wav', '*.mp3', '*.flac', '*.m4a']
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(glob.glob(os.path.join(input_dir, ext)))
    
    if not audio_files:
        print(f"❌ 在 {input_dir} 中未找到音频文件")
        return
    
    print(f"📁 找到 {len(audio_files)} 个音频文件")
    
    # 批量处理
    successful = 0
    failed = 0
    
    for i, audio_file in enumerate(audio_files, 1):
        print(f"\n[{i}/{len(audio_files)}] 处理: {os.path.basename(audio_file)}")
        
        result = transcribe_audio_to_midi(audio_file, model, output_dir)
        if result:
            successful += 1
        else:
            failed += 1
    
    # 统计结果
    print(f"\n📊 处理完成:")
    print(f"✅ 成功: {successful}")
    print(f"❌ 失败: {failed}")
    print(f"📁 输出目录: {output_dir}")

def main():
    parser = argparse.ArgumentParser(description="MR-MT3 音频转MIDI工具")
    parser.add_argument("--input_dir", required=True, help="输入音频目录")
    parser.add_argument("--output_dir", required=True, help="输出MIDI目录")
    parser.add_argument("--model_path", help="预训练模型路径 (可选)")
    
    args = parser.parse_args()
    
    # 检查输入目录
    if not os.path.exists(args.input_dir):
        print(f"❌ 输入目录不存在: {args.input_dir}")
        return
    
    # 检查MR-MT3目录
    if not os.path.exists(MR_MT3_PATH):
        print(f"❌ MR-MT3目录不存在: {MR_MT3_PATH}")
        print("请确保MR-MT3文件夹与diversity-eval在同一目录下")
        return
    
    print("🎼 MR-MT3 音频转MIDI工具")
    print(f"📂 输入目录: {args.input_dir}")
    print(f"📁 输出目录: {args.output_dir}")
    print(f"🔗 MR-MT3路径: {MR_MT3_PATH}")
    
    batch_transcribe(args.input_dir, args.output_dir, args.model_path)

if __name__ == "__main__":
    main()