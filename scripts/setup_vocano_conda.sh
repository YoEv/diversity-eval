#!/bin/bash

# Setup VOCANO with dedicated conda environment
# Repository: https://github.com/B05901022/VOCANO

set -e

echo "Setting up VOCANO with dedicated conda environment..."

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "Error: conda is not installed or not in PATH"
    echo "Please install Anaconda or Miniconda first"
    exit 1
fi

# Create conda environment for VOCANO
ENV_NAME="vocano"
PYTHON_VERSION="3.8"

echo "Creating conda environment: $ENV_NAME with Python $PYTHON_VERSION"

# Remove existing environment if it exists
conda env remove -n $ENV_NAME -y 2>/dev/null || true

# Create new environment
conda create -n $ENV_NAME python=$PYTHON_VERSION -y

echo "Conda environment '$ENV_NAME' created successfully"

# Navigate to VOCANO directory
cd /home/evev/diversity-eval/external/VOCANO

echo "Installing VOCANO dependencies in conda environment..."

# Activate environment and install dependencies
eval "$(conda shell.bash hook)"
conda activate $ENV_NAME

# Install PyTorch with CUDA support (compatible with requirements)
echo "Installing PyTorch with CUDA 10.1 support..."
conda install pytorch==1.6.0 torchvision torchaudio cudatoolkit=10.1 -c pytorch -y

# Install other dependencies
echo "Installing other dependencies..."
pip install numpy==1.19.2
pip install scipy==1.5.3
pip install mido==1.2.9
pip install pretty-midi==0.2.9
pip install tqdm==4.50.2
pip install pillow==8.2.0
pip install googledrivedownloader==0.4
pip install requests==2.24.0

# Install CuPy for GPU acceleration (optional)
echo "Installing CuPy for GPU acceleration..."
pip install cupy-cuda101==8.0.0 || echo "Warning: CuPy installation failed, continuing without GPU acceleration"

# Install NVIDIA-apex (optional, for advanced GPU features)
echo "Installing NVIDIA-apex..."
if [ ! -d "apex" ]; then
    git clone https://github.com/NVIDIA/apex.git
fi
cd apex
pip install -v --disable-pip-version-check --no-cache-dir . || echo "Warning: NVIDIA-apex installation failed"
cd ..

# Run setup if available
if [ -f "setup.sh" ]; then
    bash setup.sh || echo "Warning: setup.sh execution failed"
fi

echo "VOCANO conda environment setup completed!"

# Create conda-aware integration script
echo "Creating conda-aware VOCANO integration script..."
cat > /home/evev/diversity-eval/scripts/run_vocano_conda.sh << 'SCRIPT_EOF'
#!/bin/bash

# VOCANO - Vocal Note Transcription Script (with conda environment)
# Usage: ./run_vocano_conda.sh <input_wav_file> [output_name]

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

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "Error: conda is not installed or not in PATH"
    exit 1
fi

# Activate VOCANO conda environment
echo "Activating VOCANO conda environment..."
eval "$(conda shell.bash hook)"
conda activate vocano

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

# Deactivate conda environment
conda deactivate
SCRIPT_EOF

chmod +x /home/evev/diversity-eval/scripts/run_vocano_conda.sh

# Create environment management script
cat > /home/evev/diversity-eval/scripts/manage_vocano_env.sh << 'MANAGE_EOF'
#!/bin/bash

# VOCANO Environment Management Script

case "$1" in
    "activate")
        echo "Activating VOCANO conda environment..."
        eval "$(conda shell.bash hook)"
        conda activate vocano
        echo "VOCANO environment activated. Use 'conda deactivate' to exit."
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
        echo "Removing VOCANO conda environment..."
        conda env remove -n vocano -y
        echo "VOCANO environment removed."
        ;;
    "info")
        echo "VOCANO Environment Information:"
        conda env list | grep vocano || echo "VOCANO environment not found"
        ;;
    *)
        echo "VOCANO Environment Management"
        echo "Usage: $0 {activate|deactivate|list|remove|info}"
        echo ""
        echo "Commands:"
        echo "  activate    - Activate VOCANO conda environment"
        echo "  deactivate  - Deactivate current conda environment"
        echo "  list        - List all conda environments"
        echo "  remove      - Remove VOCANO conda environment"
        echo "  info        - Show VOCANO environment information"
        ;;
esac
MANAGE_EOF

chmod +x /home/evev/diversity-eval/scripts/manage_vocano_env.sh

# Update README_EXTERNAL.md with conda information
echo "Updating README_EXTERNAL.md with conda environment information..."

# Create a temporary file with the new VOCANO section
cat > /tmp/vocano_conda_section.md << 'README_EOF'

