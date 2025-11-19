#!/usr/bin/env python3
"""
使用 LLark 模型为音频生成详细的 prompt
针对 GTZAN 数据集的 pop 音频进行推理
"""

import os
import sys
import json
import argparse
import glob
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import librosa
import torch
import transformers
from tqdm import tqdm

# 添加 LLark 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..', '..')
llark_path = os.path.join(project_root, 'external', 'llark')
sys.path.append(llark_path)

from m2t.arguments import DataArguments, ModelArguments, TrainingArguments
from m2t.conversation_utils import extract_response_tokens
from m2t.data_modules import make_mm_config
from m2t.infer import infer_with_prompt
from m2t.models.utils import load_pretrained_model
from m2t.tokenizer import get_prompt_end_token_sequence
from m2t.utils import get_autocast_type

class LLarkPromptGenerator:
    """使用 LLark 模型生成音频描述 prompt"""
    
    def __init__(self, model_path: str = None, ckpt_num: int = None):
        """
        初始化 LLark 推理器
        
        Args:
            model_path: 预训练模型路径
            ckpt_num: checkpoint 编号
        """
        self.model_path = model_path
        self.ckpt_num = ckpt_num
        self.model = None
        self.tokenizer = None
        self.multimodal_cfg = None
        self.end_seq = None
        
        # 默认推理提示模板
        self.prompt_templates = {
            'detailed_description': "Describe the contents of the provided audio in detail.",
            'musical_analysis': "Analyze the musical characteristics of this audio including genre, tempo, key, instruments, and mood.",
            'creative_description': "Provide a creative and detailed description of this music that could be used for music generation.",
            'technical_analysis': "Describe the technical aspects of this music including rhythm, harmony, melody, and production style.",
            'genre_and_style': "What genre is this music and what are its stylistic characteristics?"
        }
    
    def setup_model(self):
        """设置模型和相关配置"""
        if self.model_path is None:
            print("Warning: No model path provided. LLark model is required for inference.")
            print("Please download or specify a trained LLark model checkpoint.")
            return False
            
        try:
            # LLark的load_pretrained_model期望的路径结构是: model_name/checkpoint-{ckpt_num}
            # 我们需要调整路径以匹配这个结构
            if self.ckpt_num is None:
                # 如果没有指定ckpt_num，直接使用提供的路径作为checkpoint目录
                checkpoint_dir = self.model_path
                print(f"Loading LLark model from checkpoint directory: {checkpoint_dir}")
                
                # 直接从checkpoint目录加载
                from transformers import AutoTokenizer, AutoModelForCausalLM
                self.tokenizer = AutoTokenizer.from_pretrained(checkpoint_dir)
                
                # 根据模型类型选择正确的模型类
                if "meta-llama/Llama-2" in checkpoint_dir or "Llama-2" in checkpoint_dir:
                    from m2t.models.llamav2 import WrappedLlamav2ForCausalLM
                    self.model = WrappedLlamav2ForCausalLM.from_pretrained(
                        checkpoint_dir,
                        torch_dtype=torch.float16,
                    )
                    # 初始化适配器模块
                    self.model.get_model().initialize_adapter_modules(tune_mm_mlp_adapter=False, fsdp=None)
                else:
                    # 使用通用的AutoModel
                    self.model = AutoModelForCausalLM.from_pretrained(
                        checkpoint_dir,
                        torch_dtype=torch.float16,
                    )
            else:
                # 使用原始的load_pretrained_model函数
                print(f"Loading LLark model from {self.model_path} with checkpoint {self.ckpt_num}...")
                self.model, self.tokenizer = load_pretrained_model(
                    self.model_path, 
                    ckpt_num=self.ckpt_num
                )
            
            # 设置数据参数
            data_args = DataArguments()
            data_args.is_multimodal = True
            data_args.mm_use_audio_start_end = True
            
            self.multimodal_cfg = make_mm_config(data_args)
            self.end_seq = get_prompt_end_token_sequence(self.tokenizer, self.model_path)
            
            if torch.cuda.is_available():
                self.model.cuda()
                print("Model loaded on GPU")
            else:
                print("Model loaded on CPU")
                
            return True
            
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def load_audio(self, audio_path: str, sr: int = 22050) -> np.ndarray:
        """
        加载音频文件
        
        Args:
            audio_path: 音频文件路径
            sr: 采样率
            
        Returns:
            音频数组
        """
        try:
            audio, _ = librosa.load(audio_path, sr=sr)
            return audio
        except Exception as e:
            print(f"Error loading audio {audio_path}: {e}")
            return None
    
    def audio_to_encoding(self, audio: np.ndarray) -> np.ndarray:
        """
        将音频转换为 LLark 所需的编码格式
        注意：这里需要根据 LLark 的具体要求来实现音频编码
        """
        # 这是一个占位符实现
        # 实际使用时需要根据 LLark 的音频编码方式来实现
        # 可能需要使用 Jukebox 或其他音频编码器
        print("Warning: Audio encoding not implemented. Need to use Jukebox or other encoders.")
        return np.random.randn(1024, 768)  # 占位符
    
    def generate_prompt_for_audio(self, audio_path: str, prompt_type: str = 'detailed_description') -> Dict[str, Any]:
        """
        为单个音频文件生成 prompt
        
        Args:
            audio_path: 音频文件路径
            prompt_type: 提示类型
            
        Returns:
            包含生成结果的字典
        """
        if self.model is None:
            return {"error": "Model not loaded"}
        
        # 加载音频
        audio = self.load_audio(audio_path)
        if audio is None:
            return {"error": f"Failed to load audio: {audio_path}"}
        
        # 获取提示模板
        prompt_text = self.prompt_templates.get(prompt_type, self.prompt_templates['detailed_description'])
        
        try:
            # 音频编码（需要实际实现）
            audio_encoding = self.audio_to_encoding(audio)
            
            # 使用 LLark 进行推理
            with torch.autocast(device_type="cuda" if torch.cuda.is_available() else "cpu"):
                with torch.inference_mode():
                    result = infer_with_prompt(
                        prompt_text=prompt_text,
                        model=self.model,
                        audio_encoding=audio_encoding,
                        end_seq=self.end_seq,
                        multimodal_cfg=self.multimodal_cfg,
                        tokenizer=self.tokenizer,
                        example_id=os.path.basename(audio_path),
                        max_new_tokens=512
                    )
            
            return {
                "audio_path": audio_path,
                "prompt_type": prompt_type,
                "prompt_text": prompt_text,
                "generated_description": result.get("response", ""),
                "success": True
            }
            
        except Exception as e:
            return {
                "audio_path": audio_path,
                "prompt_type": prompt_type,
                "error": str(e),
                "success": False
            }
    
    def process_gtzan_pop_directory(self, gtzan_pop_dir: str, output_dir: str, prompt_types: List[str] = None, max_files: int = None):
        """
        处理 GTZAN pop 目录下的所有音频文件
        
        Args:
            gtzan_pop_dir: GTZAN pop 音频目录
            output_dir: 输出目录
            prompt_types: 要生成的提示类型列表
            max_files: 最大处理文件数量
        """
        if prompt_types is None:
            prompt_types = ['detailed_description', 'musical_analysis', 'creative_description']
        
        # 获取所有音频文件
        audio_files = glob.glob(os.path.join(gtzan_pop_dir, "*.wav"))
        
        if not audio_files:
            print(f"No audio files found in {gtzan_pop_dir}")
            return
        
        # 限制文件数量
        if max_files is not None:
            audio_files = audio_files[:max_files]
            print(f"Found {len(glob.glob(os.path.join(gtzan_pop_dir, '*.wav')))} audio files, processing first {len(audio_files)}")
        else:
            print(f"Found {len(audio_files)} audio files")
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        
        for audio_file in tqdm(audio_files, desc="Processing audio files"):
            file_results = {
                "filename": os.path.basename(audio_file),
                "audio_path": audio_file,
                "prompts": {}
            }
            
            for prompt_type in prompt_types:
                print(f"Generating {prompt_type} for {os.path.basename(audio_file)}")
                result = self.generate_prompt_for_audio(audio_file, prompt_type)
                file_results["prompts"][prompt_type] = result
            
            results.append(file_results)
        
        # 保存结果
        output_file = os.path.join(output_dir, "llark_generated_prompts.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to {output_file}")
        
        # 生成简化的 CSV 格式
        self.save_csv_summary(results, output_dir)
    
    def save_csv_summary(self, results: List[Dict], output_dir: str):
        """保存 CSV 格式的摘要"""
        import pandas as pd
        
        rows = []
        for result in results:
            for prompt_type, prompt_result in result["prompts"].items():
                if prompt_result.get("success", False):
                    rows.append({
                        "filename": result["filename"],
                        "prompt_type": prompt_type,
                        "generated_description": prompt_result.get("generated_description", ""),
                        "prompt_text": prompt_result.get("prompt_text", "")
                    })
        
        if rows:
            df = pd.DataFrame(rows)
            csv_file = os.path.join(output_dir, "llark_prompts_summary.csv")
            df.to_csv(csv_file, index=False)
            print(f"CSV summary saved to {csv_file}")

