#!/usr/bin/env python3
"""
修复版MR-MT3模型下载脚本
正确下载MR-MT3仓库和模型
"""

import os
import sys
import subprocess
from pathlib import Path

def download_mr_mt3_repo():
    """下载完整的MR-MT3仓库"""
    try:
        mr_mt3_path = "../MR-MT3"
        
        # 如果目录已存在，先检查是否是git仓库
        if os.path.exists(mr_mt3_path):
            if os.path.exists(os.path.join(mr_mt3_path, ".git")):
                print("🔄 MR-MT3仓库已存在，尝试更新...")
                result = subprocess.run(
                    ["git", "pull"], 
                    cwd=mr_mt3_path, 
                    capture_output=True, 
                    text=True
                )
                if result.returncode == 0:
                    print("✅ 仓库更新成功")
                    return True
                else:
                    print(f"⚠️  更新失败: {result.stderr}")
            else:
                print("⚠️  目录存在但不是git仓库，跳过下载")
                return True
        
        print("🔄 克隆MR-MT3仓库...")
        print(f"📁 目标路径: {os.path.abspath(mr_mt3_path)}")
        
        # 使用正确的GitHub仓库地址
        cmd = ["git", "clone", "https://github.com/gudgud96/MR-MT3.git", mr_mt3_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 仓库克隆成功!")
            return True
        else:
            print(f"❌ 克隆失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return False

def download_pretrained_models():
    """下载预训练模型"""
    try:
        from huggingface_hub import hf_hub_download, snapshot_download
        
        mr_mt3_path = "../MR-MT3"
        if not os.path.exists(mr_mt3_path):
            print("❌ MR-MT3目录不存在，请先下载仓库")
            return False
        
        print("🔄 下载预训练模型...")
        print("📍 使用正确的Hugging Face地址: gudgud1014/MR-MT3")
        
        # 使用正确的Hugging Face仓库地址
        try:
            # 尝试下载整个模型仓库到pretrained目录
            pretrained_path = os.path.join(mr_mt3_path, "pretrained")
            os.makedirs(pretrained_path, exist_ok=True)
            
            snapshot_download(
                repo_id="gudgud1014/MR-MT3",
                local_dir=pretrained_path,
                local_dir_use_symlinks=False
            )
            print("✅ 预训练模型下载成功!")
            return True
            
        except Exception as e:
            print(f"⚠️  snapshot_download失败: {e}")
            
            # 备选方案：尝试下载单个文件
            print("🔄 尝试下载单个模型文件...")
            model_files = [
                "pytorch_model.bin",
                "config.json", 
                "model.safetensors",
                "tokenizer.json",
                "tokenizer_config.json",
                "preprocessor_config.json"
            ]
            
            downloaded_files = []
            for filename in model_files:
                try:
                    print(f"📥 下载: {filename}")
                    file_path = hf_hub_download(
                        repo_id="gudgud1014/MR-MT3",
                        filename=filename,
                        local_dir=os.path.join(mr_mt3_path, "pretrained"),
                        local_dir_use_symlinks=False
                    )
                    downloaded_files.append(file_path)
                    print(f"✅ 下载成功: {filename}")
                except Exception as file_e:
                    print(f"⚠️  跳过 {filename}: {file_e}")
            
            if downloaded_files:
                print(f"✅ 成功下载 {len(downloaded_files)} 个模型文件")
                return True
            else:
                print("❌ 未能下载任何模型文件")
                return False
            
    except ImportError:
        print("❌ huggingface_hub未安装")
        print("请运行: pip install huggingface_hub")
        return False
    except Exception as e:
        print(f"❌ 模型下载失败: {e}")
        return False

def check_installation():
    """检查安装结果"""
    mr_mt3_path = "../MR-MT3"
    
    print("\n📊 检查安装结果:")
    
    if not os.path.exists(mr_mt3_path):
        print("❌ MR-MT3目录不存在")
        return False
    
    print(f"✅ MR-MT3目录: {os.path.abspath(mr_mt3_path)}")
    
    # 检查关键文件
    key_files = ["inference.py", "README.md", "requirements.txt"]
    for file in key_files:
        file_path = os.path.join(mr_mt3_path, file)
        if os.path.exists(file_path):
            print(f"✅ 找到: {file}")
        else:
            print(f"⚠️  缺失: {file}")
    
    # 检查预训练目录
    pretrained_path = os.path.join(mr_mt3_path, "pretrained")
    if os.path.exists(pretrained_path):
        print(f"✅ 预训练目录: {pretrained_path}")
        
        # 检查模型文件
        model_extensions = ['.bin', '.safetensors', '.ckpt', '.pt', '.pth', '.json']
        model_files = []
        
        for root, dirs, files in os.walk(pretrained_path):
            for file in files:
                if any(file.endswith(ext) for ext in model_extensions):
                    rel_path = os.path.relpath(os.path.join(root, file), pretrained_path)
                    model_files.append(rel_path)
        
        if model_files:
            print(f"✅ 找到 {len(model_files)} 个模型文件:")
            for file in model_files[:5]:  # 只显示前5个
                print(f"   - {file}")
            if len(model_files) > 5:
                print(f"   ... 还有 {len(model_files) - 5} 个文件")
        else:
            print("⚠️  预训练目录中未找到模型文件")
    else:
        print("⚠️  预训练目录不存在")
    
    return True

def main():
    print("🎼 修复版MR-MT3下载工具")
    print("=" * 50)
    print("📍 GitHub: https://github.com/gudgud96/MR-MT3")
    print("📍 Hugging Face: https://huggingface.co/gudgud1014/MR-MT3")
    
    # 检查当前目录
    current_dir = os.path.basename(os.getcwd())
    if current_dir != "diversity-eval":
        print(f"❌ 当前目录: {current_dir}")
        print("⚠️  请在diversity-eval目录下运行此脚本")
        sys.exit(1)
    
    print(f"📂 当前目录: {os.getcwd()}")
    
    # 步骤1: 下载仓库
    print("\n🔄 步骤1: 下载MR-MT3仓库")
    repo_success = download_mr_mt3_repo()
    
    # 步骤2: 下载预训练模型
    if repo_success:
        print("\n🔄 步骤2: 下载预训练模型")
        model_success = download_pretrained_models()
    else:
        model_success = False
    
    # 步骤3: 检查安装
    print("\n🔄 步骤3: 检查安装结果")
    check_installation()
    
    # 总结
    print("\n📋 安装总结:")
    if repo_success:
        print("✅ MR-MT3仓库下载成功")
    else:
        print("❌ MR-MT3仓库下载失败")
    
    if model_success:
        print("✅ 预训练模型下载成功")
    else:
        print("⚠️  预训练模型下载可能不完整")
    
    if repo_success:
        print("\n🎉 可以开始测试:")
        print("python test_mr_mt3_working.py --input_dir Shutter_Songs --output_dir mr_mt3_output/test --check_only")
    else:
        print("\n❌ 请手动下载MR-MT3:")
        print("git clone https://github.com/gudgud96/MR-MT3.git ../MR-MT3")
        print("然后从 https://huggingface.co/gudgud1014/MR-MT3 下载模型文件")

if __name__ == "__main__":
    main()