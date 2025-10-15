#!/usr/bin/env python3
"""
使用VOCANO提取GTZAN数据集pop流派的主旋律
输入: data/input/GTZAN_Dataset/Data/genres_original/pop
输出: data/output/gtzan_test_mainM_out
"""

import os
import sys
import glob
import time
import torch
from pathlib import Path
import subprocess
import shutil

# 添加VOCANO路径到系统路径
VOCANO_PATH = "/home/evev/diversity-eval/external/VOCANO"
sys.path.append(VOCANO_PATH)

def verify_model_files():
    """
    验证VOCANO模型文件的完整性
    """
    print("🔍 验证VOCANO模型文件...")
    
    checkpoint_dir = Path(VOCANO_PATH) / "checkpoint"
    model_files = {
        "model.pt": "PyramidNet模型",
        "model3_patch25.npy": "Patch-CNN模型"
    }
    
    all_valid = True
    
    for filename, description in model_files.items():
        filepath = checkpoint_dir / filename
        
        if not filepath.exists():
            print(f"❌ {description}文件不存在: {filepath}")
            all_valid = False
            continue
        
        file_size = filepath.stat().st_size
        print(f"📁 {description}: {file_size:,} bytes")
        
        # 验证PyTorch模型文件
        if filename == "model.pt":
            try:
                # 尝试加载模型文件头部
                checkpoint = torch.load(filepath, map_location='cpu')
                if isinstance(checkpoint, dict) and ('model' in checkpoint or 'state_dict' in checkpoint):
                    print(f"✅ {description}: 格式验证通过")
                else:
                    print(f"⚠️  {description}: 格式可能有问题")
                    all_valid = False
            except Exception as e:
                print(f"❌ {description}: 加载失败 - {str(e)}")
                print(f"   可能的原因: 文件损坏或下载不完整")
                all_valid = False
        
        # 验证numpy文件 - 使用与VOCANO相同的加载方式
        elif filename.endswith('.npy'):
            try:
                import numpy as np
                # 使用与VOCANO Patch_CNN.py相同的加载方式
                if filename == "model3_patch25.npy":
                    # 模拟VOCANO的load_weights函数
                    try:
                        weights_dict = np.load(filepath, allow_pickle=True).item()
                        print(f"✅ {description}: 格式验证通过 (权重字典，{len(weights_dict)} 个键)")
                    except:
                        weights_dict = np.load(filepath, allow_pickle=True, encoding='bytes').item()
                        print(f"✅ {description}: 格式验证通过 (权重字典，使用bytes编码)")
                else:
                    # 其他numpy文件的标准加载
                    data = np.load(filepath, allow_pickle=True)
                    print(f"✅ {description}: 格式验证通过 (shape: {data.shape})")
            except Exception as e:
                print(f"❌ {description}: 加载失败 - {str(e)}")
                all_valid = False
    
    if not all_valid:
        print("\n💡 模型文件问题解决方案:")
        print("1. 删除损坏的模型文件:")
        print("   rm /home/evev/diversity-eval/external/VOCANO/checkpoint/model.pt")
        print("   rm /home/evev/diversity-eval/external/VOCANO/checkpoint/model3_patch25.npy")
        print("2. 重新下载模型文件:")
        print("   PyramidNet: https://drive.google.com/file/d/1m9YT7207CXQv1KdU0ivkRQrwvPnOuR3W/view")
        print("   Patch-CNN: https://drive.google.com/file/d/1tq_LcZwWQYV7wM6dBAeDZeQn39UNkPdl/view")
        print("3. 确保下载完整（model.pt应该约为109MB）")
    
    return all_valid

def setup_vocano_environment():
    """
    设置VOCANO运行环境
    """
    print("🔧 设置VOCANO运行环境...")
    
    # 检查VOCANO目录是否存在
    if not os.path.exists(VOCANO_PATH):
        print(f"❌ VOCANO目录不存在: {VOCANO_PATH}")
        return False
    
    # 检查必要的文件
    vocano_module = os.path.join(VOCANO_PATH, "vocano")
    if not os.path.exists(vocano_module):
        print(f"❌ VOCANO模块不存在: {vocano_module}")
        return False
    
    # 验证模型文件
    if not verify_model_files():
        print("❌ 模型文件验证失败，请重新下载")
        return False
    
    print(f"✅ VOCANO路径: {VOCANO_PATH}")
    return True

