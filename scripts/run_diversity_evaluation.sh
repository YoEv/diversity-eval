#!/bin/bash
INPUT_DIR=${1:-"data/output/generated"}
OUTPUT_DIR=${2:-"data/results/analysis"}
python pipelines/04_diversity_evaluation/key_distribution_analysis.py --input $INPUT_DIR --output $OUTPUT_DIR
