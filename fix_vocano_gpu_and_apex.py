#!/usr/bin/env python3
"""
修复VOCANO的GPU支持和Apex安装问题
"""

import os
import sys
import subprocess
import torch
from pathlib import Path

def check_gpu_availability():
    """检查GPU可用性"""
    print("🔍 检查GPU可用性...")
    
    # 检查CUDA是否可用
    if torch.cuda.is_available():
        gpu_count = torch.cuda.device_count()
        print(f"✅ 检测到 {gpu_count} 个GPU")
        for i in range(gpu_count):
            gpu_name = torch.cuda.get_device_name(i)
            print(f"   GPU {i}: {gpu_name}")
        return True
    else:
        print("❌ 未检测到可用的GPU")
        return False

def check_nvidia_smi():
    """检查nvidia-smi命令"""
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ nvidia-smi 可用")
            return True
        else:
            print("❌ nvidia-smi 不可用")
            return False
    except FileNotFoundError:
        print("❌ nvidia-smi 命令未找到")
        return False

def check_apex_installation():
    """检查Apex安装状态"""
    print("\n🔍 检查Apex安装状态...")
    
    try:
        import apex
        print("✅ Apex已安装")
        
        # 检查AMP功能
        try:
            from apex import amp
            print("✅ Apex AMP功能可用")
            return True
        except ImportError as e:
            print(f"⚠️  Apex AMP功能不可用: {e}")
            return False
    except ImportError:
        print("❌ Apex未安装")
        return False

def install_apex_properly():
    """按照官方推荐方式安装Apex"""
    print("\n🔧 安装Apex...")
    
    vocano_path = "/home/evev/diversity-eval/external/VOCANO"
    apex_path = os.path.join(vocano_path, "apex")
    
    if not os.path.exists(apex_path):
        print("❌ Apex源码目录不存在")
        return False
    
    try:
        # 切换到apex目录
        os.chdir(apex_path)
        
        # 使用官方推荐的安装方式
        print("📦 使用官方推荐方式安装Apex...")
        cmd = [
            sys.executable, "-m", "pip", "install", "-v", 
            "--disable-pip-version-check", "--no-cache-dir", 
            "--no-build-isolation", "."
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Apex安装成功")
            return True
        else:
            print(f"❌ Apex安装失败: {result.stderr}")
            
            # 尝试Python-only安装
            print("🔄 尝试Python-only安装...")
            cmd_python_only = [
                sys.executable, "-m", "pip", "install", "-v",
                "--disable-pip-version-check", "--no-cache-dir",
                "--no-build-isolation", "."
            ]
            
            result2 = subprocess.run(cmd_python_only, capture_output=True, text=True)
            if result2.returncode == 0:
                print("✅ Apex Python-only安装成功")
                return True
            else:
                print(f"❌ Python-only安装也失败: {result2.stderr}")
                return False
                
    except Exception as e:
        print(f"❌ 安装过程出错: {e}")
        return False

def fix_vocano_device_selection():
    """修复VOCANO脚本中的设备选择"""
    print("\n🔧 修复VOCANO设备选择...")
    
    script_path = "/home/evev/diversity-eval/pipelines/melody_extraction/vocano_melody_extraction.py"
    
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有GPU可用
        has_gpu = torch.cuda.is_available()
        
        if has_gpu:
            # 替换CPU为auto或GPU
            content = content.replace('"-d", "cpu"', '"-d", "auto"')
            device_choice = "auto"
        else:
            device_choice = "cpu"
        
        # 添加CuPy支持标志
        if '"-use_cp"' not in content and has_gpu:
            # 在设备参数后添加CuPy标志
            content = content.replace(
                '"-d", "auto"',
                '"-d", "auto", "-use_cp"'
            )
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 设备选择已更新为: {device_choice}")
        if has_gpu:
            print("✅ 已启用CuPy加速")
        
        return True
        
    except Exception as e:
        print(f"❌ 修复设备选择失败: {e}")
        return False

def install_cupy():
    """安装CuPy以获得GPU加速"""
    print("\n🔧 安装CuPy...")
    
    if not torch.cuda.is_available():
        print("⚠️  没有GPU，跳过CuPy安装")
        return True
    
    try:
        # 检查CUDA版本
        cuda_version = torch.version.cuda
        print(f"检测到CUDA版本: {cuda_version}")
        
        # 根据CUDA版本安装对应的CuPy
        if cuda_version.startswith("11."):
            cupy_package = "cupy-cuda11x"
        elif cuda_version.startswith("12."):
            cupy_package = "cupy-cuda12x"
        else:
            cupy_package = "cupy"
        
        cmd = [sys.executable, "-m", "pip", "install", cupy_package]
        print(f"执行命令: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ CuPy安装成功")
            return True
        else:
            print(f"❌ CuPy安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ CuPy安装过程出错: {e}")
        return False

def main():
    print("🎼 VOCANO GPU和Apex修复工具")
    print("=" * 50)
    
    # 检查GPU可用性
    has_gpu = check_gpu_availability()
    
    # 检查nvidia-smi
    has_nvidia_smi = check_nvidia_smi()
    
    # 检查Apex安装
    apex_ok = check_apex_installation()
    
    # 修复设备选择
    device_ok = fix_vocano_device_selection()
    
    # 安装CuPy（如果有GPU）
    cupy_ok = True
    if has_gpu:
        cupy_ok = install_cupy()
    
    # 重新安装Apex（如果需要）
    if not apex_ok:
        apex_ok = install_apex_properly()
    
    print("\n" + "=" * 50)
    print("🎯 修复结果:")
    print(f"   GPU可用: {'✅' if has_gpu else '❌'}")
    print(f"   nvidia-smi: {'✅' if has_nvidia_smi else '❌'}")
    print(f"   Apex安装: {'✅' if apex_ok else '❌'}")
    print(f"   设备选择: {'✅' if device_ok else '❌'}")
    print(f"   CuPy安装: {'✅' if cupy_ok else '❌'}")
    
    if all([device_ok, apex_ok, cupy_ok]):
        print("\n🎉 所有修复完成！")
        if has_gpu:
            print("💡 现在VOCANO将使用GPU加速运行")
        else:
            print("💡 VOCANO将在CPU上运行（建议使用GPU以获得更好性能）")
        print("📝 重新运行: python pipelines/melody_extraction/vocano_melody_extraction.py")
    else:
        print("\n⚠️  部分修复失败，请检查错误信息")

if __name__ == "__main__":
    main()