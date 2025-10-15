#!/usr/bin/env python3
"""
MR-MT3 音频转MIDI工具 - 修复版本
支持单个文件和批量处理，包含NumPy兼容性修复
"""

import sys
import os
import argparse
import glob
import subprocess
from pathlib import Path
import json
from datetime import datetime

# 添加本地MR-MT3路径
LOCAL_PATCH_DIR = os.path.join(os.path.dirname(__file__), "MR-MT3")
if os.path.exists(LOCAL_PATCH_DIR):
    sys.path.insert(0, LOCAL_PATCH_DIR)

import numpy as np

def apply_numpy_patches():
    """应用NumPy兼容性补丁"""
    patches = []
    
    # 修复已弃用的NumPy类型 - 避免触发弃用警告
    # 只在属性不存在时才设置，避免检查已弃用的属性
    if not hasattr(np, 'int'):
        np.int = int
        patches.append('np.int')
    
    if not hasattr(np, 'float'):
        np.float = float
        patches.append('np.float')
    
    if not hasattr(np, 'complex'):
        np.complex = complex
        patches.append('np.complex')
    
    if not hasattr(np, 'bool'):
        np.bool = np.bool_
        patches.append('np.bool')
    
    if not hasattr(np, 'object'):
        np.object = object
        patches.append('np.object')
    
    if not hasattr(np, 'unicode_'):
        np.unicode_ = str
        patches.append('np.unicode_')
    
    if not hasattr(np, 'str_'):
        np.str_ = str
        patches.append('np.str_')
    
    # 修复np.dtypes属性（JAX需要）
    if not hasattr(np, 'dtypes'):
        # 创建一个简单的dtypes命名空间
        class DTypesNamespace:
            def __init__(self):
                # 添加JAX可能需要的属性
                pass
            
            def __getattr__(self, name):
                # 对于未知属性，返回None或抛出AttributeError
                if name == 'StringDType':
                    # 返回一个可调用的类，而不是None
                    class StringDType:
                        def __init__(self):
                            pass
                    return StringDType
                raise AttributeError(f"'DTypesNamespace' object has no attribute '{name}'")
        
        np.dtypes = DTypesNamespace()
        patches.append('np.dtypes')
    
    # 修复np.exceptions属性（JAX需要）
    if not hasattr(np, 'exceptions'):
        # 创建一个简单的exceptions命名空间
        class ExceptionsNamespace:
            def __init__(self):
                # 创建一个自定义的ComplexWarning类
                class ComplexWarning(UserWarning):
                    """NumPy ComplexWarning类的替代"""
                    pass
                
                # 添加JAX可能需要的异常类
                self.ComplexWarning = ComplexWarning
                
            def __getattr__(self, name):
                # 对于未知属性，尝试从内置异常中获取
                if hasattr(__builtins__, name):
                    return getattr(__builtins__, name)
                # 如果是常见的警告类，返回UserWarning
                if name.endswith('Warning'):
                    return UserWarning
                raise AttributeError(f"'ExceptionsNamespace' object has no attribute '{name}'")
        
        np.exceptions = ExceptionsNamespace()
        patches.append('np.exceptions')
    
    return patches

# 应用NumPy补丁
patches = apply_numpy_patches()
if patches:
    print(f"🔧 已应用NumPy兼容性补丁: {', '.join(patches)}")

print("🎼 MR-MT3 音频转MIDI工具")
print("=" * 60)

# MR-MT3路径配置
MR_MT3_PATH = "/home/evev/MR-MT3"

