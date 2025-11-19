#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import torch
from transformers import AutoModel, AutoProcessor

def log_device_info(model):
    dm = getattr(model, "hf_device_map", None)
    print(f"[DEV] cuda_available={torch.cuda.is_available()}, gpu_count={torch.cuda.device_count()}")
    if torch.cuda.is_available():
        cur = torch.cuda.current_device()
        print(f"[DEV] current_gpu={cur}, name={torch.cuda.get_device_name(cur)}")
    if dm:
        cpu_parts = [k for k, v in dm.items() if isinstance(v, str) and v.startswith("cpu")]
        gpu_parts = [k for k, v in dm.items() if isinstance(v, str) and v.startswith("cuda")]
        print(f"[DEV] device_map: GPU={len(gpu_parts)} parts, CPU={len(cpu_parts)} parts")
        if cpu_parts:
            print(f"[DEV] CPU modules (sample): {cpu_parts[:8]}")

def load_payload(json_path: Path) -> Dict[str, Any]:
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def build_messages(audio_path: str, prompt_text: str) -> List[Dict[str, Any]]:
    # 与你的示例保持一致的消息格式
    return [
        {
            "role": "user",
            "content": [
                {"type": "audio", "audio": audio_path},
                {"type": "text", "text": prompt_text},
            ],
        }
    ]

def init_model_and_processor(model_id: str, device: str, flash_attn2: bool):
    # 对于 GPU 使用 bfloat16，CPU 用 float32
    use_cuda = (device == "cuda" and torch.cuda.is_available())
    try:
        dev_name = torch.cuda.get_device_name(0).lower() if use_cuda else ""
        dtype = torch.bfloat16 if ("h100" in dev_name or "hopper" in dev_name) else (torch.float16 if use_cuda else torch.float32)
    except Exception:
        dtype = torch.bfloat16 if use_cuda else torch.float32

    device_map = "auto"

    cache_dir = os.environ.get("TRANSFORMERS_CACHE")
    if not cache_dir:
        hf_home = os.environ.get("HF_HOME")
        if hf_home:
            cache_dir = os.path.join(hf_home, "transformers")
    extra_kwargs = {}
    if flash_attn2:
        extra_kwargs["attn_implementation"] = "flash_attention_2"
    model = AutoModel.from_pretrained(
        model_id,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
        device_map=device_map,
        dtype=dtype,
        cache_dir=cache_dir,
        **extra_kwargs,
    )
    model.eval()
    log_device_info(model)

    processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)

    eos_id = getattr(model.config, "eos_token_id", None) or getattr(getattr(processor, "tokenizer", None), "eos_token_id", None)
    if getattr(model.config, "pad_token_id", None) is None and eos_id is not None:
        model.config.pad_token_id = eos_id
    if hasattr(processor, "tokenizer") and getattr(processor.tokenizer, "pad_token_id", None) is None and eos_id is not None:
        processor.tokenizer.pad_token_id = eos_id

    return model, processor

def generate_caption_with_transformers(model, processor, messages: List[Dict[str, Any]], max_new_tokens: int = 512) -> str:
    """
    优先使用处理器的 chat 模板；若不可用且模型提供 chat 方法，则直接调用 chat。
    """
    # 统一走远程模型提供的 chat 接口（Qwen3-Omni 官方实现）
    if hasattr(model, "chat"):
        out = model.chat(messages=messages, processor=processor, max_new_tokens=max_new_tokens)
        return out if isinstance(out, str) else str(out)
    # 若极端情况下没有 chat 方法，退回到处理器模板 + generate
    if hasattr(processor, "apply_chat_template"):
        inputs = processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_tensors="pt",
        )
        inputs = {k: (v.to(model.device) if hasattr(v, "to") else v) for k, v in inputs.items()}
        # 显式设置 pad_token_id
        if getattr(model.config, "pad_token_id", None) is None:
            eos_id = getattr(model.config, "eos_token_id", None) or getattr(getattr(processor, "tokenizer", None), "eos_token_id", None)
            if eos_id is not None:
                model.config.pad_token_id = eos_id
        # 确保 attention_mask 存在
        if "attention_mask" not in inputs:
            inputs["attention_mask"] = torch.ones_like(inputs["input_ids"])
        for k, v in list(inputs.items()):
            if hasattr(v, "dtype") and torch.is_floating_point(v):
                inputs[k] = v.to(model.dtype)

        with torch.inference_mode():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
            )

        # 新增：稳健获取 sequences 并统一为 2D LongTensor
        sequences = None
        if hasattr(outputs, "sequences"):
            sequences = outputs.sequences
        elif isinstance(outputs, torch.Tensor):
            sequences = outputs
        elif isinstance(outputs, (tuple, list)) and len(outputs) > 0:
            cand = outputs[0]
            sequences = cand.sequences if hasattr(cand, "sequences") else cand
        else:
            raise RuntimeError(f"未知的生成返回类型：{type(outputs)}")

        if isinstance(sequences, (list, tuple)):
            sequences = torch.tensor(sequences, dtype=torch.long, device=model.device)
        if sequences.ndim == 1:
            sequences = sequences.unsqueeze(0)

        start = inputs["input_ids"].shape[1]
        text = processor.batch_decode(sequences[:, start:], skip_special_tokens=True)[0]
        return text
    raise RuntimeError("当前环境不支持 chat 或模板，请升级 transformers 或使用官方实现。")

