#!/usr/bin/env python3
import numpy as np
import torch
import sys
import os

# 添加LLark路径
sys.path.insert(0, '/home/evev/diversity-eval/external/llark')

def check_encoding_file(file_path):
    """检查编码文件的格式和内容"""
    print(f"检查文件: {file_path}")
    
    try:
        # 加载编码文件
        encoding = np.load(file_path)
        print(f"  形状: {encoding.shape}")
        print(f"  数据类型: {encoding.dtype}")
        print(f"  数值范围: [{encoding.min():.4f}, {encoding.max():.4f}]")
        print(f"  是否包含NaN: {np.isnan(encoding).any()}")
        print(f"  是否包含Inf: {np.isinf(encoding).any()}")
        
        return encoding
    except Exception as e:
        print(f"  错误: {e}")
        return None

def test_tokenizer_sequence():
    """测试tokenizer的end_seq生成"""
    from transformers import AutoTokenizer
    from m2t.tokenizer import get_prompt_end_token_sequence
    
    try:
        tokenizer_path = "/home/evev/diversity-eval/external/llark/checkpoints/meta-llama/Llama-2-7b-chat-hf/checkpoint-100000"
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, local_files_only=True)
        
        # 设置pad_token
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            print(f"设置pad_token为: {tokenizer.pad_token}")
        
        model_name = "/home/evev/diversity-eval/external/llark/checkpoints/meta-llama/Llama-2-7b-chat-hf"
        end_seq = get_prompt_end_token_sequence(tokenizer, model_name)
        print(f"End sequence: {end_seq}")
        
        return tokenizer, end_seq
    except Exception as e:
        print(f"Tokenizer错误: {e}")
        return None, None

def test_inference_step():
    """测试推理的关键步骤"""
    print("=" * 50)
    print("开始调试LLark推理问题")
    print("=" * 50)
    
    # 1. 检查编码文件
    encoding_file = "/home/evev/diversity-eval/data/output/llark_encodings/daeh-Yi_sha_shi-Suo_lin_nang-qm_004_15s.npy"
    encoding = check_encoding_file(encoding_file)
    
    if encoding is None:
        print("编码文件有问题，无法继续")
        return
    
    # 2. 检查tokenizer
    print("\n" + "=" * 30)
    print("检查Tokenizer")
    print("=" * 30)
    tokenizer, end_seq = test_tokenizer_sequence()
    
    if tokenizer is None or end_seq is None:
        print("Tokenizer有问题，无法继续")
        return
    
    # 3. 模拟推理过程
    print("\n" + "=" * 30)
    print("模拟推理过程")
    print("=" * 30)
    
    try:
        # 模拟生成的token序列
        prompt = "Describe this music"
        
        # 模拟一个简单的生成序列
        prompt_tokens = tokenizer.encode(prompt, return_tensors="pt")
        print(f"Prompt tokens: {prompt_tokens}")
        print(f"End sequence: {end_seq}")
        
        # 模拟生成的完整序列（包含prompt + 生成的内容）
        generated_tokens = torch.cat([
            prompt_tokens.flatten(),
            torch.tensor(end_seq),
            torch.tensor([123, 456, 789])  # 模拟生成的token
        ])
        
        print(f"Generated tokens: {generated_tokens}")
        
        # 测试extract_response_tokens
        from m2t.conversation_utils import extract_response_tokens, subsequence_pos
        
        # 检查subsequence_pos函数
        result = subsequence_pos(generated_tokens.tolist(), end_seq)
        print(f"Subsequence position result: {result}")
        
        if result is None:
            print("❌ 问题找到了！subsequence_pos返回None")
            print("这意味着在生成的token序列中找不到end_seq")
            print("可能的原因:")
            print("1. 模型没有正确生成end_seq")
            print("2. end_seq的定义有问题")
            print("3. 生成过程被提前截断")
        else:
            response_tokens = extract_response_tokens(generated_tokens, end_seq)
            print(f"Response tokens: {response_tokens}")
            response_text = tokenizer.decode(response_tokens)
            print(f"Response text: {response_text}")
            
    except Exception as e:
        print(f"推理测试错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_inference_step()
