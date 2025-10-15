#!/usr/bin/env python3

import os
import numpy as np
import librosa
from libf0 import yin, pyin, swipe as libf0_swipe
from pathlib import Path
import argparse
import json
from librosa import stft
from scipy import ndimage, linalg
from numba import njit

# 添加salience方法的实现
def salience_f0_estimation(audio, sr, hop_length=512, frame_length=2048, f_min=80, f_max=800):
    """
    基于显著性的F0估计方法
    
    Args:
        audio: 音频信号
        sr: 采样率
        hop_length: 帧移
        frame_length: 帧长
        f_min: 最小频率
        f_max: 最大频率
    
    Returns:
        tuple: (时间轴, 基频序列)
    """
    # 计算STFT
    S = stft(audio, hop_length=hop_length, n_fft=frame_length)
    magnitude = np.abs(S)
    
    # 频率轴
    freqs = librosa.fft_frequencies(sr=sr, n_fft=frame_length)
    
    # 计算显著性函数
    salience = compute_salience(magnitude, freqs, f_min, f_max)
    
    # 提取F0
    f0_sequence = extract_f0_from_salience(salience, freqs, f_min, f_max)
    
    # 时间轴
    times = librosa.frames_to_time(np.arange(len(f0_sequence)), sr=sr, hop_length=hop_length)
    
    return times, f0_sequence

@njit
def compute_salience(magnitude, freqs, f_min, f_max):
    """
    计算显著性函数
    """
    n_frames = magnitude.shape[1]
    n_freqs = magnitude.shape[0]
    
    # 找到频率范围内的索引
    f_min_idx = np.searchsorted(freqs, f_min)
    f_max_idx = np.searchsorted(freqs, f_max)
    
    salience = np.zeros((f_max_idx - f_min_idx, n_frames))
    
    for i in range(f_min_idx, f_max_idx):
        freq = freqs[i]
        # 计算谐波的显著性 - 初始化为与帧数相同的数组
        harmonic_salience = np.zeros(n_frames)
        for h in range(1, 6):  # 考虑前5个谐波
            harmonic_freq = freq * h
            if harmonic_freq < freqs[-1]:
                harmonic_idx = np.searchsorted(freqs, harmonic_freq)
                if harmonic_idx < n_freqs:
                    weight = 1.0 / h  # 谐波权重
                    # 修复：确保两边都是数组
                    harmonic_salience = harmonic_salience + weight * magnitude[harmonic_idx, :]
        
        salience[i - f_min_idx, :] = harmonic_salience
    
    return salience

def extract_f0_from_salience(salience, freqs, f_min, f_max):
    """
    从显著性函数中提取F0
    """
    f_min_idx = np.searchsorted(freqs, f_min)
    f_max_idx = np.searchsorted(freqs, f_max)
    
    # 找到每帧的最大显著性对应的频率
    max_indices = np.argmax(salience, axis=0)
    f0_sequence = freqs[f_min_idx + max_indices]
    
    # 应用阈值，去除低显著性的帧
    max_salience = np.max(salience, axis=0)
    threshold = np.percentile(max_salience, 30)  # 使用30%分位数作为阈值
    f0_sequence[max_salience < threshold] = 0
    
    return f0_sequence