def extract_melody_with_vocano(input_wav, output_dir, filename_prefix=""):
    """
    使用VOCANO提取单个音频文件的主旋律
    
    Args:
        input_wav: 输入音频文件路径
        output_dir: 输出目录
        filename_prefix: 输出文件名前缀
    
    Returns:
        提取是否成功
    """
    try:
        print(f"🎵 正在处理: {os.path.basename(input_wav)}")
        start_time = time.time()
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成输出文件名
        audio_filename = Path(input_wav).stem
        output_name = f"{filename_prefix}{audio_filename}" if filename_prefix else audio_filename
        
        # 切换到VOCANO目录
        original_cwd = os.getcwd()
        os.chdir(VOCANO_PATH)
        
        try:
            # 检查GPU可用性并选择设备
            if torch.cuda.is_available():
                device = "auto"  # 自动选择最佳GPU
                use_cupy = True
                print(f"   🚀 使用GPU加速 (检测到 {torch.cuda.device_count()} 个GPU)")
            else:
                device = "cpu"
                use_cupy = False
                print("   ⚠️  使用CPU运行 (未检测到GPU)")
            
            # 构建VOCANO命令
            cmd = [
                sys.executable, "-m", "vocano.transcription",
                "-n", output_name,
                "-wd", input_wav,
                "-d", device
            ]
            
            # 如果有GPU且CuPy可用，添加CuPy加速标志
            if use_cupy:
                try:
                    import cupy
                    cmd.extend(["-use_cp"])
                    print("   ⚡ 启用CuPy加速")
                except ImportError:
                    print("   ⚠️  CuPy未安装，使用标准GPU加速")
            
            print(f"   执行命令: {' '.join(cmd)}")
            
            # 执行VOCANO转录
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            # 如果GPU模式失败且错误包含argmax，尝试CPU模式
            if result.returncode != 0 and device == "auto" and "argmax of an empty sequence" in result.stderr:
                print("   ⚠️  GPU模式失败，尝试CPU模式...")
                cmd_cpu = [
                    sys.executable, "-m", "vocano.transcription",
                    "-n", output_name,
                    "-wd", input_wav,
                    "-d", "cpu"
                ]
                print(f"   执行CPU命令: {' '.join(cmd_cpu)}")
                result = subprocess.run(
                    cmd_cpu,
                    capture_output=True,
                    text=True,
                    timeout=600  # CPU模式给更长时间
                )
            
            if result.returncode == 0:
                # 查找生成的文件
                generated_wav_dir = os.path.join(VOCANO_PATH, "generated", "wav")
                generated_midi_dir = os.path.join(VOCANO_PATH, "generated", "midi")
                
                # 移动生成的文件到目标目录
                success = False
                
                # 查找并移动WAV文件
                if os.path.exists(generated_wav_dir):
                    for wav_file in glob.glob(os.path.join(generated_wav_dir, f"{output_name}*")):
                        target_wav = os.path.join(output_dir, os.path.basename(wav_file))
                        shutil.move(wav_file, target_wav)
                        print(f"   ✅ 主旋律音频: {target_wav}")
                        success = True
                
                # 查找并移动MIDI文件
                if os.path.exists(generated_midi_dir):
                    for midi_file in glob.glob(os.path.join(generated_midi_dir, f"{output_name}*")):
                        target_midi = os.path.join(output_dir, os.path.basename(midi_file))
                        shutil.move(midi_file, target_midi)
                        print(f"   ✅ 主旋律MIDI: {target_midi}")
                        success = True
                
                if success:
                    processing_time = time.time() - start_time
                    print(f"   ⏱️  处理时间: {processing_time:.2f}秒")
                    print("-" * 50)
                    return True
                else:
                    print(f"   ❌ 未找到生成的文件")
                    return False
            else:
                print(f"   ❌ VOCANO执行失败:")
                print(f"   错误输出: {result.stderr}")
                return False
                
        finally:
            # 恢复原始工作目录
            os.chdir(original_cwd)
            
    except subprocess.TimeoutExpired:
        print(f"   ❌ 处理超时: {input_wav}")
        return False
    except Exception as e:
        print(f"   ❌ 处理失败: {str(e)}")
        return False

