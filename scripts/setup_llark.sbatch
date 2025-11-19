#!/bin/bash
#SBATCH --job-name=llark_setup
#SBATCH --account=musi
#SBATCH --qos=coe-ice
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --partition=coe-gpu
#SBATCH --gres=gpu:1
#SBATCH --output=logs/llark_setup_%j.out
#SBATCH --error=logs/llark_setup_%j.err
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=xli3252@gatech.edu

# LLark Setup on PACE ICE GPU
# Multimodal Instruction-Following Language Model for Music

set -e

echo "=== SLURM Job Information ==="
echo "Job ID: $SLURM_JOB_ID"
echo "Job Name: $SLURM_JOB_NAME"
echo "Node: $SLURMD_NODENAME"
echo "Partition: $SLURM_JOB_PARTITION"
echo "Account: $SLURM_JOB_ACCOUNT"
echo "CPUs: $SLURM_CPUS_PER_TASK"
echo "Memory: $SLURM_MEM_PER_NODE MB"
echo "GPU: $CUDA_VISIBLE_DEVICES"
echo "Start Time: $(date)"
echo "Working Directory: $(pwd)"
echo "=========================="

# Create necessary directories
mkdir -p /home/hice1/xli3252/Desktop/diversity-eval/logs
mkdir -p /home/hice1/xli3252/Desktop/diversity-eval/external

# Load required modules
echo "Loading required modules..."
module purge
module load anaconda3/2023.03
module load cuda/11.8
module load gcc/9.3.0

# Verify modules are loaded
echo "Loaded modules:"
module list

# Check CUDA availability
echo "CUDA Information:"
nvidia-smi
echo "NVCC version:"
nvcc --version

# Navigate to project directory
cd /home/hice1/xli3252/Desktop/diversity-eval

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "Error: conda is not installed or not in PATH"
    echo "Available conda installations:"
    find /usr/local -name "conda" 2>/dev/null || echo "No conda found"
    exit 1
fi

echo "Conda version: $(conda --version)"
echo "Python version: $(python --version)"

# Navigate to external directory
cd external

# Handle LLark repository
echo "Setting up LLark repository..."
if [ -d "llark" ]; then
    echo "LLark directory exists. Checking for updates..."
    cd llark
    git fetch origin
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/main)
    if [ "$LOCAL" != "$REMOTE" ]; then
        echo "Updates available. Pulling latest changes..."
        git pull origin main
    else
        echo "Repository is up to date."
    fi
    cd ..
else
    echo "Cloning LLark repository..."
    git clone https://github.com/spotify-research/llark.git
    echo "LLark repository cloned successfully"
fi

# Create conda environment for LLark
ENV_NAME="llark"
PYTHON_VERSION="3.9"

echo "Setting up conda environment: $ENV_NAME with Python $PYTHON_VERSION"

# Remove existing environment if it exists
echo "Checking for existing environment..."
if conda env list | grep -q "^$ENV_NAME "; then
    echo "Removing existing $ENV_NAME environment..."
    conda env remove -n $ENV_NAME -y
fi

# Create new environment
echo "Creating new conda environment..."
conda create -n $ENV_NAME python=$PYTHON_VERSION -y

echo "Conda environment '$ENV_NAME' created successfully"

# Activate environment
echo "Activating conda environment..."
eval "$(conda shell.bash hook)"
conda activate $ENV_NAME

# Verify environment activation
echo "Active conda environment: $CONDA_DEFAULT_ENV"
echo "Python path: $(which python)"
echo "Python version: $(python --version)"

# Navigate to LLark directory
cd llark

echo "Installing LLark dependencies..."

# Update pip first
pip install --upgrade pip

# Install PyTorch with CUDA support (compatible with CUDA 11.8)
echo "Installing PyTorch with CUDA 11.8 support..."
pip install torch==1.13.0+cu117 torchvision==0.14.0+cu117 torchaudio==0.13.0+cu117 --extra-index-url https://download.pytorch.org/whl/cu117

# Install core ML libraries
echo "Installing core ML libraries..."
pip install transformers==4.29.2
pip install datasets==2.10.1
pip install accelerate
pip install numpy
pip install scipy

# Install audio processing libraries
echo "Installing audio processing libraries..."
pip install librosa
pip install soundfile
pip install pretty_midi
pip install music21
pip install mido

# Install Apache Beam for data processing
echo "Installing Apache Beam..."
pip install apache-beam[gcp]

# Install LLark specific requirements
echo "Installing LLark requirements..."
if [ -f "requirements.txt" ]; then
    echo "Found requirements.txt, installing..."
    pip install -r requirements.txt
else
    echo "No requirements.txt found, installing common dependencies..."
    pip install openai
    pip install google-cloud-storage
fi

# Install training requirements (optional)
if [ -f "train-requirements.txt" ]; then
    echo "Installing training requirements..."
    pip install -r train-requirements.txt
