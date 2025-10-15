# numpy 1.23.5 兼容：为 numpy 添加 dtypes 属性以满足 JAX 的检查
import numpy as np

# 1) dtypes 兼容：提供可调用的 StringDType
if not hasattr(np, 'dtypes'):
    class DTypesCompat:
        def __init__(self):
            pass

        def StringDType(self, *args, **kwargs):
            # 兼容 StringDType(10) 这类调用
            if args and isinstance(args[0], int):
                try:
                    return np.dtype(f'U{args[0]}')
                except Exception:
                    pass
            # 默认返回通用的 unicode dtype
            try:
                return np.dtype('U')
            except Exception:
                return np.dtype('object')

        def __getattr__(self, name):
            # 其他属性回退到 numpy.dtype
            return getattr(np.dtype, name, None)

    np.dtypes = DTypesCompat()

# 2) exceptions 兼容：提供 ComplexWarning
if not hasattr(np, 'exceptions'):
    class ExceptionsCompat:
        # 优先复用 numpy 顶层的 ComplexWarning，如果没有就定义一个 Warning 子类
        ComplexWarning = getattr(np, 'ComplexWarning', type('ComplexWarning', (Warning,), {}))

        def __getattr__(self, name):
            # 其他异常名称尽量从 numpy 顶层拿（如 VisibleDeprecationWarning 等）
            return getattr(np, name, None)

    np.exceptions = ExceptionsCompat()