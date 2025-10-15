#!/bin/bash
echo "🔧 快速修复VOCANO GPU支持..."

# 激活环境
source ~/miniconda3/etc/profile.d/conda.sh
conda activate vocano

# 检查GPU状态
echo "🔍 检查GPU状态..."
python -c "
import torch
print(f'CUDA可用: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU数量: {torch.cuda.device_count()}')
    for i in range(torch.cuda.device_count()):
        print(f'GPU {i}: {torch.cuda.get_device_name(i)}')
"

# 修复VOCANO脚本中的设备选择
echo "🔧 修复设备选择..."
sed -i 's/"-d", "cpu"/"-d", "auto"/' /home/evev/diversity-eval/pipelines/melody_extraction/vocano_melody_extraction.py

# 安装CuPy（如果有GPU）
echo "📦 安装CuPy..."
python -c "
import torch
if torch.cuda.is_available():
    import subprocess
    import sys
    cuda_version = torch.version.cuda
    if cuda_version.startswith('11.'):
        package = 'cupy-cuda11x'
    elif cuda_version.startswith('12.'):
        package = 'cupy-cuda12x'
    else:
        package = 'cupy'
    print(f'安装 {package}...')
    subprocess.run([sys.executable, '-m', 'pip', 'install', package])
else:
    print('没有GPU，跳过CuPy安装')
"

echo "✅ 修复完成！现在重新运行VOCANO..."