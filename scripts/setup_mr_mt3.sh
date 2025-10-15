#!/bin/bash
# MR-MT3 环境设置脚本

echo "🎼 MR-MT3 环境设置"
echo "=================="

# 检查当前目录
if [ "$(basename "$PWD")" != "diversity-eval" ]; then
    echo "❌ 请在diversity-eval目录下运行此脚本"
    echo "正确的执行方式:"
    echo "cd /home/evev/diversity-eval"
    echo "bash setup_mr_mt3.sh"
    exit 1
fi

# 激活conda环境
echo "🔄 激活mrmt3环境..."
source ~/miniconda3/etc/profile.d/conda.sh
conda activate mrmt3

# 检查环境
if [ "$CONDA_DEFAULT_ENV" != "mrmt3" ]; then
    echo "❌ 无法激活mrmt3环境"
    echo "请先创建环境: conda create -n mrmt3 python=3.10"
    exit 1
fi

echo "✅ 当前环境: $CONDA_DEFAULT_ENV"

# 安装huggingface_hub (如果未安装)
echo "🔄 检查huggingface_hub..."
if ! python -c "import huggingface_hub" 2>/dev/null; then
    echo "📦 安装huggingface_hub..."
    pip install huggingface_hub
else
    echo "✅ huggingface_hub已安装"
fi

# 运行下载脚本
echo "🔄 开始下载模型..."
python download_mr_mt3_models.py

echo "🎉 设置完成!"