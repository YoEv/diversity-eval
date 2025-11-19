#!/bin/bash

# 设置 LLark 环境的脚本
# 创建 conda 环境名为 llark

echo "Setting up LLark environment..."

# 检查是否已存在 llark 环境
# if conda env list | grep -q "llark"; then
#     echo "LLark environment already exists. Activating..."
#     conda activate llark
# else
#     echo "Creating new conda environment: llark"
    
#     # 创建基础环境
#     conda create -n llark python=3.9 -y
    
#     # 激活环境
#     conda activate llark
    
# 基础模型之外，为了加速，又按炸胡干了很多其他的。

# 安装基础依赖
    echo "Installing basic dependencies..."
    cd /home/evev/diversity-eval/external/llark
    
    # Install LLark base requirements first (uses torch 1.13.0)
    echo "Installing LLark base requirements..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    # Install additional dependencies compatible with torch 1.13.0
    echo "Installing additional dependencies..."
    pip install apache-beam tqdm
    
    # # Handle train requirements with version fixes
    # echo "Installing train requirements with compatible versions..."
    # if [ -f "train-requirements.txt" ]; then
    #     # Install train requirements but skip problematic triton version
    #     echo "Installing accelerate and wandb..."
    #     pip install accelerate wandb
        
    #     # Try to install a compatible triton version
    #     echo "Installing compatible triton version..."
    #     pip install triton==2.0.0 || echo "Warning: Could not install triton, continuing without it..."
        
    #     # Try to install flash-attn (may fail on some systems)
    #     echo "Installing flash-attn..."
    #     pip install flash-attn==1.0.3.post0 || echo "Warning: Could not install flash-attn, continuing without it..."
    # fi
    
    pip install transformers
    pip install librosa
    pip install numpy pandas
    pip install tqdm
    pip install apache-beam
    pip install madmom
    
    # 安装 LLark 特定依赖
    echo "Installing LLark specific dependencies..."
    cd /home/evev/diversity-eval/external/llark
    
    # 如果有 requirements.txt，安装它
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    # 如果有 train-requirements.txt，也安装它
    if [ -f "train-requirements.txt" ]; then
        pip install -r train-requirements.txt
    fi
    
    # 手动添加 LLark 路径到 Python 路径（而不是 pip install -e）
    echo "Adding LLark to Python path..."
    echo "export PYTHONPATH=\"/home/evev/diversity-eval/external/llark:\$PYTHONPATH\"" >> ~/.bashrc
# fi

echo "LLark environment setup complete!"
echo "To activate the environment, run: conda activate llark"
echo ""
echo "IMPORTANT: After setup, restart your terminal or run:"
echo "   source ~/.bashrc"
echo "   conda activate llark"
echo ""
echo "Test the installation with:"
echo "   python -c 'import torch; print(f\"PyTorch version: {torch.__version__}\")'"
echo "   python -c 'import sys; print(sys.path)'"
echo "   python -c 'from llark.m2t.models.utils import load_pretrained_model; print(\"LLark imported successfully\")'"
echo ""
echo "Note: Some optional packages (triton, flash-attn) may not install on all systems."
echo "This is normal and won't affect basic LLark functionality."
echo ""
echo "Usage examples:"
echo "1. Demo mode (no model required):"
echo "   conda activate llark"
echo "   python /home/evev/diversity-eval/pipelines/prompt_generation/llark_prompt_generator.py --demo_mode"
echo ""
echo "2. With actual LLark model (when available):"
echo "   conda activate llark"
echo "   python /home/evev/diversity-eval/pipelines/prompt_generation/llark_prompt_generator.py --model_path /path/to/llark/model"