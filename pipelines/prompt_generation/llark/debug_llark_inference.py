#!/usr/bin/env python3
"""
Debug version of LLARK inference script to fix OverflowError
"""
import os
import sys
import glob
import numpy as np
import pandas as pd
import torch
import transformers
from tqdm import tqdm

# Add the llark directory to Python path
sys.path.insert(0, '/home/hice1/xli3252/Desktop/diversity-eval/external/llark')

from m2t.arguments import DataArguments, ModelArguments, TrainingArguments
from m2t.conversation_utils import extract_response_tokens
from m2t.data_modules import make_mm_config
from m2t.infer import infer_with_prompt
from m2t.models.utils import load_pretrained_model
from m2t.tokenizer import get_prompt_end_token_sequence
from m2t.utils import get_autocast_type

def safe_tokenize_fn(strings, tokenizer, max_length=512):
    """Safe tokenization function that prevents overflow"""
    # Ensure max_length is reasonable
    safe_max_length = min(max_length, 2048)  # Cap at 2048 to prevent overflow
    
    print(f"[DEBUG] Using safe max_length: {safe_max_length}")
    print(f"[DEBUG] Tokenizer model_max_length: {getattr(tokenizer, 'model_max_length', 'Not set')}")
    
    tokenized_list = []
    for text in strings:
        try:
            tokenized = tokenizer(
                text,
                return_tensors="pt",
                padding="longest",
                max_length=safe_max_length,
                truncation=True,
            )
            tokenized_list.append(tokenized)
        except Exception as e:
            print(f"[ERROR] Tokenization failed: {e}")
            print(f"[ERROR] Text length: {len(text)}")
            # Fallback with even smaller max_length
            tokenized = tokenizer(
                text,
                return_tensors="pt",
                padding="longest", 
                max_length=512,
                truncation=True,
            )
            tokenized_list.append(tokenized)
    
    input_ids = labels = [tokenized.input_ids[0] for tokenized in tokenized_list]
    input_ids_lens = labels_lens = [
        tokenized.input_ids.ne(tokenizer.pad_token_id).sum().item() for tokenized in tokenized_list
    ]
    return dict(
        input_ids=input_ids,
        labels=labels,
        input_ids_lens=input_ids_lens,
        labels_lens=labels_lens,
    )

