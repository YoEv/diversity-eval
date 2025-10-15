#!/usr/bin/env python3

import os
import numpy as np
import librosa
import subprocess
import tempfile
from pathlib import Path
import argparse
import json

def extract_melody_swipe(audio_file, pmin=75, pmax=500, st=0.3, dt=0.01):
    """
    使用SWIPE算法提取音频文件的旋律（基频）
    
    Args:
        audio_file: 音频文件路径
        pmin: 最小基频 (Hz)
        pmax: 最大基频 (Hz) 
        st: 强度阈值
        dt: 时间步长 (秒)
    
    Returns:
        tuple: (时间轴, 基频序列)
    """
    try:
        # 检查SWIPE是否已安装
        try:
            subprocess.run(['swipe', '--help'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("错误: SWIPE未安装或不在PATH中")
            print("请确保已编译并安装SWIPE: make && make install")
            return None, None
        
        # 创建临时文件来存储SWIPE输出
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as tmp_file:
            tmp_output = tmp_file.name
        
        try:
            # 构建SWIPE命令
            cmd = [
                'swipe',
                '-i', str(audio_file),
                '-o', tmp_output,
                '-r', str(pmin), str(pmax),  # 基频范围
                '-s', str(st),               # 强度阈值
                '-t', str(dt)                # 时间步长
            ]
            
            # 执行SWIPE
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"SWIPE执行失败: {result.stderr}")
                return None, None
            
            # 读取SWIPE输出
            times = []
            f0_values = []
            
            with open(tmp_output, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split()
                        if len(parts) >= 2:
                            time = float(parts[0])
                            f0 = float(parts[1])
                            times.append(time)
                            f0_values.append(f0 if f0 > 0 else 0)  # SWIPE用0表示无声
            
            return np.array(times), np.array(f0_values)
            
        finally:
            # 清理临时文件
            if os.path.exists(tmp_output):
                os.unlink(tmp_output)
                
    except Exception as e:
        print(f"处理文件 {audio_file} 时出错: {e}")
        return None, None

def convert_to_wav_if_needed(audio_file):
    """
    如果音频文件不是WAV格式，转换为临时WAV文件
    SWIPE可能对某些格式支持有限
    """
    if audio_file.suffix.lower() == '.wav':
        return str(audio_file), False
    
    # 创建临时WAV文件
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
        tmp_wav = tmp_file.name
    
    try:
        # 使用librosa加载并保存为WAV
        y, sr = librosa.load(str(audio_file), sr=None)
        librosa.output.write_wav(tmp_wav, y, sr)
        return tmp_wav, True
    except Exception as e:
        print(f"转换音频格式失败: {e}")
        if os.path.exists(tmp_wav):
            os.unlink(tmp_wav)
        return None, False

def process_dataset(dataset_dir, output_file, pmin=75, pmax=500, st=0.3, dt=0.01):
    """
    处理整个数据集并保存结果
    
    Args:
        dataset_dir: 数据集目录路径
        output_file: 输出文件路径
        pmin, pmax, st, dt: SWIPE参数
    """
    dataset_path = Path(dataset_dir)
    
    if not dataset_path.exists():
        print(f"数据集目录不存在: {dataset_dir}")
        return
    
    # 获取所有音频文件
    audio_files = list(dataset_path.glob("*.mp3")) + list(dataset_path.glob("*.wav"))
    
    if not audio_files:
        print(f"在 {dataset_dir} 中未找到音频文件")
        return
    
    print(f"找到 {len(audio_files)} 个音频文件")
    print(f"SWIPE参数: pmin={pmin}, pmax={pmax}, st={st}, dt={dt}")
    
    results = []
    
    for i, audio_file in enumerate(audio_files, 1):
        print(f"处理 {i}/{len(audio_files)}: {audio_file.name}")
        
        # 如果需要，转换为WAV格式
        wav_file, is_temp = convert_to_wav_if_needed(audio_file)
        
        if wav_file is None:
            print(f"跳过文件 {audio_file.name} (格式转换失败)")
            continue
        
        try:
            times, f0 = extract_melody_swipe(wav_file, pmin, pmax, st, dt)
            
            if times is not None and f0 is not None:
                # 计算统计信息
                valid_f0 = f0[f0 > 0]  # 只考虑有效的基频值
                
                if len(valid_f0) > 0:
                    mean_f0 = np.mean(valid_f0)
                    std_f0 = np.std(valid_f0)
                    min_f0 = np.min(valid_f0)
                    max_f0 = np.max(valid_f0)
                    voiced_ratio = len(valid_f0) / len(f0)
                else:
                    mean_f0 = std_f0 = min_f0 = max_f0 = voiced_ratio = 0
                
                results.append({
                    'filename': audio_file.name,
                    'mean_f0': mean_f0,
                    'std_f0': std_f0,
                    'min_f0': min_f0,
                    'max_f0': max_f0,
                    'voiced_ratio': voiced_ratio,
                    'f0_sequence': f0.tolist(),
                    'times': times.tolist()
                })
        
        finally:
            # 清理临时WAV文件
            if is_temp and os.path.exists(wav_file):
                os.unlink(wav_file)
    
    # 保存结果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存到: {output_file}")
    print(f"成功处理 {len(results)} 个文件")
    
    # 打印统计摘要
    if results:
        all_mean_f0 = [r['mean_f0'] for r in results if r['mean_f0'] > 0]
        if all_mean_f0:
            print(f"\n数据集统计摘要:")
            print(f"平均基频范围: {np.min(all_mean_f0):.2f} - {np.max(all_mean_f0):.2f} Hz")
            print(f"整体平均基频: {np.mean(all_mean_f0):.2f} Hz")
            print(f"平均有声比例: {np.mean([r['voiced_ratio'] for r in results]):.3f}")

def main():
    parser = argparse.ArgumentParser(description='使用SWIPE提取音频旋律')
    parser.add_argument('--dataset', default='Shutter_Solo_Dataset_15s',
                       help='数据集目录路径')
    parser.add_argument('--output', default='shutter_melody_swipe_results.json',
                       help='输出文件路径')
    parser.add_argument('--pmin', type=float, default=75,
                       help='最小基频 (Hz)')
    parser.add_argument('--pmax', type=float, default=500,
                       help='最大基频 (Hz)')
    parser.add_argument('--st', type=float, default=0.3,
                       help='强度阈值')
    parser.add_argument('--dt', type=float, default=0.01,
                       help='时间步长 (秒)')
    
    args = parser.parse_args()
    
    print("=== SWIPE 旋律提取工具 ===")
    print(f"数据集: {args.dataset}")
    print(f"输出文件: {args.output}")
    print(f"参数: pmin={args.pmin}, pmax={args.pmax}, st={args.st}, dt={args.dt}")
    print("=" * 40)
    
    process_dataset(args.dataset, args.output, args.pmin, args.pmax, args.st, args.dt)

if __name__ == "__main__":
    main()