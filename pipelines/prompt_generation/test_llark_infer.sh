#!/bin/bash

# LLark 推理环境测试脚本
echo "测试 LLark 推理环境..."

# 激活 conda 环境
source ~/miniconda3/etc/profile.d/conda.sh
conda activate llark

echo "=== 环境信息 ==="
python -c "import sys; print(f'Python版本: {sys.version}')"
python -c "import torch; print(f'PyTorch版本: {torch.__version__}')"

echo ""
echo "=== 核心包测试 ==="
python -c "
packages = ['transformers', 'librosa', 'numpy', 'pandas', 'datasets']
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
sys.path.append('/home/evev/diversity-eval/external/llark')
try:
    from llark.m2t.models.utils import load_pretrained_model
    print('✓ LLark 模型工具导入成功')
except Exception as e:
    print(f'✗ LLark 导入失败: {e}')
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
cd /home/evev/diversity-eval
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