def extract_melody_libf0(audio_file, method='pyin', hop_length=512, frame_length=2048):
    """
    使用libf0库提取音频文件的旋律（基频）
    
    Args:
        audio_file: 音频文件路径
        method: 提取方法 ('yin', 'pyin', 'swipe', 'salience')
        hop_length: 帧移 (用于时间轴计算)
        frame_length: 帧长 (用于时间轴计算)
    
    Returns:
        tuple: (时间轴, 基频序列)
    """
    try:
        # 加载音频文件
        y, sr = librosa.load(audio_file, sr=None)
        
        # 根据选择的方法提取基频
        if method == 'yin':
            result = yin(y, sr)
        elif method == 'pyin':
            result = pyin(y, sr)
        elif method == 'swipe':
            result = libf0_swipe(y, sr)
        elif method == 'salience':
            result = salience_f0_estimation(y, sr, hop_length, frame_length)
        else:
            raise ValueError(f"不支持的方法: {method}. 可用方法: yin, pyin, swipe, salience")
        
        # 处理不同的返回值格式
        if isinstance(result, tuple):
            if len(result) == 2:
                times, f0 = result
            elif len(result) == 3:
                # 可能是 (times, f0, confidence) 或类似格式
                times, f0, _ = result
            else:
                # 如果返回值数量不确定，取前两个
                times, f0 = result[0], result[1]
        else:
            # 如果只返回f0
            f0 = result
            times = librosa.frames_to_time(np.arange(len(f0)), sr=sr, hop_length=hop_length)
        
        # 确保f0是numpy数组
        if not isinstance(f0, np.ndarray):
            f0 = np.array(f0)
        
        # 确保times是numpy数组
        if not isinstance(times, np.ndarray):
            times = np.array(times)
            
        return times, f0
        
    except Exception as e:
        print(f"处理文件 {audio_file} 时出错: {e}")
        return None, None

def process_dataset(dataset_dir, output_file, method='pyin'):
    """
    处理整个数据集并保存结果
    
    Args:
        dataset_dir: 数据集目录路径
        output_file: 输出JSON文件路径
        method: 提取方法
    """
    print("=== libf0 旋律提取工具 ===")
    print(f"数据集: {dataset_dir}")
    print(f"输出文件: {output_file}")
    print(f"方法: {method}")
    print("=" * 40)
    
    # 获取所有音频文件
    dataset_path = Path(dataset_dir)
    audio_extensions = ['.mp3', '.wav', '.flac', '.m4a']
    audio_files = []
    
    for ext in audio_extensions:
        audio_files.extend(dataset_path.glob(f'*{ext}'))
    
    print(f"找到 {len(audio_files)} 个音频文件")
    print(f"使用方法: {method}")
    
    results = []
    
    for i, audio_file in enumerate(audio_files, 1):
        print(f"处理 {i}/{len(audio_files)}: {audio_file.name}")
        
        times, f0 = extract_melody_libf0(str(audio_file), method=method)
        
        if times is not None and f0 is not None:
            # 确保f0是numpy数组并计算统计信息
            f0_array = np.array(f0) if not isinstance(f0, np.ndarray) else f0
            valid_f0 = f0_array[f0_array > 0]  # 只考虑有效的基频值
            
            if len(valid_f0) > 0:
                mean_f0 = float(np.mean(valid_f0))
                std_f0 = float(np.std(valid_f0))
                min_f0 = float(np.min(valid_f0))
                max_f0 = float(np.max(valid_f0))
                voiced_ratio = len(valid_f0) / len(f0_array)
            else:
                mean_f0 = std_f0 = min_f0 = max_f0 = voiced_ratio = 0
            
            result = {
                'filename': audio_file.name,
                'method': method,
                'statistics': {
                    'mean_f0': mean_f0,
                    'std_f0': std_f0,
                    'min_f0': min_f0,
                    'max_f0': max_f0,
                    'voiced_ratio': voiced_ratio
                },
                'f0_sequence': f0_array.tolist(),
                'times': times.tolist() if isinstance(times, np.ndarray) else list(times)
            }
            
            results.append(result)
        else:
            print(f"  跳过文件 {audio_file.name} (处理失败)")
    
    # 保存结果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n处理完成！成功处理 {len(results)} 个文件")
    print(f"结果已保存到: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='使用libf0库提取音频旋律')
    parser.add_argument('--dataset', required=True, help='数据集目录路径')
    parser.add_argument('--output', required=True, help='输出JSON文件路径')
    parser.add_argument('--method', choices=['yin', 'pyin', 'swipe', 'salience'], 
                       default='pyin', help='提取方法')
    
    args = parser.parse_args()
    
    process_dataset(args.dataset, args.output, args.method)

if __name__ == "__main__":
    main()