#!/usr/bin/env python3
"""
分析转换结果的脚本
"""

import os
import glob
import pretty_midi
import numpy as np
import sys; sys.path.append("../../external/basic-pitch-torch"); from basic_pitch_torch.inference import predict

def analyze_midi_file(midi_path):
    """分析MIDI文件的内容"""
    try:
        midi_data = pretty_midi.PrettyMIDI(midi_path)
        
        print(f"\n📊 MIDI文件分析: {os.path.basename(midi_path)}")
        print(f"   时长: {midi_data.get_end_time():.2f}秒")
        print(f"   乐器数量: {len(midi_data.instruments)}")
        
        if midi_data.instruments:
            instrument = midi_data.instruments[0]
            notes = instrument.notes
            
            print(f"   音符总数: {len(notes)}")
            
            if notes:
                pitches = [note.pitch for note in notes]
                velocities = [note.velocity for note in notes]
                durations = [note.end - note.start for note in notes]
                
                print(f"   音高范围: {min(pitches)} - {max(pitches)} (MIDI)")
                print(f"   力度范围: {min(velocities)} - {max(velocities)}")
                print(f"   平均音符时长: {np.mean(durations):.3f}秒")
                print(f"   最短音符: {min(durations):.3f}秒")
                print(f"   最长音符: {max(durations):.3f}秒")
                
                # 音高分布
                unique_pitches = sorted(set(pitches))
                print(f"   不同音高数量: {len(unique_pitches)}")
                
    except Exception as e:
        print(f"❌ 分析MIDI文件失败: {str(e)}")

def compare_with_original_audio(audio_path, midi_path):
    """比较原始音频和转换后的MIDI"""
    try:
        import librosa
        
        # 分析原始音频
        y, sr = librosa.load(audio_path)
        duration = len(y) / sr
        
        # 分析MIDI
        midi_data = pretty_midi.PrettyMIDI(midi_path)
        midi_duration = midi_data.get_end_time()
        
        print(f"\n🔍 音频vs MIDI对比:")
        print(f"   原始音频时长: {duration:.2f}秒")
        print(f"   MIDI时长: {midi_duration:.2f}秒")
        print(f"   时长差异: {abs(duration - midi_duration):.2f}秒")
        
    except Exception as e:
        print(f"❌ 对比分析失败: {str(e)}")

def batch_analyze():
    """批量分析所有转换结果"""
    
    # 查找所有MIDI文件
    midi_files = glob.glob("output_midi/*.mid")
    
    if not midi_files:
        print("❌ 没有找到MIDI文件，请先运行转换")
        return
    
    print(f"🎼 找到 {len(midi_files)} 个MIDI文件")
    print("=" * 60)
    
    for midi_file in midi_files:
        analyze_midi_file(midi_file)
        
        # 尝试找到对应的原始音频文件
        base_name = os.path.basename(midi_file).replace("_basic_pitch.mid", "")
        audio_candidates = [
            f"Shutter_Songs/{base_name}.mp3",
            f"Shutter_Songs/{base_name}.wav"
        ]
        
        for audio_file in audio_candidates:
            if os.path.exists(audio_file):
                compare_with_original_audio(audio_file, midi_file)
                break
        
        print("-" * 40)

if __name__ == "__main__":
    batch_analyze()