def batch_extract_gtzan_pop():
    """
    批量提取GTZAN数据集pop流派的主旋律
    """
    # 输入和输出路径
    input_dir = "/home/evev/diversity-eval/data/input/GTZAN_Dataset/Data/genres_original/pop"
    output_dir = "/home/evev/diversity-eval/data/output/gtzan_test_mainM_out"
    
    print("🎼 VOCANO主旋律提取 - GTZAN Pop流派")
    print("=" * 60)
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    
    # 检查输入目录
    if not os.path.exists(input_dir):
        print(f"❌ 输入目录不存在: {input_dir}")
        return
    
    # 查找所有WAV文件
    wav_files = glob.glob(os.path.join(input_dir, "*.wav"))
    
    if not wav_files:
        print(f"❌ 在输入目录中没有找到WAV文件")
        return
    
    print(f"🎵 找到 {len(wav_files)} 个音频文件")
    print("=" * 60)
    
    # 批量处理
    successful_extractions = 0
    failed_extractions = 0
    total_start_time = time.time()
    
    for i, wav_file in enumerate(wav_files, 1):
        print(f"[{i}/{len(wav_files)}] 处理文件...")
        
        if extract_melody_with_vocano(wav_file, output_dir, "pop_"):
            successful_extractions += 1
        else:
            failed_extractions += 1
    
    total_time = time.time() - total_start_time
    
    # 输出统计信息
    print("=" * 60)
    print("🎯 批量主旋律提取完成!")
    print(f"   总文件数: {len(wav_files)}")
    print(f"   成功提取: {successful_extractions}")
    print(f"   提取失败: {failed_extractions}")
    print(f"   总耗时: {total_time:.2f}秒")
    if len(wav_files) > 0:
        print(f"   平均每个文件: {total_time/len(wav_files):.2f}秒")
    
    if successful_extractions > 0:
        print(f"\n✨ 主旋律文件已保存到: {output_dir}")
        
        # 显示输出目录内容
        if os.path.exists(output_dir):
            output_files = os.listdir(output_dir)
            print(f"   输出文件数量: {len(output_files)}")
            print("   输出文件类型统计:")
            wav_count = len([f for f in output_files if f.endswith('.wav')])
            midi_count = len([f for f in output_files if f.endswith('.mid')])
            print(f"     WAV文件: {wav_count}")
            print(f"     MIDI文件: {midi_count}")

def test_single_file():
    """
    测试单个文件的主旋律提取（用于调试）
    """
    input_dir = "/home/evev/diversity-eval/data/input/GTZAN_Dataset/Data/genres_original/pop"
    test_files = glob.glob(os.path.join(input_dir, "*.wav"))
    
    if test_files:
        test_file = test_files[0]
        output_dir = "/home/evev/diversity-eval/data/output/gtzan_test_mainM_out"
        
        print(f"🧪 测试单个文件主旋律提取: {os.path.basename(test_file)}")
        print("=" * 60)
        
        if extract_melody_with_vocano(test_file, output_dir, "test_"):
            print("✅ 测试成功!")
        else:
            print("❌ 测试失败!")
    else:
        print("❌ 没有找到测试文件")

def main():
    """
    主函数
    """
    print("🎼 VOCANO主旋律提取工具")
    print("=" * 60)
    
    # 设置环境
    if not setup_vocano_environment():
        return
    
    # 选择运行模式
    print("\n请选择运行模式:")
    print("1. 批量提取所有GTZAN pop文件")
    print("2. 测试单个文件")
    
    try:
        choice = input("请输入选择 (1 或 2): ").strip()
        
        if choice == "1":
            batch_extract_gtzan_pop()
        elif choice == "2":
            test_single_file()
        else:
            print("❌ 无效选择，默认运行批量提取")
            batch_extract_gtzan_pop()
            
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断操作")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {str(e)}")

if __name__ == "__main__":
    main()