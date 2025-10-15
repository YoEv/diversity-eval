#!/bin/bash

# 完整音频处理pipeline
INPUT_DIR=${1:-"data/input/Shutter_Solo_Dataset_15s"}
OUTPUT_DIR=${2:-"data/output/pipeline_results"}

echo "开始完整pipeline处理..."
echo "输入目录: $INPUT_DIR"
echo "输出目录: $OUTPUT_DIR"

mkdir -p $OUTPUT_DIR

# 步骤1: 音频转MIDI
echo "步骤1: 音频转MIDI..."
python pipelines/01_wav_to_midi/test_mr_mt3_patched.py --input $INPUT_DIR --output $OUTPUT_DIR/midi

# 步骤2: 旋律提取
echo "步骤2: 旋律提取..."
python pipelines/02_melody_extraction/swipe_melody_extraction.py --input $INPUT_DIR --output $OUTPUT_DIR/melody.json

# 步骤3: 音乐生成
echo "步骤3: 音乐生成..."
python pipelines/03_music_generation/gen_musicgen_audio_input.py --input $INPUT_DIR --output $OUTPUT_DIR/generated

# 步骤4: 音频合成
echo "步骤4: 音频合成..."
python pipelines/05_audio_synthesis/f0_to_audio_synthesis_pure_midi.py --input $OUTPUT_DIR/melody.json --output $OUTPUT_DIR/synthesized

# 步骤5: 多样性评估
echo "步骤5: 多样性评估..."
python pipelines/04_diversity_evaluation/key_distribution_analysis.py --input $OUTPUT_DIR/generated --output $OUTPUT_DIR/analysis

echo "Pipeline完成!"
