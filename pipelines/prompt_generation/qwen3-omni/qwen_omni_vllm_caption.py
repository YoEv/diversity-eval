#!/usr/bin/env python3
import argparse
import json
import os
import sys
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import torch
from vllm import LLM, SamplingParams, EngineArgs
from transformers import Qwen3OmniMoeProcessor
from qwen_omni_utils import process_mm_info
from huggingface_hub import snapshot_download

def ensure_dir(p: Path):
    try:
        p.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

def load_payload(json_path: Path) -> Dict[str, Any]:
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def rewrite_path_prefix(p: str, mapping: Optional[Tuple[str, str]]) -> str:
    if not mapping:
        return p
    src, dst = mapping
    return (dst + p[len(src):]) if p.startswith(src) else p

def build_messages(audio_path: str, prompt_text: str) -> List[Dict[str, Any]]:
    return [{"role": "user", "content": [{"type": "audio", "audio": audio_path}, {"type": "text", "text": prompt_text}]}]


def resolve_model_local_dir(model_id: str, download_dir: str, token: Optional[str] = None) -> str:
    if isinstance(model_id, str):
        if re.match(r"^[^/]+/[^/]+$", model_id):
            return snapshot_download(repo_id=model_id, local_dir=download_dir, local_dir_use_symlinks=False, token=token)
        if os.path.isdir(model_id) and os.path.exists(os.path.join(model_id, "config.json")):
            return model_id
        if model_id.startswith("/root/.cache/huggingface/hub/models--"):
            return model_id
    return snapshot_download(repo_id=str(model_id).strip(), local_dir=download_dir, local_dir_use_symlinks=False, token=token)


def resolve_path(pstr: str, bases: List[Path]) -> Path:
    p = Path(pstr)
    if p.is_absolute():
        return p
    for b in bases:
        try:
            cand = (b / pstr)
            if cand.exists():
                return cand
        except Exception:
            continue
    return (Path.cwd() / p).resolve()


def main():
    parser = argparse.ArgumentParser(description="vLLM离线推理：Qwen3-Omni音频描述")
    parser.add_argument("--input-json", type=str, default="data/output/omni_prompt_input/omni_prompts_batch_blues.json")
    parser.add_argument("--output-json", type=str, default="data/output/omni_prompt_output/captions_vllm_batch_blues.json")
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-Omni-30B-A3B-Instruct")
    parser.add_argument("--cuda-devices", type=str, default="")
    parser.add_argument("--tensor-parallel-size", type=int, default=0)
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.95)
    parser.add_argument("--max-model-len", type=int, default=16384)
    parser.add_argument("--max-num-seqs", type=int, default=2)
    parser.add_argument("--limit-audio-per-prompt", type=int, default=1)
    parser.add_argument("--limit-image-per-prompt", type=int, default=0)
    parser.add_argument("--limit-video-per-prompt", type=int, default=0)
    parser.add_argument("--use-audio-in-video", action="store_true")
    parser.add_argument("--temperature", type=float, default=0.6)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--max-new-tokens", type=int, default=1024)
    parser.add_argument("--path-remap", type=str, default="")
    parser.add_argument("--download-dir", type=str, default="/root/.cache/huggingface/hub")
    parser.add_argument("--hf-token", type=str, default="")
    args = parser.parse_args()

    base_candidates: List[Path] = []
    try:
        repo_root = Path(__file__).resolve().parents[4]
        base_candidates.append(repo_root)
    except Exception:
        pass
    base_candidates.extend([Path.cwd(), Path('/data/shared/Qwen-Omni'), Path('/data/shared/Qwen3-Omni'), Path('/home/hice1/xli3252/Desktop/diversity-eval')])
    input_path = resolve_path(args.input_json, base_candidates)
    output_path = resolve_path(args.output_json, base_candidates)
    ensure_dir(output_path.parent)
    print(f"[INFO] Using input_json: {input_path}")
    print(f"[INFO] Writing to output_json: {output_path}")
    hf_token = args.hf_token or os.environ.get("HF_TOKEN")

    if args.cuda_devices:
        os.environ["CUDA_VISIBLE_DEVICES"] = args.cuda_devices
    os.environ["VLLM_USE_V1"] = "0"

    payload = load_payload(input_path)
    model_id = args.model
    items: List[Dict[str, Any]] = payload.get("items", [])

    tp = args.tensor_parallel_size if args.tensor_parallel_size and args.tensor_parallel_size > 0 else torch.cuda.device_count()
    local_model_dir = resolve_model_local_dir(model_id, args.download_dir, token=hf_token)
    print(f"[INFO] Using local_model_dir: {local_model_dir}")
    llm = LLM(
        model=local_model_dir,
        trust_remote_code=True,
        tensor_parallel_size=tp,
        gpu_memory_utilization=args.gpu_memory_utilization,
        max_num_seqs=args.max_num_seqs,
        max_model_len=args.max_model_len,
        limit_mm_per_prompt={"audio": args.limit_audio_per_prompt, "image": args.limit_image_per_prompt, "video": args.limit_video_per_prompt},
        seed=1234,
    )
    sampling_params = SamplingParams(temperature=args.temperature, top_p=args.top_p, top_k=args.top_k, max_tokens=args.max_new_tokens)
    processor = Qwen3OmniMoeProcessor.from_pretrained(local_model_dir, local_files_only=True)

    results = []
    processed_ids = set()
    if output_path.exists():
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                if "results" in existing_data:
                    results = existing_data["results"]
                    processed_ids = {it.get("id") for it in results}
        except Exception:
            pass

    remap: Optional[Tuple[str, str]] = None
    if args.path_remap and "=" in args.path_remap:
        s = args.path_remap.strip()
        src, dst = s.split("=", 1)
        remap = (os.path.expanduser(src), os.path.expanduser(dst))

    items_to_process = [it for it in items if it.get("id") not in processed_ids]
    total_to_process = len(items_to_process)

    for idx, it in enumerate(items_to_process, 1):
        audio_path = rewrite_path_prefix(it["audio"], remap)
        prompt_text = it.get("prompt") or "请对该人声片段进行音乐分析与描述。"
        messages = build_messages(audio_path, prompt_text)
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        audios, images, videos = process_mm_info(messages, use_audio_in_video=args.use_audio_in_video)

        inputs: Dict[str, Any] = {"prompt": text, "multi_modal_data": {}, "mm_processor_kwargs": {"use_audio_in_video": args.use_audio_in_video}}
        if audios is not None:
            inputs["multi_modal_data"]["audio"] = audios
        if images is not None:
            inputs["multi_modal_data"]["image"] = images
        if videos is not None:
            inputs["multi_modal_data"]["video"] = videos

        try:
            outputs = llm.generate(inputs, sampling_params=sampling_params)
            caption = outputs[0].outputs[0].text if outputs and outputs[0].outputs else ""
        except Exception as e:
            caption = f"[ERROR] {e}"

        results.append({"id": it.get("id"), "audio": audio_path, "prompt": prompt_text, "caption": caption})
        out_payload = {"model": model_id, "count": len(results), "results": results}
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(out_payload, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

if __name__ == "__main__":
    main()