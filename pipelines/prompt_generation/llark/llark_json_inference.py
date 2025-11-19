#!/usr/bin/env python3
"""
LLaRK JSON Inference Script
生成JSON格式的音乐分析结果，支持多种提示类型
"""

import os
import json
import glob
import numpy as np
import torch
import transformers
from tqdm import tqdm
from typing import Dict, List, Any

# LLaRK imports
from m2t.arguments import DataArguments, ModelArguments, TrainingArguments
from m2t.data_modules import make_mm_config
from m2t.infer import infer_with_prompt
from m2t.models.utils import load_pretrained_model
from m2t.tokenizer import get_prompt_end_token_sequence
from m2t.utils import get_autocast_type
from m2t.conversation_utils import extract_response_tokens


def safe_tokenize_fn(tokenizer, text, max_length=512):
    """安全的tokenization函数，防止溢出"""
    try:
        # 确保max_length不会导致溢出
        safe_max_length = min(max_length, 2048)
        
        result = tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=safe_max_length
        )
        return result
    except Exception as e:
        print(f"[ERROR] Tokenization failed: {e}")
        return None


def run_json_inference():
    """运行JSON格式的推理"""
    
    # 设置参数
    model_args = ModelArguments(
        model_name_or_path="checkpoints/meta-llama",
        model_max_length=512
    )
    
    data_args = DataArguments(
        is_multimodal=True,
        mm_use_audio_start_end=True
    )
    
    training_args = TrainingArguments(
        output_dir="tmp",
        bf16=True,
        tf32=True,
        model_max_length=512
    )
    
    # 路径设置
    encodings_dir = "/home/hice1/xli3252/Desktop/diversity-eval/data/output/llark_encodings_official"
    output_file = "/home/hice1/xli3252/Desktop/diversity-eval/data/output/llark_results.json"
    
    # 检查路径
    if not os.path.exists(encodings_dir):
        print(f"[ERROR] Encodings directory not found: {encodings_dir}")
        return
    
    print("Loading model and tokenizer...")
    try:
        model, tokenizer = load_pretrained_model(
            model_name=model_args.model_name_or_path,
            ckpt_num=100000,
            torch_dtype=torch.float16,
            mm_use_audio_start_end=True,
            device="cuda:0"
        )
        
        # 设置tokenizer max_length防止溢出
        if hasattr(tokenizer, 'model_max_length'):
            original_max_length = tokenizer.model_max_length
            print(f"[DEBUG] Changed tokenizer max_length from {original_max_length} to 512")
            tokenizer.model_max_length = 512
        
        # 创建multimodal config和end sequence
        multimodal_cfg = make_mm_config(data_args)
        end_seq = get_prompt_end_token_sequence(tokenizer, model_args.model_name_or_path)
        
        model.cuda()
        
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        return
    
    # 定义多种提示
    prompts = {
        "detailed_description": {
            "prompt_text": "Describe the contents of the provided audio in detail.",
        },
        "musical_analysis": {
            "prompt_text": "Analyze the musical characteristics of this audio including genre, tempo, key, instruments, and mood.",
        },
        "genre_classification": {
            "prompt_text": "What genre is this music? Provide a detailed classification.",
        },
        "mood_analysis": {
            "prompt_text": "Describe the mood and emotional characteristics of this music.",
        }
    }
    
    # 获取编码文件
    encoding_files = glob.glob(os.path.join(encodings_dir, "*.npy"))
    max_samples = 3  # 限制样本数量
    encoding_files = encoding_files[:max_samples]
    
    print(f"Processing {len(encoding_files)} files...")
    
    results = []
    
    with torch.autocast(device_type="cuda", dtype=get_autocast_type(training_args)):
        with torch.inference_mode():
            for encoding_file in tqdm(encoding_files):
                filename = os.path.basename(encoding_file).replace('.npy', '.wav')
                print(f"[DEBUG] Processing file: {filename}")
                
                try:
                    # 加载编码
                    encoding = np.load(encoding_file)
                    encoding = torch.from_numpy(encoding).float()
                    print(f"[DEBUG] Encoding shape: {encoding.shape}")
                    
                    # 为每个文件创建结果条目
                    file_result = {
                        "filename": filename,
                        "audio_path": f"/path/to/audio/{filename}",  # 可以根据需要调整
                        "prompts": {}
                    }
                    
                    # 对每种提示进行推理
                    for prompt_key, prompt_info in prompts.items():
                        print(f"[DEBUG] Running prompt: {prompt_key}")
                        
                        try:
                            # 运行推理
                            output = infer_with_prompt(
                                prompt_text=prompt_info["prompt_text"],
                                model=model,
                                audio_encoding=encoding,
                                end_seq=end_seq,
                                multimodal_cfg=multimodal_cfg,
                                tokenizer=tokenizer,
                                audio_first=True,
                                max_new_tokens=256,
                                do_sample=True,
                                temperature=0.7
                            )
                            
                            # 解码输出
                            if output is not None and len(output) > 0:
                                # 提取响应部分
                                response_tokens = extract_response_tokens(output[0], end_seq)
                                generated_text = tokenizer.decode(response_tokens, skip_special_tokens=True)
                                
                                file_result["prompts"][prompt_key] = {
                                    "prompt_text": prompt_info["prompt_text"],
                                    "generated_description": generated_text.strip(),
                                    "success": True
                                }
                                print(f"[DEBUG] {prompt_key} successful")
                            else:
                                file_result["prompts"][prompt_key] = {
                                    "prompt_text": prompt_info["prompt_text"],
                                    "generated_description": "Failed to generate response",
                                    "success": False
                                }
                                print(f"[DEBUG] {prompt_key} failed - no output")
                                
                        except Exception as e:
                            print(f"[ERROR] Failed to process prompt {prompt_key}: {e}")
                            file_result["prompts"][prompt_key] = {
                                "prompt_text": prompt_info["prompt_text"],
                                "generated_description": f"Error: {str(e)}",
                                "success": False
                            }
                    
                    results.append(file_result)
                    
                except Exception as e:
                    print(f"[ERROR] Failed to process {encoding_file}: {e}")
                    continue
    
    # 保存结果
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n=== Results saved to {output_file} ===")
    print(f"Processed {len(results)} files successfully")
    
    return results


if __name__ == "__main__":
    run_json_inference()