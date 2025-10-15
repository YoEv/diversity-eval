#!/bin/bash

echo "🎼 Basic Pitch PyTorch - 音频转MIDI工具"
echo "=================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
python3 -c "import torch, librosa, pretty_midi; print('✅ 依赖检查通过')" || {
    echo "❌ 缺少依赖，请运行: pip install -r requirements.txt"
    exit 1
}

# 检查模型文件
if [ ! -f "assets/basic_pitch_pytorch_icassp_2022.pth" ]; then
    echo "❌ 模型文件不存在: assets/basic_pitch_pytorch_icassp_2022.pth"
    exit 1
fi

echo "✅ 环境检查完成"
echo ""

# 运行转换
echo "🚀 开始转换..."
python3 test_shutter_songs.py

echo ""
echo "🎯 转换完成！查看 output_midi 目录中的结果"