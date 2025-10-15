#!/usr/bin/env python3
"""
修复版MR-MT3 音频转MIDI测试脚本
先检查MR-MT3的实际代码结构，然后进行适配
"""

import os
import sys
import argparse
import glob
from pathlib import Path

# 添加MR-MT3路径到系统路径
MR_MT3_PATH = "../MR-MT3"

def check_mr_mt3_structure():
    """检查MR-MT3的目录结构和可用模块"""
    print("🔍 检查MR-MT3目录结构...")
    
    if not os.path.exists(MR_MT3_PATH):
        print(f"❌ MR-MT3目录不存在: {MR_MT3_PATH}")
        print("请确保:")
        print("1. 已下载MR-MT3到正确位置")
        print("2. 运行: python download_mr_mt3_models.py")
        return False
    
    print(f"✅ MR-MT3目录存在: {os.path.abspath(MR_MT3_PATH)}")
    
    # 列出MR-MT3目录内容
    try:
        items = os.listdir(MR_MT3_PATH)
        print(f"📁 MR-MT3目录内容:")
        for item in sorted(items):
            item_path = os.path.join(MR_MT3_PATH, item)
            if os.path.isdir(item_path):
                print(f"   📁 {item}/")
            else:
                print(f"   📄 {item}")
    except Exception as e:
        print(f"❌ 无法读取MR-MT3目录: {e}")
        return False
    
    return True

def check_python_files():
    """检查MR-MT3中的Python文件"""
    print("\n🐍 检查Python文件...")
    
    python_files = []
    for root, dirs, files in os.walk(MR_MT3_PATH):
        for file in files:
            if file.endswith('.py'):
                rel_path = os.path.relpath(os.path.join(root, file), MR_MT3_PATH)
                python_files.append(rel_path)
    
    if python_files:
        print(f"📄 找到 {len(python_files)} 个Python文件:")
        for file in sorted(python_files)[:10]:  # 只显示前10个
            print(f"   - {file}")
        if len(python_files) > 10:
            print(f"   ... 还有 {len(python_files) - 10} 个文件")
    else:
        print("❌ 未找到Python文件")
    
    return python_files

def try_import_mr_mt3():
    """尝试导入MR-MT3模块"""
    print("\n📦 尝试导入MR-MT3模块...")
    
    # 添加路径
    sys.path.insert(0, MR_MT3_PATH)
    
    # 尝试常见的导入
    import_attempts = [
        ("torch", "PyTorch"),
        ("transformers", "Transformers"),
        ("librosa", "Librosa"),
        ("numpy", "NumPy"),
    ]
    
    for module, name in import_attempts:
        try:
            __import__(module)
            print(f"✅ {name} 可用")
        except ImportError:
            print(f"❌ {name} 未安装")
    
    # 尝试导入MR-MT3特定模块
    mr_mt3_modules = []
    
    # 检查是否有常见的模型文件
    potential_files = [
        "model.py", "models.py", "mt3_model.py", "mr_mt3.py",
        "inference.py", "predict.py", "transcribe.py"
    ]
    
    for file in potential_files:
        file_path = os.path.join(MR_MT3_PATH, file)
        if os.path.exists(file_path):
            print(f"📄 找到: {file}")
            mr_mt3_modules.append(file)
    
    return mr_mt3_modules

def create_simple_transcriber():
    """创建一个简单的转录器，基于实际可用的模块"""
    print("\n🔧 创建简化转录器...")
    
    # 这里我们创建一个占位符函数
    # 实际实现需要根据MR-MT3的真实API调整
    def transcribe_audio(audio_file, output_file):
        """占位符转录函数"""
        print(f"🎵 模拟处理: {os.path.basename(audio_file)}")
        print(f"📁 输出: {output_file}")
        
        # 创建一个空的MIDI文件作为占位符
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write("# 占位符MIDI文件\n")
            f.write(f"# 原始音频: {audio_file}\n")
        
        return True
    
    return transcribe_audio

def batch_transcribe(input_dir, output_dir):
    """批量处理音频目录"""
    print(f"\n🎼 开始批量转录")
    print(f"📂 输入目录: {input_dir}")
    print(f"📁 输出目录: {output_dir}")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 查找音频文件
    audio_extensions = ['*.wav', '*.mp3', '*.flac', '*.m4a']
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(glob.glob(os.path.join(input_dir, ext)))
    
    if not audio_files:
        print(f"❌ 在 {input_dir} 中未找到音频文件")
        return
    
    print(f"📁 找到 {len(audio_files)} 个音频文件")
    
    # 获取转录器
    transcriber = create_simple_transcriber()
    
    # 批量处理
    successful = 0
    failed = 0
    
    for i, audio_file in enumerate(audio_files, 1):
        print(f"\n[{i}/{len(audio_files)}] 处理: {os.path.basename(audio_file)}")
        
        # 生成输出文件名
        audio_name = Path(audio_file).stem
        output_file = os.path.join(output_dir, f"{audio_name}.mid")
        
        try:
            result = transcriber(audio_file, output_file)
            if result:
                successful += 1
                print(f"✅ 成功")
            else:
                failed += 1
                print(f"❌ 失败")
        except Exception as e:
            failed += 1
            print(f"❌ 错误: {e}")
    
    # 统计结果
    print(f"\n📊 处理完成:")
    print(f"✅ 成功: {successful}")
    print(f"❌ 失败: {failed}")
    print(f"📁 输出目录: {output_dir}")

def main():
    parser = argparse.ArgumentParser(description="修复版MR-MT3 音频转MIDI工具")
    parser.add_argument("--input_dir", required=True, help="输入音频目录")
    parser.add_argument("--output_dir", required=True, help="输出MIDI目录")
    parser.add_argument("--check_only", action="store_true", help="仅检查环境，不进行转录")
    
    args = parser.parse_args()
    
    print("🎼 修复版MR-MT3 音频转MIDI工具")
    print("=" * 50)
    
    # 检查MR-MT3结构
    if not check_mr_mt3_structure():
        return
    
    # 检查Python文件
    python_files = check_python_files()
    
    # 尝试导入模块
    mr_mt3_modules = try_import_mr_mt3()
    
    if args.check_only:
        print("\n✅ 环境检查完成")
        return
    
    # 检查输入目录
    if not os.path.exists(args.input_dir):
        print(f"❌ 输入目录不存在: {args.input_dir}")
        return
    
    print(f"\n⚠️  注意: 当前使用占位符转录器")
    print("实际的MR-MT3转录功能需要根据真实的API进行适配")
    
    # 进行批量转录
    batch_transcribe(args.input_dir, args.output_dir)

if __name__ == "__main__":
    main()