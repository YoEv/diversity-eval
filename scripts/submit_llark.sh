#!/bin/bash

# Submit LLark setup job to SLURM

echo "Submitting LLark setup job to PACE ICE GPU..."

# Ensure logs directory exists
mkdir -p /home/hice1/xli3252/Desktop/diversity-eval/logs

# Submit the job
JOB_ID=$(sbatch --parsable /home/hice1/xli3252/Desktop/diversity-eval/scripts/setup_llark.sbatch)

if [ $? -eq 0 ]; then
    echo "✅ Job submitted successfully!"
    echo "Job ID: $JOB_ID"
    echo ""
    echo "Monitor commands:"
    echo "  Job status: squeue -u $USER"
    echo "  Job details: scontrol show job $JOB_ID"
    echo "  Output log: tail -f logs/llark_setup_${JOB_ID}.out"
    echo "  Error log: tail -f logs/llark_setup_${JOB_ID}.err"
    echo ""
    echo "Cancel job: scancel $JOB_ID"
    echo ""
    echo "Estimated completion time: ~30-60 minutes"
else
    echo "❌ Failed to submit job"
    exit 1
fi