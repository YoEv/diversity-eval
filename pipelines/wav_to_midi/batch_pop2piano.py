#!/usr/bin/env python3
"""
Batch Pop2Piano Audio to MIDI Converter for GTZAN Dataset
批量Pop2Piano音频转MIDI转换器 - 专用于GTZAN数据集
支持CUDA加速的钢琴伴奏生成
"""

import os
import glob
import librosa
from transformers import Pop2PianoForConditionalGeneration, Pop2PianoProcessor
import torch
import numpy as np
from datetime import datetime
import argparse
from pathlib import Path

def process_audio_directory(input_dir, output_dir, model=None, processor=None, device=None):
    """
    批量处理音频目录，转换为MIDI文件
    
    Args:
        input_dir: 输入音频目录
        output_dir: 输出MIDI目录
        model: Pop2Piano模型（可选，用于复用）
        processor: Pop2Piano处理器（可选，用于复用）
        device: 计算设备（可选）
    """
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 支持的音频格式
    audio_extensions = ['*.mp3', '*.wav', '*.flac', '*.m4a', '*.aac']
    
    # 获取所有音频文件
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(glob.glob(os.path.join(input_dir, ext)))
        audio_files.extend(glob.glob(os.path.join(input_dir, '**', ext), recursive=True))
    
    if not audio_files:
        print(f"❌ 在目录 {input_dir} 中未找到音频文件")
        return []
    
    print(f"🎵 找到 {len(audio_files)} 个音频文件")
    
    # 加载模型（如果未提供）
    if model is None or processor is None:
        print("🔄 加载Pop2Piano模型...")
        model = Pop2PianoForConditionalGeneration.from_pretrained("sweetcocoa/pop2piano")
        processor = Pop2PianoProcessor.from_pretrained("sweetcocoa/pop2piano")
        
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        model = model.to(device)
        print(f"🖥️  使用设备: {device}")
    
    successful_conversions = []
    failed_conversions = []
    
    for i, audio_file in enumerate(audio_files, 1):
        try:
            print(f"\n[{i}/{len(audio_files)}] 处理: {os.path.basename(audio_file)}")
            
            # 生成输出文件名
            audio_name = Path(audio_file).stem
            midi_output_file = os.path.join(output_dir, f"{audio_name}_piano_accompaniment.mid")
            
            # 检查是否已存在
            if os.path.exists(midi_output_file):
                print(f"⏭️  跳过（已存在）: {midi_output_file}")
                successful_conversions.append(midi_output_file)
                continue
            
            # 加载音频
            audio, sr = librosa.load(audio_file, sr=22050)  # Pop2Piano使用22050Hz采样率
            print(f"📊 音频信息: 长度={len(audio)/sr:.2f}秒, 采样率={sr}Hz")
            
            # 预处理音频
            inputs = processor(audio=audio, sampling_rate=sr, return_tensors="pt")
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # 生成钢琴伴奏
            print("🎹 生成钢琴伴奏...")
            with torch.no_grad():
                # 使用与test文件相同的生成参数
                piano_output = model.generate(
                    input_features=inputs["input_features"],
                    composer="composer1",  # 可以选择不同的作曲家风格
                    generation_config=model.generation_config,
                    guidance_scale=1.0,
                    max_length=1024,
                    do_sample=True,
                    temperature=1.0
                )
            
            # 解码为MIDI - 将CUDA张量移动到CPU
            print("🔄 解码MIDI...")
            # 关键修复：将token_ids移动到CPU，并确保inputs也在CPU上
            piano_output_cpu = piano_output.cpu()
            inputs_cpu = {k: v.cpu() for k, v in inputs.items()}
            
            decoded_outputs = processor.batch_decode(
                token_ids=piano_output_cpu,
                feature_extractor_output=inputs_cpu
            )
            
            # 提取MIDI对象
            if "pretty_midi_objects" in decoded_outputs:
                midi_objects = decoded_outputs["pretty_midi_objects"]
                if midi_objects and len(midi_objects) > 0:
                    midi_object = midi_objects[0]
                    print(f"✅ 成功解码MIDI对象: {type(midi_object)}")
                    
                    # 保存MIDI文件
                    midi_object.write(midi_output_file)
                    
                    print(f"✅ 钢琴MIDI生成成功！")
                    print(f"📁 输出文件: {midi_output_file}")
                    print(f"🎼 MIDI文件包含 {len(midi_object.instruments)} 个乐器轨道")
                    print(f"🎵 总时长: {midi_object.get_end_time():.2f}秒")
                    
                    successful_conversions.append(midi_output_file)
                else:
                    print("❌ 解码失败：未生成有效的MIDI对象")
                    failed_conversions.append(audio_file)
            else:
                print("❌ 解码失败：输出中没有MIDI对象")
                failed_conversions.append(audio_file)
                
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            failed_conversions.append(audio_file)
            import traceback
            traceback.print_exc()
    
    return successful_conversions, failed_conversions

def main():
    parser = argparse.ArgumentParser(description='批量将音频文件转换为钢琴伴奏MIDI')
    parser.add_argument('input_dir', help='输入音频目录')
    parser.add_argument('output_dir', help='输出MIDI目录')
    parser.add_argument('--device', choices=['cpu', 'cuda'], help='计算设备')
    
    args = parser.parse_args()
    
    print("🎹 批量Pop2Piano音频转MIDI转换器")
    print("=" * 50)
    print(f"📂 输入目录: {args.input_dir}")
    print(f"📁 输出目录: {args.output_dir}")
    print(f"📅 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not os.path.exists(args.input_dir):
        print(f"❌ 输入目录不存在: {args.input_dir}")
        return
    
    successful, failed = process_audio_directory(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        device=args.device
    )
    
    print("\n" + "=" * 50)
    print("📊 批量转换完成统计:")
    print(f"✅ 成功转换: {len(successful)} 个文件")
    print(f"❌ 转换失败: {len(failed)} 个文件")
    print(f"📅 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if failed:
        print("\n❌ 失败的文件:")
        for f in failed:
            print(f"  - {f}")
    
    print(f"\n📁 输出目录: {args.output_dir}")

if __name__ == "__main__":
    main()