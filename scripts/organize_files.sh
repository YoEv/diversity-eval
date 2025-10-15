#!/bin/bash

echo "开始整理文件结构（移动文件和txt文件）..."

# 创建主要目录
mkdir -p pipelines/01_wav_to_midi
mkdir -p pipelines/02_melody_extraction  
mkdir -p pipelines/03_music_generation
mkdir -p pipelines/04_diversity_evaluation
mkdir -p pipelines/05_audio_synthesis
mkdir -p pipelines/06_pop2piano
mkdir -p pipelines/utils
mkdir -p scripts
mkdir -p data/input
mkdir -p data/output
mkdir -p data/results/key_analysis
mkdir -p data/results/comparison_results

echo "创建目录完成"

# 移动文件到对应目录
echo "开始移动Python文件..."

# 01_wav_to_midi - MIDI转换相关
mv test_mr_mt3*.py pipelines/01_wav_to_midi/ 2>/dev/null || true
mv download_mr_mt3*.py pipelines/01_wav_to_midi/ 2>/dev/null || true
mv setup_mr_mt3.sh pipelines/01_wav_to_midi/ 2>/dev/null || true
mv run_mr_mt3_test.py pipelines/01_wav_to_midi/ 2>/dev/null || true

# 02_melody_extraction - 旋律提取相关
mv *melody_extraction.py pipelines/02_melody_extraction/ 2>/dev/null || true
mv libf0_*.py pipelines/02_melody_extraction/ 2>/dev/null || true
mv libf0_*.json pipelines/02_melody_extraction/ 2>/dev/null || true

# 03_music_generation - 音乐生成相关
mv gen_musicgen_audio_input.py pipelines/03_music_generation/ 2>/dev/null || true
mv gen/ pipelines/03_music_generation/ 2>/dev/null || true

# 04_diversity_evaluation - 多样性评估相关
mv key_*.py pipelines/04_diversity_evaluation/ 2>/dev/null || true
mv *analysis*.py pipelines/04_diversity_evaluation/ 2>/dev/null || true
mv compare_key_results.py pipelines/04_diversity_evaluation/ 2>/dev/null || true
mv create_uniform_distribution.py pipelines/04_diversity_evaluation/ 2>/dev/null || true
mv match_bj_keys.py pipelines/04_diversity_evaluation/ 2>/dev/null || true
mv normalize_bj_keys.py pipelines/04_diversity_evaluation/ 2>/dev/null || true

# 05_audio_synthesis - 音频合成相关
mv f0_to_audio_synthesis*.py pipelines/05_audio_synthesis/ 2>/dev/null || true
mv batch_midi2wav.py pipelines/05_audio_synthesis/ 2>/dev/null || true
mv midi2wav.py pipelines/05_audio_synthesis/ 2>/dev/null || true
mv run_batch_synthesis.py pipelines/05_audio_synthesis/ 2>/dev/null || true

# 06_pop2piano - Pop2Piano相关
mv *pop2piano*.py pipelines/06_pop2piano/ 2>/dev/null || true
mv batch_pop2piano.py pipelines/06_pop2piano/ 2>/dev/null || true

# utils - 工具文件
mv cut_audio_15s.py pipelines/utils/ 2>/dev/null || true
mv divide_audio_15s.py pipelines/utils/ 2>/dev/null || true
mv fix_numpy_compatibility.py pipelines/utils/ 2>/dev/null || true
mv numpy_patch.py pipelines/utils/ 2>/dev/null || true
mv shutterstock_music_downloader.py pipelines/utils/ 2>/dev/null || true

echo "开始移动txt文件..."

# 移动key相关的txt文件到diversity_evaluation
mv *keys*.txt pipelines/04_diversity_evaluation/ 2>/dev/null || true
mv *Key*.txt pipelines/04_diversity_evaluation/ 2>/dev/null || true
mv gen_melody_keys*.txt pipelines/04_diversity_evaluation/ 2>/dev/null || true
mv key_comparison_results.txt pipelines/04_diversity_evaluation/ 2>/dev/null || true
mv uniform_distri.txt pipelines/04_diversity_evaluation/ 2>/dev/null || true

# 移动分析结果目录
mv *analysis_results* data/results/key_analysis/ 2>/dev/null || true
mv analysis_* data/results/key_analysis/ 2>/dev/null || true
mv uniform_comparison_results/ data/results/comparison_results/ 2>/dev/null || true

# 移动其他txt文件
mv test.txt pipelines/utils/ 2>/dev/null || true

# 移动数据目录（如果还没移动的话）
echo "移动数据目录..."
if [ ! -d "data/input/Shutter_Solo_Dataset" ]; then
    mv Shutter_Solo_Dataset* data/input/ 2>/dev/null || true
fi
if [ ! -d "data/input/BJ_opera" ]; then
    mv BJ_opera* data/input/ 2>/dev/null || true
