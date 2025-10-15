#!/usr/bin/env python3
"""
修复numpy 1.23.5兼容性问题的脚本
"""

import sys
import os

def patch_numpy_compatibility():
    """为numpy 1.23.5添加兼容性补丁"""
    try:
        import numpy as np
        
        # 检查numpy版本
        print(f"当前numpy版本: {np.__version__}")
        
        # 如果numpy没有dtypes属性，添加一个兼容性补丁
        if not hasattr(np, 'dtypes'):
            print("🔧 添加numpy.dtypes兼容性补丁...")
            
            # 创建一个简单的dtypes模拟对象
            class DTypesCompat:
                def __init__(self):
                    # 检查是否有StringDType（numpy >= 2.0的特性）
                    self.StringDType = None
                    
                def __getattr__(self, name):
                    # 对于StringDType，返回None（表示不存在）
                    if name == 'StringDType':
                        return None
                    # 其他属性尝试从numpy.dtype获取
                    return getattr(np.dtype, name, None)
            
            # 添加dtypes属性
            np.dtypes = DTypesCompat()
            print("✅ numpy.dtypes兼容性补丁已添加")
            
            # 验证补丁
            print(f"hasattr(np.dtypes, 'StringDType'): {hasattr(np.dtypes, 'StringDType')}")
            print(f"np.dtypes.StringDType: {getattr(np.dtypes, 'StringDType', 'Not found')}")
            
        else:
            print("✅ numpy.dtypes已存在，无需补丁")
            
        return True
        
    except Exception as e:
        print(f"❌ 添加numpy兼容性补丁失败: {e}")
        return False

if __name__ == "__main__":
    patch_numpy_compatibility()