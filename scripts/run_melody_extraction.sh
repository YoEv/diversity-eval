#!/bin/bash
INPUT_DIR=${1:-"data/input/Shutter_Solo_Dataset_15s"}
OUTPUT_FILE=${2:-"data/output/melody.json"}
python pipelines/02_melody_extraction/swipe_melody_extraction.py --input $INPUT_DIR --output $OUTPUT_FILE