else
    echo "No train-requirements.txt found, skipping training dependencies"
fi

# Install additional useful packages
echo "Installing additional packages..."
pip install jupyter
pip install matplotlib
pip install seaborn
pip install pandas
pip install tqdm

# Install madmom (music analysis library)
echo "Installing madmom..."
pip install Cython
pip install madmom

# Test installation
echo "Testing installation..."
python -c "
import sys
print(f'Python version: {sys.version}')

import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'CUDA device count: {torch.cuda.device_count()}')
if torch.cuda.is_available():
    print(f'CUDA device: {torch.cuda.get_device_name(0)}')
    print(f'CUDA version: {torch.version.cuda}')

import transformers
print(f'Transformers version: {transformers.__version__}')

import librosa
print(f'Librosa version: {librosa.__version__}')

import numpy as np
print(f'NumPy version: {np.__version__}')

try:
    import datasets
    print(f'Datasets version: {datasets.__version__}')
except ImportError:
    print('Datasets not available')

try:
    import apache_beam
    print(f'Apache Beam version: {apache_beam.__version__}')
except ImportError:
    print('Apache Beam not available')

print('\\n=== Installation Test Successful ===')
"

# Create a simple test script
echo "Creating test script..."
cat > test_llark_setup.py << 'EOF'
#!/usr/bin/env python3
"""
Test script for LLark setup verification
"""

import torch
import transformers
import librosa
import numpy as np
import sys
import os

def test_cuda():
    """Test CUDA availability"""
    print("=== CUDA Test ===")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA device count: {torch.cuda.device_count()}")
        print(f"Current CUDA device: {torch.cuda.current_device()}")
        print(f"CUDA device name: {torch.cuda.get_device_name()}")
        
        # Test tensor operations on GPU
        x = torch.randn(1000, 1000).cuda()
        y = torch.randn(1000, 1000).cuda()
        z = torch.mm(x, y)
        print(f"GPU tensor operation successful: {z.shape}")
    else:
        print("CUDA not available, using CPU")

def test_transformers():
    """Test transformers library"""
    print("\n=== Transformers Test ===")
    from transformers import AutoTokenizer
    print("Transformers import successful")

def test_audio():
    """Test audio processing"""
    print("\n=== Audio Processing Test ===")
    # Create a simple sine wave
    import librosa
    import soundfile as sf
    
    sr = 22050
    duration = 1.0
    frequency = 440.0
    
    t = np.linspace(0, duration, int(sr * duration))
    audio = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    # Test librosa
    mfcc = librosa.feature.mfcc(y=audio, sr=sr)
    print(f"MFCC shape: {mfcc.shape}")
    print("Audio processing test successful")

if __name__ == "__main__":
    print("=== LLark Setup Verification ===")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    try:
        test_cuda()
        test_transformers()
        test_audio()
        print("\n=== All Tests Passed ===")
    except Exception as e:
        print(f"\n=== Test Failed ===")
        print(f"Error: {e}")
        sys.exit(1)
EOF

# Run the test
echo "Running installation test..."
python test_llark_setup.py

# Deactivate environment
conda deactivate

# Create environment info file
echo "Creating environment info file..."
cat > /home/hice1/xli3252/Desktop/diversity-eval/llark_env_info.txt << EOF
LLark Environment Setup Information
==================================

Setup Date: $(date)
Job ID: $SLURM_JOB_ID
Node: $SLURMD_NODENAME

Environment Details:
- Name: llark
- Python Version: $PYTHON_VERSION
- Location: ~/.conda/envs/llark (symlinked to ~/scratch/.conda/envs/llark)

Key Packages Installed:
- PyTorch 1.13.0 (with CUDA 11.7 support)
- Transformers 4.29.2
- Datasets 2.10.1
- Librosa (latest)
- Apache Beam (with GCP support)
- Jupyter, Matplotlib, Pandas

Usage Instructions:
1. Load modules: module load anaconda3/2023.03 cuda/11.8
2. Activate environment: conda activate llark
3. Navigate to LLark: cd ~/Desktop/diversity-eval/external/llark
4. Run LLark scripts

Repository Location: ~/Desktop/diversity-eval/external/llark

Test Results: $(if [ -f "test_llark_setup.py" ]; then echo "Passed"; else echo "Not run"; fi)
EOF

echo ""
echo "=== LLark Setup Complete ==="
echo "Job ID: $SLURM_JOB_ID"
echo "End Time: $(date)"
echo "Duration: $SECONDS seconds"
echo ""
echo "Environment created: llark"
echo "Repository location: ~/Desktop/diversity-eval/external/llark"
echo "Environment info saved to: ~/Desktop/diversity-eval/llark_env_info.txt"
echo ""
echo "To use LLark:"
echo "1. module load anaconda3/2023.03 cuda/11.8"
echo "2. conda activate llark"
echo "3. cd ~/Desktop/diversity-eval/external/llark"
echo ""
echo "=== Job Complete ==="