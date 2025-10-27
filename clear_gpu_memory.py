#!/usr/bin/env python3
import torch
import gc
import os

def aggressive_gpu_cleanup():
    """更激进的GPU内存清理"""
    print("Starting aggressive GPU memory cleanup...")
    
    # 清理PyTorch缓存
    if torch.cuda.is_available():
        print(f"GPU memory before cleanup: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        print(f"GPU memory after cleanup: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
    
    # 强制垃圾回收
    for _ in range(3):
        gc.collect()
    
    print("GPU memory cleanup completed.")

if __name__ == "__main__":
    aggressive_gpu_cleanup()