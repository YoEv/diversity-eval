#!/bin/bash
echo "🔧 按照官方推荐方式安装NVIDIA Apex..."

# 激活vocano环境
source ~/miniconda3/etc/profile.d/conda.sh
conda activate vocano

# 进入VOCANO的apex目录
cd /home/evev/diversity-eval/external/VOCANO/apex

echo "📦 检查当前环境..."
python -c "import torch; print(f'PyTorch版本: {torch.__version__}'); print(f'CUDA可用: {torch.cuda.is_available()}')"

echo "🚀 安装Apex (推荐方式)..."
# 尝试完整安装
APEX_CPP_EXT=1 APEX_CUDA_EXT=1 pip install -v --no-build-isolation .

# 如果失败，尝试Python-only安装
if [ $? -ne 0 ]; then
    echo "⚠️  完整安装失败，尝试Python-only安装..."
    pip install -v --disable-pip-version-check --no-cache-dir --no-build-isolation .
fi

echo "✅ Apex安装完成"

# 验证安装
echo "🧪 验证Apex安装..."
python -c "
try:
    import apex
    print('✅ Apex导入成功')
    try:
        from apex import amp
        print('✅ AMP功能可用')
    except ImportError as e:
        print(f'⚠️  AMP功能不可用: {e}')
except ImportError as e:
    print(f'❌ Apex导入失败: {e}')
"