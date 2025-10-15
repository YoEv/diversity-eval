#!/usr/bin/env python3
"""
测试MR-MT3官方脚本的工具
直接使用MR-MT3项目中的test.py和inference.py
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# MR-MT3路径
MR_MT3_PATH = "../MR-MT3"

def check_mr_mt3_files():
    """检查MR-MT3的关键文件"""
    print("🔍 检查MR-MT3关键文件...")
    
    if not os.path.exists(MR_MT3_PATH):
        print(f"❌ MR-MT3目录不存在: {MR_MT3_PATH}")
        return False
    
    # 检查关键文件
    key_files = [
        "test.py",
        "test.sh", 
        "inference.py",
        "pretrained"
    ]
    
    found_files = []
    missing_files = []
    
    for file in key_files:
        file_path = os.path.join(MR_MT3_PATH, file)
        if os.path.exists(file_path):
            found_files.append(file)
            print(f"✅ 找到: {file}")
        else:
            missing_files.append(file)
            print(f"❌ 缺失: {file}")
    
    # 列出MR-MT3目录的所有内容
    print(f"\n📁 MR-MT3目录内容:")
    try:
        items = os.listdir(MR_MT3_PATH)
        for item in sorted(items):
            item_path = os.path.join(MR_MT3_PATH, item)
            if os.path.isdir(item_path):
                print(f"   📁 {item}/")
            else:
                print(f"   📄 {item}")
    except Exception as e:
        print(f"❌ 无法读取目录: {e}")
        return False
    
    return len(found_files) > 0

def run_mr_mt3_test_sh():
    """运行MR-MT3的test.sh脚本"""
    test_sh_path = os.path.join(MR_MT3_PATH, "test.sh")
    
    if not os.path.exists(test_sh_path):
        print(f"❌ test.sh不存在: {test_sh_path}")
        return False
    
    print(f"🔧 运行MR-MT3官方test.sh...")
    
    try:
        # 读取test.sh内容
        with open(test_sh_path, 'r') as f:
            content = f.read()
        
        print(f"📄 test.sh内容:")
        print("-" * 50)
        print(content)
        print("-" * 50)
        
        # 尝试执行test.sh
        result = subprocess.run(
            ["bash", "test.sh"],
            cwd=MR_MT3_PATH,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(f"📝 执行结果:")
        print(f"返回码: {result.returncode}")
        if result.stdout:
            print(f"标准输出:\n{result.stdout}")
        if result.stderr:
            print(f"错误输出:\n{result.stderr}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 执行test.sh失败: {e}")
        return False

def run_mr_mt3_test_py(audio_dir=None):
    """运行MR-MT3的test.py脚本"""
    test_py_path = os.path.join(MR_MT3_PATH, "test.py")
    
    if not os.path.exists(test_py_path):
        print(f"❌ test.py不存在: {test_py_path}")
        return False
    
    print(f"🔧 运行MR-MT3官方test.py...")
    
    try:
        # 读取test.py的帮助信息
        result = subprocess.run(
            [sys.executable, "test.py", "--help"],
            cwd=MR_MT3_PATH,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"📄 test.py帮助信息:")
        print("-" * 50)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        print("-" * 50)
        
        # 如果提供了音频目录，尝试运行测试
        if audio_dir and os.path.exists(audio_dir):
            print(f"🎵 使用音频目录测试: {audio_dir}")
            
            cmd = [sys.executable, "test.py"]
            # 根据帮助信息添加参数
            if "--audio_dir" in result.stdout or "audio_dir" in result.stdout:
                cmd.extend(["--audio_dir", os.path.abspath(audio_dir)])
            elif "--input" in result.stdout:
                cmd.extend(["--input", os.path.abspath(audio_dir)])
            
            print(f"🔧 执行命令: {' '.join(cmd)}")
            
            test_result = subprocess.run(
                cmd,
                cwd=MR_MT3_PATH,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            print(f"📝 测试结果:")
            print(f"返回码: {test_result.returncode}")
            if test_result.stdout:
                print(f"标准输出:\n{test_result.stdout}")
            if test_result.stderr:
                print(f"错误输出:\n{test_result.stderr}")
            
            return test_result.returncode == 0
        
        return True
        
    except Exception as e:
        print(f"❌ 执行test.py失败: {e}")
        return False

def run_mr_mt3_inference(audio_file):
    """运行MR-MT3的inference.py脚本"""
    inference_py_path = os.path.join(MR_MT3_PATH, "inference.py")
    
    if not os.path.exists(inference_py_path):
        print(f"❌ inference.py不存在: {inference_py_path}")
        return False
    
    if not os.path.exists(audio_file):
        print(f"❌ 音频文件不存在: {audio_file}")
        return False
    
    print(f"🔧 运行MR-MT3官方inference.py...")
    
    try:
        # 先查看inference.py的帮助信息
        help_result = subprocess.run(
            [sys.executable, "inference.py", "--help"],
            cwd=MR_MT3_PATH,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"📄 inference.py帮助信息:")
        print("-" * 50)
        if help_result.stdout:
            print(help_result.stdout)
        if help_result.stderr:
            print(help_result.stderr)
        print("-" * 50)
        
        # 创建输出目录
        output_dir = "mr_mt3_official_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # 构建inference命令
        cmd = [sys.executable, "inference.py"]
        
        # 根据帮助信息添加参数
        if "--input_audio" in help_result.stdout:
            cmd.extend(["--input_audio", os.path.abspath(audio_file)])
        elif "--audio" in help_result.stdout:
            cmd.extend(["--audio", os.path.abspath(audio_file)])
        
        if "--output_dir" in help_result.stdout:
            cmd.extend(["--output_dir", os.path.abspath(output_dir)])
        elif "--output" in help_result.stdout:
            cmd.extend(["--output", os.path.abspath(output_dir)])
        
        print(f"🔧 执行命令: {' '.join(cmd)}")
        
        # 执行inference
        result = subprocess.run(
            cmd,
            cwd=MR_MT3_PATH,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        print(f"📝 inference结果:")
        print(f"返回码: {result.returncode}")
        if result.stdout:
            print(f"标准输出:\n{result.stdout}")
        if result.stderr:
            print(f"错误输出:\n{result.stderr}")
        
        # 检查输出文件
        if os.path.exists(output_dir):
            output_files = os.listdir(output_dir)
            if output_files:
                print(f"📁 生成的输出文件: {output_files}")
            else:
                print("⚠️  输出目录为空")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 执行inference.py失败: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="测试MR-MT3官方脚本")
    parser.add_argument("--test_audio", help="测试用的音频文件路径")
    parser.add_argument("--test_audio_dir", help="测试用的音频目录路径")
    parser.add_argument("--run_test_sh", action="store_true", help="运行test.sh")
    parser.add_argument("--run_test_py", action="store_true", help="运行test.py")
    parser.add_argument("--run_inference", action="store_true", help="运行inference.py")
    
    args = parser.parse_args()
    
    print("🎼 MR-MT3官方脚本测试工具")
    print("=" * 50)
    
    # 检查MR-MT3文件
    if not check_mr_mt3_files():
        print("\n❌ MR-MT3环境检查失败")
        return
    
    success_count = 0
    total_tests = 0
    
    # 运行test.sh
    if args.run_test_sh:
        total_tests += 1
        print(f"\n{'='*20} 测试 test.sh {'='*20}")
        if run_mr_mt3_test_sh():
            success_count += 1
            print("✅ test.sh 测试成功")
        else:
            print("❌ test.sh 测试失败")
    
    # 运行test.py
    if args.run_test_py:
        total_tests += 1
        print(f"\n{'='*20} 测试 test.py {'='*20}")
        if run_mr_mt3_test_py(args.test_audio_dir):
            success_count += 1
            print("✅ test.py 测试成功")
        else:
            print("❌ test.py 测试失败")
    
    # 运行inference.py
    if args.run_inference and args.test_audio:
        total_tests += 1
        print(f"\n{'='*20} 测试 inference.py {'='*20}")
        if run_mr_mt3_inference(args.test_audio):
            success_count += 1
            print("✅ inference.py 测试成功")
        else:
            print("❌ inference.py 测试失败")
    
    # 如果没有指定具体测试，默认检查所有文件
    if not any([args.run_test_sh, args.run_test_py, args.run_inference]):
        print(f"\n📋 使用示例:")
        print(f"python {sys.argv[0]} --run_test_sh")
        print(f"python {sys.argv[0]} --run_test_py --test_audio_dir Shutter_Songs")
        print(f"python {sys.argv[0]} --run_inference --test_audio Shutter_Songs/some_audio.wav")
    
    if total_tests > 0:
        print(f"\n📊 测试总结: {success_count}/{total_tests} 成功")

if __name__ == "__main__":
    main()