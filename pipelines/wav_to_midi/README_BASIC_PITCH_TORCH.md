# Basic Pitch Torch Pipeline

这个目录包含了从external/basic-pitch-torch整合过来的处理文件。

## 文件说明

### 主要脚本
- `bpt_quick_test.py` - 快速测试单个音频文件转换
- `bpt_batch_convert.py` - 批量转换音频文件为MIDI
- `bpt_analyze_results.py` - 分析转换结果
- `bpt_run_conversion.sh` - Shell脚本版本的转换工具

### 测试文件
- `bpt_tests/` - 测试脚本目录
  - `test_compare_midi.py` - MIDI比较测试
  - `test_compare_model_outputs.py` - 模型输出比较测试

## 使用方法

### 快速测试
```bash
# 从项目根目录运行
./scripts/run_bpt_quick_test.sh [测试文件路径]
```

### 批量转换
```bash
# 从项目根目录运行
./scripts/run_basic_pitch_torch.sh [输入目录] [输出目录]
```

### 直接调用
```bash
# 快速测试
python pipelines/01_wav_to_midi/bpt_quick_test.py

# 批量转换
python pipelines/01_wav_to_midi/bpt_batch_convert.py --input data/input --output data/output

# 分析结果
python pipelines/01_wav_to_midi/bpt_analyze_results.py
```

## 注意事项
- 所有脚本已更新导入路径，指向 `external/basic-pitch-torch`
- 确保basic_pitch_torch模块在external目录中可用
- 需要安装requirements.txt中的依赖