def main():
    parser = argparse.ArgumentParser(description="使用 LLark 为 GTZAN pop 音频生成 prompt")
    parser.add_argument(
        "--gtzan_pop_dir", 
        default="/home/hice1/xli3252/Desktop/diversity-eval/data/input/GTZAN_Dataset/Solo/genres_original/pop",
        help="GTZAN pop 音频目录路径"
    )
    parser.add_argument(
        "--output_dir",
        default="/home/hice1/xli3252/Desktop/diversity-eval/data/output/llark_prompts",
        help="输出目录"
    )
    parser.add_argument(
        "--model_path",
        default=None,
        help="LLark 模型路径（需要预训练模型）"
    )
    parser.add_argument(
        "--ckpt_num",
        type=int,
        default=None,
        help="Checkpoint 编号"
    )
    parser.add_argument(
        "--prompt_types",
        nargs='+',
        default=['detailed_description', 'musical_analysis', 'creative_description'],
        help="要生成的提示类型"
    )
    parser.add_argument(
        "--demo_mode",
        action='store_true',
        help="演示模式（不需要实际模型）"
    )
    parser.add_argument(
        "--max_files",
        type=int,
        default=None,
        help="最大处理文件数量（用于测试）"
    )
    
    args = parser.parse_args()
    
    # 创建生成器
    generator = LLarkPromptGenerator(args.model_path, args.ckpt_num)
    
    if args.demo_mode:
        print("Running in demo mode - generating sample prompts without LLark model")
        # 演示模式：生成示例提示
        demo_results = []
        audio_files = glob.glob(os.path.join(args.gtzan_pop_dir, "*.wav"))
        
        for audio_file in audio_files[:3]:  # 只处理前3个文件作为演示
            filename = os.path.basename(audio_file)
            demo_results.append({
                "filename": filename,
                "audio_path": audio_file,
                "prompts": {
                    "detailed_description": {
                        "prompt_text": "Describe the contents of the provided audio in detail.",
                        "generated_description": f"This is a pop music track ({filename}) with upbeat tempo, featuring vocals, drums, and melodic instruments. The song has a modern pop production style with clear vocals and rhythmic accompaniment.",
                        "success": True
                    },
                    "musical_analysis": {
                        "prompt_text": "Analyze the musical characteristics of this audio including genre, tempo, key, instruments, and mood.",
                        "generated_description": f"Genre: Pop | Tempo: ~120 BPM | Key: Major | Instruments: Vocals, drums, bass, synthesizers | Mood: Upbeat and energetic",
                        "success": True
                    }
                }
            })
        
        # 保存演示结果
        os.makedirs(args.output_dir, exist_ok=True)
        with open(os.path.join(args.output_dir, "demo_prompts.json"), 'w') as f:
            json.dump(demo_results, f, indent=2)
        
        print(f"Demo results saved to {args.output_dir}/demo_prompts.json")
        
    else:
        # 实际模式：需要 LLark 模型
        if not generator.setup_model():
            print("Failed to setup LLark model. Please provide a valid model path.")
            print("You can run with --demo_mode to see the expected output format.")
            return
        
        # 处理音频文件
        generator.process_gtzan_pop_directory(
            args.gtzan_pop_dir,
            args.output_dir,
            args.prompt_types,
            args.max_files
        )

if __name__ == "__main__":
    main()