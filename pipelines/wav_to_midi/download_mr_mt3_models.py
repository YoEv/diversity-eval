#!/usr/bin/env python3
"""
MR-MT3 预训练模型下载脚本
从Hugging Face下载MR-MT3模型到正确的目录
"""

import os
import sys
from pathlib import Path

def download_with_huggingface_hub():
    """使用huggingface_hub下载模型"""
    try:
        from huggingface_hub import snapshot_download
        
        # 设置下载路径 (从diversity-eval目录执行，下载到../MR-MT3/pretrained)
        download_path = "../MR-MT3/pretrained"
        os.makedirs(download_path, exist_ok=True)
        
        print("🔄 使用huggingface_hub下载MR-MT3模型...")
        print(f"📁 下载路径: {os.path.abspath(download_path)}")
        
        # 下载模型
        snapshot_download(
            repo_id="gudgud96/MR-MT3",
            local_dir=download_path,
            local_dir_use_symlinks=False
        )
        
        print("✅ 模型下载完成!")
        return True
        
    except ImportError:
        print("❌ huggingface_hub未安装")
        print("请运行: pip install huggingface_hub")
        return False
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return False

def download_with_git():
    """使用git clone下载模型"""
    try:
        import subprocess
        
        # 设置下载路径
        mr_mt3_path = "../MR-MT3"
        
        print("🔄 使用git clone下载MR-MT3仓库...")
        print(f"📁 下载路径: {os.path.abspath(mr_mt3_path)}")
        
        # 克隆仓库
        cmd = ["git", "clone", "https://huggingface.co/gudgud96/MR-MT3", mr_mt3_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 仓库克隆完成!")
            return True
        else:
            print(f"❌ 克隆失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 克隆失败: {e}")
        return False

def check_download():
    """检查下载结果"""
    mr_mt3_path = "../MR-MT3"
    pretrained_path = os.path.join(mr_mt3_path, "pretrained")
    
    if os.path.exists(mr_mt3_path):
        print(f"✅ MR-MT3目录存在: {os.path.abspath(mr_mt3_path)}")
        
        if os.path.exists(pretrained_path):
            files = os.listdir(pretrained_path)
            print(f"📁 预训练目录内容 ({len(files)} 个文件):")
            for file in files[:10]:  # 只显示前10个文件
                print(f"   - {file}")
            if len(files) > 10:
                print(f"   ... 还有 {len(files) - 10} 个文件")
        else:
            print("⚠️  预训练目录不存在")
    else:
        print("❌ MR-MT3目录不存在")

def main():
    print("🎼 MR-MT3 模型下载工具")
    print("=" * 50)
    
    # 检查当前目录
    current_dir = os.path.basename(os.getcwd())
    if current_dir != "diversity-eval":
        print(f"❌ 当前目录: {current_dir}")
        print("⚠️  请在diversity-eval目录下运行此脚本")
        print("正确的执行方式:")
        print("cd /home/evev/diversity-eval")
        print("python download_mr_mt3_models.py")
        sys.exit(1)
    
    print(f"📂 当前目录: {os.getcwd()}")
    
    # 尝试不同的下载方法
    success = False
    
    # 方法1: huggingface_hub
    print("\n🔄 尝试方法1: huggingface_hub")
    success = download_with_huggingface_hub()
    
    # 方法2: git clone (如果方法1失败)
    if not success:
        print("\n🔄 尝试方法2: git clone")
        success = download_with_git()
    
    # 检查下载结果
    print("\n📊 检查下载结果:")
    check_download()
    
    if success:
        print("\n🎉 下载完成! 现在可以运行:")
        print("python test_mr_mt3.py --input_dir Shutter_Solo_Dataset_15s --output_dir mr_mt3_output/test")
    else:
        print("\n❌ 自动下载失败，请手动下载:")
        print("1. 访问: https://huggingface.co/gudgud96/MR-MT3")
        print("2. 下载所有文件到: ../MR-MT3/pretrained/")
        print("3. 或者运行: git clone https://huggingface.co/gudgud96/MR-MT3 ../MR-MT3")

if __name__ == "__main__":
    main()