def rewrite_path_prefix(p: str, mapping: Optional[Tuple[str, str]]) -> str:
    if not mapping:
        return p
    src, dst = mapping
    return (dst + p[len(src):]) if p.startswith(src) else p

def init_official_transformers_and_utils(qwen_repo: str, checkpoint_path: str, flash_attn2: bool):
    # Force default dtype to bfloat16 to counter remote code override
    torch.set_default_dtype(torch.bfloat16)

    repo = Path(qwen_repo).expanduser().resolve()
    if str(repo) not in sys.path:
        sys.path.append(str(repo))
    from transformers import Qwen3OmniMoeForConditionalGeneration, Qwen3OmniMoeProcessor
    from qwen_omni_utils import process_mm_info
    if flash_attn2:
        model = Qwen3OmniMoeForConditionalGeneration.from_pretrained(
            checkpoint_path,
            dtype=torch.bfloat16,
            attn_implementation="flash_attention_2",
            device_map="auto",
        )
    else:
        model = Qwen3OmniMoeForConditionalGeneration.from_pretrained(
            checkpoint_path,
            device_map="auto",
            dtype="auto",
        )
    model.eval()
    log_device_info(model)
    processor = Qwen3OmniMoeProcessor.from_pretrained(checkpoint_path)
    return model, processor, process_mm_info

def generate_caption_official(model, processor, process_mm_info_fn, messages, temperature: float, top_p: float, top_k: int, max_new_tokens: int):
    text = processor.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
    audios, _, _ = process_mm_info_fn(messages, use_audio_in_video=True)
    inputs = processor(text=text, audio=audios, return_tensors="pt", padding=True)
    inputs = inputs.to(model.device)
    # 显式设置 pad_token_id
    if getattr(model.config, "pad_token_id", None) is None:
        eos_id = getattr(model.config, "eos_token_id", None) or getattr(getattr(processor, "tokenizer", None), "eos_token_id", None)
        if eos_id is not None:
            model.config.pad_token_id = eos_id
    # 确保 attention_mask 存在
    if "attention_mask" not in inputs:
        inputs["attention_mask"] = torch.ones_like(inputs["input_ids"])
    # 仅将浮点张量转换到模型 dtype，避免把整数张量误转成浮点
    for k, v in list(inputs.items()):
        if hasattr(v, "dtype") and torch.is_floating_point(v):
            inputs[k] = v.to(model.dtype)

    outputs = model.generate(
        **inputs,
        thinker_return_dict_in_generate=True,
        thinker_max_new_tokens=max_new_tokens,
        thinker_do_sample=True,
        thinker_temperature=temperature,
        thinker_top_p=top_p,
        thinker_top_k=top_k,
        use_audio_in_video=True,
    )

    # 新增：稳健获取 sequences 并统一为 2D LongTensor
    sequences = None
    if hasattr(outputs, "sequences"):
        sequences = outputs.sequences
    elif isinstance(outputs, torch.Tensor):
        sequences = outputs
    elif isinstance(outputs, (tuple, list)) and len(outputs) > 0:
        cand = outputs[0]
        sequences = cand.sequences if hasattr(cand, "sequences") else cand
    else:
        raise RuntimeError(f"未知的生成返回类型：{type(outputs)}")

    if isinstance(sequences, (list, tuple)):
        sequences = torch.tensor(sequences, dtype=torch.long, device=model.device)
    if sequences.ndim == 1:
        sequences = sequences.unsqueeze(0)

    start = inputs["input_ids"].shape[1]
    response = processor.batch_decode(
        sequences[:, start:],
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )[0]
    return response

