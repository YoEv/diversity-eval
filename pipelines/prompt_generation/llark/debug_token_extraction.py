#!/usr/bin/env python3

import os
import sys
import torch
import numpy as np

# 添加LLark路径
llark_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "external/llark"))
sys.path.insert(0, llark_root)

from m2t.models.utils import load_pretrained_model
from m2t.data_modules import make_mm_config
from m2t.infer import infer_with_prompt
from m2t.tokenizer import get_prompt_end_token_sequence
from m2t.conversation_utils import extract_response_tokens, subsequence_pos
from m2t.arguments import DataArguments, ModelArguments, TrainingArguments

def debug_token_extraction():
    print("🔍 调试token提取问题...")
    
    # 设置参数
    model_args = ModelArguments()
    model_args.model_name_or_path = "external/llark/checkpoints/meta-llama/Llama-2-7b-chat-hf"
    
    data_args = DataArguments()
    data_args.mm_use_audio_start_end = True
    
    training_args = TrainingArguments(output_dir="./tmp")
    
    # 加载模型和tokenizer
    print("📥 加载模型和tokenizer...")
    model, tokenizer = load_pretrained_model(
        model_args.model_name_or_path,
        ckpt_num=100000,
        low_memory=True,
    )
    
    # 修复pad_token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        print(f"[INFO] Set pad_token to eos_token: {tokenizer.pad_token}")
    
    # 获取end_seq
    end_seq = get_prompt_end_token_sequence(tokenizer, model_args.model_name_or_path)
    print(f"🎯 end_seq: {end_seq}")
    print(f"🎯 end_seq tokens: {tokenizer.decode(end_seq)}")
    
    # 加载一个编码文件
    encoding_path = "/home/evev/diversity-eval/data/output/llark_encodings/daeh-Yi_sha_shi-Suo_lin_nang-qm_004_15s.npy"
    audio_encoding = torch.from_numpy(np.load(encoding_path)).float()
    print(f"📊 音频编码形状: {audio_encoding.shape}")
    
    # 创建multimodal配置
    multimodal_cfg = make_mm_config(data_args)
    
    # 进行推理
    prompt = "Describe this music"
    print(f"💬 提示词: {prompt}")
    
    print("🚀 开始推理...")
    with torch.autocast(device_type="cuda", dtype=torch.float16):
        with torch.inference_mode():
            outputs = infer_with_prompt(
                prompt,
                model=model,
                audio_encoding=audio_encoding,
                multimodal_cfg=multimodal_cfg,
                end_seq=end_seq,
                tokenizer=tokenizer,
                audio_first=True,
                max_new_tokens=64,  # 减少token数量便于调试
                use_cache=False,
                temperature=0.0,
                num_beams=1,
                top_p=0.9,
            )
    
    print("📋 推理结果分析:")
    generated_tokens = outputs[0]
    print(f"生成的token数量: {len(generated_tokens)}")
    print(f"生成的tokens: {generated_tokens.tolist()}")
    print(f"解码结果: {repr(tokenizer.decode(generated_tokens))}")
    
    # 检查end_seq是否在生成的tokens中
    generated_list = generated_tokens.tolist()
    print(f"\n🔍 查找end_seq {end_seq} 在生成tokens中的位置:")
    
    # 手动查找
    found_positions = []
    for i in range(len(generated_list) - len(end_seq) + 1):
        if generated_list[i:i+len(end_seq)] == end_seq:
            found_positions.append(i)
    
    if found_positions:
        print(f"✅ 找到end_seq在位置: {found_positions}")
        for pos in found_positions:
            print(f"   位置 {pos}: {generated_list[pos:pos+len(end_seq)]}")
    else:
        print("❌ 未找到end_seq")
        print("🔍 让我们检查生成序列的各个部分:")
        
        # 分段显示生成的内容
        for i in range(0, len(generated_list), 10):
            segment = generated_list[i:i+10]
            decoded = tokenizer.decode(segment)
            print(f"   位置 {i}-{i+len(segment)-1}: {segment} -> {repr(decoded)}")
    
    # 测试subsequence_pos函数
    print(f"\n🧪 测试subsequence_pos函数:")
    result = subsequence_pos(generated_list, end_seq)
    print(f"subsequence_pos结果: {result}")
    
    # 尝试extract_response_tokens
    print(f"\n🎯 测试extract_response_tokens:")
    try:
        response_tokens = extract_response_tokens(generated_tokens, end_seq)
        if response_tokens is not None:
            print(f"✅ 成功提取响应tokens: {response_tokens.tolist()}")
            print(f"解码响应: {repr(tokenizer.decode(response_tokens))}")
        else:
            print("❌ extract_response_tokens返回None")
    except Exception as e:
        print(f"❌ extract_response_tokens出错: {e}")

if __name__ == "__main__":
    debug_token_extraction()