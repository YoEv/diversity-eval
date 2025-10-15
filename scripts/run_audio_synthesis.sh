#!/bin/bash
INPUT_FILE=${1:-"data/output/melody.json"}
OUTPUT_DIR=${2:-"data/output/synthesized"}
python pipelines/05_audio_synthesis/f0_to_audio_synthesis_pure_midi.py --input $INPUT_FILE --output $OUTPUT_DIR