def main():
    # 解析参数
    parser = argparse.ArgumentParser(description="批量运行 Qwen Omni 对人声片段进行音乐描述（captioning）")
    parser.add_argument("--input-json", type=str, default="data/output/omni_prompt_input/omni_prompts_batch.json",
                        help="由 qwen_omni_prepare_prompts.py 生成的输入 JSON")
    parser.add_argument("--output-json", type=str, default="data/output/omni_prompt_output/captions_batch_test.json",
                        help="输出的汇总 JSON 文件（包含每条的 caption）")
    parser.add_argument("--device", type=str, default="cuda", choices=["cuda", "cpu"],
                        help="推理设备：cuda 或 cpu")
    parser.add_argument("--max-new-tokens", type=int, default=512, help="生成的最大 token 数")
    parser.add_argument("--qwen-repo", type=str, default="/data/shared/Qwen3-Omni",
                        help="（可选）官方仓库路径，若存在将优先尝试使用 web_demo_captioner.run_model")
    parser.add_argument("--path-remap", type=str, default="", help="将JSON中的音频路径前缀替换为容器前缀，例如 '/home/hice1=/workspace'")
    parser.add_argument("--flash-attn2", action="store_true", help="使用 FlashAttention-2（容器支持时更快）")
    parser.add_argument("--temperature", type=float, default=0.6, help="生成温度")
    parser.add_argument("--top-p", type=float, default=0.95, help="生成 Top-P")
    parser.add_argument("--top-k", type=int, default=50, help="生成 Top-K")
    parser.add_argument("--force-gpu", action="store_true", help="尽量将权重全部放在 GPU（可能导致 OOM）")
    args = parser.parse_args()

    input_path = Path(args.input_json).resolve()
    output_path = Path(args.output_json).resolve()
    ensure_dir(output_path.parent)

    payload = load_payload(input_path)
    model_id = payload.get("model", "Qwen/Qwen3-Omni-30B-A3B-Instruct")
    items: List[Dict[str, Any]] = payload.get("items", [])

    # 检查已处理的项目
    results = []
    processed_ids = set()
    if output_path.exists():
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                if "results" in existing_data:
                    results = existing_data["results"]
                    processed_ids = {item.get("id") for item in results}
            print(f"[INFO] 发现已存在的输出文件，加载了 {len(results)} 条结果。")
        except (json.JSONDecodeError, IOError) as e:
            print(f"[WARN] 无法读取已存在的输出文件 {output_path}: {e}。将重新开始。")

    items_to_process = [it for it in items if it.get("id") not in processed_ids]
    if not items_to_process:
        print("[INFO] 所有项目均已处理完毕。")
        return

    total_items = len(items)
    print(f"[INFO] 加载模型：{model_id}，总items={total_items}，已处理={len(processed_ids)}，本次处理={len(items_to_process)}，设备={args.device}")


    # 解析 --path-remap，例如 '/home/hice1=/workspace'
    remap: Optional[Tuple[str, str]] = None
    if args.path_remap:
        s = args.path_remap.strip()
        if "=" in s:
            src, dst = s.split("=", 1)
            remap = (os.path.expanduser(src), os.path.expanduser(dst))
            print(f"[INFO] 路径前缀替换：{remap[0]} -> {remap[1]}")
        else:
            print(f"[WARN] --path-remap 格式不正确：{s}；应为 'SRC=DEST'。")

    # 删除无用且未定义的导入分支
    # wdc = try_import_web_captioner(args.qwen_repo)

    # 优先尝试官方 Transformers 路径
    official_tuple = None
    if args.qwen_repo:
        try:
            official_tuple = init_official_transformers_and_utils(
                qwen_repo=args.qwen_repo,
                checkpoint_path=model_id,
                flash_attn2=args.flash_attn2,
            )
            print("[INFO] 使用官方 Transformers 推理路径。")
        except Exception as e:
            print(f"[WARN] 官方 Transformers 初始化失败：{e}；将尝试 AutoModel 远程代码。")

    # 初始化模型与处理器（官方优先，其次 AutoModel）
    if official_tuple is not None:
        model, processor, process_mm_info_fn = official_tuple
    else:
        if args.force_gpu and torch.cuda.is_available():
            os.environ["FORCE_GPU"] = "1"
        model, processor = init_model_and_processor(model_id, args.device, args.flash_attn2)
        process_mm_info_fn = None

    for idx, it in enumerate(items_to_process, 1):
        current_count = len(results) + 1
        audio_path = it["audio"]
        audio_path = rewrite_path_prefix(audio_path, remap)
        prompt_text = it.get("prompt") or "请对该人声片段进行音乐分析与描述。"
        messages = build_messages(audio_path, prompt_text)
        print(f"[{current_count}/{total_items}] 正在处理：{it.get('id')} -> {audio_path}", flush=True)
        try:
            if process_mm_info_fn is not None:
                caption = generate_caption_official(
                    model=model,
                    processor=processor,
                    process_mm_info_fn=process_mm_info_fn,
                    messages=messages,
                    temperature=args.temperature,
                    top_p=args.top_p,
                    top_k=args.top_k,
                    max_new_tokens=args.max_new_tokens,
                )
            else:
                caption = generate_caption_with_transformers(
                    model=model,
                    processor=processor,
                    messages=messages,
                    max_new_tokens=args.max_new_tokens,
                )
        except Exception as e:
            print(f"[ERROR] 推理失败 {it.get('id')}：{e}", flush=True)
            caption = f"[ERROR] {e}"

        results.append({
            "id": it.get("id"),
            "audio": audio_path,
            "prompt": prompt_text,
            "caption": caption,
        })

        out_payload = {
            "model": model_id,
            "count": len(results),
            "results": results,
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(out_payload, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        
        # 使用更新后的 results 长度
        print(f"[{len(results)}/{total_items}] 处理完毕并保存：{it.get('id')}", flush=True)

    print(f"[INFO] 所有任务处理完成，总计 {len(results)} 条结果已保存至 {output_path}")

    # 开启 TF32 以提速（A100/H100/RTX 支持）
    if torch.cuda.is_available():
        torch.backends.cuda.matmul.allow_tf32 = True
        try:
            torch.set_float32_matmul_precision("high")
        except Exception:
            pass

if __name__ == "__main__":
    main()