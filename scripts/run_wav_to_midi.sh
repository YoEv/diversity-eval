#!/bin/bash
INPUT_DIR=${1:-"data/input/Shutter_Solo_Dataset_15s"}
OUTPUT_DIR=${2:-"data/output/midi"}
python pipelines/01_wav_to_midi/test_mr_mt3_patched.py --input $INPUT_DIR --output $OUTPUT_DIR
