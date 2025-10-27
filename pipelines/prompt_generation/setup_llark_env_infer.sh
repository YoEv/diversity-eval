#!/bin/bash

# LLark 推理环境设置脚本
# 只安装推理所需的依赖，避免训练相关的包冲突

echo "设置 LLark 推理环境..."

# 设置 LLark 路径
LLARK_PATH="/home/evev/diversity-eval/external/llark"

# 检查是否已存在 llark 环境
if conda env list | grep -q "llark"; then
    echo "LLark 环境已存在，将重新配置..."
    conda activate llark
else
    echo "创建新的 conda 环境: llark"
    conda create -n llark python=3.9 -y
    conda activate llark
fi

# 切换到 LLark 目录
cd "$LLARK_PATH"

echo "安装 LLark 推理依赖..."
# 只安装 requirements.txt (推理用)，不安装 train-requirements.txt (训练用)
if [ -f "requirements.txt" ]; then
    echo "安装基础推理依赖..."
    pip install -r requirements.txt
else
    echo "警告: 未找到 requirements.txt"
fi

# 安装额外的推理工具
echo "安装额外的推理工具..."
pip install apache-beam tqdm

# 手动添加 LLark 路径到 Python 路径
echo "添加 LLark 到 Python 路径..."
BASHRC_LINE="export PYTHONPATH=\"$LLARK_PATH:\$PYTHONPATH\""
if ! grep -q "$BASHRC_LINE" ~/.bashrc; then
    echo "$BASHRC_LINE" >> ~/.bashrc
    echo "已添加 PYTHONPATH 到 ~/.bashrc"
else
    echo "PYTHONPATH 已存在于 ~/.bashrc"
fi

echo ""
echo "✓ LLark 推理环境设置完成!"
echo ""
echo "重要提示:"
echo "1. 重启终端或运行: source ~/.bashrc"
echo "2. 激活环境: conda activate llark"
echo ""
echo "测试安装:"
echo "  python -c 'import torch; print(f\"PyTorch版本: {torch.__version__}\")'"
echo "  python -c 'from llark.m2t.models.utils import load_pretrained_model; print(\"LLark导入成功\")'"
echo ""
echo "环境特点:"
echo "- 使用 PyTorch 1.13.0 (LLark 推理要求)"
echo "- 跳过训练相关依赖 (accelerate, triton, flash-attn)"
echo "- 专注于推理功能，避免版本冲突"
echo ""
echo "使用示例:"
echo "1. 演示模式 (无需模型):"
echo "   conda activate llark"
echo "   python /home/evev/diversity-eval/pipelines/prompt_generation/llark_prompt_generator.py --demo"
echo ""
echo "2. 实际推理 (需要模型):"
echo "   conda activate llark"
echo "   python /home/evev/diversity-eval/external/llark/scripts/inference/infer_from_encodings.py \\"
echo "     --audio-encodings-dir /path/to/encodings \\"
echo "     --model_name_or_path /path/to/model \\"
echo "     --prompt 'Describe this music:'"