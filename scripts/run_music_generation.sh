#!/bin/bash
INPUT_DIR=${1:-"data/input/Shutter_Solo_Dataset_15s"}
OUTPUT_DIR=${2:-"data/output/generated"}
python pipelines/03_music_generation/gen_musicgen_audio_input.py --input $INPUT_DIR --output $OUTPUT_DIR
