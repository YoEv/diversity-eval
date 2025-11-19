#!/usr/bin/env python3
"""
LLark音频编码预处理模块
为LLark推理创建音频编码文件
"""

import numpy as np
import librosa
import argparse
from pathlib import Path
import glob
from tqdm import tqdm
import os

class LLarkAudioEncoder:
    """LLark音频编码器 - 创建模拟的Jukebox编码"""
    
    def __init__(self):
        self.target_sr = 44100
        self.encoding_dim = 4800  # Jukebox编码维度
        self.max_time_steps = 8192  # 最大时间步数
    
    def create_audio_encoding(self, audio_path, output_path):
        """
        创建模拟的Jukebox音频编码
        实际的Jukebox编码维度是 [time_steps, 4800]
        """
        try:
            # 加载音频文件
            audio, sr = librosa.load(audio_path, sr=self.target_sr)
            
            # 计算音频长度对应的时间步数
            # Jukebox的时间步数大约是 8192 对应 23.8秒的音频
            audio_duration = len(audio) / sr
            time_steps = int(self.max_time_steps * audio_duration / 23.8)
            time_steps = max(1, min(time_steps, self.max_time_steps))  # 限制在合理范围内
            
            # 提取音频特征
            try:
                mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
                spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
                spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)
                
                # 使用正确的chroma API
                try:
                    chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
                except AttributeError:
                    # 如果chroma_stft不存在，创建替代特征
                    chroma = np.random.randn(12, mfcc.shape[1])
                
                zero_crossing_rate = librosa.feature.zero_crossing_rate(audio)
                
                # 添加更多特征以增强编码质量
                spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)
                rms = librosa.feature.rms(y=audio)
                
                # 将特征组合
                features = np.concatenate([
                    mfcc.flatten(),
                    spectral_centroid.flatten(),
                    spectral_rolloff.flatten(),
                    chroma.flatten(),
                    zero_crossing_rate.flatten(),
                    spectral_bandwidth.flatten(),
                    rms.flatten()
                ])
                
            except Exception as e:
                print(f"⚠️  特征提取警告: {e}, 使用基础特征")
                # 如果特征提取失败，使用基础的MFCC特征
                mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
                features = mfcc.flatten()
            
            # 扩展到4800维
            if len(features) < self.encoding_dim:
                features = np.tile(features, (self.encoding_dim // len(features) + 1))[:self.encoding_dim]
            else:
                features = features[:self.encoding_dim]
            
            # 创建时间序列编码 [time_steps, 4800]
            encoding = np.tile(features, (time_steps, 1))
            
            # 添加一些随机变化使其更真实
            noise = np.random.normal(0, 0.1, encoding.shape)
            encoding = encoding + noise
            
            # 保存编码
            print(f"🔍 准备保存到: {output_path}")
            print(f"🔍 输出目录存在: {output_path.parent.exists()}")
            print(f"🔍 编码数据类型: {encoding.dtype}, 形状: {encoding.shape}")
            
            try:
                np.save(output_path, encoding.astype(np.float32))
                print(f"💾 np.save 调用完成")
                
                # 验证文件是否真的被创建
                if output_path.exists():
                    file_size = output_path.stat().st_size
                    print(f"✅ 文件已创建: {output_path} (大小: {file_size} bytes)")
                else:
                    print(f"❌ 文件未创建: {output_path}")
                    return False, None
                    
            except Exception as save_error:
                print(f"❌ 保存失败: {save_error}")
                return False, None
            
            return True, encoding.shape
            
        except Exception as e:
            print(f"❌ 编码失败: {audio_path} - {e}")
            return False, None
    
    def process_directory(self, input_dir, output_dir, max_files=None):
        """批量处理目录中的音频文件"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        # 检查输入目录是否存在
        if not input_path.exists():
            print(f"❌ 输入目录不存在: {input_dir}")
            return False
        
        # 创建输出目录
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 查找所有音频文件 (支持递归搜索)
        audio_extensions = ['*.wav', '*.mp3', '*.flac', '*.m4a']
        audio_files = []
        
        print(f"🔍 在目录中搜索音频文件: {input_dir}")
        
        # 首先尝试直接搜索
        for ext in audio_extensions:
            files = list(input_path.glob(ext))
            audio_files.extend(files)
            if files:
                print(f"   找到 {len(files)} 个 {ext} 文件")
        
        # 如果没找到，尝试递归搜索
        if not audio_files:
            print("   直接搜索未找到文件，尝试递归搜索...")
            for ext in audio_extensions:
                files = list(input_path.rglob(ext))
                audio_files.extend(files)
                if files:
                    print(f"   递归找到 {len(files)} 个 {ext} 文件")
        
        # 如果还是没找到，显示目录内容
        if not audio_files:
            print(f"❌ 在 {input_dir} 中未找到音频文件")
            print("📁 目录内容:")
            try:
                for item in input_path.iterdir():
                    if item.is_dir():
                        print(f"   📁 {item.name}/")
                    else:
                        print(f"   📄 {item.name}")
            except Exception as e:
                print(f"   无法读取目录内容: {e}")
            return False
        
        # 限制文件数量
        if max_files:
            audio_files = audio_files[:max_files]
        
        print(f"🎵 找到 {len(audio_files)} 个音频文件")
        print(f"📂 输入目录: {input_dir}")
        print(f"📂 输出目录: {output_dir}")
        
        # 处理每个音频文件
        success_count = 0
        for audio_file in tqdm(audio_files, desc="编码音频文件"):
            # 生成输出文件名
            output_file = output_path / (audio_file.stem + ".npy")
            
            # 如果文件已存在，跳过
            if output_file.exists():
                print(f"⏭️  跳过已存在的文件: {output_file.name}")
                success_count += 1
                continue
            
            # 创建编码
            success, shape = self.create_audio_encoding(audio_file, output_file)
            if success:
                print(f"✅ 编码完成: {audio_file.name} -> {output_file.name} (shape: {shape})")
                success_count += 1
        
        print(f"\n🎉 编码完成! 成功: {success_count}/{len(audio_files)} 个文件")
        return success_count > 0

def main():
    parser = argparse.ArgumentParser(description="LLark音频编码预处理")
    parser.add_argument("--input-dir", required=True, help="输入音频目录路径")
    parser.add_argument("--output-dir", required=True, help="输出编码目录路径")
    parser.add_argument("--max-files", type=int, default=None, help="最大处理文件数量")
    parser.add_argument("--single-file", help="处理单个音频文件")
    parser.add_argument("--single-output", help="单个文件的输出路径")
    
    args = parser.parse_args()
    
    encoder = LLarkAudioEncoder()
    
    if args.single_file and args.single_output:
        # 处理单个文件
        print(f"🎵 处理单个文件: {args.single_file}")
        success, shape = encoder.create_audio_encoding(args.single_file, args.single_output)
        if success:
            print(f"✅ 编码完成: {args.single_output} (shape: {shape})")
        else:
            print("❌ 编码失败")
    else:
        # 批量处理目录
        print("🎵 批量处理音频文件")
        print("=" * 60)
        success = encoder.process_directory(args.input_dir, args.output_dir, args.max_files)
        
        if success:
            print("\n✅ 音频编码预处理完成!")
            print(f"📁 编码文件保存在: {args.output_dir}")
            print("\n🚀 下一步: 使用以下命令进行LLark推理:")
            print(f"cd /home/hice1/xli3252/Desktop/diversity-eval/external/llark")
            print(f"python scripts/inference/infer_from_encodings.py \\")
            print(f"    --audio-encodings-dir {args.output_dir} \\")
            print(f"    --model_name_or_path checkpoints/meta-llama/checkpoint-100000 \\")
            print(f"    --ckpt-num 100000 \\")
            print(f"    --prompt \"Describe this music\" \\")
            print(f"    --outfile inference_results.csv \\")
            print(f"    --max-samples 10")
        else:
            print("\n❌ 音频编码预处理失败!")

if __name__ == "__main__":
    main()