def debug_llark_inference():
    print("=== LLARK Inference Debug (Fixed Version) ===")
    
    # Check CUDA
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA device: {torch.cuda.get_device_name()}")
        print(f"CUDA memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    
    # Check encodings directory
    encodings_dir = "/home/hice1/xli3252/Desktop/diversity-eval/data/output/llark_encodings_official"
    print(f"\nChecking encodings directory: {encodings_dir}")
    
    if os.path.exists(encodings_dir):
        files = [f for f in os.listdir(encodings_dir) if f.endswith('.npy')]
        print(f"Found {len(files)} .npy files")
        for f in files[:3]:  # Show first 3 files
            print(f"  - {f}")
            # Check file size
            file_path = os.path.join(encodings_dir, f)
            try:
                data = np.load(file_path)
                print(f"    Shape: {data.shape}, Size: {data.nbytes / 1024:.1f} KB")
            except Exception as e:
                print(f"    Error loading: {e}")
        if len(files) > 3:
            print(f"  ... and {len(files) - 3} more files")
    else:
        print("ERROR: Encodings directory not found!")
        return False
    
    # Check model path
    model_path = "/home/hice1/xli3252/Desktop/diversity-eval/external/llark/checkpoints/meta-llama"
    print(f"\nChecking model path: {model_path}")
    
    if os.path.exists(model_path):
        print("Model directory exists")
        checkpoint_path = os.path.join(model_path, "checkpoint-100000")
        if os.path.exists(checkpoint_path):
            print("Checkpoint-100000 exists")
            files = [f for f in os.listdir(checkpoint_path) if f.endswith('.bin')]
            print(f"Model files: {files}")
        else:
            print("ERROR: checkpoint-100000 not found!")
            return False
    else:
        print("ERROR: Model directory not found!")
        return False
    
    print("\n=== All checks passed! ===")
    return True

def run_fixed_inference():
    """Run inference with fixed parameters to avoid overflow"""
    print("\n=== Running Fixed Inference ===")
    
    # Patch the tokenization function to prevent overflow
    import m2t.data_modules
    original_tokenize_fn = m2t.data_modules._tokenize_fn
    m2t.data_modules._tokenize_fn = safe_tokenize_fn
    
    try:
        # Set up arguments with safe parameters
        model_args = ModelArguments(
            model_name_or_path="/home/hice1/xli3252/Desktop/diversity-eval/external/llark/checkpoints/meta-llama"
        )
        
        data_args = DataArguments()
        
        training_args = TrainingArguments(
            output_dir="tmp",
            model_max_length=512,  # Safe value
            bf16=True,
            tf32=True,
            report_to="none"
        )
        
        # Load model and tokenizer
        print("Loading model and tokenizer...")
        model, tokenizer = load_pretrained_model(
            model_name=model_args.model_name_or_path,
            ckpt_num=100000,
            torch_dtype=torch.float16,
            mm_use_audio_start_end=True,
            device="cuda:0"
        )
        
        # Create a dummy audio_processor for compatibility
        audio_processor = None
        
        # Set safe max_length for tokenizer
        if hasattr(tokenizer, 'model_max_length'):
            original_max_length = tokenizer.model_max_length
            tokenizer.model_max_length = 512
            print(f"[DEBUG] Changed tokenizer max_length from {original_max_length} to {tokenizer.model_max_length}")
        
        # Set up multimodal config and get end sequence
        mm_config = make_mm_config(data_args)
        end_seq = get_prompt_end_token_sequence(tokenizer, model_args.model_name_or_path)
        
        # Get encoding files
        encodings_dir = "/home/hice1/xli3252/Desktop/diversity-eval/data/output/llark_encodings_official"
        encoding_files = glob.glob(os.path.join(encodings_dir, "*.npy"))[:1]  # Test with just 1 file
        
        print(f"Processing {len(encoding_files)} files...")
        
        results = []
        for i, encoding_file in enumerate(tqdm(encoding_files)):
            try:
                print(f"\n[DEBUG] Processing file: {os.path.basename(encoding_file)}")
                
                # Load encoding
                audio_encoding = np.load(encoding_file)
                print(f"[DEBUG] Encoding shape: {audio_encoding.shape}")
                
                # Run inference
                prompt_text = "Describe this music:"
                end_seq = get_prompt_end_token_sequence(tokenizer, model_args.model_name_or_path)
                output = infer_with_prompt(
                    prompt_text=prompt_text,
                    audio_encoding=audio_encoding,
                    tokenizer=tokenizer,
                    model=model,
                    audio_processor=audio_processor,
                    end_seq=end_seq,
                    multimodal_cfg=mm_config,
                    max_new_tokens=256  # Reduced from 512
                )
                
                print(f"[DEBUG] Inference successful!")
                print(f"[DEBUG] Output: {output[:100]}...")  # Show first 100 chars
                
                results.append({
                    'file': os.path.basename(encoding_file),
                    'output': output
                })
                
            except Exception as e:
                print(f"[ERROR] Failed to process {encoding_file}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # Save results
        if results:
            output_file = "/home/hice1/xli3252/Desktop/diversity-eval/data/output/llark_results_fixed.csv"
            df = pd.DataFrame(results)
            df.to_csv(output_file, index=False)
            print(f"\n=== Results saved to {output_file} ===")
            print(f"Processed {len(results)} files successfully")
        else:
            print("\n=== No results to save ===")
            
    except Exception as e:
        print(f"[ERROR] Inference failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Restore original function
        m2t.data_modules._tokenize_fn = original_tokenize_fn

if __name__ == "__main__":
    if debug_llark_inference():
        run_fixed_inference()
    else:
        print("Debug checks failed, not running inference")
