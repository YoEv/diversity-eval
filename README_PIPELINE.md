
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
