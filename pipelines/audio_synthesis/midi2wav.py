#!/usr/bin/env python3
"""
MIDI to WAV converter using FluidSynth
将MIDI文件转换为WAV音频文件
支持单个文件和批量处理
"""

import os
import sys
import subprocess
import argparse
import glob
import time
from pathlib import Path

def check_fluidsynth():
    """检查FluidSynth是否已安装"""
    try:
        # Python 3.6兼容的写法
        result = subprocess.run(['fluidsynth', '--version'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               universal_newlines=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def midi_to_wav(midi_file, output_file=None, soundfont=None, sample_rate=44100):
    """
    将MIDI文件转换为WAV文件
    
    Args:
        midi_file: 输入的MIDI文件路径
        output_file: 输出的WAV文件路径（可选）
        soundfont: SoundFont文件路径（可选）
        sample_rate: 采样率（默认44100Hz）
    """
    
    # 检查FluidSynth
    if not check_fluidsynth():
        print("❌ FluidSynth未安装！")
        print("请运行: sudo apt-get install fluidsynth")
        return False
    
    # 检查输入文件
    if not os.path.exists(midi_file):
        print(f"❌ MIDI文件不存在: {midi_file}")
        return False
    
    # 设置输出文件名
    if output_file is None:
        midi_path = Path(midi_file)
        output_file = midi_path.with_suffix('.wav')
    
    # 设置SoundFont
    if soundfont is None:
        # 使用当前目录的GeneralUser-GS.sf2
        soundfont = "external/GeneralUser-GS.sf2"
        if not os.path.exists(soundfont):
            print(f"❌ SoundFont文件不存在: {soundfont}")
            print("请确保GeneralUser-GS.sf2文件在当前目录中")
            return False
    
    print(f"🎵 转换MIDI文件: {midi_file}")
    print(f"🔊 输出WAV文件: {output_file}")
    print(f"🎼 使用SoundFont: {soundfont}")
    print(f"📊 采样率: {sample_rate}Hz")
    
    # 构建FluidSynth命令
    cmd = [
        'fluidsynth',
        '-ni',  # 非交互模式
        '-g', '0.5',  # 增益
        '-r', str(sample_rate),  # 采样率
        '-F', str(output_file),  # 输出文件
        str(soundfont),  # SoundFont文件
        str(midi_file)   # MIDI文件
    ]
    
    try:
        print("🔄 开始转换...")
        # Python 3.6兼容的写法
        result = subprocess.run(cmd, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               universal_newlines=True)
        
        if result.returncode == 0:
            print(f"✅ 转换成功！")
            print(f"📁 输出文件: {output_file}")
            
            # 显示文件信息
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
                print(f"📊 文件大小: {file_size:.2f} MB")
            
            return True
        else:
            print(f"❌ 转换失败！")
            print(f"错误信息: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 转换过程中出错: {e}")
        return False

def batch_midi_to_wav(input_dir, output_dir=None, soundfont=None, sample_rate=44100):
    """
    批量将MIDI文件转换为WAV文件
    
    Args:
        input_dir: 输入目录路径或MIDI文件路径模式
        output_dir: 输出目录路径（可选）
        soundfont: SoundFont文件路径（可选）
        sample_rate: 采样率（默认44100Hz）
    """
    
    # 检查FluidSynth
    if not check_fluidsynth():
        print("❌ FluidSynth未安装！")
        print("请运行: sudo apt-get install fluidsynth")
        return False
    
    # 查找MIDI文件
    midi_files = []
    
    if os.path.isdir(input_dir):
        # 如果是目录，查找所有MIDI文件
        midi_extensions = ['*.mid', '*.midi', '*.MID', '*.MIDI']
        for ext in midi_extensions:
            pattern = os.path.join(input_dir, ext)
            midi_files.extend(glob.glob(pattern))
    else:
        # 如果是文件模式，使用glob匹配
        midi_files = glob.glob(input_dir)
    
    if not midi_files:
        print(f"❌ 在指定路径中没有找到MIDI文件: {input_dir}")
        return False
    
    # 设置输出目录
    if output_dir is None:
        if os.path.isdir(input_dir):
            output_dir = input_dir
        else:
            output_dir = os.path.dirname(input_dir) or '.'
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🎼 批量MIDI转WAV转换")
    print("=" * 50)
    print(f"📁 输入路径: {input_dir}")
    print(f"📁 输出目录: {output_dir}")
    print(f"🎵 找到 {len(midi_files)} 个MIDI文件")
    print("=" * 50)
    
    # 批量转换
    successful_conversions = 0
    failed_conversions = 0
    total_start_time = time.time()
    
    for i, midi_file in enumerate(midi_files, 1):
        print(f"\n[{i}/{len(midi_files)}] 处理文件: {os.path.basename(midi_file)}")
        
        # 生成输出文件路径
        midi_filename = Path(midi_file).stem
        output_file = os.path.join(output_dir, f"{midi_filename}.wav")
        
        # 转换单个文件
        if midi_to_wav(midi_file, output_file, soundfont, sample_rate):
            successful_conversions += 1
        else:
            failed_conversions += 1
        
        print("-" * 40)
    
    total_time = time.time() - total_start_time
    
    # 输出统计信息
    print("\n" + "=" * 50)
    print("🎯 批量转换完成!")
    print(f"   总文件数: {len(midi_files)}")
    print(f"   成功转换: {successful_conversions}")
    print(f"   转换失败: {failed_conversions}")
    print(f"   总耗时: {total_time:.2f}秒")
    if len(midi_files) > 0:
        print(f"   平均每个文件: {total_time/len(midi_files):.2f}秒")
    
    if successful_conversions > 0:
        print(f"\n✨ WAV文件已保存到: {output_dir}")
        
        # 显示输出目录内容
        wav_files = glob.glob(os.path.join(output_dir, "*.wav"))
        print(f"   生成的WAV文件数量: {len(wav_files)}")
    
    return successful_conversions > 0

def main():
    parser = argparse.ArgumentParser(description='将MIDI文件转换为WAV音频文件（支持单个文件和批量处理）')
    parser.add_argument('-i', '--input', required=True, help='输入的MIDI文件路径或目录路径')
    parser.add_argument('-o', '--output', help='输出的WAV文件路径或目录路径')
    parser.add_argument('-s', '--soundfont', help='SoundFont文件路径')
    parser.add_argument('-r', '--rate', type=int, default=44100, help='采样率（默认44100Hz）')
    parser.add_argument('-b', '--batch', action='store_true', help='批量处理模式')
    
    args = parser.parse_args()
    
    print("🎹 MIDI转WAV转换器")
    print("=" * 40)
    
    # 判断处理模式
    if args.batch or os.path.isdir(args.input) or '*' in args.input:
        # 批量处理模式
        print("📦 批量处理模式")
        success = batch_midi_to_wav(
            input_dir=args.input,
            output_dir=args.output,
            soundfont=args.soundfont,
            sample_rate=args.rate
        )
    else:
        # 单文件处理模式
        print("📄 单文件处理模式")
        success = midi_to_wav(
            midi_file=args.input,
            output_file=args.output,
            soundfont=args.soundfont,
            sample_rate=args.rate
        )
    
    if success:
        print("\n🎉 转换完成！")
        sys.exit(0)
    else:
        print("\n❌ 转换失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()