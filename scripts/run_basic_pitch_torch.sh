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
