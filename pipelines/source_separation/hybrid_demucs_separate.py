#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import torch
import torchaudio

def separate_sources(model, mix, sample_rate, segment=10.0, overlap=1.0, device=None):
    if device is None:
        device = mix.device
    else:
        device = torch.device(device)

    # mix: [batch=1, channels, time]
    batch, channels, length = mix.shape
    overlap_frames = int(overlap * sample_rate)
    chunk_len = int(sample_rate * segment) + overlap_frames
    start = 0
    end = min(chunk_len, length)

    fade = torchaudio.transforms.Fade(
        fade_in_len=0, fade_out_len=overlap_frames, fade_shape="linear"
    ).to(device)

    final = torch.zeros(batch, len(model.sources), channels, length, device=device)

    model.eval()
    with torch.no_grad():
        while start < length:
            chunk = mix[:, :, start:end]  # [1, C, T_chunk]
            out = model.forward(chunk)    # [1, S, C, T_chunk]
            out = fade(out)

            final[:, :, :, start:end] += out

            if start == 0:
                fade.fade_in_len = overlap_frames

            if end >= length:
                break

            # slide window with overlap
            start = end - overlap_frames
            end = min(start + chunk_len, length)
            if end >= length:
                fade.fade_out_len = 0

    return final  # [1, S, C, T]

def ensure_stereo(wave):
    # wave: [channels, time]
    if wave.shape[0] == 1:
        return wave.repeat(2, 1)
    elif wave.shape[0] > 2:
        # use first 2 channels if more than stereo
        return wave[:2, :]
    return wave

def process_file(model, bundle_sr, in_root: Path, in_path: Path, out_dir: Path, segment, overlap, device):
    wave, sr = torchaudio.load(str(in_path))
    # resample if needed
    if sr != bundle_sr:
        resampler = torchaudio.transforms.Resample(sr, bundle_sr)
        wave = resampler(wave)
        sr = bundle_sr

    wave = ensure_stereo(wave)           # [2, T]
    mix = wave.unsqueeze(0).to(device)   # [1, 2, T]

    separated = separate_sources(
        model=model,
        mix=mix,
        sample_rate=sr,
        segment=segment,
        overlap=overlap,
        device=device,
    )  # [1, S, 2, T]

    try:
        rel_parent = in_path.parent.relative_to(in_root)
    except Exception:
        rel_parent = Path()
    stems_dir = out_dir / rel_parent / in_path.stem
    stems_dir.mkdir(parents=True, exist_ok=True)

    sources = list(model.sources)
    for s_idx, s_name in enumerate(sources):
        audio = separated[0, s_idx].cpu()  # [2, T]
        out_path = stems_dir / f"{in_path.stem}_{s_name}.wav"
        torchaudio.save(str(out_path), audio, sr)

    print(f"[OK] {in_path} -> {stems_dir} ({', '.join(sources)})")

def main():
    parser = argparse.ArgumentParser(description="Hybrid Demucs source separation (torchaudio.pipelines)")
    in_default = "/home/hice1/xli3252/scratch/datasets/generated"
    parser.add_argument(
        "--input",
        type=str,
        default=in_default,
        help="输入音频文件夹（递归处理）",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="/home/hice1/xli3252/scratch/data/output/separated/Qwen3_Omni_Prompt",
        help="输出分离结果文件夹",
    )
    parser.add_argument(
        "--segment",
        type=float,
        default=10.0,
        help="分块长度（秒），减小显存占用",
    )
    parser.add_argument(
        "--overlap",
        type=float,
        default=1.0,
        help="分块之间重叠（秒），降低边界伪影",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="计算设备（cuda 或 cpu），默认自动选择",
    )
    parser.add_argument(
        "--exts",
        type=str,
        default=".wav,.mp3,.flac",
        help="处理的文件扩展名，逗号分隔",
    )
    parser.add_argument(
        "--subdirs",
        type=str,
        default="",
        help="仅处理输入根目录下指定子文件夹，逗号分隔；默认处理全部",
    )

    args = parser.parse_args()

    device = torch.device(args.device) if args.device else (
        torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    )

    # torchaudio pipeline: Hybrid Demucs
    from torchaudio.pipelines import HDEMUCS_HIGH_MUSDB_PLUS
    bundle = HDEMUCS_HIGH_MUSDB_PLUS
    model = bundle.get_model().to(device)

    in_dir = Path(args.input).expanduser().resolve()
    out_dir = Path(args.output).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    exts = {e.strip().lower() for e in args.exts.split(",") if e.strip()}
    target_subdirs = {d.strip() for d in args.subdirs.split(",") if d.strip()}
    files = []
    for root, _, fnames in os.walk(in_dir):
        rel = Path(root).relative_to(in_dir)
        if target_subdirs and (len(rel.parts) == 0 or rel.parts[0] not in target_subdirs):
            continue
        for f in fnames:
            p = Path(root) / f
            if p.suffix.lower() in exts:
                files.append(p)

    if not files:
        print(f"[WARN] 未在 {in_dir} 找到可处理的音频文件（扩展名：{sorted(exts)}）")
        return

    print(f"[INFO] 设备: {device}, 模型源: {model.sources}, 采样率: {bundle.sample_rate}")
    for fp in sorted(files):
        process_file(
            model=model,
            bundle_sr=bundle.sample_rate,
            in_root=in_dir,
            in_path=fp,
            out_dir=out_dir,
            segment=args.segment,
            overlap=args.overlap,
            device=device,
        )

if __name__ == "__main__":
    main()