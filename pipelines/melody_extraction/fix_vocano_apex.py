#!/usr/bin/env python3
"""
VOCANO Apex兼容性修复脚本

这个脚本修复VOCANO与新版本apex的兼容性问题。
主要问题：VOCANO使用的apex.amp模块在新版本中已被弃用或重构。

解决方案：
1. 创建一个兼容性补丁，模拟旧版本的amp接口
2. 修改VOCANO的core.py文件，使其兼容新版本的apex
3. 提供一个无amp版本的VOCANO运行方式
4. 验证和修复模型文件问题
"""

import os
import sys
import shutil
import torch
import requests
from pathlib import Path

def verify_and_fix_model_files():
    """
    验证并修复VOCANO模型文件
    """
    print("🔍 验证VOCANO模型文件...")
    
    vocano_path = Path("/home/evev/diversity-eval/external/VOCANO")
    checkpoint_dir = vocano_path / "checkpoint"
    
    model_files = {
        "model.pt": {
            "description": "PyramidNet模型",
            "file_id": "1m9YT7207CXQv1KdU0ivkRQrwvPnOuR3W",
            "expected_size": 109 * 1024 * 1024  # 约109MB
        },
        "model3_patch25.npy": {
            "description": "Patch-CNN模型", 
            "file_id": "1tq_LcZwWQYV7wM6dBAeDZeQn39UNkPdl",
            "expected_size": None
        }
    }
    
    needs_redownload = []
    
    for filename, info in model_files.items():
        filepath = checkpoint_dir / filename
        
        print(f"\n📁 检查 {info['description']} ({filename})...")
        
        if not filepath.exists():
            print(f"❌ 文件不存在: {filepath}")
            needs_redownload.append((filename, info))
            continue
        
        file_size = filepath.stat().st_size
        print(f"   文件大小: {file_size:,} bytes")
        
        # 检查文件是否太小（可能是HTML错误页面）
        if file_size < 1000:
            print(f"❌ 文件太小，可能是下载错误")
            needs_redownload.append((filename, info))
            continue
        
        # 验证PyTorch模型文件
        if filename == "model.pt":
            try:
                # 检查文件头
                with open(filepath, 'rb') as f:
                    header = f.read(100)
                    if b'<!DOCTYPE html>' in header or b'<html>' in header:
                        print(f"❌ 检测到HTML文件，这是Google Drive错误页面")
                        needs_redownload.append((filename, info))
                        continue
                
                # 尝试加载模型
                checkpoint = torch.load(filepath, map_location='cpu')
                if isinstance(checkpoint, dict):
                    print(f"✅ {info['description']}: 格式验证通过")
                else:
                    print(f"⚠️  {info['description']}: 格式可能有问题")
                    
            except Exception as e:
                print(f"❌ {info['description']}: 加载失败 - {str(e)}")
                if "failed finding central directory" in str(e):
                    print("   错误原因: 文件损坏或下载不完整")
                needs_redownload.append((filename, info))
                continue
        
        # 验证numpy文件
        elif filename.endswith('.npy'):
            try:
                import numpy as np
                data = np.load(filepath)
                print(f"✅ {info['description']}: 格式验证通过 (shape: {data.shape})")
            except Exception as e:
                print(f"❌ {info['description']}: 加载失败 - {str(e)}")
                needs_redownload.append((filename, info))
                continue
    
    # 处理需要重新下载的文件
    if needs_redownload:
        print(f"\n⚠️  发现 {len(needs_redownload)} 个文件需要重新下载")
        
        for filename, info in needs_redownload:
            filepath = checkpoint_dir / filename
            
            print(f"\n🗑️  删除损坏的文件: {filename}")
            if filepath.exists():
                filepath.unlink()
            
            print(f"💡 请手动下载 {info['description']}:")
            print(f"   链接: https://drive.google.com/file/d/{info['file_id']}/view")
            print(f"   保存为: {filepath}")
            if info['expected_size']:
                print(f"   预期大小: {info['expected_size'] // (1024*1024)}MB")
        
        print(f"\n📋 下载步骤:")
        print("1. 点击上面的Google Drive链接")
        print("2. 点击 'Download anyway' 按钮")
        print("3. 将下载的文件保存到指定路径")
        print("4. 确保文件名正确")
        
        return False
    else:
        print(f"\n✅ 所有模型文件验证通过!")
        return True

