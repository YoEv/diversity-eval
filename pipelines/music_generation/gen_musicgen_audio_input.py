import torch
import torchaudio
import argparse
import os
from pathlib import Path
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write

def load_audio(file_path, sample_rate=32000, duration=None):
    """
    Load audio file and resample to the target sample rate.
    
    Args:
        file_path: Path to the audio file
        sample_rate: Target sample rate (MusicGen uses 32kHz)
        duration: Optional duration to trim the audio to
    
    Returns:
        torch.Tensor: Audio tensor of shape (1, channels, samples)
    """
    waveform, sr = torchaudio.load(file_path)
    
    # Resample if necessary
    if sr != sample_rate:
        resampler = torchaudio.transforms.Resample(sr, sample_rate)
        waveform = resampler(waveform)
    
    # Convert to mono if stereo
    if waveform.shape[0] > 1:
        waveform = torch.mean(waveform, dim=0, keepdim=True)
    
    # Trim to specified duration if provided
    if duration is not None:
        max_samples = int(duration * sample_rate)
        if waveform.shape[1] > max_samples:
            waveform = waveform[:, :max_samples]
    
    # Add batch dimension
    waveform = waveform.unsqueeze(0)  # Shape: (1, 1, samples)
    
    return waveform

def generate_music_from_audio(input_audio_path, output_path, model_name='facebook/musicgen-melody', 
                             duration=15.0, top_k=250, top_p=0.0, temperature=1.0, 
                             use_sampling=True):
    """
    Generate music using MusicGen model with audio conditioning.
    
    Args:
        input_audio_path: Path to input audio file
        output_path: Path to save generated audio
        model_name: MusicGen model to use
        duration: Duration of generated audio in seconds
        top_k: Top-k sampling parameter
        top_p: Top-p sampling parameter
        temperature: Sampling temperature
        use_sampling: Whether to use sampling or greedy decoding
    """
    print(f"Loading MusicGen model: {model_name}")
    
    # Load the model
    model = MusicGen.get_pretrained(model_name)
    
    # Set generation parameters
    model.set_generation_params(
        duration=duration,
        top_k=top_k,
        top_p=top_p,
        temperature=temperature,
        use_sampling=use_sampling
    )
    
    print(f"Loading input audio: {input_audio_path}")
    
    # Load and preprocess the input audio
    audio_input = load_audio(input_audio_path, sample_rate=model.sample_rate)
    
    print(f"Generating {duration}s of music...")
    
    # Generate music conditioned on the input audio
    # Note: MusicGen uses audio conditioning through the melody parameter
    with torch.no_grad():
        generated_audio = model.generate_with_chroma(
            descriptions=[""],  # Empty text description
            melody_wavs=audio_input,
            melody_sample_rate=model.sample_rate
        )
    
    # Save the generated audio
    print(f"Saving generated audio to: {output_path}")
    
    # Remove batch dimension and convert to CPU
    generated_audio = generated_audio.squeeze(0).cpu()
    
    # Save using audiocraft's audio_write function
    output_stem = str(Path(output_path).with_suffix(''))
    audio_write(output_stem, generated_audio, model.sample_rate, strategy="loudness")
    
    print(f"Generation complete! Audio saved as {output_stem}.wav")

def batch_generate(input_dir, output_dir, **generation_kwargs):
    """
    Generate music for all audio files in a directory.
    
    Args:
        input_dir: Directory containing input audio files
        output_dir: Directory to save generated audio files
        **generation_kwargs: Additional arguments for generate_music_from_audio
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Supported audio extensions
    audio_extensions = {'.wav', '.mp3', '.flac', '.m4a', '.ogg', '.aac'}
    
    # Find all audio files
    audio_files = [f for f in input_path.iterdir() 
                   if f.is_file() and f.suffix.lower() in audio_extensions]
    
    if not audio_files:
        print(f"No audio files found in {input_dir}")
        return
    
    print(f"Found {len(audio_files)} audio files to process")
    
    for i, audio_file in enumerate(audio_files, 1):
        print(f"\nProcessing {i}/{len(audio_files)}: {audio_file.name}")
        
        # Generate output filename
        output_file = output_path / f"{audio_file.stem}_musicgen_15s"
        
        try:
            generate_music_from_audio(
                str(audio_file),
                str(output_file),
                **generation_kwargs
            )
        except Exception as e:
            print(f"Error processing {audio_file.name}: {e}")
            continue

def main():
    parser = argparse.ArgumentParser(
        description='Generate 15-second music using MusicGen with audio input conditioning'
    )
    
    # Input/output arguments
    parser.add_argument('--input', '-i', required=True,
                        help='Input audio file or directory')
    parser.add_argument('--output', '-o', required=True,
                        help='Output file or directory')
    
    # Model arguments
    parser.add_argument('--model', default='facebook/musicgen-melody',
                        choices=['facebook/musicgen-melody', 'facebook/musicgen-small', 
                                'facebook/musicgen-medium', 'facebook/musicgen-large'],
                        help='MusicGen model to use (default: facebook/musicgen-melody)')
    
    # Generation parameters
    parser.add_argument('--duration', type=float, default=15.0,
                        help='Duration of generated audio in seconds (default: 15.0)')
    parser.add_argument('--top-k', type=int, default=250,
                        help='Top-k sampling parameter (default: 250)')
    parser.add_argument('--top-p', type=float, default=0.0,
                        help='Top-p sampling parameter (default: 0.0)')
    parser.add_argument('--temperature', type=float, default=1.0,
                        help='Sampling temperature (default: 1.0)')
    parser.add_argument('--no-sampling', action='store_true',
                        help='Use greedy decoding instead of sampling')
    
    # Processing mode
    parser.add_argument('--batch', action='store_true',
                        help='Process all audio files in input directory')
    
    args = parser.parse_args()
    
    # Check if input exists
    if not os.path.exists(args.input):
        print(f"Error: Input path '{args.input}' does not exist")
        return
    
    # Prepare generation parameters
    generation_params = {
        'model_name': args.model,
        'duration': args.duration,
        'top_k': args.top_k,
        'top_p': args.top_p,
        'temperature': args.temperature,
        'use_sampling': not args.no_sampling
    }
    
    if args.batch or os.path.isdir(args.input):
        # Batch processing
        batch_generate(args.input, args.output, **generation_params)
    else:
        # Single file processing
        generate_music_from_audio(args.input, args.output, **generation_params)

if __name__ == "__main__":
    main()