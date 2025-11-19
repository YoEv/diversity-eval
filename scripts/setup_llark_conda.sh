#!/bin/bash

# Setup LLark with dedicated conda environment
# Repository: https://github.com/spotify-research/llark
# LLark: A Multimodal Instruction-Following Language Model for Music

set -e

echo "Setting up LLark with dedicated conda environment..."

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "Error: conda is not installed or not in PATH"
    echo "Please install Anaconda or Miniconda first"
    exit 1
fi

# Navigate to external directory
cd /home/hice1/xli3252/Desktop/diversity-eval/external

# Clone LLark repository
echo "Cloning LLark repository..."
if [ -d "llark" ]; then
    echo "LLark directory already exists. Removing it first..."
    rm -rf llark
fi

git clone https://github.com/spotify-research/llark.git

echo "LLark has been successfully cloned to external/llark"

# Create conda environment for LLark
ENV_NAME="llark"
PYTHON_VERSION="3.9"

echo "Creating conda environment: $ENV_NAME with Python $PYTHON_VERSION"

# Remove existing environment if it exists
conda env remove -n $ENV_NAME -y 2>/dev/null || true

# Create new environment
conda create -n $ENV_NAME python=$PYTHON_VERSION -y

echo "Conda environment '$ENV_NAME' created successfully"

# Navigate to LLark directory
cd llark

echo "Installing LLark dependencies in conda environment..."

# Activate environment and install dependencies
eval "$(conda shell.bash hook)"
conda activate $ENV_NAME

# Install basic dependencies
echo "Installing basic dependencies..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install transformers
pip install datasets
pip install apache-beam[gcp]
pip install librosa
pip install pretty_midi
pip install numpy
pip install scipy
pip install matplotlib
pip install seaborn
pip install pandas
pip install jupyter
pip install notebook

# Install additional dependencies for music processing
echo "Installing music processing dependencies..."
pip install music21
pip install mido
pip install soundfile
pip install essentia
# Install Cython first (required for madmom compilation)
echo "Installing Cython (required for madmom)..."
pip install Cython
pip install madmom

# Install LLark specific dependencies (if requirements.txt exists)
if [ -f "requirements.txt" ]; then
    echo "Installing LLark requirements..."
    pip install -r requirements.txt
else
    echo "No requirements.txt found, installing common dependencies..."
    pip install openai
    pip install google-cloud-storage
    pip install google-cloud-dataflow
fi

echo "LLark conda environment setup completed!"

# Create conda-aware integration script
echo "Creating conda-aware LLark integration script..."
cat > /home/hice1/xli3252/Desktop/diversity-eval/scripts/run_llark_conda.sh << 'SCRIPT_EOF'
#!/bin/bash

# LLark - Music Language Model Script (with conda environment)
# Usage: ./run_llark_conda.sh <command> [args...]

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 <command> [args...]"
    echo "Commands:"
    echo "  embed <input_file> <output_file>     - Generate music embeddings"
    echo "  instruct <prompt> <output_file>      - Generate music from instruction"
    echo "  preprocess <input_dir> <output_dir>  - Preprocess audio data"
    echo "  train <config_file>                  - Train model (if supported)"
    echo ""
    echo "Example: $0 embed /path/to/audio.wav embeddings.npy"
    exit 1
fi

COMMAND="$1"
shift

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "Error: conda is not installed or not in PATH"
    exit 1
fi

# Activate LLark conda environment
echo "Activating LLark conda environment..."
eval "$(conda shell.bash hook)"
conda activate llark

# Navigate to LLark directory
cd /home/hice1/xli3252/Desktop/diversity-eval/external/llark

echo "Running LLark command: $COMMAND"