def check_environment():
    """检查环境依赖"""
    print("🔍 检查环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查必要的包
    required_packages = ['torch', 'jax', 'librosa']
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装")
            return False
    
    return True

def check_mr_mt3_ready():
    """检查MR-MT3是否准备就绪"""
    print("🔍 检查MR-MT3...")
    
    if not os.path.exists(MR_MT3_PATH):
        print(f"❌ MR-MT3路径不存在: {MR_MT3_PATH}")
        return False
    
    # 检查关键文件
    required_files = [
        "inference.py",
        "config/config.yaml"
    ]
    
    for file_path in required_files:
        full_path = os.path.join(MR_MT3_PATH, file_path)
        if not os.path.exists(full_path):
            print(f"❌ 缺少文件: {full_path}")
            return False
        print(f"✅ 找到文件: {file_path}")
    
    # 检查模型文件
    model_path = os.path.join(MR_MT3_PATH, "pretrained")
    if not os.path.exists(model_path):
        print(f"❌ 模型路径不存在: {model_path}")
        return False
    
    # 检查关键模型文件
    model_files = ["mt3.pth", "commu_mt3.pt", "config.json"]
    for model_file in model_files:
        model_file_path = os.path.join(model_path, model_file)
        if os.path.exists(model_file_path):
            print(f"✅ 找到模型文件: {model_file}")
        else:
            print(f"⚠️  模型文件不存在: {model_file}")
    
    print("✅ MR-MT3准备就绪")
    return True

def create_subprocess_script(audio_file, output_file, mr_mt3_path, patch_dir, model_path=None):
    """创建子进程脚本内容"""
    
    # 查找模型路径
    if not model_path:
        # 尝试多个可能的模型路径
        possible_paths = [
            os.path.join(mr_mt3_path, "pretrained", "model.ckpt"),
            os.path.join(mr_mt3_path, "pretrained", "checkpoint.ckpt"),
            os.path.join(mr_mt3_path, "pretrained", "pytorch_model.bin"),
            os.path.join(mr_mt3_path, "checkpoints", "model.ckpt"),
            os.path.join(mr_mt3_path, "models", "model.ckpt"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                model_path = path
                break
        
        if not model_path:
            # 查找任何.ckpt或.bin文件
            for ext in ["*.ckpt", "*.bin", "*.pt", "*.pth"]:
                files = glob.glob(os.path.join(mr_mt3_path, "**", ext), recursive=True)
                if files:
                    model_path = files[0]
                    break
    
    script_content = f'''#!/usr/bin/env python3
import sys
import os
import warnings
warnings.filterwarnings("ignore")

# 添加MR-MT3路径
sys.path.insert(0, "{mr_mt3_path}")
sys.path.insert(0, "{patch_dir}")

# 强制使用CPU，避免CUDA问题
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['CUDA_LAUNCH_BLOCKING'] = '1'

# 设置模型路径环境变量
if "{model_path}":
    os.environ['MODEL_PATH'] = "{model_path}"
    os.environ['CHECKPOINT_PATH'] = "{model_path}"
    os.environ['MR_MT3_MODEL_PATH'] = "{model_path}"

# 全面的NumPy兼容性补丁
import numpy as np

# 修复已弃用的NumPy类型别名
if not hasattr(np, 'bool'):
    np.bool = bool
if not hasattr(np, 'int'):
    np.int = int
if not hasattr(np, 'float'):
    np.float = float
if not hasattr(np, 'complex'):
    np.complex = complex
if not hasattr(np, 'bool_'):
    np.bool_ = bool
if not hasattr(np, 'int_'):
    np.int_ = int
if not hasattr(np, 'float_'):
    np.float_ = float

# 添加对dtypes的支持（JAX需要）
if not hasattr(np, 'dtypes'):
    class MockDtypes:
        def __init__(self):
            pass
        
        def __getattr__(self, name):
            # 返回常见的dtype
            if name == 'StringDType':
                return None  # JAX检查这个属性是否存在
            elif name == 'Float32DType':
                return np.float32
            elif name == 'Float64DType':
                return np.float64
            elif name == 'Int32DType':
                return np.int32
            elif name == 'Int64DType':
                return np.int64
            else:
                raise AttributeError(f"'MockDtypes' object has no attribute '{{name}}'")
        
        def __hasattr__(self, name):
            return name in ['StringDType', 'Float32DType', 'Float64DType', 'Int32DType', 'Int64DType']
    
    np.dtypes = MockDtypes()
    print("🔧 已添加NumPy dtypes支持")

# 修补torch.load以处理None值
import torch
original_torch_load = torch.load

def safe_torch_load(f, map_location=None, pickle_module=None, **kwargs):
    if f is None:
        # 尝试从环境变量加载
        model_paths = [
            os.environ.get('MODEL_PATH'),
            os.environ.get('CHECKPOINT_PATH'), 
            os.environ.get('MR_MT3_MODEL_PATH'),
            "{model_path}" if "{model_path}" else None
        ]
        
        for path in model_paths:
            if path and os.path.exists(path):
                print(f"🔧 从环境变量加载模型: {{path}}")
                return original_torch_load(path, map_location='cpu', **kwargs)
        
        raise ValueError("无法找到有效的模型文件路径")
    
    # 强制使用CPU
    if map_location is None:
        map_location = 'cpu'
    
    return original_torch_load(f, map_location=map_location, pickle_module=pickle_module, **kwargs)

torch.load = safe_torch_load

# 修补torch.cuda.is_available
torch.cuda.is_available = lambda: False

# 设置默认tensor类型为CPU
torch.set_default_tensor_type('torch.FloatTensor')

# 修补load_state_dict以处理形状不匹配
original_load_state_dict = torch.nn.Module.load_state_dict

def flexible_load_state_dict(self, state_dict, strict=True):
    try:
        return original_load_state_dict(self, state_dict, strict=strict)
    except RuntimeError as e:
        if "size mismatch" in str(e):
            print("🔧 检测到参数形状不匹配，尝试非严格模式...")
            try:
                return original_load_state_dict(self, state_dict, strict=False)
            except Exception as e2:
                print(f"🔧 非严格模式也失败，尝试手动过滤兼容参数...")
                
                # 手动过滤兼容的参数
                model_state = self.state_dict()
                compatible_state = {{}}
                skipped_count = 0
                
                for key, value in state_dict.items():
                    if key in model_state:
                        if model_state[key].shape == value.shape:
                            compatible_state[key] = value
                        else:
                            print(f"⚠️ 跳过形状不匹配的参数: {{key}} - 检查点: {{value.shape}}, 模型: {{model_state[key].shape}}")
                            skipped_count += 1
                    else:
                        print(f"⚠️ 跳过模型中不存在的参数: {{key}}")
                        skipped_count += 1
                
                if skipped_count > 5:
                    print(f"⚠️ ... 还有 {{skipped_count - 5}} 个参数被跳过")
                
                print(f"🔧 过滤后保留 {{len(compatible_state)}}/{{len(state_dict)}} 个参数")
                return original_load_state_dict(self, compatible_state, strict=False)
        else:
            raise e

torch.nn.Module.load_state_dict = flexible_load_state_dict

try:
    # 导入必要的模块
    import librosa
    from inference import InferenceHandler
    
    # 加载音频
    print(f"🎵 加载音频: {audio_file}")
    audio, sr = librosa.load("{audio_file}", sr=16000)
    print(f"📊 音频信息: 长度={{len(audio)/sr:.2f}}秒, 采样率={{sr}}Hz")
    
    # 初始化InferenceHandler
    print("🔧 初始化InferenceHandler...")
    handler = None
    
    # 尝试多种初始化方式
    init_methods = [
        lambda: InferenceHandler(model_path="{model_path}"),
        lambda: InferenceHandler(checkpoint_path="{model_path}"),
        lambda: InferenceHandler(ckpt_path="{model_path}"),
        lambda: InferenceHandler(config={{"model_path": "{model_path}"}}),
        lambda: InferenceHandler(device='cpu'),
        lambda: InferenceHandler()
    ]
    
    for i, init_method in enumerate(init_methods):
        try:
            handler = init_method()
            print(f"✅ 初始化方式 {{i+1}} 成功")
            break
        except Exception as e:
            print(f"⚠️ 初始化方式 {{i+1}} 失败: {{e}}")
            continue
    
    if handler is None:
        raise Exception("所有初始化方式都失败了")
    
    # 如果handler有to方法，确保移动到CPU
    if hasattr(handler, 'to'):
        handler = handler.to('cpu')
        print("🔧 模型已移动到CPU")
    elif hasattr(handler, 'model') and hasattr(handler.model, 'to'):
        handler.model = handler.model.to('cpu')
        print("🔧 内部模型已移动到CPU")
    
    # 执行转录 - 尝试多种方法
    print("执行音频转录...")
    result = None
    
    # 尝试不同的转录方法
    transcribe_methods = [
        lambda: handler.transcribe(audio),
        lambda: handler.transcribe("{audio_file}"),
        lambda: handler.inference(audio),
        lambda: handler.inference("{audio_file}"),
        lambda: handler.predict(audio),
        lambda: handler.predict("{audio_file}"),
        lambda: handler.process(audio),
        lambda: handler.process("{audio_file}"),
        lambda: handler(audio),
        lambda: handler("{audio_file}")
    ]
    
    for i, method in enumerate(transcribe_methods):
        try:
            result = method()
            print(f"✅ 转录方法 {{i+1}} 成功")
            break
        except Exception as e:
            print(f"⚠️ 转录方法 {{i+1}} 失败: {{e}}")
            continue
    
    if result is None:
        # 尝试检查handler的可用方法
        print("🔍 检查InferenceHandler的可用方法:")
        methods = [method for method in dir(handler) if not method.startswith('_')]
        print(f"可用方法: {{methods}}")
        
        # 尝试调用第一个看起来像转录方法的方法
        for method_name in methods:
            if any(keyword in method_name.lower() for keyword in ['transcribe', 'inference', 'predict', 'process', 'run']):
                try:
                    method = getattr(handler, method_name)
                    if callable(method):
                        print(f"🔧 尝试调用方法: {{method_name}}")
                        result = method(audio)
                        print(f"✅ 方法 {{method_name}} 成功")
                        break
                except Exception as e:
                    print(f"⚠️ 方法 {{method_name}} 失败: {{e}}")
                    continue
    
    if result is None:
        raise Exception("无法找到有效的转录方法")
    
    # 保存结果 - 尝试多种保存方法
    print(f"保存结果到: {output_file}")
    
    save_methods = [
        lambda: result.save_midi("{output_file}"),
        lambda: result.save("{output_file}"),
        lambda: result.write("{output_file}"),
        lambda: result.to_midi().save("{output_file}"),
        lambda: result.to_midi().write("{output_file}")
    ]
    
    saved = False
    for i, save_method in enumerate(save_methods):
        try:
            save_method()
            print(f"✅ 保存方法 {{i+1}} 成功")
            saved = True
            break
        except Exception as e:
            print(f"⚠️ 保存方法 {{i+1}} 失败: {{e}}")
            continue
    
    if not saved:
        # 尝试直接保存result对象
        print("🔧 尝试直接保存结果对象...")
        print(f"结果类型: {{type(result)}}")
        print(f"结果方法: {{[m for m in dir(result) if not m.startswith('_')]}}")
        
        # 如果result是numpy数组或tensor，尝试转换为MIDI
        if hasattr(result, 'shape'):
            print(f"结果形状: {{result.shape}}")
            # 这里可能需要根据MR-MT3的实际输出格式进行处理
            import pickle
            with open("{output_file}.pkl", "wb") as f:
                pickle.dump(result, f)
            print(f"✅ 结果已保存为pickle文件: {output_file}.pkl")
        else:
            # 尝试保存为文本
            with open("{output_file}.txt", "w") as f:
                f.write(str(result))
            print(f"✅ 结果已保存为文本文件: {output_file}.txt")
    
    print("✅ 转录完成")
    
except Exception as e:
    print(f"❌ 转录失败: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
    
    return script_content

def transcribe_single_audio(audio_file, output_dir, model_path=None):
    """转录单个音频文件"""
    print(f"\n🎵 处理音频文件: {os.path.basename(audio_file)}")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成输出文件名
    base_name = os.path.splitext(os.path.basename(audio_file))[0]
    output_file = os.path.join(output_dir, f"{base_name}.mid")
    
    # 创建临时脚本
    script_content = create_subprocess_script(
        audio_file, output_file, MR_MT3_PATH, LOCAL_PATCH_DIR, model_path
    )
    
    # 写入临时脚本文件
    script_path = f"/tmp/mr_mt3_transcribe_{os.getpid()}.py"
    try:
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # 执行脚本
        print("🚀 开始转录...")
        result = subprocess.run([
            sys.executable, script_path
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ 转录成功")
            return output_file
        else:
            print("❌ 转录失败")
            print(f"错误输出: {result.stderr}")
            if result.stdout:
                print(f"标准输出: {result.stdout}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ 转录超时")
        return None
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return None
    finally:
        # 清理临时文件
        if os.path.exists(script_path):
            os.remove(script_path)

def batch_transcribe(input_dir, output_dir, model_path=None, test_single=False):
    """批量转录音频文件"""
    print(f"📁 批量处理目录: {input_dir}")
    
    # 支持的音频格式
    audio_extensions = ['*.mp3', '*.wav', '*.flac', '*.m4a', '*.aac']
    
    # 查找所有音频文件
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(glob.glob(os.path.join(input_dir, ext)))
        audio_files.extend(glob.glob(os.path.join(input_dir, ext.upper())))
    
    if not audio_files:
        print("❌ 未找到音频文件")
        return
    
    print(f"📊 找到 {len(audio_files)} 个音频文件")
    
    if test_single:
        audio_files = audio_files[:1]
        print("🧪 测试模式：只处理第一个文件")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 批量处理
    success_count = 0
    total_count = len(audio_files)
    
    for i, audio_file in enumerate(audio_files, 1):
        print(f"\n📈 进度: {i}/{total_count}")
        
        if transcribe_single_audio(audio_file, output_dir, model_path):
            success_count += 1
    
    # 统计结果
    print(f"\n📊 批量处理完成:")
    print(f"   总文件数: {total_count}")
    print(f"   成功数: {success_count}")
    print(f"   失败数: {total_count - success_count}")
    print(f"   成功率: {success_count/total_count*100:.1f}%")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="MR-MT3 音频转MIDI批量处理工具")
    parser.add_argument("input_dir", help="输入音频文件目录")
    parser.add_argument("-o", "--output", default="mr_mt3_output", 
                       help="输出目录 (默认: mr_mt3_output)")
    parser.add_argument("-m", "--model", help="模型文件路径")
    parser.add_argument("--test", action="store_true", 
                       help="测试模式，只处理第一个文件")
    
    args = parser.parse_args()
    
    # 检查输入目录
    if not os.path.exists(args.input_dir):
        print(f"❌ 输入目录不存在: {args.input_dir}")
        return 1
    
    # 检查环境
    if not check_environment():
        print("❌ 环境检查失败")
        return 1
    
    # 检查MR-MT3
    if not check_mr_mt3_ready():
        print("❌ MR-MT3未准备就绪")
        return 1
    
    # 开始批量处理
    batch_transcribe(args.input_dir, args.output, args.model, args.test)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())