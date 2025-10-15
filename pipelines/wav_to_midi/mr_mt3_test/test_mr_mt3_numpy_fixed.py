#!/usr/bin/env python3
"""
修复numpy兼容性的MR-MT3 音频转MIDI测试脚本
在导入其他模块前先修复numpy兼容性问题
"""

import sys
import os

# 首先修复numpy兼容性
def fix_numpy_compatibility():
    """修复numpy 1.23.5兼容性问题"""
    try:
        import numpy as np
        
        # 如果numpy没有dtypes属性，添加兼容性补丁
        if not hasattr(np, 'dtypes'):
            class DTypesCompat:
                def __init__(self):
                    self.StringDType = None
                    
                def __getattr__(self, name):
                    if name == 'StringDType':
                        return None
                    return getattr(np.dtype, name, None)
            
            np.dtypes = DTypesCompat()
            print("🔧 已修复numpy.dtypes兼容性问题")
            
        return True
    except Exception as e:
        print(f"❌ 修复numpy兼容性失败: {e}")
        return False

# 在导入其他模块前先修复numpy
fix_numpy_compatibility()

# 现在导入其他模块
import argparse
import glob
import subprocess
from pathlib import Path
import json
from datetime import datetime

# 添加MR-MT3路径到系统路径
MR_MT3_PATH = "../MR-MT3"

