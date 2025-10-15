#!/bin/bash

# Basic Pitch Torch 快速测试脚本
TEST_FILE=${1:-"data/input/Shutter_Solo_Dataset_15s"}

echo "运行Basic Pitch Torch快速测试..."
echo "测试文件/目录: $TEST_FILE"

python pipelines/01_wav_to_midi/bpt_quick_test.py $TEST_FILE

echo "快速测试完成!"