## VOCANO - Vocal Note Transcription (Conda Environment)

VOCANO is a note transcription framework for singing voice in polyphonic music that can transcribe vocal into MIDI files.

### Features
- Vocal note transcription from polyphonic music
- Pitch extraction using pre-trained Patch-CNN
- Note segmentation using PyramidNet-110 with ShakeDrop regularization
- Support for both monophonic and polyphonic audio (with source separation)
- **Dedicated conda environment for dependency isolation**

### Location
- **Path**: `external/VOCANO/`
- **Repository**: https://github.com/B05901022/VOCANO
- **Conda Environment**: `vocano`

### Setup (Conda Environment)
Run the setup script to create a dedicated conda environment:
```bash
./scripts/setup_vocano_conda.sh
```

This will:
1. Create a conda environment named `vocano` with Python 3.8
2. Install PyTorch 1.6.0 with CUDA 10.1 support
3. Install all required dependencies
4. Install CuPy for GPU acceleration
5. Install NVIDIA-apex for advanced GPU features

### Environment Management
Use the environment management script:
```bash
# Activate VOCANO environment
./scripts/manage_vocano_env.sh activate

# Deactivate environment
./scripts/manage_vocano_env.sh deactivate

# List all environments
./scripts/manage_vocano_env.sh list

# Remove VOCANO environment
./scripts/manage_vocano_env.sh remove

# Show environment info
./scripts/manage_vocano_env.sh info
```

### Usage

#### Using the conda-aware integration script:
```bash
# Basic usage (automatically activates/deactivates conda environment)
./scripts/run_vocano_conda.sh /path/to/audio.wav

# With custom output name
./scripts/run_vocano_conda.sh /path/to/audio.wav my_transcription
```

#### Manual usage with conda environment:
```bash
# Activate environment
conda activate vocano

# Navigate to VOCANO directory
cd external/VOCANO

# Run transcription
python -m vocano.transcription -n output_name -wd input_file.wav

# Deactivate environment
conda deactivate
```

### Advanced Options
```bash
# With GPU acceleration (if CuPy installed)
python -m vocano.transcription -n output_name -wd input_file.wav -use_cp

# Skip preprocessing if already done
python -m vocano.transcription -n output_name -wd input_file.wav -use_pre

# Auto-select GPU (Linux only)
python -m vocano.transcription -n output_name -wd input_file.wav -d auto
```

### Output
- **WAV files**: `external/VOCANO/generated/wav/`
- **MIDI files**: `external/VOCANO/generated/midi/`
- **Pipeline output**: `data/output/vocano_output/`

### Dependencies (Conda Environment)
- Python 3.8
- PyTorch 1.6.0 (with CUDA 10.1)
- NumPy 1.19.2
- SciPy 1.5.3
- CuPy 8.0.0 (for GPU acceleration)
- NVIDIA-apex (for advanced GPU features)
- Other dependencies as specified in requirements.txt

### Integration with Pipeline
VOCANO can be integrated into the vocal transcription pipeline as an alternative to basic-pitch-torch for vocal-specific transcription tasks.

### Notes
- **Isolated Environment**: Uses dedicated conda environment to avoid conflicts
- **GPU Support**: Optimized for NVIDIA GPUs with CUDA 10.1
- **Vocal Specific**: Specialized for vocal transcription in polyphonic music
- **Source Separation**: Consider using Demucs for better polyphonic results
- **Environment Activation**: Scripts automatically handle conda environment activation/deactivation

README_EOF

# Append the new section to README_EXTERNAL.md
cat /tmp/vocano_conda_section.md >> /home/evev/diversity-eval/README_EXTERNAL.md
rm /tmp/vocano_conda_section.md

echo ""
echo "=== VOCANO Conda Setup Complete ==="
echo "Conda environment 'vocano' has been created and configured"
echo "Integration scripts created:"
echo "  - scripts/run_vocano_conda.sh (conda-aware transcription)"
echo "  - scripts/manage_vocano_env.sh (environment management)"
echo "README_EXTERNAL.md has been updated"
echo ""
echo "Next steps:"
echo "1. Test VOCANO with: ./scripts/run_vocano_conda.sh <your_audio_file.wav>"
echo "2. Manage environment with: ./scripts/manage_vocano_env.sh {activate|deactivate|list|remove|info}"
echo "3. Check output in: data/output/vocano_output/"
echo ""
echo "To manually use VOCANO:"
echo "  conda activate vocano"
echo "  cd external/VOCANO"
echo "  python -m vocano.transcription -n output_name -wd input_file.wav"
echo "  conda deactivate"