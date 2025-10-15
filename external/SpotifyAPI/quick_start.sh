#!/bin/bash

# Spotify API 快速开始脚本

echo "🎵 Spotify API 数据集获取 - 快速开始"
echo "=================================="

# 激活环境
echo "🐍 激活spotifyapi环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate spotifyapi

# 检查当前目录
SPOTIFY_DIR="/home/evev/diversity-eval/external/SpotifyAPI"
cd "$SPOTIFY_DIR"

echo "📍 当前目录: $(pwd)"

# 选择操作
echo ""
echo "请选择要执行的操作:"
echo "1. 运行示例数据集获取"
echo "2. 处理自定义CSV文件"
echo "3. 测试Spotify API连接"
echo "4. 查看帮助信息"

read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        echo "🎵 运行示例数据集获取..."
        python examples/dataset_example.py
        ;;
    2)
        read -p "请输入CSV文件路径: " csv_file
        if [ -f "$csv_file" ]; then
            echo "🔄 处理自定义数据集..."
            python scripts/process_custom_dataset.py "$csv_file"
        else
            echo "❌ 文件不存在: $csv_file"
        fi
        ;;
    3)
        echo "🧪 测试Spotify API连接..."
        python test_spotify_connection.py
        ;;
    4)
        echo "📚 帮助信息:"
        echo ""
        echo "🎯 主要功能:"
        echo "  - 从Spotify获取音频特征数据"
        echo "  - 下载30秒预览音频"
        echo "  - 分析音乐多样性指标"
        echo ""
        echo "📂 文件结构:"
        echo "  - examples/dataset_example.py: 示例脚本"
        echo "  - scripts/process_custom_dataset.py: 自定义数据集处理"
        echo "  - config/spotify_config.json: API配置文件"
        echo ""
        echo "🚀 使用方法:"
        echo "  1. 确保已配置Spotify API凭据"
        echo "  2. 准备包含歌曲名和艺术家的CSV文件"
        echo "  3. 运行处理脚本获取丰富的音乐数据"
        ;;
    *)
        echo "❌ 无效选项"
        ;;
esac

echo ""
echo "✅ 操作完成！"