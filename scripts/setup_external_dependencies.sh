#!/bin/bash

echo "设置外部依赖..."

# 确保external目录存在
mkdir -p external

# 检查basic-pitch-torch是否存在
if [ -d "/home/evev/basic-pitch-torch" ]; then
    echo "发现basic-pitch-torch目录，正在移动到external..."
    
    # 移动整个basic-pitch-torch目录到external
    mv /home/evev/basic-pitch-torch external/
    
    echo "basic-pitch-torch已移动到external/basic-pitch-torch"
    
    # 创建符号链接以保持向后兼容性
    ln -sf $(pwd)/external/basic-pitch-torch /home/evev/basic-pitch-torch
    
    echo "已创建符号链接 /home/evev/basic-pitch-torch -> $(pwd)/external/basic-pitch-torch"
    
else
    echo "未找到/home/evev/basic-pitch-torch目录"
fi

# 检查是否有其他外部依赖需要移动
echo "检查其他外部依赖..."

# 如果有MR-MT3目录，也移动到external
if [ -d "MR-MT3" ]; then
    echo "移动MR-MT3到external..."
    mv MR-MT3 external/
    echo "MR-MT3已移动到external/MR-MT3"
fi

# 如果有swipe目录，也移动到external
if [ -d "swipe" ]; then
    echo "移动swipe到external..."
    mv swipe external/
    echo "swipe已移动到external/swipe"
fi

# 更新README文件
cat > README_EXTERNAL.md << 'EOF'
# External Dependencies

这个目录包含项目的外部依赖：

## 目录结构