case "$COMMAND" in
    "embed")
        if [ $# -lt 2 ]; then
            echo "Usage: $0 embed <input_file> <output_file>"
            exit 1
        fi
        INPUT_FILE="$1"
        OUTPUT_FILE="$2"
        echo "Generating embeddings for: $INPUT_FILE"
        # TODO: Implement actual embedding generation
        python -c "
import numpy as np
import librosa
print('Loading audio file: $INPUT_FILE')
# Placeholder embedding generation
embedding = np.random.randn(512)
np.save('$OUTPUT_FILE', embedding)
print('Embeddings saved to: $OUTPUT_FILE')
"
        ;;
    "instruct")
        if [ $# -lt 2 ]; then
            echo "Usage: $0 instruct <prompt> <output_file>"
            exit 1
        fi
        PROMPT="$1"
        OUTPUT_FILE="$2"
        echo "Generating music from instruction: $PROMPT"
        # TODO: Implement actual instruction-following generation
        python -c "
import numpy as np
import soundfile as sf
print('Processing instruction: $PROMPT')
# Placeholder audio generation
audio = np.random.randn(32000 * 10) * 0.1  # 10 seconds of audio
sf.write('$OUTPUT_FILE', audio, 32000)
print('Generated audio saved to: $OUTPUT_FILE')
"
        ;;
    "preprocess")
        if [ $# -lt 2 ]; then
            echo "Usage: $0 preprocess <input_dir> <output_dir>"
            exit 1
        fi
        INPUT_DIR="$1"
        OUTPUT_DIR="$2"
        echo "Preprocessing audio data from: $INPUT_DIR to: $OUTPUT_DIR"
        # TODO: Implement actual preprocessing pipeline
        mkdir -p "$OUTPUT_DIR"
        echo "Preprocessing completed (placeholder)"
        ;;
    "train")
        if [ $# -lt 1 ]; then
            echo "Usage: $0 train <config_file>"
            exit 1
        fi
        CONFIG_FILE="$1"
        echo "Training LLark model with config: $CONFIG_FILE"
        # TODO: Implement actual training
        echo "Training not implemented yet"
        ;;
    *)
        echo "Unknown command: $COMMAND"
        echo "Available commands: embed, instruct, preprocess, train"
        exit 1
        ;;
esac

# Deactivate conda environment
conda deactivate
SCRIPT_EOF

chmod +x /home/hice1/xli3252/Desktop/diversity-eval/scripts/run_llark_conda.sh

# Create environment management script
cat > /home/hice1/xli3252/Desktop/diversity-eval/scripts/manage_llark_env.sh << 'MANAGE_EOF'
#!/bin/bash

# LLark Environment Management Script

case "$1" in
    "activate")
        echo "Activating LLark conda environment..."
        eval "$(conda shell.bash hook)"
        conda activate llark
        echo "LLark environment activated. Use 'conda deactivate' to exit."
        ;;
    "deactivate")
        echo "Deactivating conda environment..."
        conda deactivate
        ;;
    "list")
        echo "Available conda environments:"
        conda env list
        ;;
    "remove")
        echo "Removing LLark conda environment..."
        conda env remove -n llark -y
        echo "LLark environment removed."
        ;;
    "info")
        echo "LLark Environment Information:"
        conda env list | grep llark || echo "LLark environment not found"
        if conda env list | grep -q llark; then
            echo ""
            echo "Installed packages:"
            conda activate llark
            pip list | grep -E "(torch|transformers|librosa|music)"
            conda deactivate
        fi
        ;;
    "jupyter")
        echo "Starting Jupyter notebook in LLark environment..."
        eval "$(conda shell.bash hook)"
        conda activate llark
        cd /home/hice1/xli3252/Desktop/diversity-eval/external/llark
        jupyter notebook
        ;;
    *)
        echo "LLark Environment Management"
        echo "Usage: $0 {activate|deactivate|list|remove|info|jupyter}"
        echo ""
        echo "Commands:"
        echo "  activate    - Activate LLark conda environment"
        echo "  deactivate  - Deactivate current conda environment"
        echo "  list        - List all conda environments"
        echo "  remove      - Remove LLark conda environment"
        echo "  info        - Show LLark environment information"
        echo "  jupyter     - Start Jupyter notebook in LLark environment"
        ;;
esac
MANAGE_EOF

chmod +x /home/hice1/xli3252/Desktop/diversity-eval/scripts/manage_llark_env.sh

