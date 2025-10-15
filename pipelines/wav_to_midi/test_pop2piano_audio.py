#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pop2Piano音频转换测试脚本
使用指定的音频文件进行钢琴伴奏生成
"""

import os
import librosa
import soundfile as sf
from transformers import Pop2PianoForConditionalGeneration, Pop2PianoProcessor
import torch
import numpy as np
from datetime import datetime

def test_pop2piano_conversion():
    # 音频文件路径
    audio_file = "Shutter_Solo_Dataset_15s/395423_sorry-sea-dog_preview_15s.mp3"
    
    # 检查文件是否存在
    if not os.path.exists(audio_file):
        print(f"❌ 音频文件不存在: {audio_file}")
        return
    
    print(f"🎵 开始处理音频文件: {audio_file}")
    print(f"📅 处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 加载模型和处理器
        print("🔄 加载Pop2Piano模型...")
        model = Pop2PianoForConditionalGeneration.from_pretrained("sweetcocoa/pop2piano")
        processor = Pop2PianoProcessor.from_pretrained("sweetcocoa/pop2piano")
        
        # 设置设备
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = model.to(device)
        print(f"🖥️  使用设备: {device}")
        
        # 加载音频
        print("🔄 加载音频文件...")
        audio, sr = librosa.load(audio_file, sr=22050)  # Pop2Piano使用22050Hz采样率
        print(f"📊 音频信息: 长度={len(audio)/sr:.2f}秒, 采样率={sr}Hz")
        
        # 预处理音频
        print("🔄 预处理音频...")
        inputs = processor(audio=audio, sampling_rate=sr, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # 生成钢琴伴奏
        print("🎹 生成钢琴伴奏...")
        with torch.no_grad():
            piano_output = model.generate(
                input_features=inputs["input_features"],
                composer="composer1",  # 可以选择不同的作曲家风格
                generation_config=model.generation_config,
                guidance_scale=1.0,
                max_length=1024,
                do_sample=True,
                temperature=1.0
            )
        
        # 解码输出 - 使用正确的Pop2Piano解码方法
        print("🔄 解码钢琴输出...")
        try:
            # 根据官方文档，batch_decode返回包含pretty_midi_objects的字典
            tokenizer_output = processor.batch_decode(
                token_ids=piano_output, 
                feature_extractor_output=inputs
            )
            
            # 提取MIDI对象
            midi_object = tokenizer_output["pretty_midi_objects"][0]
            
            print(f"✅ 成功解码MIDI对象: {type(midi_object)}")
            
            # 保存结果
            output_dir = "pop2piano_output"
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成输出文件名
            base_name = os.path.splitext(os.path.basename(audio_file))[0]
            midi_output_file = os.path.join(output_dir, f"{base_name}_piano_accompaniment.mid")
            
            # 保存MIDI文件
            midi_object.write(midi_output_file)
            
            print(f"✅ 钢琴MIDI生成成功！")
            print(f"📁 输出文件: {midi_output_file}")
            print(f"🎼 MIDI文件包含 {len(midi_object.instruments)} 个乐器轨道")
            print(f"🎵 总时长: {midi_object.get_end_time():.2f}秒")
            
            # 显示一些统计信息
            print("\n📈 处理统计:")
            print(f"📊 输入音频长度: {len(audio)/sr:.2f}秒")
            print(f"📊 输入采样率: {sr}Hz")
            print(f"🎼 生成的MIDI文件: {midi_output_file}")
            print(f"⏱️  处理完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            return midi_output_file
            
        except Exception as e:
            print(f"❌ 解码错误: {e}")
            print(f"🔍 错误类型: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return None
        
    except Exception as e:
        print(f"❌ 处理过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🎹 Pop2Piano音频转换测试")
    print("=" * 50)
    
    result = test_pop2piano_conversion()
    
    if result:
        print("\n🎉 测试完成！你可以播放生成的钢琴伴奏文件。")
        print(f"💡 提示: 使用音频播放器打开 {result} 来听听效果！")
    else:
        print("\n❌ 测试失败，请检查错误信息。")