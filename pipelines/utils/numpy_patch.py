#!/usr/bin/env python3
"""
numpy 1.23.5兼容性补丁模块
必须在导入任何其他库之前导入此模块
"""

def apply_numpy_patch():
    """应用numpy兼容性补丁"""
    import numpy as np
    
    if not hasattr(np, 'dtypes'):
        class DTypesCompat:
            """numpy.dtypes兼容性类"""
            def __init__(self):
                # 对于numpy 1.23.5，StringDType不存在
                self.StringDType = None
                
            def __getattr__(self, name):
                if name == 'StringDType':
                    return None
                # 其他属性尝试从numpy获取
                return getattr(np, name, None)
        
        # 添加dtypes属性到numpy模块
        np.dtypes = DTypesCompat()
        print("🔧 已应用numpy.dtypes兼容性补丁")

# 立即应用补丁
apply_numpy_patch()