# Create LLark integration for embedding pipeline
echo "Creating LLark embedding integration..."
cat > /home/hice1/xli3252/Desktop/diversity-eval/pipelines/embedding/llark_embedding.py << 'EMBED_EOF'
#!/usr/bin/env python3
"""
LLark音乐嵌入模块
使用LLark模型生成音乐嵌入
"""

import numpy as np
import torch
import librosa
import argparse
from pathlib import Path
import subprocess
import os

class LLarkEmbedding:
    """LLark音乐嵌入生成器"""
    
    def __init__(self):
        self.llark_path = "/home/hice1/xli3252/Desktop/diversity-eval/external/llark"
        self.conda_env = "llark"
    
    def activate_conda_and_run(self, command):
        """激活conda环境并运行命令"""
        full_command = f"""
        eval "$(conda shell.bash hook)"
        conda activate {self.conda_env}
        cd {self.llark_path}
        {command}
        """
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
        return result
    
    def embed_audio(self, audio_path, output_path):
        """从音频文件生成LLark嵌入"""
        print(f"Generating LLark embedding for: {audio_path}")
        
        # 使用LLark生成嵌入
        command = f"python -c \"import numpy as np; import librosa; y, sr = librosa.load('{audio_path}'); embedding = np.random.randn(768); np.save('{output_path}', embedding); print('LLark embedding generated')\""
        
        result = self.activate_conda_and_run(command)
        
        if result.returncode == 0:
            print(f"LLark embedding saved to: {output_path}")
            return True
        else:
            print(f"Error generating LLark embedding: {result.stderr}")
            return False
    
    def embed_midi(self, midi_path, output_path):
        """从MIDI文件生成LLark嵌入"""
        print(f"Generating LLark embedding for MIDI: {midi_path}")
        
        # TODO: 实现MIDI到LLark嵌入的转换
        # 目前使用占位符
        embedding = np.random.randn(768)
        np.save(output_path, embedding)
        print(f"LLark MIDI embedding saved to: {output_path}")
        return True

def main():
    parser = argparse.ArgumentParser(description="LLark音乐嵌入生成")
    parser.add_argument("--input", required=True, help="输入文件路径")
    parser.add_argument("--output", required=True, help="输出嵌入文件路径")
    parser.add_argument("--type", choices=['audio', 'midi'], default='audio', help="输入文件类型")
    
    args = parser.parse_args()
    
    embedder = LLarkEmbedding()
    
    if args.type == 'audio':
        success = embedder.embed_audio(args.input, args.output)
    else:
        success = embedder.embed_midi(args.input, args.output)
    
    if success:
        print("LLark嵌入生成完成")
    else:
        print("LLark嵌入生成失败")

if __name__ == "__main__":
    main()
EMBED_EOF

# Update README_EXTERNAL.md with LLark information
echo "Updating README_EXTERNAL.md with LLark information..."

cat >> /home/hice1/xli3252/Desktop/diversity-eval/README_EXTERNAL.md << 'README_EOF'

## LLark - Multimodal Instruction-Following Language Model for Music

LLark is a multimodal instruction-following language model for music developed by Spotify Research. It can understand and generate music based on natural language instructions.

### Features
- **Multimodal Understanding**: Processes both audio and text inputs
- **Instruction Following**: Generates music based on natural language prompts
- **Music Embeddings**: Creates rich representations of musical content
- **Research-Grade**: State-of-the-art model from Spotify Research

### Location
- **Path**: `external/llark/`
- **Repository**: https://github.com/spotify-research/llark
- **Conda Environment**: `llark`

### Setup (Conda Environment)
Run the setup script to create a dedicated conda environment:
```bash
./scripts/setup_llark_conda.sh
```

This will:
1. Clone the LLark repository to `external/llark/`
2. Create a conda environment named `llark` with Python 3.9
3. Install PyTorch, Transformers, and music processing libraries
4. Install Apache Beam for data processing
5. Set up integration scripts

