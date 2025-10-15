#!/usr/bin/env python3
"""
批量转换GTZAN数据集pop音乐文件为MIDI
输入: data/input/GTZAN_Dataset/Data/genres_original/pop
输出: data/output/midi_output/gtzan_bpt
基于basic-pitch-torch项目
"""

import os
import glob
import time
from pathlib import Path
import sys

# 添加basic-pitch-torch路径
sys.path.append("/home/evev/diversity-eval/external/basic-pitch-torch")
from basic_pitch_torch.inference import predict

def convert_audio_to_midi(audio_path, output_dir):
    """
    将单个音频文件转换为MIDI
    
    Args:
        audio_path: 音频文件路径
        output_dir: 输出目录
    
    Returns:
        转换是否成功
    """
    try:
        print(f"🎵 正在处理: {os.path.basename(audio_path)}")
        start_time = time.time()
        
        # 调用predict函数进行转换
        model_output, midi_data, note_events = predict(
            audio_path=audio_path,
            model_path="/home/evev/diversity-eval/external/basic-pitch-torch/assets/basic_pitch_pytorch_icassp_2022.pth",
            onset_threshold=0.5,
            frame_threshold=0.3,
            minimum_note_length=127.70,  # 毫秒
            midi_tempo=120
        )
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成输出文件名
        audio_filename = Path(audio_path).stem
        midi_output_path = os.path.join(output_dir, f"{audio_filename}_bpt.mid")
        
        # 保存MIDI文件
        midi_data.write(midi_output_path)
        
        processing_time = time.time() - start_time
        print(f"   ✅ 成功转换: {audio_filename}")
        print(f"   输出文件: {midi_output_path}")
        print(f"   处理时间: {processing_time:.2f}秒")
        print(f"   检测到音符数量: {len(note_events)}")
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"   ❌ 转换失败: {os.path.basename(audio_path)}")
        print(f"   错误信息: {str(e)}")
        print("-" * 50)
        return False

def batch_convert_gtzan_melody():
    """
    批量转换GTZAN数据集pop音乐文件为MIDI
    """
    # 输入和输出路径
    input_dir = "/home/evev/diversity-eval/data/input/GTZAN_Dataset/Solo/genres_original/pop"
    output_dir = "/home/evev/diversity-eval/data/output/midi_output/gtzan_bpt_solo"
    
    print("🎼 Basic Pitch PyTorch - GTZAN Pop音乐转MIDI")
    print("=" * 60)
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    
    # 检查输入目录
    if not os.path.exists(input_dir):
        print(f"❌ 输入目录不存在: {input_dir}")
        print("请确保GTZAN数据集已正确下载并解压到指定位置")
        return
    
    # 支持的音频格式
    audio_extensions = ['*.mp3', '*.wav', '*.flac', '*.m4a', '*.aac']
    
    # 查找所有音频文件
    audio_files = []
    for ext in audio_extensions:
        pattern = os.path.join(input_dir, ext)
        audio_files.extend(glob.glob(pattern))
    
    if not audio_files:
        print(f"❌ 在输入目录中没有找到音频文件")
        print("支持的格式: {', '.join(audio_extensions)}")
        return
    
    print(f"🎵 找到 {len(audio_files)} 个音频文件:")
    for i, file in enumerate(audio_files, 1):
        print(f"   {i}. {os.path.basename(file)}")
    print("=" * 60)
    
    # 检查模型文件
    model_path = "/home/evev/diversity-eval/external/basic-pitch-torch/assets/basic_pitch_pytorch_icassp_2022.pth"
    if not os.path.exists(model_path):
        print(f"❌ 模型文件不存在: {model_path}")
        print("请确保basic-pitch-torch模型权重文件已下载")
        return
    
    print(f"✅ 模型文件存在: {model_path}")
    print("=" * 60)
    
    # 批量转换
    successful_conversions = 0
    failed_conversions = 0
    total_start_time = time.time()
    
    for i, audio_file in enumerate(audio_files, 1):
        print(f"[{i}/{len(audio_files)}] 转换文件...")
        
        if convert_audio_to_midi(audio_file, output_dir):
            successful_conversions += 1
        else:
            failed_conversions += 1
    
    total_time = time.time() - total_start_time
    
    # 输出统计信息
    print("=" * 60)
    print("🎯 批量转换完成!")
    print(f"   总文件数: {len(audio_files)}")
    print(f"   成功转换: {successful_conversions}")
    print(f"   转换失败: {failed_conversions}")
    print(f"   总耗时: {total_time:.2f}秒")
    if len(audio_files) > 0:
        print(f"   平均每个文件: {total_time/len(audio_files):.2f}秒")
    
    if successful_conversions > 0:
        print(f"\n✨ MIDI文件已保存到: {output_dir}")
        
        # 显示输出目录内容
        if os.path.exists(output_dir):
            midi_files = glob.glob(os.path.join(output_dir, "*.mid"))
            print(f"   生成的MIDI文件数量: {len(midi_files)}")

def test_single_file():
    """
    测试单个文件的转换（用于调试）
    """
    input_dir = "/home/evev/diversity-eval/data/input/GTZAN_Dataset/Data/genres_original/pop"
    test_files = glob.glob(os.path.join(input_dir, "*.wav"))
    
    if test_files:
        test_file = test_files[0]
        output_dir = "/home/evev/diversity-eval/data/output/midi_output/gtzan_bpt"
        
        print(f"🧪 测试单个文件转换: {os.path.basename(test_file)}")
        print("=" * 60)
        
        if convert_audio_to_midi(test_file, output_dir):
            print("✅ 测试成功!")
        else:
            print("❌ 测试失败!")
    else:
        print("❌ 没有找到测试文件")
        print("请确保GTZAN数据集已正确下载并解压到指定位置")

def main():
    """
    主函数
    """
    print("🎼 Basic Pitch PyTorch - GTZAN Pop音乐转MIDI工具")
    print("=" * 60)
    
    # 选择运行模式
    print("\n请选择运行模式:")
    print("1. 批量转换所有pop音乐文件")
    print("2. 测试单个文件")
    
    try:
        choice = input("请输入选择 (1 或 2): ").strip()
        
        if choice == "1":
            batch_convert_gtzan_melody()
        elif choice == "2":
            test_single_file()
        else:
            print("❌ 无效选择，默认运行批量转换")
            batch_convert_gtzan_melody()
            
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断操作")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {str(e)}")

if __name__ == "__main__":
    main()