fi
if [ ! -d "data/input/Shutter_Songs" ]; then
    mv Shutter_Songs data/input/ 2>/dev/null || true
fi

# 移动输出目录（如果还没移动的话）
if [ ! -d "data/output/midi_output" ]; then
    mv *_output data/output/ 2>/dev/null || true
fi
if [ ! -d "data/output/swipe_synthesized_audio" ]; then
    mv *_synthesized_audio data/output/ 2>/dev/null || true
fi
if [ ! -d "data/output/wav_output" ]; then
    mv wav_output data/output/ 2>/dev/null || true
fi

# 移动生成的音频目录
mv gen_*melody* data/output/ 2>/dev/null || true

echo "文件移动完成"

# 创建执行脚本
echo "创建执行脚本..."

# 创建完整pipeline脚本
cat > scripts/run_full_pipeline.sh << 'EOF'
#!/bin/bash

# 完整音频处理pipeline
INPUT_DIR=${1:-"data/input/Shutter_Solo_Dataset_15s"}
OUTPUT_DIR=${2:-"data/output/pipeline_results"}

echo "开始完整pipeline处理..."
echo "输入目录: $INPUT_DIR"
echo "输出目录: $OUTPUT_DIR"

mkdir -p $OUTPUT_DIR

# 步骤1: 音频转MIDI
echo "步骤1: 音频转MIDI..."
python pipelines/01_wav_to_midi/test_mr_mt3_patched.py --input $INPUT_DIR --output $OUTPUT_DIR/midi

# 步骤2: 旋律提取
echo "步骤2: 旋律提取..."
python pipelines/02_melody_extraction/swipe_melody_extraction.py --input $INPUT_DIR --output $OUTPUT_DIR/melody.json

# 步骤3: 音乐生成
echo "步骤3: 音乐生成..."
python pipelines/03_music_generation/gen_musicgen_audio_input.py --input $INPUT_DIR --output $OUTPUT_DIR/generated

# 步骤4: 音频合成
echo "步骤4: 音频合成..."
python pipelines/05_audio_synthesis/f0_to_audio_synthesis_pure_midi.py --input $OUTPUT_DIR/melody.json --output $OUTPUT_DIR/synthesized

# 步骤5: 多样性评估
echo "步骤5: 多样性评估..."
python pipelines/04_diversity_evaluation/key_distribution_analysis.py --input $OUTPUT_DIR/generated --output $OUTPUT_DIR/analysis

echo "Pipeline完成!"
EOF

# 创建单步执行脚本
cat > scripts/run_wav_to_midi.sh << 'EOF'
#!/bin/bash
INPUT_DIR=${1:-"data/input/Shutter_Solo_Dataset_15s"}
OUTPUT_DIR=${2:-"data/output/midi"}
python pipelines/01_wav_to_midi/test_mr_mt3_patched.py --input $INPUT_DIR --output $OUTPUT_DIR
EOF

cat > scripts/run_melody_extraction.sh << 'EOF'
#!/bin/bash
INPUT_DIR=${1:-"data/input/Shutter_Solo_Dataset_15s"}
OUTPUT_FILE=${2:-"data/output/melody.json"}
python pipelines/02_melody_extraction/swipe_melody_extraction.py --input $INPUT_DIR --output $OUTPUT_FILE
EOF

cat > scripts/run_music_generation.sh << 'EOF'
#!/bin/bash
INPUT_DIR=${1:-"data/input/Shutter_Solo_Dataset_15s"}
OUTPUT_DIR=${2:-"data/output/generated"}
python pipelines/03_music_generation/gen_musicgen_audio_input.py --input $INPUT_DIR --output $OUTPUT_DIR
EOF

cat > scripts/run_audio_synthesis.sh << 'EOF'
#!/bin/bash
INPUT_FILE=${1:-"data/output/melody.json"}
OUTPUT_DIR=${2:-"data/output/synthesized"}
python pipelines/05_audio_synthesis/f0_to_audio_synthesis_pure_midi.py --input $INPUT_FILE --output $OUTPUT_DIR
EOF

cat > scripts/run_pop2piano.sh << 'EOF'
#!/bin/bash
INPUT_DIR=${1:-"data/input/Shutter_Solo_Dataset_15s"}
OUTPUT_DIR=${2:-"data/output/pop2piano"}
python pipelines/06_pop2piano/batch_pop2piano.py --input $INPUT_DIR --output $OUTPUT_DIR
EOF

cat > scripts/run_diversity_evaluation.sh << 'EOF'
#!/bin/bash
INPUT_DIR=${1:-"data/output/generated"}
OUTPUT_DIR=${2:-"data/results/analysis"}
python pipelines/04_diversity_evaluation/key_distribution_analysis.py --input $INPUT_DIR --output $OUTPUT_DIR
EOF

# 设置执行权限
chmod +x scripts/*.sh

echo "执行脚本创建完成"

# 创建README文件
cat > README_PIPELINE.md << 'EOF'
# 音频处理Pipeline

## 目录结构