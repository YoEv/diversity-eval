#!/usr/bin/env python3
"""
完整修复VOCANO的GPU支持、Apex安装和CuPy加速问题
"""

import os
import sys
import subprocess
import torch
import re
from pathlib import Path

def check_system_status():
    """检查系统状态"""
    print("🔍 检查系统状态...")
    
    # 检查CUDA
    cuda_available = torch.cuda.is_available()
    gpu_count = torch.cuda.device_count() if cuda_available else 0
    
    print(f"   CUDA可用: {'✅' if cuda_available else '❌'}")
    if cuda_available:
        print(f"   GPU数量: {gpu_count}")
        for i in range(gpu_count):
            print(f"   GPU {i}: {torch.cuda.get_device_name(i)}")
    
    # 检查nvidia-smi
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=10)
        nvidia_smi_ok = result.returncode == 0
        print(f"   nvidia-smi: {'✅' if nvidia_smi_ok else '❌'}")
    except:
        nvidia_smi_ok = False
        print("   nvidia-smi: ❌")
    
    # 检查Apex
    try:
        import apex
        apex_ok = True
        print("   Apex: ✅")
        
        try:
            from apex import amp
            print("   Apex AMP: ✅")
        except:
            print("   Apex AMP: ❌")
    except:
        apex_ok = False
        print("   Apex: ❌")
    
    # 检查CuPy
    try:
        import cupy
        cupy_ok = True
        print("   CuPy: ✅")
    except:
        cupy_ok = False
        print("   CuPy: ❌")
    
    return {
        'cuda': cuda_available,
        'gpu_count': gpu_count,
        'nvidia_smi': nvidia_smi_ok,
        'apex': apex_ok,
        'cupy': cupy_ok
    }

def fix_vocano_script():
    """修复VOCANO脚本中的设备选择"""
    print("\n🔧 修复VOCANO脚本...")
    
    script_path = "/home/evev/diversity-eval/pipelines/melody_extraction/vocano_melody_extraction.py"
    
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已经修复过
        if 'torch.cuda.is_available()' in content:
            print("   ✅ 脚本已经包含GPU检测代码")
            return True
        
        # 找到需要替换的部分
        old_pattern = r'# 构建VOCANO命令\s*\n\s*cmd = \[\s*\n\s*sys\.executable, "-m", "vocano\.transcription",\s*\n\s*"-n", output_name,\s*\n\s*"-wd", input_wav,\s*\n\s*"-d", "cpu"[^\]]*\]'
        
        new_code = '''# 检查GPU可用性并选择设备
            if torch.cuda.is_available():
                device = "auto"  # 自动选择最佳GPU
                use_cupy = True
                print(f"   🚀 使用GPU加速 (检测到 {torch.cuda.device_count()} 个GPU)")
            else:
                device = "cpu"
                use_cupy = False
                print("   ⚠️  使用CPU运行 (未检测到GPU)")
            
            # 构建VOCANO命令
            cmd = [
                sys.executable, "-m", "vocano.transcription",
                "-n", output_name,
                "-wd", input_wav,
                "-d", device
            ]
            
            # 如果有GPU，添加CuPy加速标志
            if use_cupy:
                cmd.extend(["-use_cp"])'''
        
        # 执行替换
        new_content = re.sub(old_pattern, new_code, content, flags=re.MULTILINE | re.DOTALL)
        
        # 如果正则替换失败，尝试简单替换
        if new_content == content:
            new_content = content.replace('"-d", "cpu"', '"-d", "auto"')
            if '"-use_cp"' not in new_content:
                new_content = new_content.replace('"-d", "auto"', '"-d", "auto", "-use_cp"')
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("   ✅ VOCANO脚本已修复")
        return True
        
    except Exception as e:
        print(f"   ❌ 修复失败: {e}")
        return False

