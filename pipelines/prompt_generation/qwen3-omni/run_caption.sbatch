#!/bin/bash
#SBATCH --job-name=qwen_caption
#SBATCH --account=musi
#SBATCH --qos=coe-ice
#SBATCH --partition=coe-gpu
#SBATCH --gres=gpu:2
#SBATCH --time=12:00:00 
#SBATCH --mem=128G
#SBATCH --cpus-per-task=8
#SBATCH --output=qwen_caption_%j.out
#SBATCH --error=qwen_caption_%j.err

# 加载 Apptainer 或其他环境（如果需要）
# ...

# 执行你的 Python 脚本
apptainer exec --nv \
    --bind "$HOME/scratch/qwen3_omni_ws:/data/shared/Qwen3-Omni" \
    "$HOME/scratch/qwen3-omni-3-cu124.sif" \
    python /home/hice1/xli3252/Desktop/diversity-eval/pipelines/prompt_generation/qwen3-omni/qwen_omni_batch_caption_test.py \
    --device cuda \
    --max-new-tokens 256 \
    --flash-attn2 \
    --force-gpu \
    --batch-size 4 \
    --num-workers 8 \