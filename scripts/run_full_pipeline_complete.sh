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