def create_amp_compatibility_patch():
    """
    创建apex.amp兼容性补丁
    """
    print("🔧 创建apex.amp兼容性补丁...")
    
    vocano_core_path = Path("/home/evev/diversity-eval/external/VOCANO/vocano/core.py")
    backup_path = vocano_core_path.with_suffix('.py.backup')
    
    # 备份原始文件
    if not backup_path.exists():
        shutil.copy2(vocano_core_path, backup_path)
        print(f"✅ 已备份原始文件: {backup_path}")
    
    # 读取原始文件
    with open(vocano_core_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经修复过
    if "class MockAmp:" in content:
        print("✅ apex兼容性补丁已存在")
        return True
    
    # 创建修复后的内容
    fixed_content = content.replace(
        "from apex import amp",
        """# from apex import amp  # 注释掉原始导入

# 创建MockAmp类来替代apex.amp
class MockAmp:
    @staticmethod
    def initialize(model, opt_level="O0"):
        # 返回原始模型，不进行AMP优化
        return model
    
    @staticmethod
    def load_state_dict(state_dict):
        # 空实现，跳过AMP状态加载
        pass

# 使用MockAmp替代amp
amp = MockAmp()"""
    )
    
    # 写入修复后的文件
    with open(vocano_core_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("✅ apex兼容性补丁已应用")
    return True

def create_no_amp_vocano_script():
    """创建一个不使用AMP的VOCANO运行脚本"""
    
    script_content = '''#!/usr/bin/env python3
"""
无AMP版本的VOCANO主旋律提取脚本

这个脚本绕过apex.amp的问题，直接使用PyTorch进行推理。
适用于CPU推理或不需要混合精度训练的场景。
"""

import os
import sys
import torch
import numpy as np
import pretty_midi
import scipy.io.wavfile as wavfile
from pathlib import Path
from tqdm import tqdm

# 添加VOCANO路径
vocano_path = "/home/evev/diversity-eval/external/VOCANO"
if vocano_path not in sys.path:
    sys.path.insert(0, vocano_path)

def extract_melody_no_amp(input_wav_path, output_dir, device='cpu'):
    """
    不使用AMP的主旋律提取函数
    
    Args:
        input_wav_path: 输入音频文件路径
        output_dir: 输出目录
        device: 设备 ('cpu' 或 'cuda')
    """
    
    try:
        # 导入VOCANO模块（但不使用amp）
        from vocano.model.PyramidNet_ShakeDrop import PyramidNet_ShakeDrop
        from vocano.utils.feature_extraction import test_flow as feature_extraction_np
        from vocano.utils.evaluate_tools import Smooth_sdt6_modified, Naive_pitch
        from vocano.utils.est2midi import Est2MIDI
        
        print(f"🎵 开始处理: {Path(input_wav_path).name}")
        
        # 1. 特征提取
        print("   📊 提取音频特征...")
        feature, pitch = feature_extraction_np(input_wav_path)
        
        # 2. 加载模型（不使用AMP）
        print("   🤖 加载模型...")
        model = PyramidNet_ShakeDrop(depth=110, alpha=270, shakedrop=True)
        
        # 检查模型文件
        checkpoint_file = Path(vocano_path) / "checkpoint" / "model.pt"
        if not checkpoint_file.exists():
            print(f"   ❌ 模型文件不存在: {checkpoint_file}")
            print("   💡 请先运行VOCANO的下载脚本获取模型文件")
            return False
        
        # 加载检查点（跳过AMP部分）
        checkpoint = torch.load(checkpoint_file, map_location=device)
        model = model.to(device)
        
        # 只加载模型权重，跳过AMP状态
        if 'model' in checkpoint:
            model.load_state_dict(checkpoint['model'])
        else:
            model.load_state_dict(checkpoint)
        
        model.eval()
        
        # 3. 推理
        print("   🎼 进行主旋律转录...")
        with torch.no_grad():
            # 准备输入数据
            feature_tensor = torch.FloatTensor(feature).unsqueeze(0).to(device)
            
            # 模型推理
            output = model(feature_tensor)
            output = output.cpu().numpy().squeeze()
        
        # 4. 后处理
        print("   🎯 后处理和平滑...")
        smoothed_output = Smooth_sdt6_modified(output)
        
        # 5. 转换为MIDI
        print("   🎹 转换为MIDI...")
        est2midi = Est2MIDI()
        midi_data = est2midi.est2midi(smoothed_output, pitch)
        
        # 6. 保存结果
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 保存MIDI文件
        midi_filename = Path(input_wav_path).stem + "_melody.mid"
        midi_path = output_path / midi_filename
        midi_data.write(str(midi_path))
        
        print(f"   ✅ 主旋律提取完成: {midi_path}")
        return True
        
    except Exception as e:
        print(f"   ❌ 处理失败: {str(e)}")
        return False

def batch_extract_melodies(input_dir, output_dir, device='cpu'):
    """批量提取主旋律"""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        print(f"❌ 输入目录不存在: {input_path}")
        return
    
    # 获取所有wav文件
    wav_files = list(input_path.glob("*.wav"))
    if not wav_files:
        print(f"❌ 在 {input_path} 中没有找到.wav文件")
        return
    
    print(f"🎵 找到 {len(wav_files)} 个音频文件")
    print(f"📁 输出目录: {output_path}")
    print(f"🖥️  使用设备: {device}")
    print("-" * 50)
    
    success_count = 0
    for i, wav_file in enumerate(wav_files, 1):
        print(f"[{i}/{len(wav_files)}] 处理文件...")
        
        if extract_melody_no_amp(wav_file, output_path, device):
            success_count += 1
        
        print()
    
    print("-" * 50)
    print(f"✅ 处理完成: {success_count}/{len(wav_files)} 个文件成功")

if __name__ == "__main__":
    # 测试参数
    input_directory = "/home/evev/diversity-eval/data/input/GTZAN_Dataset/Data/genres_original/pop"
    output_directory = "/home/evev/diversity-eval/data/output/gtzan_test_mainM_out"
    device = "cpu"  # 使用CPU避免CUDA相关问题
    
    print("🎼 无AMP版本VOCANO主旋律提取器")
    print("=" * 50)
    
    batch_extract_melodies(input_directory, output_directory, device)
'''
    
    script_path = Path("/home/evev/diversity-eval/pipelines/melody_extraction/vocano_no_amp.py")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # 设置执行权限
    os.chmod(script_path, 0o755)
    
    print(f"✅ 已创建无AMP版本的VOCANO脚本: {script_path}")
    return script_path

def restore_original_vocano():
    """恢复原始的VOCANO文件"""
    
    vocano_core_file = Path("/home/evev/diversity-eval/external/VOCANO/vocano/core.py")
    backup_file = vocano_core_file.with_suffix('.py.backup')
    
    if backup_file.exists():
        shutil.copy2(backup_file, vocano_core_file)
        print(f"✅ 已恢复原始VOCANO文件")
        return True
    else:
        print(f"❌ 备份文件不存在: {backup_file}")
        return False

def main():
    """
    主函数：提供修复选项菜单
    """
    print("🎼 VOCANO修复工具")
    print("=" * 50)
    print("这个工具可以修复VOCANO的常见问题:")
    print("- apex.amp兼容性问题")
    print("- 模型文件下载/损坏问题")
    print("- 提供无AMP版本的替代方案")
    print("=" * 50)
    
    print("\n请选择修复选项:")
    print("1. 验证并修复模型文件")
    print("2. 修复apex兼容性问题")
    print("3. 创建无AMP版本脚本")
    print("4. 恢复原始VOCANO文件")
    print("5. 全部修复（推荐）")
    
    choice = input("\n请选择 (1-5): ").strip()
    
    if choice == "1":
        verify_and_fix_model_files()
    elif choice == "2":
        create_amp_compatibility_patch()
    elif choice == "3":
        create_no_amp_vocano_script()
    elif choice == "4":
        restore_original_vocano()
    elif choice == "5":
        print("🔄 执行全部修复...")
        model_ok = verify_and_fix_model_files()
        if model_ok:
            create_amp_compatibility_patch()
            create_no_amp_vocano_script()
            print("\n✅ 所有修复方案已完成")
        else:
            print("\n⚠️  请先手动下载模型文件，然后重新运行此脚本")
    else:
        print("❌ 无效选择")
        return
    
    print("\n🎯 修复完成！")
    print("\n💡 建议:")
    print("   - 如果模型文件有问题，请先手动下载")
    print("   - 对于CPU推理，无AMP版本通常更稳定")
    print("   - 修复后可以运行 vocano_melody_extraction.py 测试")

if __name__ == "__main__":
    main()