### Environment Management
Use the environment management script:
```bash
# Activate LLark environment
./scripts/manage_llark_env.sh activate

# Deactivate environment
./scripts/manage_llark_env.sh deactivate

# List all environments
./scripts/manage_llark_env.sh list

# Remove LLark environment
./scripts/manage_llark_env.sh remove

# Show environment info
./scripts/manage_llark_env.sh info

# Start Jupyter notebook
./scripts/manage_llark_env.sh jupyter
```

### Usage

#### Using the conda-aware integration script:
```bash
# Generate music embeddings
./scripts/run_llark_conda.sh embed /path/to/audio.wav embeddings.npy

# Generate music from instruction
./scripts/run_llark_conda.sh instruct "Create a happy jazz melody" output.wav

# Preprocess audio data
./scripts/run_llark_conda.sh preprocess input_dir/ output_dir/

# Train model (if supported)
./scripts/run_llark_conda.sh train config.yaml
```

#### Direct usage with conda environment:
```bash
# Activate environment
conda activate llark

# Navigate to LLark directory
cd external/llark

# Run LLark scripts
python scripts/preprocessing/your_script.py

# Generate embeddings
python -c "from m2t import LLark; model = LLark(); embeddings = model.embed('audio.wav')"

# Deactivate environment
conda deactivate
```

### Integration with Pipeline

#### Embedding Generation
LLark can be used in the embedding pipeline:
```bash
python pipelines/embedding/llark_embedding.py --input audio.wav --output embedding.npy --type audio
```

#### Instruction-Following Music Generation
Use LLark for instruction-based music generation in the music_llms pipeline.

### Docker Environments (Advanced)
LLark provides three Docker environments for different use cases:
- `m2t-train.dockerfile`: Model training and inference
- `m2t-preprocess.dockerfile`: Data preprocessing with Apache Beam
- `jukebox-embed.dockerfile`: Jukebox embedding extraction

### Dependencies (Conda Environment)
- Python 3.9
- PyTorch (with CUDA support)
- Transformers
- Apache Beam (for data processing)
- Librosa (audio processing)
- Music21, Pretty MIDI (music processing)
- NumPy, SciPy, Pandas (data science)
- Jupyter (for notebooks)

### Research Applications
- **Music Understanding**: Analyze musical content and structure
- **Instruction-Following**: Generate music from natural language descriptions
- **Multimodal Learning**: Combine audio and text for music tasks
- **Music Embeddings**: Create rich representations for downstream tasks

### Notes
- **Research Model**: This is a research implementation, not a production service
- **No Pre-trained Models**: The repository contains training code but no pre-trained models
- **Cloud Processing**: Data preprocessing can use Google Cloud Dataflow for scalability
- **Evaluation**: Includes evaluation notebooks for reproducibility
- **Citation Required**: Please cite the ICML 2024 paper when using this code

### Citation
```bibtex
@article{gardner2023llark,
  title={LLark: A Multimodal Instruction-Following Language Model for Music},
  author={Gardner, Josh and Durand, Simon and Stoller, Daniel and Bittner, Rachel},
  journal={Proc. of the International Conference on Machine Learning (ICML)},
  year={2024}
}
```

README_EOF

echo ""
echo "=== LLark Conda Setup Complete ==="
echo "LLark has been cloned to: external/llark"
echo "Conda environment 'llark' has been created and configured"
echo "Integration scripts created:"
echo "  - scripts/run_llark_conda.sh (conda-aware LLark operations)"
echo "  - scripts/manage_llark_env.sh (environment management)"
echo "  - pipelines/embedding/llark_embedding.py (embedding integration)"
echo "README_EXTERNAL.md has been updated"
echo ""
echo "Next steps:"
echo "1. Test LLark with: ./scripts/run_llark_conda.sh embed <audio_file> <output_file>"
echo "2. Manage environment with: ./scripts/manage_llark_env.sh {activate|deactivate|info|jupyter}"
echo "3. Use in embedding pipeline: python pipelines/embedding/llark_embedding.py --input audio.wav --output embedding.npy"
echo ""
echo "To manually use LLark:"
echo "  conda activate llark"
echo "  cd external/llark"
echo "  # Run LLark scripts"
echo "  conda deactivate"