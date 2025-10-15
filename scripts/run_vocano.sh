#!/bin/bash

# VOCANO - Vocal Note Transcription Script
# Usage: ./run_vocano.sh <input_wav_file> [output_name]

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 <input_wav_file> [output_name]"
    echo "Example: $0 /path/to/audio.wav my_transcription"
    exit 1
fi

INPUT_WAV="$1"
OUTPUT_NAME="${2:-$(basename "$INPUT_WAV" .wav)}"

# Check if input file exists
if [ ! -f "$INPUT_WAV" ]; then
    echo "Error: Input file '$INPUT_WAV' not found"
    exit 1
fi

# Navigate to VOCANO directory
cd /home/evev/diversity-eval/external/VOCANO

echo "Running VOCANO transcription on: $INPUT_WAV"
echo "Output name: $OUTPUT_NAME"

# Run VOCANO transcription
python -m vocano.transcription -n "$OUTPUT_NAME" -wd "$INPUT_WAV"

echo "VOCANO transcription completed!"
echo "Results can be found in:"
echo "  - WAV: VOCANO/generated/wav/"
echo "  - MIDI: VOCANO/generated/midi/"

# Copy results to our pipeline output directory
OUTPUT_DIR="/home/evev/diversity-eval/data/output/vocano_output"
mkdir -p "$OUTPUT_DIR"

if [ -d "generated/wav" ]; then
    cp -r generated/wav/* "$OUTPUT_DIR/" 2>/dev/null || true
fi

if [ -d "generated/midi" ]; then
    cp -r generated/midi/* "$OUTPUT_DIR/" 2>/dev/null || true
fi

echo "Results also copied to: $OUTPUT_DIR"
