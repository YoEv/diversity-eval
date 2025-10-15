#!/usr/bin/env python3
"""
实用版MR-MT3 音频转MIDI测试脚本
基于实际的MR-MT3 inference.py文件
"""

import os
import sys
import argparse
import glob
import subprocess
from pathlib import Path
import json
from datetime import datetime

# 添加MR-MT3路径到系统路径
MR_MT3_PATH = "../MR-MT3"

def check_mr_mt3_ready():
    """检查MR-MT3是否准备就绪"""
    print("🔍 检查MR-MT3环境...")
    
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
        model_files = [f for f in os.listdir(pretrained_dir) if f.endswith(('.ckpt', '.pt', '.pth', '.bin'))]
        if model_files:
            print(f"✅ 找到预训练模型: {model_files[0]}")
        else:
            print("⚠️  预训练目录存在但未找到模型文件")
    else:
        print("⚠️  预训练目录不存在")
    
    return True

def transcribe_single_audio(audio_file, output_dir, model_path=None):
    """
    使用MR-MT3转录单个音频文件
    通过调用inference.py实现
    """
    try:
        print(f"🎵 处理音频: {os.path.basename(audio_file)}")
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成输出文件名
        audio_name = Path(audio_file).stem
        output_file = os.path.join(output_dir, f"{audio_name}.mid")
        
        # 构建inference命令
        # 这里的参数可能需要根据实际的inference.py调整
        cmd = [
            "python", 
            os.path.join(MR_MT3_PATH, "inference.py"),
            "--audio_path", audio_file,
            "--output_path", output_file
        ]
        
        # 如果指定了模型路径，添加到命令中
        if model_path:
            cmd.extend(["--model_path", model_path])
        
        print(f"🔄 执行命令: {' '.join(cmd)}")
        
        # 执行转录
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd=MR_MT3_PATH  # 在MR-MT3目录下执行
        )
        
        if result.returncode == 0:
            print(f"✅ 转录成功: {output_file}")
            if result.stdout:
                print(f"📝 输出: {result.stdout.strip()}")
            return output_file
        else:
            print(f"❌ 转录失败")
            print(f"错误信息: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        return None

def transcribe_with_python_api(audio_file, output_dir):
    """
    尝试直接使用Python API进行转录
    """
    try:
        print(f"🐍 尝试Python API转录: {os.path.basename(audio_file)}")
        
        # 添加MR-MT3路径
        sys.path.insert(0, MR_MT3_PATH)
        
        # 尝试导入inference模块
        import inference
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成输出文件名
        audio_name = Path(audio_file).stem
        output_file = os.path.join(output_dir, f"{audio_name}.mid")
        
        # 调用inference函数（具体函数名可能需要调整）
        # 这里是常见的API调用模式
        if hasattr(inference, 'transcribe'):
            result = inference.transcribe(audio_file, output_file)
        elif hasattr(inference, 'main'):
            # 如果inference.py有main函数，尝试调用
            sys.argv = ['inference.py', '--audio_path', audio_file, '--output_path', output_file]
            result = inference.main()
        else:
            print("❌ 无法找到合适的转录函数")
            return None
        
        if os.path.exists(output_file):
            print(f"✅ 转录成功: {output_file}")
            return output_file
        else:
            print("❌ 输出文件未生成")
            return None
            
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return None
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        return None

def batch_transcribe(input_dir, output_dir, model_path=None, use_python_api=False):
    """批量处理音频目录"""
    print(f"\n🎼 开始批量转录")
    print(f"📂 输入目录: {input_dir}")
    print(f"📁 输出目录: {output_dir}")
    print(f"🔧 使用Python API: {use_python_api}")
    
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
    
    # 记录处理结果
    results = {
        "start_time": datetime.now().isoformat(),
        "input_dir": input_dir,
        "output_dir": output_dir,
        "total_files": len(audio_files),
        "successful": 0,
        "failed": 0,
        "files": []
    }
    
    # 批量处理
    for i, audio_file in enumerate(audio_files, 1):
        print(f"\n[{i}/{len(audio_files)}] 处理: {os.path.basename(audio_file)}")
        
        start_time = datetime.now()
        
        if use_python_api:
            result = transcribe_with_python_api(audio_file, output_dir)
        else:
            result = transcribe_single_audio(audio_file, output_dir, model_path)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        file_result = {
            "audio_file": audio_file,
            "output_file": result,
            "success": result is not None,
            "duration_seconds": duration,
            "timestamp": start_time.isoformat()
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
    parser = argparse.ArgumentParser(description="实用版MR-MT3 音频转MIDI工具")
    parser.add_argument("--input_dir", required=True, help="输入音频目录")
    parser.add_argument("--output_dir", required=True, help="输出MIDI目录")
    parser.add_argument("--model_path", help="预训练模型路径 (可选)")
    parser.add_argument("--use_python_api", action="store_true", help="使用Python API而不是命令行")
    parser.add_argument("--check_only", action="store_true", help="仅检查环境，不进行转录")
    
    args = parser.parse_args()
    
    print("🎼 实用版MR-MT3 音频转MIDI工具")
    print("=" * 50)
    
    # 检查MR-MT3环境
    if not check_mr_mt3_ready():
        print("\n❌ MR-MT3环境检查失败")
        print("请确保:")
        print("1. 已下载MR-MT3到正确位置")
        print("2. 运行: python download_mr_mt3_models.py")
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
        args.model_path,
        args.use_python_api
    )

if __name__ == "__main__":
    main()