#!/bin/bash
INPUT_DIR=${1:-"data/input/Shutter_Solo_Dataset_15s"}
OUTPUT_DIR=${2:-"data/output/pop2piano"}
python pipelines/06_pop2piano/batch_pop2piano.py --input $INPUT_DIR --output $OUTPUT_DIR
