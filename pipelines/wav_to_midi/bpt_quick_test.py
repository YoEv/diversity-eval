#!/usr/bin/env python3
"""
快速测试脚本：使用basic-pitch-torch转换单个音频文件
"""

import sys; sys.path.append("../../external/basic-pitch-torch"); from basic_pitch_torch.inference import predict
import os

def quick_test():
    """快速测试一个音频文件的转换"""
    
    # 选择第一个可用的音频文件
    audio_files = [
        "Shutter_Songs/1231293_the-clearing_preview.mp3",
        "Shutter_Songs/1233903_all-the-beautiful-things_preview.mp3", 
        "Shutter_Songs/1237268_i'm-coming-home-to-you_preview.mp3",
        "Shutter_Songs/1239825_all-that-you-need-to-know_preview.mp3"
    ]
    
    # 找到第一个存在的文件
    test_file = None
    for file in audio_files:
        if os.path.exists(file):
            test_file = file
            break
    
    if not test_file:
        print("❌ 没有找到音频文件")
        return
    
    print(f"🎵 测试文件: {test_file}")
    print("🔄 开始转换...")
    
    try:
        # 使用predict函数进行转换
        model_output, midi_data, note_events = predict(test_file)
        
        # 保存MIDI文件
        output_file = "test_output.mid"
        midi_data.write(output_file)
        
        print(f"✅ 转换成功!")
        print(f"📁 输出文件: {output_file}")
        print(f"🎼 检测到音符数量: {len(note_events)}")
        
        # 显示前几个音符信息
        if note_events:
            print("\n🎵 前5个音符:")
            for i, (start, end, pitch, velocity, pitch_bend) in enumerate(note_events[:5]):
                print(f"   {i+1}. 音高:{pitch}, 开始:{start:.2f}s, 结束:{end:.2f}s, 力度:{velocity}")
        
    except Exception as e:
        print(f"❌ 转换失败: {str(e)}")

if __name__ == "__main__":
    quick_test()