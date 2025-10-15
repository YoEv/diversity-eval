#!/usr/bin/env python3
"""
应用VOCANO Apex兼容性修复
"""

import shutil
from pathlib import Path

def apply_fix():
    """应用VOCANO的apex兼容性修复"""
    
    vocano_core_file = Path("/home/evev/diversity-eval/external/VOCANO/vocano/core.py")
    
    # 备份原始文件
    backup_file = vocano_core_file.with_suffix('.py.backup')
    if not backup_file.exists():
        shutil.copy2(vocano_core_file, backup_file)
        print(f"✅ 已备份原始文件: {backup_file}")
    
    # 读取原始文件内容
    with open(vocano_core_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换apex.amp导入和使用
    modified_content = content.replace(
        "from apex import amp",
        """# from apex import amp  # 原始导入已注释
# 兼容性补丁：创建一个模拟的amp模块
class MockAmp:
    @staticmethod
    def initialize(model, opt_level="O0"):
        '''模拟amp.initialize，直接返回模型'''
        print(f"⚠️  使用模拟AMP初始化 (opt_level={opt_level})")
        return model
    
    @staticmethod
    def load_state_dict(state_dict):
        '''模拟amp.load_state_dict'''
        print("⚠️  跳过AMP状态字典加载")
        pass

amp = MockAmp()"""
    )
    
    # 写入修改后的文件
    with open(vocano_core_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"✅ 已修复VOCANO的apex兼容性问题")
    print(f"📁 修改文件: {vocano_core_file}")
    print(f"💾 备份文件: {backup_file}")

if __name__ == "__main__":
    print("🔧 应用VOCANO Apex兼容性修复")
    print("=" * 40)
    apply_fix()
    print("\n🎯 修复完成！现在可以重新运行VOCANO了。")