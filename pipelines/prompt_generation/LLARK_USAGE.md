# LLark 音频推理使用指南

## 概述

LLark 是一个多模态指令遵循语言模型，可以对音频进行分析并生成详细的文本描述。本指南说明如何使用 LLark 为 GTZAN 数据集的 pop 音频生成详细的 prompt。

## 环境设置

### 1. 设置 LLark 推理环境

推荐使用推理专用环境，避免训练依赖冲突：

```bash
cd /home/evev/diversity-eval
chmod +x pipelines/prompt_generation/setup_llark_env_infer.sh
./pipelines/prompt_generation/setup_llark_env_infer.sh
```

或者使用完整环境（可能有依赖冲突）：

```bash
chmod +x pipelines/prompt_generation/setup_llark_env.sh
./pipelines/prompt_generation/setup_llark_env.sh
```

或手动创建：

```bash
conda create -n llark python=3.9 -y
conda activate llark
```

### 2. 安装依赖

```bash
# 激活环境
conda activate llark

# 安装 PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 安装其他依赖
pip install transformers librosa numpy pandas tqdm apache-beam madmom einops

# 安装 LLark
cd /home/evev/diversity-eval/external/llark
pip install -e .
```

## 使用方法

### 1. 演示模式（无需模型）

如果你还没有训练好的 LLark 模型，可以使用演示模式来查看预期的输出格式：

```bash
conda activate llark
python /home/evev/diversity-eval/pipelines/prompt_generation/llark_prompt_generator.py --demo_mode
```

### 2. 实际推理模式

如果你有训练好的 LLark 模型：

```bash
conda activate llark
python /home/evev/diversity-eval/pipelines/prompt_generation/llark_prompt_generator.py \
    --model_path /path/to/your/llark/model \
    --ckpt_num 1000 \
    --output_dir /home/evev/diversity-eval/data/output/llark_prompts
```

### 3. 自定义提示类型

```bash
python /home/evev/diversity-eval/pipelines/prompt_generation/llark_prompt_generator.py \
    --demo_mode \
    --prompt_types detailed_description musical_analysis creative_description technical_analysis
```

## 参数说明

- `--gtzan_pop_dir`: GTZAN pop 音频目录路径（默认：`/home/evev/diversity-eval/data/input/GTZAN_Dataset/Solo/genres_original/pop`）
- `--output_dir`: 输出目录（默认：`/home/evev/diversity-eval/data/output/llark_prompts`）
- `--model_path`: LLark 模型路径（实际推理时必需）
- `--ckpt_num`: Checkpoint 编号
- `--prompt_types`: 要生成的提示类型列表
- `--demo_mode`: 演示模式标志

## 提示类型

脚本支持以下提示类型：

1. **detailed_description**: 详细描述音频内容
2. **musical_analysis**: 分析音乐特征（流派、节拍、调性、乐器、情绪）
3. **creative_description**: 创意描述，适用于音乐生成
4. **technical_analysis**: 技术分析（节奏、和声、旋律、制作风格）
5. **genre_and_style**: 流派和风格特征

## 输出格式

脚本会生成以下输出文件：

1. `llark_generated_prompts.json`: 完整的 JSON 格式结果
2. `llark_prompts_summary.csv`: CSV 格式摘要
3. `demo_prompts.json`: 演示模式的示例结果

### JSON 输出示例

```json
{
  "filename": "pop.00000 (Vocals).wav",
  "audio_path": "/path/to/audio.wav",
  "prompts": {
    "detailed_description": {
      "prompt_text": "Describe the contents of the provided audio in detail.",
      "generated_description": "This is a pop music track with upbeat tempo...",
      "success": true
    }
  }
}
```

## LLark 模型获取

要使用实际的 LLark 模型进行推理，你需要：

1. **预训练模型**: 从 Spotify Research 或相关来源获取预训练的 LLark 模型
2. **音频编码器**: 配置 Jukebox 或其他音频编码器
3. **模型权重**: 确保模型权重文件可访问

## 注意事项

1. **音频编码**: 当前脚本中的音频编码部分是占位符实现，实际使用时需要根据 LLark 的要求实现正确的音频编码
2. **模型依赖**: LLark 需要特定的模型架构和权重文件
3. **GPU 支持**: 推荐使用 GPU 进行推理以获得更好的性能
4. **内存要求**: 大型音频文件可能需要较多内存

## 故障排除

### 常见问题

1. **模块导入错误**: 确保 LLark 路径正确添加到 Python 路径
2. **CUDA 错误**: 检查 PyTorch 和 CUDA 版本兼容性
3. **音频加载失败**: 确认音频文件格式和路径正确
4. **模型加载失败**: 验证模型路径和权重文件

### 调试命令

```bash
# 检查环境
conda list

# 测试 LLark 导入
python -c "import sys; sys.path.append('/home/evev/diversity-eval/external/llark'); from m2t.infer import infer_with_prompt; print('LLark import successful')"

# 检查音频文件
ls -la /home/evev/diversity-eval/data/input/GTZAN_Dataset/Solo/genres_original/pop/
```

## 扩展使用

你可以修改脚本来：

1. 支持其他音频格式
2. 添加新的提示模板
3. 集成到其他音乐分析流水线
4. 批量处理多个数据集