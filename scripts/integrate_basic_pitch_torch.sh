#!/bin/bash

echo "整合basic-pitch-torch处理文件到pipeline..."

# 确保目标目录存在
mkdir -p pipelines/01_wav_to_midi

# 移动并重命名处理文件
echo "移动处理文件到01_wav_to_midi pipeline..."

# 移动主要的处理脚本
if [ -f "external/basic-pitch-torch/quick_test.py" ]; then
    mv external/basic-pitch-torch/quick_test.py pipelines/01_wav_to_midi/bpt_quick_test.py
    echo "✓ quick_test.py -> bpt_quick_test.py"
fi

if [ -f "external/basic-pitch-torch/test_shutter_songs.py" ]; then
    mv external/basic-pitch-torch/test_shutter_songs.py pipelines/01_wav_to_midi/bpt_batch_convert.py
    echo "✓ test_shutter_songs.py -> bpt_batch_convert.py"
fi

if [ -f "external/basic-pitch-torch/analyze_results.py" ]; then
    mv external/basic-pitch-torch/analyze_results.py pipelines/01_wav_to_midi/bpt_analyze_results.py
    echo "✓ analyze_results.py -> bpt_analyze_results.py"
fi

# 移动shell脚本
if [ -f "external/basic-pitch-torch/run_conversion.sh" ]; then
    mv external/basic-pitch-torch/run_conversion.sh pipelines/01_wav_to_midi/bpt_run_conversion.sh
    echo "✓ run_conversion.sh -> bpt_run_conversion.sh"
fi

# 移动scripts目录中的转换脚本
if [ -d "external/basic-pitch-torch/scripts" ]; then
    mkdir -p pipelines/utils/bpt_scripts
    mv external/basic-pitch-torch/scripts/* pipelines/utils/bpt_scripts/
    rmdir external/basic-pitch-torch/scripts 2>/dev/null || true
    echo "✓ scripts/ -> pipelines/utils/bpt_scripts/"
fi

# 移动测试文件
if [ -d "external/basic-pitch-torch/tests" ]; then
    mkdir -p pipelines/01_wav_to_midi/bpt_tests
    mv external/basic-pitch-torch/tests/* pipelines/01_wav_to_midi/bpt_tests/
    rmdir external/basic-pitch-torch/tests 2>/dev/null || true
    echo "✓ tests/ -> pipelines/01_wav_to_midi/bpt_tests/"
fi

echo "修改文件中的导入路径..."

# 修改bpt_quick_test.py中的导入路径
if [ -f "pipelines/01_wav_to_midi/bpt_quick_test.py" ]; then
    sed -i 's|from basic_pitch_torch.inference|import sys; sys.path.append("../../external/basic-pitch-torch"); from basic_pitch_torch.inference|g' pipelines/01_wav_to_midi/bpt_quick_test.py
    echo "✓ 更新bpt_quick_test.py导入路径"
fi

# 修改bpt_batch_convert.py中的导入路径
if [ -f "pipelines/01_wav_to_midi/bpt_batch_convert.py" ]; then
    sed -i 's|from basic_pitch_torch.inference|import sys; sys.path.append("../../external/basic-pitch-torch"); from basic_pitch_torch.inference|g' pipelines/01_wav_to_midi/bpt_batch_convert.py
    echo "✓ 更新bpt_batch_convert.py导入路径"
fi

# 修改bpt_analyze_results.py中的导入路径
if [ -f "pipelines/01_wav_to_midi/bpt_analyze_results.py" ]; then
    sed -i 's|from basic_pitch_torch.inference|import sys; sys.path.append("../../external/basic-pitch-torch"); from basic_pitch_torch.inference|g' pipelines/01_wav_to_midi/bpt_analyze_results.py
    echo "✓ 更新bpt_analyze_results.py导入路径"
fi

# 创建basic-pitch-torch的执行脚本
cat > scripts/run_basic_pitch_torch.sh << 'EOF'
#!/bin/bash

# Basic Pitch Torch 音频转MIDI脚本
INPUT_DIR=${1:-"data/input/Shutter_Solo_Dataset_15s"}
OUTPUT_DIR=${2:-"data/output/basic_pitch_midi"}

echo "使用Basic Pitch Torch进行音频转MIDI转换..."
echo "输入目录: $INPUT_DIR"
echo "输出目录: $OUTPUT_DIR"

mkdir -p $OUTPUT_DIR

# 运行批量转换
python pipelines/01_wav_to_midi/bpt_batch_convert.py --input $INPUT_DIR --output $OUTPUT_DIR

echo "Basic Pitch Torch转换完成!"
EOF

# 创建快速测试脚本
cat > scripts/run_bpt_quick_test.sh << 'EOF'
#!/bin/bash

# Basic Pitch Torch 快速测试脚本
TEST_FILE=${1:-"data/input/Shutter_Solo_Dataset_15s"}

echo "运行Basic Pitch Torch快速测试..."
echo "测试文件/目录: $TEST_FILE"

python pipelines/01_wav_to_midi/bpt_quick_test.py $TEST_FILE

echo "快速测试完成!"
EOF

# 设置执行权限
chmod +x scripts/run_basic_pitch_torch.sh
chmod +x scripts/run_bpt_quick_test.sh
chmod +x pipelines/01_wav_to_midi/bpt_run_conversion.sh 2>/dev/null || true

echo "创建Basic Pitch Torch使用说明..."

# 创建Basic Pitch Torch的README
cat > pipelines/01_wav_to_midi/README_BASIC_PITCH_TORCH.md << 'EOF'
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
EOF

echo "更新主pipeline的README..."

# 更新主要的pipeline README
cat >> README_PIPELINE.md << 'EOF'

## Basic Pitch Torch集成

Basic Pitch Torch的处理文件已整合到pipeline中：

### 新增脚本
```bash
./scripts/run_basic_pitch_torch.sh [输入目录] [输出目录]  # 批量转换
./scripts/run_bpt_quick_test.sh [测试文件]              # 快速测试
```

### 文件位置
- 主要脚本: `pipelines/01_wav_to_midi/bpt_*.py`
- 测试文件: `pipelines/01_wav_to_midi/bpt_tests/`
- 工具脚本: `pipelines/utils/bpt_scripts/`

### 使用示例
```bash
# 使用Basic Pitch Torch转换音频
./scripts/run_basic_pitch_torch.sh data/input/audio data/output/bpt_midi

# 快速测试
./scripts/run_bpt_quick_test.sh data/input/test.wav
```
EOF

echo "Basic Pitch Torch集成完成!"
echo ""
echo "已移动的文件:"
echo "- quick_test.py -> pipelines/01_wav_to_midi/bpt_quick_test.py"
echo "- test_shutter_songs.py -> pipelines/01_wav_to_midi/bpt_batch_convert.py"
echo "- analyze_results.py -> pipelines/01_wav_to_midi/bpt_analyze_results.py"
echo "- run_conversion.sh -> pipelines/01_wav_to_midi/bpt_run_conversion.sh"
echo "- scripts/ -> pipelines/utils/bpt_scripts/"
echo "- tests/ -> pipelines/01_wav_to_midi/bpt_tests/"
echo ""
echo "新增执行脚本:"
echo "- scripts/run_basic_pitch_torch.sh"
echo "- scripts/run_bpt_quick_test.sh"
echo ""
echo "请查看 pipelines/01_wav_to_midi/README_BASIC_PITCH_TORCH.md 了解详细使用方法"