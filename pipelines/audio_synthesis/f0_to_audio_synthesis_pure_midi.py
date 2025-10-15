import json
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
import argparse
import os

try:
    import pretty_midi as pm
    PRETTY_MIDI_AVAILABLE = True
except ImportError:
    PRETTY_MIDI_AVAILABLE = False
    print("错误: pretty_midi未安装")
    exit(1)

def f0_to_soundfont_audio_pure(f0_values, times, soundfont_path, output_path, fs=44100):
    """
    使用 pretty_midi 和 SoundFont 将 F0 序列转换为音频
    
    Args:
        f0_values: F0频率值列表 (Hz)
        times: 对应的时间戳列表 (秒)
        soundfont_path: SoundFont文件路径
        output_path: 输出音频文件路径
        fs: 采样率
    """
    # 创建MIDI对象
    midi_data = pm.PrettyMIDI()
    
    # 创建钢琴音轨
    piano_program = pm.instrument_name_to_program('Acoustic Grand Piano')
    piano = pm.Instrument(program=piano_program)
    
    # 将F0转换为MIDI音符
    for i in range(len(f0_values)):
        f0 = f0_values[i]
        time_start = times[i] if i < len(times) else times[-1]
        
        # 跳过无效的F0值
        if f0 <= 0 or f0 > 4000:  # 跳过静音和异常高频
            continue
            
        # 计算音符持续时间
        if i < len(times) - 1:
            duration = times[i + 1] - time_start
        else:
            duration = 0.1  # 最后一个音符的默认持续时间
            
        if duration <= 0:
            duration = 0.1
            
        # 将频率转换为MIDI音符号
        midi_note = int(round(69 + 12 * np.log2(f0 / 440.0)))
        
        # 确保MIDI音符在有效范围内
        if 21 <= midi_note <= 108:  # 钢琴音符范围
            note = pm.Note(
                velocity=80,
                pitch=midi_note,
                start=time_start,
                end=time_start + duration
            )
            piano.notes.append(note)
    
    midi_data.instruments.append(piano)
    
    # 使用SoundFont合成音频
    try:
        audio_data = midi_data.fluidsynth(fs=fs, sf2_path=soundfont_path)
        
        # 保存音频文件
        sf.write(output_path, audio_data, fs)
        return True
    except Exception as e:
        print(f"合成音频时出错: {e}")
        return False

def process_f0_results(json_file, output_dir, soundfont_path):
    """
    处理F0提取结果并生成音频
    """
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # 检测数据格式
    if isinstance(data, list):
        # 数组格式：[{"filename": "...", "f0_sequence": [...], "times": [...]}, ...]
        items = data
    else:
        # 字典格式：{"filename1": {"f0_sequence": [...], "times": [...]}, ...}
        items = [{"filename": k, **v} for k, v in data.items()]
    
    os.makedirs(output_dir, exist_ok=True)
    
    for i, item in enumerate(items, 1):
        filename = item['filename']
        # 注意：这里times是频率值，f0_sequence是时间戳
        f0_values = item.get('times', [])  # 频率值
        time_stamps = item.get('f0_sequence', [])  # 时间戳
        
        print(f"处理 {i}/{len(items)}: {filename}")
        
        if not f0_values or not time_stamps:
            print(f"  ⚠️ 跳过: 无有效F0数据")
            continue
            
        # 确保数据长度一致
        min_len = min(len(f0_values), len(time_stamps))
        f0_values = f0_values[:min_len]
        time_stamps = time_stamps[:min_len]
        
        # 生成输出文件名
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}_soundfont_synthesized.wav"
        output_path = os.path.join(output_dir, output_filename)
        
        # 生成音频
        success = f0_to_soundfont_audio_pure(
            f0_values=f0_values,
            times=time_stamps,
            soundfont_path=soundfont_path,
            output_path=output_path
        )
        
        if success:
            print(f"  ✓ 已保存: {output_path}")
        else:
            print(f"  ✗ 生成失败: {filename}")

def main():
    parser = argparse.ArgumentParser(description='F0序列到音频合成 - 纯pretty_midi版本')
    parser.add_argument('--input', required=True, help='输入JSON文件路径')
    parser.add_argument('--output', required=True, help='输出目录')
    parser.add_argument('--soundfont', required=True, help='SoundFont文件路径')
    parser.add_argument('--sr', type=int, default=22050, help='采样率')
    
    args = parser.parse_args()
    
    if not PRETTY_MIDI_AVAILABLE:
        print("错误: 需要安装pretty_midi库")
        print("安装命令: pip install pretty_midi")
        return
    
    process_f0_results(args.input, args.output, args.soundfont)
    print("\n合成完成！")

if __name__ == "__main__":
    main()