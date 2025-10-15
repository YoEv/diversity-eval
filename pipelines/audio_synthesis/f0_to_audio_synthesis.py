#!/usr/bin/env python3

import json
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
import argparse
from scipy.signal import sawtooth, square

def f0_to_audio(f0_sequence, times, sr=22050, synthesis_method='sine'):
    """
    将F0序列合成为音频信号
    
    Args:
        f0_sequence: 基频序列
        times: 时间轴
        sr: 采样率
        synthesis_method: 合成方法 ('sine', 'sawtooth', 'square', 'harmonic')
    
    Returns:
        audio: 合成的音频信号
    """
    # 计算总的音频长度
    duration = times[-1] if len(times) > 0 else len(f0_sequence) * 512 / sr
    n_samples = int(duration * sr)
    audio = np.zeros(n_samples)
    
    # 为每个时间帧生成音频
    for i, (t, f0) in enumerate(zip(times, f0_sequence)):
        if f0 > 0:  # 只处理有声段
            # 计算当前帧对应的采样点范围
            start_sample = int(t * sr)
            if i < len(times) - 1:
                end_sample = int(times[i + 1] * sr)
            else:
                end_sample = min(start_sample + int(0.023 * sr), n_samples)  # 默认23ms帧长
            
            if start_sample < n_samples:
                frame_length = min(end_sample - start_sample, n_samples - start_sample)
                t_frame = np.linspace(0, frame_length / sr, frame_length)
                
                if synthesis_method == 'sine':
                    # 纯正弦波合成
                    frame_audio = 0.3 * np.sin(2 * np.pi * f0 * t_frame)
                    
                elif synthesis_method == 'sawtooth':
                    # 锯齿波合成
                    frame_audio = 0.2 * sawtooth(2 * np.pi * f0 * t_frame)
                    
                elif synthesis_method == 'square':
                    # 方波合成
                    frame_audio = 0.2 * square(2 * np.pi * f0 * t_frame)
                    
                elif synthesis_method == 'harmonic':
                    # 谐波合成（更自然的声音）
                    frame_audio = np.zeros(frame_length)
                    # 添加基频和几个谐波
                    harmonics = [1.0, 0.5, 0.25, 0.125, 0.0625]  # 谐波幅度
                    for h, amp in enumerate(harmonics, 1):
                        if f0 * h < sr / 2:  # 避免混叠
                            frame_audio += amp * np.sin(2 * np.pi * f0 * h * t_frame)
                    frame_audio *= 0.2
                
                # 应用简单的包络以避免点击声
                envelope = np.ones(frame_length)
                fade_samples = min(int(0.005 * sr), frame_length // 4)  # 5ms淡入淡出
                if fade_samples > 0:
                    envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
                    envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
                
                frame_audio *= envelope
                
                # 添加到总音频中
                end_idx = min(start_sample + frame_length, n_samples)
                audio[start_sample:end_idx] += frame_audio[:end_idx - start_sample]
    
    return audio

def process_f0_results(json_file, output_dir, synthesis_method='harmonic', sr=22050):
    """
    处理F0结果文件并生成音频
    
    Args:
        json_file: F0结果JSON文件路径
        output_dir: 输出目录
        synthesis_method: 合成方法 ('sine', 'harmonic', 'sawtooth', 'square')
        sr: 采样率
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 读取F0结果
    with open(json_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    print(f"找到 {len(results)} 个F0序列")
    
    for i, result in enumerate(results, 1):
        filename = result['filename']
        f0_sequence = np.array(result['f0_sequence'])
        times = np.array(result['times'])
        method = result.get('method', 'unknown')
        
        # 检测数据格式并修正
        # 如果f0_sequence的值都很小（<20），可能是时间值
        # 如果times的值都很大（>20），可能是频率值
        if len(f0_sequence) > 0 and len(times) > 0:
            f0_max = np.max(f0_sequence[f0_sequence > 0]) if np.any(f0_sequence > 0) else 0
            times_max = np.max(times[times > 0]) if np.any(times > 0) else 0
            
            # 如果f0_sequence看起来像时间值，而times看起来像频率值，就交换它们
            if f0_max < 20 and times_max > 50:
                print(f"  检测到数据格式异常，交换f0_sequence和times")
                f0_sequence, times = times, f0_sequence
        
        print(f"处理 {i}/{len(results)}: {filename}")
        
        # 合成音频
        audio = f0_to_audio(f0_sequence, times, sr, synthesis_method)
        
        # 归一化音频
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio)) * 0.8
        
        # 生成输出文件名
        base_name = Path(filename).stem
        output_filename = f"{base_name}_{method}_{synthesis_method}_synthesized.wav"
        output_file = output_path / output_filename
        
        # 保存音频
        sf.write(output_file, audio, sr)
        
        print(f"  已保存: {output_file}")
        print(f"  音频长度: {len(audio)/sr:.2f}秒")
        print(f"  有声帧比例: {result['statistics']['voiced_ratio']:.2%}")
        print(f"  平均F0: {result['statistics']['mean_f0']:.1f}Hz")
    
    print(f"\n合成完成！共处理 {len(results)} 个文件")
    print(f"音频文件已保存到: {output_dir}")

def main():
    parser = argparse.ArgumentParser(description='将F0序列合成为音频')
    parser.add_argument('--input', required=True, help='F0结果JSON文件路径')
    parser.add_argument('--output', required=True, help='输出音频目录')
    parser.add_argument('--method', choices=['sine', 'sawtooth', 'square', 'harmonic'], 
                       default='harmonic', help='合成方法')
    parser.add_argument('--sr', type=int, default=22050, help='采样率')
    
    args = parser.parse_args()
    
    process_f0_results(args.input, args.output, args.method, args.sr)

if __name__ == "__main__":
    main()