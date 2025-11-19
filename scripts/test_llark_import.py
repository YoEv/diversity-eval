#!/usr/bin/env python3
"""
测试LLark模块导入
"""

import os
import sys

# 添加LLark路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # 从scripts目录回到项目根目录
llark_path = os.path.join(project_root, 'external', 'llark')
sys.path.insert(0, llark_path)

print(f"Python路径: {sys.path[:3]}...")
print(f"LLark路径: {llark_path}")
print(f"LLark路径存在: {os.path.exists(llark_path)}")
print(f"m2t路径存在: {os.path.exists(os.path.join(llark_path, 'm2t'))}")

try:
    print("\n=== 测试模块导入 ===")
    
    # 测试m2t模块导入
    print("导入 m2t...")
    import m2t
    print("✓ m2t 导入成功")
    
    # 测试子模块导入
    print("导入 m2t.arguments...")
    from m2t.arguments import DataArguments, ModelArguments, TrainingArguments
    print("✓ m2t.arguments 导入成功")
    
    print("导入 m2t.conversation_utils...")
    from m2t.conversation_utils import extract_response_tokens
    print("✓ m2t.conversation_utils 导入成功")
    
    print("导入 m2t.data_modules...")
    from m2t.data_modules import make_mm_config
    print("✓ m2t.data_modules 导入成功")
    
    print("导入 m2t.infer...")
    from m2t.infer import infer_with_prompt
    print("✓ m2t.infer 导入成功")
    
    print("导入 m2t.models.utils...")
    from m2t.models.utils import load_pretrained_model
    print("✓ m2t.models.utils 导入成功")
    
    print("\n🎉 所有LLark模块导入成功！")
    
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print(f"错误类型: {type(e).__name__}")
    
    # 详细诊断
    print("\n=== 诊断信息 ===")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"Python版本: {sys.version}")
    
    # 检查文件是否存在
    files_to_check = [
        "m2t/__init__.py",
        "m2t/arguments.py", 
        "m2t/conversation_utils.py",
        "m2t/data_modules.py",
        "m2t/infer.py",
        "m2t/models/__init__.py",
        "m2t/models/utils.py"
    ]
    
    for file_path in files_to_check:
        full_path = os.path.join(llark_path, file_path)
        exists = os.path.exists(full_path)
        print(f"  {file_path}: {'✓' if exists else '❌'}")

except Exception as e:
    print(f"❌ 其他错误: {e}")
    print(f"错误类型: {type(e).__name__}")