def check_environment():
    """检查基础环境"""
    print("🔍 检查基础环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"🐍 Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查必要的包
    required_packages = ['numpy', 'torch', 'librosa', 'transformers']
    for package in required_packages:
        try:
            module = __import__(package)
            if package == 'numpy':
                print(f"✅ {package}: {module.__version__} (已修复兼容性)")
            else:
                print(f"✅ {package}: 已安装")
        except ImportError:
            print(f"❌ {package}: 未安装")
            return False
        except Exception as e:
            print(f"⚠️  {package}: 导入异常 - {e}")
    
    return True

def check_mr_mt3_ready():
    """检查MR-MT3是否准备就绪"""
    print("\n🔍 检查MR-MT3环境...")
    
    if not os.path.exists(MR_MT3_PATH):
        print(f"❌ MR-MT3目录不存在: {MR_MT3_PATH}")
        return False
    
    # 检查inference.py
    inference_file = os.path.join(MR_MT3_PATH, "inference.py")
    if not os.path.exists(inference_file):
        print(f"❌ inference.py不存在: {inference_file}")
        return False
    
    print(f"✅ 找到inference.py: {inference_file}")
    
    # 检查预训练模型
    pretrained_dir = os.path.join(MR_MT3_PATH, "pretrained")
    if os.path.exists(pretrained_dir):
        model_files = []
        for ext in ['.ckpt', '.pt', '.pth', '.bin']:
            model_files.extend(glob.glob(os.path.join(pretrained_dir, f"*{ext}")))
        
        if model_files:
            print(f"✅ 找到预训练模型: {os.path.basename(model_files[0])}")
            return True
        else:
            print("⚠️  预训练目录存在但未找到模型文件")
            return False
    else:
        print("❌ 预训练目录不存在")
        return False

def transcribe_single_audio(audio_file, output_dir, model_path=None):
    """使用命令行方式调用MR-MT3转录单个音频文件"""
    try:
        print(f"🎵 处理音频: {os.path.basename(audio_file)}")
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成输出文件名
        audio_name = Path(audio_file).stem
        output_file = os.path.join(output_dir, f"{audio_name}.mid")
        
        # 构建命令
        cmd = [
            sys.executable, "inference.py",
            "--input_audio", os.path.abspath(audio_file),
            "--output_dir", os.path.abspath(output_dir)
        ]
        
        # 如果指定了模型路径
        if model_path:
            cmd.extend(["--model_path", model_path])
        
        print(f"🔧 执行命令: {' '.join(cmd)}")
        
        # 设置环境变量，确保numpy兼容性
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.abspath('.') + ':' + env.get('PYTHONPATH', '')
        
        # 执行命令
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd=MR_MT3_PATH,
            env=env,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            print(f"✅ 转录成功")
            if result.stdout:
                print(f"📝 输出: {result.stdout.strip()}")
            
            # 检查输出文件
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"📄 输出文件: {output_file} ({file_size} bytes)")
                return output_file
            else:
                # 查找可能的输出文件
                possible_files = glob.glob(os.path.join(output_dir, f"{audio_name}*"))
                if possible_files:
                    print(f"📄 找到输出文件: {possible_files[0]}")
                    return possible_files[0]
                else:
                    print("⚠️  命令成功但未找到输出文件")
                    return None
        else:
            print(f"❌ 转录失败 (返回码: {result.returncode})")
            if result.stderr:
                print(f"错误信息: {result.stderr}")
            if result.stdout:
                print(f"标准输出: {result.stdout}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"❌ 转录超时 (>5分钟)")
        return None
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        return None

def batch_transcribe(input_dir, output_dir, model_path=None):
    """批量转录音频文件"""
    print(f"\n🎼 开始批量转录")
    print(f"📁 输入目录: {input_dir}")
    print(f"📁 输出目录: {output_dir}")
    
    # 支持的音频格式
    audio_extensions = ['.wav', '.mp3', '.flac', '.m4a', '.aac']
    
    # 查找音频文件
    audio_files = []
    for ext in audio_extensions:
        pattern = os.path.join(input_dir, f"*{ext}")
        audio_files.extend(glob.glob(pattern))
    
    if not audio_files:
        print(f"❌ 在 {input_dir} 中未找到音频文件")
        return
    
    print(f"🎵 找到 {len(audio_files)} 个音频文件")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 处理结果统计
    results = {
        "start_time": datetime.now().isoformat(),
        "input_dir": input_dir,
        "output_dir": output_dir,
        "total_files": len(audio_files),
        "successful": 0,
        "failed": 0,
        "files": []
    }
    
    # 逐个处理音频文件
    for i, audio_file in enumerate(audio_files, 1):
        print(f"\n📊 进度: {i}/{len(audio_files)}")
        
        start_time = datetime.now()
        result = transcribe_single_audio(audio_file, output_dir, model_path)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 记录结果
        file_result = {
            "input_file": audio_file,
            "output_file": result,
            "success": result is not None,
            "duration": duration,
            "timestamp": end_time.isoformat()
        }
        
        results["files"].append(file_result)
        
        if result:
            results["successful"] += 1
            print(f"✅ 成功 (耗时: {duration:.1f}秒)")
        else:
            results["failed"] += 1
            print(f"❌ 失败 (耗时: {duration:.1f}秒)")
    
    # 保存结果报告
    results["end_time"] = datetime.now().isoformat()
    results["total_duration"] = (datetime.fromisoformat(results["end_time"]) - 
                                datetime.fromisoformat(results["start_time"])).total_seconds()
    
    report_file = os.path.join(output_dir, "transcription_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # 统计结果
    print(f"\n📊 处理完成:")
    print(f"✅ 成功: {results['successful']}")
    print(f"❌ 失败: {results['failed']}")
    print(f"⏱️  总耗时: {results['total_duration']:.1f}秒")
    print(f"📁 输出目录: {output_dir}")
    print(f"📄 详细报告: {report_file}")

def main():
    parser = argparse.ArgumentParser(description="修复numpy兼容性的MR-MT3 音频转MIDI工具")
    parser.add_argument("--input_dir", required=True, help="输入音频目录")
    parser.add_argument("--output_dir", required=True, help="输出MIDI目录")
    parser.add_argument("--model_path", help="预训练模型路径 (可选)")
    parser.add_argument("--check_only", action="store_true", help="仅检查环境，不进行转录")
    
    args = parser.parse_args()
    
    print("🎼 修复numpy兼容性的MR-MT3 音频转MIDI工具")
    print("=" * 60)
    
    # 检查基础环境
    if not check_environment():
        print("\n❌ 基础环境检查失败")
        return
    
    # 检查MR-MT3环境
    if not check_mr_mt3_ready():
        print("\n❌ MR-MT3环境检查失败")
        print("请确保:")
        print("1. 已下载MR-MT3到正确位置")
        print("2. 运行: python download_mr_mt3_models_fixed.py")
        return
    
    if args.check_only:
        print("\n✅ 环境检查完成，MR-MT3准备就绪")
        return
    
    # 检查输入目录
    if not os.path.exists(args.input_dir):
        print(f"❌ 输入目录不存在: {args.input_dir}")
        return
    
    # 进行批量转录
    batch_transcribe(
        args.input_dir, 
        args.output_dir, 
        args.model_path
    )

if __name__ == "__main__":
    main()