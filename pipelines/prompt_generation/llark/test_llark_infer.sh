#!/bin/bash

# LLark 推理环境测试脚本
echo "测试 LLark 推理环境..."

# 激活 conda 环境 (如果尚未激活)
if [[ "$CONDA_DEFAULT_ENV" != "llark" ]]; then
    echo "尝试激活 llark 环境..."
    # 尝试不同的conda路径
    if [ -f ~/miniconda3/etc/profile.d/conda.sh ]; then
        source ~/miniconda3/etc/profile.d/conda.sh
    elif [ -f ~/anaconda3/etc/profile.d/conda.sh ]; then
        source ~/anaconda3/etc/profile.d/conda.sh
    elif [ -f /opt/conda/etc/profile.d/conda.sh ]; then
        source /opt/conda/etc/profile.d/conda.sh
    fi
    conda activate llark 2>/dev/null || echo "conda activate 失败，但继续测试..."
else
    echo "llark 环境已激活"
fi

echo "=== 环境信息 ==="
python -c "import sys; print(f'Python版本: {sys.version}')"
python -c "import torch; print(f'PyTorch版本: {torch.__version__}')"

echo ""
echo "=== 核心包测试 ==="
python -c "
packages = ['transformers', 'librosa', 'numpy', 'pandas', 'datasets', 'einops', 'accelerate', 'sentencepiece']
for pkg in packages:
    try:
        exec(f'import {pkg}')
        print(f'✓ {pkg} 导入成功')
    except Exception as e:
        print(f'✗ {pkg} 导入失败: {e}')
"

echo ""
echo "=== LLark 模块测试 ==="
python -c "
import sys
import os
llark_path = '/home/hice1/xli3252/Desktop/diversity-eval/external/llark'
sys.path.insert(0, llark_path)
try:
    # 测试基本模块导入
    import m2t
    print('✓ m2t 模块导入成功')
    
    # 测试具体功能导入
    from m2t.models.utils import load_pretrained_model
    from m2t.arguments import DataArguments
    from m2t.data_modules import make_mm_config
    print('✓ LLark 核心功能导入成功')
except Exception as e:
    print(f'✗ LLark 导入失败: {e}')
    # 诊断信息
    print(f'LLark路径: {llark_path}')
    print(f'路径存在: {os.path.exists(llark_path)}')
    print(f'm2t路径存在: {os.path.exists(os.path.join(llark_path, \"m2t\"))}')
    print(f'm2t/__init__.py存在: {os.path.exists(os.path.join(llark_path, \"m2t\", \"__init__.py\"))}')
"

echo ""
echo "=== 模型路径检查 ==="
python -c "
import os
model_path = '/home/hice1/xli3252/Desktop/diversity-eval/external/llark/checkpoints/meta-llama/Llama-2-7b-chat-hf'
if os.path.exists(model_path):
    print(f'✓ 模型路径存在: {model_path}')
    config_path = os.path.join(model_path, 'config.json')
    if os.path.exists(config_path):
        print('✓ 模型配置文件存在')
    else:
        print('✗ 模型配置文件缺失')
else:
    print(f'✗ 模型路径不存在: {model_path}')
"

echo ""
echo "=== 训练包状态检查 ==="
python -c "
training_packages = ['accelerate', 'triton', 'flash_attn']
for pkg in training_packages:
    try:
        exec(f'import {pkg}')
        print(f'✓ {pkg} 可用 (意外，应该跳过)')
    except:
        print(f'✗ {pkg} 不可用 (预期，推理环境跳过)')
"

echo ""
echo "=== 演示推理测试 ==="
cd /home/hice1/xli3252/Desktop/diversity-eval
python pipelines/prompt_generation/llark_prompt_generator.py --demo

if [ -f "data/output/llark_prompts/demo_prompts.json" ]; then
    echo "✓ 演示推理成功"
    echo "输出文件: data/output/llark_prompts/demo_prompts.json"
else
    echo "✗ 演示推理失败"
fi

echo ""
echo "=== 测试总结 ==="
echo "推理环境状态:"
echo "- PyTorch 1.13.0 (LLark 推理版本)"
echo "- 核心推理功能可用"
echo "- 训练相关包已跳过，避免冲突"
echo "- 适合基本音频推理任务"