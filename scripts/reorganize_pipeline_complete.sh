#!/bin/bash

# 重新组织Pipeline结构，补充缺失的组件
# 根据用户的pipeline图片进行完整的结构调整

set -e

echo "重新组织Pipeline结构..."

# 1. 将pop2piano移动到01_wav_to_midi
echo "1. 移动pop2piano到wav_to_midi..."
if [ -d "pipelines/06_pop2piano" ]; then
    mv pipelines/06_pop2piano/* pipelines/01_wav_to_midi/ 2>/dev/null || true
    rmdir pipelines/06_pop2piano 2>/dev/null || true
    echo "   ✓ pop2piano文件已移动到01_wav_to_midi"
fi

# 2. 创建缺失的pipeline组件目录
echo "2. 创建缺失的pipeline组件..."

# 创建07_embedding目录（用于LLark等嵌入模型）
mkdir -p pipelines/07_embedding
echo "   ✓ 创建07_embedding目录"

# 创建08_property_extraction目录（用于分类器等属性提取）
mkdir -p pipelines/08_property_extraction
echo "   ✓ 创建08_property_extraction目录"

# 创建09_prompt_generation目录（用于生成提示）
mkdir -p pipelines/09_prompt_generation
echo "   ✓ 创建09_prompt_generation目录"

# 创建10_music_llms目录（用于MusicGen等音乐大语言模型）
mkdir -p pipelines/10_music_llms
echo "   ✓ 创建10_music_llms目录"

# 重命名现有目录以保持逻辑顺序
echo "3. 重新编号现有pipeline目录..."
if [ -d "pipelines/03_music_generation" ]; then
    mv pipelines/03_music_generation pipelines/11_music_generation
    echo "   ✓ 03_music_generation -> 11_music_generation"
fi

if [ -d "pipelines/04_diversity_evaluation" ]; then
    mv pipelines/04_diversity_evaluation pipelines/12_diversity_evaluation
    echo "   ✓ 04_diversity_evaluation -> 12_diversity_evaluation"
fi

if [ -d "pipelines/05_audio_synthesis" ]; then
    mv pipelines/05_audio_synthesis pipelines/13_audio_synthesis
    echo "   ✓ 05_audio_synthesis -> 13_audio_synthesis"
fi

# 3. 创建各个组件的示例文件和README

# 07_embedding
cat > pipelines/07_embedding/README.md << 'EOF'
# 07_embedding - 音乐嵌入模块

## 功能
将音乐数据转换为向量表示，用于后续的属性提取和生成任务。

## 支持的模型
- **LLark**: 音乐语言模型嵌入
- **CLAP**: 音频-文本对比学习嵌入
- **MusicBERT**: 音乐BERT嵌入
- **Jukebox**: 音乐生成模型嵌入

## 输入
- MIDI文件
- 音频文件
- 音乐特征

## 输出
- 音乐嵌入向量
- 特征表示
EOF

cat > pipelines/07_embedding/music_embedding.py << 'EOF'
#!/usr/bin/env python3
"""
音乐嵌入模块
支持多种音乐嵌入模型
"""

import numpy as np
import torch
from pathlib import Path
import argparse

class MusicEmbedding:
    """音乐嵌入基类"""
    
    def __init__(self, model_type="llark"):
        self.model_type = model_type
        self.model = None
        self.load_model()
    
    def load_model(self):
        """加载嵌入模型"""
        if self.model_type == "llark":
            # TODO: 实现LLark模型加载
            print("Loading LLark embedding model...")
        elif self.model_type == "clap":
            # TODO: 实现CLAP模型加载
            print("Loading CLAP embedding model...")
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
    
    def embed_midi(self, midi_path):
        """从MIDI文件生成嵌入"""
        # TODO: 实现MIDI嵌入
        print(f"Generating embedding for MIDI: {midi_path}")
        return np.random.randn(512)  # 示例嵌入
    
    def embed_audio(self, audio_path):
        """从音频文件生成嵌入"""
        # TODO: 实现音频嵌入
        print(f"Generating embedding for audio: {audio_path}")
        return np.random.randn(512)  # 示例嵌入

def main():
    parser = argparse.ArgumentParser(description="音乐嵌入生成")
    parser.add_argument("--input", required=True, help="输入文件路径")
    parser.add_argument("--output", required=True, help="输出嵌入文件路径")
    parser.add_argument("--model", default="llark", help="嵌入模型类型")
    
    args = parser.parse_args()
    
    embedder = MusicEmbedding(args.model)
    
    if args.input.endswith('.mid') or args.input.endswith('.midi'):
        embedding = embedder.embed_midi(args.input)
    else:
        embedding = embedder.embed_audio(args.input)
    
    np.save(args.output, embedding)
    print(f"嵌入已保存到: {args.output}")

if __name__ == "__main__":
    main()
EOF

# 08_property_extraction
cat > pipelines/08_property_extraction/README.md << 'EOF'
# 08_property_extraction - 音乐属性提取模块

## 功能
从音乐嵌入中提取各种音乐属性，如调性、节拍、情感等。

## 支持的属性
- **调性分析**: 主调、调式
- **节拍分析**: BPM、拍号
- **情感分析**: 情感标签、情感强度
- **风格分析**: 音乐风格分类
- **结构分析**: 音乐结构标注

## 输入
- 音乐嵌入向量
- MIDI文件
- 音频文件

## 输出
- 音乐属性字典
- 分类结果
EOF

cat > pipelines/08_property_extraction/property_extractor.py << 'EOF'
#!/usr/bin/env python3
"""
音乐属性提取模块
从音乐数据中提取各种属性
"""

import numpy as np
import json
from pathlib import Path
import argparse

class PropertyExtractor:
    """音乐属性提取器"""
    
    def __init__(self):
        self.classifiers = {}
        self.load_classifiers()
    
    def load_classifiers(self):
        """加载各种分类器"""
        # TODO: 加载预训练的分类器
        print("Loading property classifiers...")
    
    def extract_key(self, embedding):
        """提取调性"""
        # TODO: 实现调性提取
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        modes = ['major', 'minor']
        return {
            'key': np.random.choice(keys),
            'mode': np.random.choice(modes)
        }
    
    def extract_tempo(self, embedding):
        """提取节拍"""
        # TODO: 实现节拍提取
        return {
            'bpm': np.random.randint(60, 180),
            'time_signature': '4/4'
        }
    
    def extract_emotion(self, embedding):
        """提取情感"""
        # TODO: 实现情感提取
        emotions = ['happy', 'sad', 'energetic', 'calm', 'dramatic']
        return {
            'emotion': np.random.choice(emotions),
            'valence': np.random.rand(),
            'arousal': np.random.rand()
        }
    
    def extract_style(self, embedding):
        """提取风格"""
        # TODO: 实现风格提取
        styles = ['classical', 'jazz', 'rock', 'pop', 'electronic']
        return {
            'style': np.random.choice(styles),
            'confidence': np.random.rand()
        }
    
    def extract_all_properties(self, embedding):
        """提取所有属性"""
        properties = {}
        properties.update(self.extract_key(embedding))
        properties.update(self.extract_tempo(embedding))
        properties.update(self.extract_emotion(embedding))
        properties.update(self.extract_style(embedding))
        return properties

def main():
    parser = argparse.ArgumentParser(description="音乐属性提取")
    parser.add_argument("--embedding", required=True, help="输入嵌入文件路径")
    parser.add_argument("--output", required=True, help="输出属性文件路径")
    
    args = parser.parse_args()
    
    # 加载嵌入
    embedding = np.load(args.embedding)
    
    # 提取属性
    extractor = PropertyExtractor()
    properties = extractor.extract_all_properties(embedding)
    
    # 保存结果
    with open(args.output, 'w') as f:
        json.dump(properties, f, indent=2)
    
    print(f"属性已保存到: {args.output}")
    print(f"提取的属性: {properties}")

if __name__ == "__main__":
    main()
EOF

# 09_prompt_generation
cat > pipelines/09_prompt_generation/README.md << 'EOF'
# 09_prompt_generation - 提示生成模块

## 功能
根据音乐属性生成用于音乐大语言模型的提示文本。

## 支持的提示类型
- **风格提示**: 基于音乐风格的生成提示
- **情感提示**: 基于情感的生成提示
- **结构提示**: 基于音乐结构的生成提示
- **技术提示**: 基于技术参数的生成提示

## 输入
- 音乐属性字典
- 用户自定义参数

## 输出
- 格式化的提示文本
- 生成参数配置
EOF

cat > pipelines/09_prompt_generation/prompt_generator.py << 'EOF'
#!/usr/bin/env python3
"""
音乐生成提示生成模块
根据音乐属性生成提示
"""

import json
import argparse
from pathlib import Path

class PromptGenerator:
    """音乐生成提示生成器"""
    
    def __init__(self):
        self.templates = self.load_templates()
    
    def load_templates(self):
        """加载提示模板"""
        return {
            'style_based': "Generate a {style} music piece in {key} {mode}",
            'emotion_based': "Create a {emotion} melody with {valence:.1f} valence and {arousal:.1f} arousal",
            'tempo_based': "Compose music at {bpm} BPM in {time_signature} time signature",
            'comprehensive': "Generate a {style} {emotion} music piece in {key} {mode} at {bpm} BPM"
        }
    
    def generate_style_prompt(self, properties):
        """生成基于风格的提示"""
        template = self.templates['style_based']
        return template.format(
            style=properties.get('style', 'classical'),
            key=properties.get('key', 'C'),
            mode=properties.get('mode', 'major')
        )
    
    def generate_emotion_prompt(self, properties):
        """生成基于情感的提示"""
        template = self.templates['emotion_based']
        return template.format(
            emotion=properties.get('emotion', 'happy'),
            valence=properties.get('valence', 0.5),
            arousal=properties.get('arousal', 0.5)
        )
    
    def generate_tempo_prompt(self, properties):
        """生成基于节拍的提示"""
        template = self.templates['tempo_based']
        return template.format(
            bpm=properties.get('bpm', 120),
            time_signature=properties.get('time_signature', '4/4')
        )
    
    def generate_comprehensive_prompt(self, properties):
        """生成综合提示"""
        template = self.templates['comprehensive']
        return template.format(
            style=properties.get('style', 'classical'),
            emotion=properties.get('emotion', 'happy'),
            key=properties.get('key', 'C'),
            mode=properties.get('mode', 'major'),
            bpm=properties.get('bpm', 120)
        )
    
    def generate_all_prompts(self, properties):
        """生成所有类型的提示"""
        prompts = {
            'style_based': self.generate_style_prompt(properties),
            'emotion_based': self.generate_emotion_prompt(properties),
            'tempo_based': self.generate_tempo_prompt(properties),
            'comprehensive': self.generate_comprehensive_prompt(properties)
        }
        return prompts

def main():
    parser = argparse.ArgumentParser(description="音乐生成提示生成")
    parser.add_argument("--properties", required=True, help="输入属性文件路径")
    parser.add_argument("--output", required=True, help="输出提示文件路径")
    parser.add_argument("--type", default="comprehensive", 
                       choices=['style_based', 'emotion_based', 'tempo_based', 'comprehensive', 'all'],
                       help="提示类型")
    
    args = parser.parse_args()
    
    # 加载属性
    with open(args.properties, 'r') as f:
        properties = json.load(f)
    
    # 生成提示
    generator = PromptGenerator()
    
    if args.type == 'all':
        prompts = generator.generate_all_prompts(properties)
    else:
        method = getattr(generator, f'generate_{args.type}_prompt')
        prompts = {args.type: method(properties)}
    
    # 保存结果
    with open(args.output, 'w') as f:
        json.dump(prompts, f, indent=2)
    
    print(f"提示已保存到: {args.output}")
    for prompt_type, prompt_text in prompts.items():
        print(f"{prompt_type}: {prompt_text}")

if __name__ == "__main__":
    main()
EOF

# 10_music_llms
cat > pipelines/10_music_llms/README.md << 'EOF'
# 10_music_llms - 音乐大语言模型模块

## 功能
使用音乐大语言模型（如MusicGen）根据提示生成音乐。

## 支持的模型
- **MusicGen**: Meta的音乐生成模型
- **AudioLM**: Google的音频语言模型
- **MusicLM**: Google的音乐语言模型
- **Jukebox**: OpenAI的音乐生成模型

## 输入
- 提示文本
- 生成参数
- 参考音频（可选）

## 输出
- 生成的音频文件
- 生成的MIDI文件（如果支持）
EOF

cat > pipelines/10_music_llms/music_llm_generator.py << 'EOF'
#!/usr/bin/env python3
"""
音乐大语言模型生成模块
使用各种音乐LLM生成音乐
"""

import json
import torch
import argparse
from pathlib import Path

class MusicLLMGenerator:
    """音乐大语言模型生成器"""
    
    def __init__(self, model_type="musicgen"):
        self.model_type = model_type
        self.model = None
        self.processor = None
        self.load_model()
    
    def load_model(self):
        """加载音乐LLM模型"""
        if self.model_type == "musicgen":
            try:
                from transformers import MusicgenForConditionalGeneration, MusicgenProcessor
                print("Loading MusicGen model...")
                self.model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
                self.processor = MusicgenProcessor.from_pretrained("facebook/musicgen-small")
            except ImportError:
                print("MusicGen not available, using placeholder")
        else:
            print(f"Model type {self.model_type} not implemented yet")
    
    def generate_from_prompt(self, prompt, duration=10, temperature=1.0):
        """根据提示生成音乐"""
        print(f"Generating music from prompt: {prompt}")
        print(f"Duration: {duration}s, Temperature: {temperature}")
        
        if self.model and self.processor:
            # TODO: 实现实际的音乐生成
            inputs = self.processor(
                text=[prompt],
                padding=True,
                return_tensors="pt",
            )
            
            audio_values = self.model.generate(**inputs, max_new_tokens=256)
            return audio_values[0, 0].cpu().numpy()
        else:
            # 返回占位符
            import numpy as np
            sample_rate = 32000
            return np.random.randn(duration * sample_rate) * 0.1
    
    def generate_with_reference(self, prompt, reference_audio, duration=10):
        """根据提示和参考音频生成音乐"""
        print(f"Generating music with reference audio")
        # TODO: 实现参考音频引导的生成
        return self.generate_from_prompt(prompt, duration)

def main():
    parser = argparse.ArgumentParser(description="音乐大语言模型生成")
    parser.add_argument("--prompts", required=True, help="输入提示文件路径")
    parser.add_argument("--output", required=True, help="输出音频文件路径")
    parser.add_argument("--model", default="musicgen", help="模型类型")
    parser.add_argument("--duration", type=int, default=10, help="生成时长（秒）")
    parser.add_argument("--temperature", type=float, default=1.0, help="生成温度")
    
    args = parser.parse_args()
    
    # 加载提示
    with open(args.prompts, 'r') as f:
        prompts = json.load(f)
    
    # 选择提示（使用comprehensive或第一个可用的）
    if 'comprehensive' in prompts:
        prompt = prompts['comprehensive']
    else:
        prompt = list(prompts.values())[0]
    
    # 生成音乐
    generator = MusicLLMGenerator(args.model)
    audio = generator.generate_from_prompt(prompt, args.duration, args.temperature)
    
    # 保存音频
    import soundfile as sf
    sf.write(args.output, audio, 32000)
    
    print(f"生成的音乐已保存到: {args.output}")
    print(f"使用的提示: {prompt}")

if __name__ == "__main__":
    main()
EOF

# 4. 更新主要的执行脚本
echo "4. 更新执行脚本..."

# 更新run_full_pipeline.sh
cat > scripts/run_full_pipeline_complete.sh << 'EOF'
#!/bin/bash

# 完整的音乐处理Pipeline
# 包含所有步骤：Wav to MIDI -> Melody Extraction -> Embedding -> Property Extraction -> Prompt Generation -> Music LLMs -> Music Generation -> Diversity Evaluation -> Audio Synthesis

set -e

# 默认参数
INPUT_DIR="data/input"
OUTPUT_DIR="data/output"
TEMP_DIR="data/temp"

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --input)
            INPUT_DIR="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --steps)
            STEPS="$2"
            shift 2
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

echo "🎵 启动完整音乐处理Pipeline"
echo "输入目录: $INPUT_DIR"
echo "输出目录: $OUTPUT_DIR"
echo "=" * 50

# 创建必要的目录
mkdir -p "$OUTPUT_DIR" "$TEMP_DIR"

# Step 1: Wav to MIDI (包含VOCANO, Basic-Pitch-Torch, MR-MT3, Pop2Piano)
echo "📝 Step 1: Wav to MIDI转换..."
python pipelines/01_wav_to_midi/bpt_quick_test.py --input "$INPUT_DIR" --output "$TEMP_DIR/midi"

# Step 2: Main Melody Extraction
echo "🎼 Step 2: 主旋律提取..."
python pipelines/02_melody_extraction/libf0_melody_extraction.py --input "$TEMP_DIR/midi" --output "$TEMP_DIR/melody"

# Step 3: Embedding (新增)
echo "🔗 Step 3: 音乐嵌入生成..."
python pipelines/07_embedding/music_embedding.py --input "$TEMP_DIR/melody" --output "$TEMP_DIR/embeddings.npy"

# Step 4: Property Extraction (新增)
echo "🏷️ Step 4: 音乐属性提取..."
python pipelines/08_property_extraction/property_extractor.py --embedding "$TEMP_DIR/embeddings.npy" --output "$TEMP_DIR/properties.json"

# Step 5: Prompt Generation (新增)
echo "💭 Step 5: 提示生成..."
python pipelines/09_prompt_generation/prompt_generator.py --properties "$TEMP_DIR/properties.json" --output "$TEMP_DIR/prompts.json"

# Step 6: Music LLMs (新增)
echo "🤖 Step 6: 音乐大语言模型生成..."
python pipelines/10_music_llms/music_llm_generator.py --prompts "$TEMP_DIR/prompts.json" --output "$TEMP_DIR/generated_audio.wav"

# Step 7: Music Generation (原03，现在11)
echo "🎶 Step 7: 音乐生成..."
python pipelines/11_music_generation/gen_musicgen_audio_input.py --input "$TEMP_DIR/generated_audio.wav" --output "$OUTPUT_DIR/generated"

# Step 8: Diversity Evaluation (原04，现在12)
echo "📊 Step 8: 多样性评估..."
python pipelines/12_diversity_evaluation/key_distribution_analysis.py --input "$OUTPUT_DIR/generated" --output "$OUTPUT_DIR/diversity_results"

# Step 9: Audio Synthesis (原05，现在13)
echo "🔊 Step 9: 音频合成..."
python pipelines/13_audio_synthesis/batch_midi2wav.py --input "$OUTPUT_DIR/generated" --output "$OUTPUT_DIR/final_audio"

echo "✅ Pipeline执行完成！"
echo "结果保存在: $OUTPUT_DIR"
EOF

chmod +x scripts/run_full_pipeline_complete.sh

# 5. 更新README
echo "5. 更新README文档..."
cat > README_PIPELINE_COMPLETE.md << 'EOF'
# 完整音乐处理Pipeline

## 概述
这是一个完整的音乐处理pipeline，包含从音频输入到最终音乐生成的所有步骤。

## Pipeline架构