def install_cupy():
    """安装CuPy"""
    print("\n🔧 安装CuPy...")
    
    if not torch.cuda.is_available():
        print("   ⚠️  没有GPU，跳过CuPy安装")
        return True
    
    try:
        # 检查是否已安装
        import cupy
        print("   ✅ CuPy已安装")
        return True
    except ImportError:
        pass
    
    try:
        # 根据CUDA版本选择CuPy包
        cuda_version = torch.version.cuda
        print(f"   检测到CUDA版本: {cuda_version}")
        
        if cuda_version.startswith("11."):
            package = "cupy-cuda11x"
        elif cuda_version.startswith("12."):
            package = "cupy-cuda12x"
        else:
            package = "cupy"
        
        print(f"   安装 {package}...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ CuPy安装成功")
            return True
        else:
            print(f"   ❌ CuPy安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ CuPy安装出错: {e}")
        return False

def reinstall_apex():
    """重新安装Apex"""
    print("\n🔧 重新安装Apex...")
    
    apex_path = "/home/evev/diversity-eval/external/VOCANO/apex"
    
    if not os.path.exists(apex_path):
        print("   ❌ Apex源码目录不存在")
        return False
    
    try:
        # 卸载现有的apex
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "apex", "-y"], 
                      capture_output=True)
        
        # 切换到apex目录
        original_cwd = os.getcwd()
        os.chdir(apex_path)
        
        try:
            # 尝试完整安装
            print("   尝试完整安装...")
            env = os.environ.copy()
            env['APEX_CPP_EXT'] = '1'
            env['APEX_CUDA_EXT'] = '1'
            
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-v", 
                "--no-build-isolation", "."
            ], capture_output=True, text=True, env=env)
            
            if result.returncode == 0:
                print("   ✅ Apex完整安装成功")
                return True
            else:
                print("   ⚠️  完整安装失败，尝试Python-only安装...")
                
                # Python-only安装
                result2 = subprocess.run([
                    sys.executable, "-m", "pip", "install", "-v",
                    "--disable-pip-version-check", "--no-cache-dir",
                    "--no-build-isolation", "."
                ], capture_output=True, text=True)
                
                if result2.returncode == 0:
                    print("   ✅ Apex Python-only安装成功")
                    return True
                else:
                    print(f"   ❌ 所有安装方式都失败")
                    return False
                    
        finally:
            os.chdir(original_cwd)
            
    except Exception as e:
        print(f"   ❌ 安装过程出错: {e}")
        return False

def main():
    print("🎼 VOCANO完整修复工具")
    print("=" * 60)
    
    # 检查系统状态
    status = check_system_status()
    
    # 修复VOCANO脚本
    script_fixed = fix_vocano_script()
    
    # 安装CuPy（如果有GPU）
    cupy_ok = True
    if status['cuda'] and not status['cupy']:
        cupy_ok = install_cupy()
    
    # 重新安装Apex（如果需要）
    apex_ok = status['apex']
    if not apex_ok:
        apex_ok = reinstall_apex()
    
    print("\n" + "=" * 60)
    print("🎯 修复结果总结:")
    print(f"   GPU可用: {'✅' if status['cuda'] else '❌'}")
    print(f"   VOCANO脚本: {'✅' if script_fixed else '❌'}")
    print(f"   Apex安装: {'✅' if apex_ok else '❌'}")
    print(f"   CuPy安装: {'✅' if cupy_ok else '❌'}")
    
    if script_fixed and apex_ok and cupy_ok:
        print("\n🎉 所有修复完成！")
        if status['cuda']:
            print("💡 VOCANO现在将使用GPU加速运行")
        else:
            print("💡 VOCANO将在CPU上运行")
        print("📝 重新运行: python pipelines/melody_extraction/vocano_melody_extraction.py")
    else:
        print("\n⚠️  部分修复失败，请检查错误信息")
    
    # 提供手动修复建议
    print("\n📋 手动修复建议:")
    if not status['cuda']:
        print("   - 安装NVIDIA驱动和CUDA工具包")
    if not apex_ok:
        print("   - 手动编译安装Apex: cd external/VOCANO/apex && pip install -v .")
    if not cupy_ok and status['cuda']:
        print("   - 手动安装CuPy: pip install cupy-cuda11x 或 cupy-cuda12x")

if __name__ == "__main__":
    main()