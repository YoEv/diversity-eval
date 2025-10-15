# External Dependencies

这个目录包含项目的外部依赖：

## 目录结构

## VOCANO - Vocal Note Transcription

VOCANO is a note transcription framework for singing voice in polyphonic music that can transcribe vocal into MIDI files.

### Features
- Vocal note transcription from polyphonic music
- Pitch extraction using pre-trained Patch-CNN
- Note segmentation using PyramidNet-110 with ShakeDrop regularization
- Support for both monophonic and polyphonic audio (with source separation)

### Location
- **Path**: `external/VOCANO/`
- **Repository**: https://github.com/B05901022/VOCANO

### Setup
1. Install NVIDIA-apex (for GPU acceleration):
```bash
cd external/VOCANO
git clone https://github.com/NVIDIA/apex.git
pip install -v --disable-pip-version-check --no-cache-dir ./apex
bash setup.sh
```

2. Install requirements:
```bash
pip install -r requirements.txt -f https://download.pytorch.org/whl/torch_stable.html
```

3. (Optional) Install CuPy for faster inference:
```bash
pip install cupy
```

### Usage

#### Using the integration script:
```bash
# Basic usage
./scripts/run_vocano.sh /path/to/audio.wav

# With custom output name
./scripts/run_vocano.sh /path/to/audio.wav my_transcription
```

#### Direct usage:
```bash
cd external/VOCANO

# Preprocessing (optional)
python -m vocano.preprocess -n output_name -wd input_file.wav -s

# Transcription (full pipeline)
python -m vocano.transcription -n output_name -wd input_file.wav

# With GPU acceleration (if CuPy installed)
python -m vocano.transcription -n output_name -wd input_file.wav -use_cp

# Skip preprocessing if already done
python -m vocano.transcription -n output_name -wd input_file.wav -use_pre
```

### Output
- **WAV files**: `external/VOCANO/generated/wav/`
- **MIDI files**: `external/VOCANO/generated/midi/`
- **Pipeline output**: `data/output/vocano_output/`

### Integration with Pipeline
VOCANO can be integrated into the vocal transcription pipeline as an alternative to basic-pitch-torch for vocal-specific transcription tasks.

### Notes
- For polyphonic audio, consider using source separation (e.g., Demucs) before transcription
- The model is optimized for vocal transcription specifically
- Supports both CPU and GPU inference
- Use `-d auto` to automatically select the least used GPU (Linux only)


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

