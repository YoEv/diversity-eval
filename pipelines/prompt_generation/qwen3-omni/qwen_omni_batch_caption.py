#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import torch
import transformers
from transformers import AutoProcessor, Qwen3OmniMoeForConditionalGeneration, Qwen3OmniMoeProcessor, AutoConfig
from transformers import BitsAndBytesConfig as HFBitsAndBytesConfig
import importlib
from accelerate import dispatch_model as _dispatch_model
import re

def log_device_info(model):
    dm = getattr(model, "hf_device_map", None)
    print(f"[DEV] cuda_available={torch.cuda.is_available()}, gpu_count={torch.cuda.device_count()}")
    if torch.cuda.is_available():
        cur = torch.cuda.current_device()
        print(f"[DEV] current_gpu={cur}, name={torch.cuda.get_device_name(cur)}")
        for i in range(torch.cuda.device_count()):
            alloc = torch.cuda.memory_allocated(i) // (1024**2)
            rsv = torch.cuda.memory_reserved(i) // (1024**2)
            cap = torch.cuda.get_device_properties(i).total_memory // (1024**2)
            print(f"[DEV] gpu[{i}] alloc={alloc}MiB reserved={rsv}MiB total={cap}MiB")
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
    try:
        p.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"[WARN] 创建目录失败 {p}: {e}")

def build_messages(audio_path: str, prompt_text: str) -> List[Dict[str, Any]]:
    return [
        {
            "role": "user",
            "content": [
                {"type": "audio", "audio": audio_path},
                {"type": "text", "text": prompt_text},
            ],
        }
    ]

def init_model_and_processor(model_id: str, device: str, dtype_opt: str, max_memory_str: str, offload_folder: str, quantize_str: str, device_map_opt: str):
    cache_dir = os.environ.get("TRANSFORMERS_CACHE")

    torch_dtype = None
    if dtype_opt and dtype_opt != "auto":
        torch_dtype = {"bfloat16": torch.bfloat16, "float16": torch.float16, "float32": torch.float32}.get(dtype_opt)

    mem = None
    if max_memory_str:
        parts = [p.strip() for p in max_memory_str.split(",") if p.strip()]
        mem = {}
        for kv in parts:
            k, v = kv.split("=", 1)
            k = k.strip(); v = v.strip()
            key = int(k) if k.isdigit() else (k if k != "" else "")
            mem[key] = v

    quantization_config = None
    if quantize_str and quantize_str != "none" and HFBitsAndBytesConfig is not None and importlib.util.find_spec("bitsandbytes") is not None:
        if quantize_str == "4bit":
            quantization_config = HFBitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True, bnb_4bit_quant_type="nf4")
            torch_dtype = None
        elif quantize_str == "8bit":
            quantization_config = HFBitsAndBytesConfig(load_in_8bit=True)
            torch_dtype = None

    cfg = None
    cfg = AutoConfig.from_pretrained(model_id, trust_remote_code=True, cache_dir=cache_dir, local_files_only=True)
    if cfg is not None and not hasattr(cfg, "initializer_range"):
        setattr(cfg, "initializer_range", 0.02)
    try:
        model = Qwen3OmniMoeForConditionalGeneration.from_pretrained(
            model_id,
            device_map=device_map_opt,
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            cache_dir=cache_dir,
            local_files_only=True,
            torch_dtype=torch_dtype,
            max_memory=mem,
            offload_folder=(offload_folder or None),
            quantization_config=quantization_config,
            config=cfg,
        )
    except Exception:
        AutoModelCls = getattr(transformers, "AutoModelForCausalLM", None) or getattr(transformers, "AutoModelForConditionalGeneration", None) or getattr(transformers, "AutoModel", None)
        model = AutoModelCls.from_pretrained(
            model_id,
            device_map=device_map_opt,
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            cache_dir=cache_dir,
            local_files_only=True,
            torch_dtype=torch_dtype,
            max_memory=mem,
            offload_folder=(offload_folder or None),
            quantization_config=quantization_config,
            config=cfg,
        )
    model.eval()
    log_device_info(model)

    processor = Qwen3OmniMoeProcessor.from_pretrained(
        model_id,
        trust_remote_code=True,
        cache_dir=cache_dir,
        local_files_only=True,
    )
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

def build_equal_max_memory(reserve_gib: int = 5) -> str:
    if not torch.cuda.is_available():
        return ""
    n = torch.cuda.device_count()
    vals = []
    for i in range(n):
        total_gib = int(torch.cuda.get_device_properties(i).total_memory // (1024**3))
        budget = max(total_gib - reserve_gib, 1)
        vals.append(f"{i}={budget}GiB")
    s = ",".join(vals)
    print(f"[DEV] computed max_memory: {s}")
    return s


def build_uniform_device_map(model, num_gpus):
    names = [n for n, _ in model.named_modules()]
    layer_names = sorted([n for n in names if re.search(r"layers\.\d+$", n)], key=lambda x: int(x.split(".")[-1]))
    device_map = {"": "cuda:0"}
    if layer_names:
        per = (len(layer_names) + num_gpus - 1) // num_gpus
        for i, ln in enumerate(layer_names):
            gid = i // per
            if gid >= num_gpus:
                gid = num_gpus - 1
            device_map[ln] = f"cuda:{gid}"
    for n in names:
        if n.endswith("embed_tokens"):
            device_map[n] = "cuda:0"
        if n.endswith("lm_head"):
            device_map[n] = "cuda:0"
    norm_names = [n for n in names if n.endswith("norm") and "layers" not in n]
    for n in norm_names:
        device_map[n] = f"cuda:{num_gpus-1}"
    return device_map

def redispatch_uniform(model, num_gpus):
    if _dispatch_model is None:
        return model
    if not torch.cuda.is_available() or num_gpus < 1:
        return model
    dm = build_uniform_device_map(model, num_gpus)
    try:
        model = _dispatch_model(model, device_map=dm)
    except Exception:
        pass
    return model

def apply_audio_device(model, audio_device):
    if not audio_device:
        return model
    d = str(audio_device).strip()
    dev = d if d.startswith("cuda:") else (f"cuda:{d}" if d.isdigit() else d)
    names = list(model.named_modules())
    mod_map = {n: m for n, m in names}
    audio_keys = [n for n, _ in names if ("code2wav" in n) or ("codec" in n) or ("audio" in n) or ("wav" in n) or ("pre_transformer" in n) or ("post_transformer" in n)]
    if not audio_keys:
        return model
    if _dispatch_model is None:
        moved = 0
        def _move_tree(x, device):
            if torch.is_tensor(x):
                return x.to(device)
            if isinstance(x, (list, tuple)):
                return type(x)(_move_tree(t, device) for t in x)
            if isinstance(x, dict):
                return {k: _move_tree(v, device) for k, v in x.items()}
            return x
        def _find_dev(x):
            if torch.is_tensor(x) and x.is_cuda:
                return x.device
            if isinstance(x, (list, tuple)):
                for t in x:
                    d0 = _find_dev(t)
                    if d0 is not None:
                        return d0
            if isinstance(x, dict):
                for v in x.values():
                    d0 = _find_dev(v)
                    if d0 is not None:
                        return d0
            return None
        for k in audio_keys:
            m = mod_map.get(k)
            if m is None:
                continue
            try:
                m.to(dev)
                def _pre_hook(mod, inputs):
                    src = _find_dev(inputs)
                    setattr(mod, "_orig_dev", src)
                    return _move_tree(inputs, dev)
                def _post_hook(mod, inputs, outputs):
                    src = getattr(mod, "_orig_dev", None)
                    return _move_tree(outputs, src) if src is not None else outputs
                try:
                    m.register_forward_pre_hook(_pre_hook)
                    m.register_forward_hook(_post_hook)
                except Exception:
                    pass
                moved += 1
            except Exception:
                pass
        dm = getattr(model, "hf_device_map", None)
        if isinstance(dm, dict):
            for k in audio_keys:
                dm[k] = dev
        print(f"[DEV] force-moved audio modules to {dev}: {moved}")
        return model
    dm = getattr(model, "hf_device_map", None) or {"": "cuda:0"}
    for k in audio_keys:
        dm[k] = dev
    try:
        model = _dispatch_model(model, device_map=dm)
    except Exception:
        pass
    return model

def init_official_transformers_and_utils(qwen_repo: str, checkpoint_path: str, flash_attn2: bool, dtype_opt: str, max_memory_str: str, offload_folder: str, quantize_str: str, device_map_opt: str):
    repo = Path(qwen_repo).expanduser().resolve()
    if str(repo) not in sys.path:
        sys.path.append(str(repo))
    from transformers import Qwen3OmniMoeForConditionalGeneration, Qwen3OmniMoeProcessor
    from qwen_omni_utils import process_mm_info
    cache_dir = os.environ.get("TRANSFORMERS_CACHE")

    torch_dtype = None
    if dtype_opt and dtype_opt != "auto":
        torch_dtype = {"bfloat16": torch.bfloat16, "float16": torch.float16, "float32": torch.float32}.get(dtype_opt)

    mem = None
    if max_memory_str:
        try:
            parts = [p.strip() for p in max_memory_str.split(",") if p.strip()]
            mem = {}
            for kv in parts:
                k, v = kv.split("=", 1)
                k = k.strip(); v = v.strip()
                key = int(k) if k.isdigit() else (k if k != "" else "")
                mem[key] = v
        except Exception:
            mem = None

    quantization_config = None
    if quantize_str and quantize_str != "none" and HFBitsAndBytesConfig is not None and importlib.util.find_spec("bitsandbytes") is not None:
        if quantize_str == "4bit":
            quantization_config = HFBitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True, bnb_4bit_quant_type="nf4")
            torch_dtype = None
        elif quantize_str == "8bit":
            quantization_config = HFBitsAndBytesConfig(load_in_8bit=True)
            torch_dtype = None

    cfg = None
    cfg = AutoConfig.from_pretrained(checkpoint_path, trust_remote_code=True, cache_dir=cache_dir, local_files_only=True)
    if cfg is not None and not hasattr(cfg, "initializer_range"):
        setattr(cfg, "initializer_range", 0.02)

    try:
        model = Qwen3OmniMoeForConditionalGeneration.from_pretrained(
            checkpoint_path,
            device_map=device_map_opt,
            cache_dir=cache_dir,
            local_files_only=True,
            torch_dtype=torch_dtype,
            max_memory=mem,
            offload_folder=(offload_folder or None),
            quantization_config=quantization_config,
            config=cfg,
        )
    except Exception:
        AutoModelCls = getattr(transformers, "AutoModelForCausalLM", None) or getattr(transformers, "AutoModelForConditionalGeneration", None) or getattr(transformers, "AutoModel", None)
        model = AutoModelCls.from_pretrained(
            checkpoint_path,
            device_map=device_map_opt,
            trust_remote_code=True,
            cache_dir=cache_dir,
            local_files_only=True,
            torch_dtype=torch_dtype,
            max_memory=mem,
            offload_folder=(offload_folder or None),
            quantization_config=quantization_config,
            config=cfg,
        )
    model.eval()
    log_device_info(model)
    processor = Qwen3OmniMoeProcessor.from_pretrained(checkpoint_path, cache_dir=cache_dir, local_files_only=True)
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
    parser.add_argument("--output-json", type=str, default="data/output/omni_prompt_output/captions_batch.json",
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
    parser.add_argument("--dtype", type=str, choices=["auto","bfloat16","float16","float32"], default="auto")
    parser.add_argument("--max-memory", type=str, default="")
    parser.add_argument("--offload-folder", type=str, default="")
    parser.add_argument("--device-map", type=str, choices=["auto","balanced","balanced_low_0","sequential"], default="auto")
    parser.add_argument("--quantize", type=str, choices=["none","4bit","8bit"], default="none")
    parser.add_argument("--cuda-devices", type=str, default="", help="限制可见GPU，例如 '0,1,2,3'")
    parser.add_argument("--equal-shard", action="store_true", help="均衡分片到所有可见GPU")
    parser.add_argument("--reserve-gib", type=int, default=5, help="每张GPU保留的GiB数")
    parser.add_argument("--audio-device", type=str, default="", help="将重型音频子模块移动到指定设备，例如 'cuda:3' 或 '3'")
    parser.add_argument("--cpu-init", action="store_true", help="先在CPU加载权重，再进行GPU分片与音频迁移")
    args = parser.parse_args()

    input_path = Path(args.input_json).resolve()
    output_path = Path(args.output_json).resolve()
    ensure_dir(output_path.parent)

    payload = load_payload(input_path)
    model_id = payload.get("model", "Qwen/Qwen3-Omni-30B-A3B-Instruct")
    items: List[Dict[str, Any]] = payload.get("items", [])
    print(f"[INFO] 加载模型：{model_id}，items={len(items)}，设备={args.device}")

    if args.cuda_devices:
        os.environ["CUDA_VISIBLE_DEVICES"] = args.cuda_devices
        print(f"[INFO] 使用CUDA设备: {args.cuda_devices}")

    mem_str = args.max_memory
    device_map_opt = args.device_map
    if args.device == "cuda" and args.equal_shard:
        mem_str = build_equal_max_memory(args.reserve_gib)
        if device_map_opt == "auto":
            device_map_opt = "balanced"
        print(f"[INFO] 使用均衡分片: device_map={device_map_opt}, max_memory={mem_str}")
    if args.device == "cuda" and args.cpu_init:
        device_map_opt = None
        print("[INFO] 初始在CPU加载权重，随后进行GPU分片与音频模块迁移")

    remap: Optional[Tuple[str, str]] = None
    if args.path_remap:
        s = args.path_remap.strip()
        if "=" in s:
            src, dst = s.split("=", 1)
            remap = (os.path.expanduser(src), os.path.expanduser(dst))
            print(f"[INFO] 路径前缀替换：{remap[0]} -> {remap[1]}")
        else:
            print(f"[WARN] --path-remap 格式不正确：{s}；应为 'SRC=DEST'。")

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
    total_to_process = len(items_to_process)
    print(f"[INFO] 总 items={len(items)}，已处理={len(processed_ids)}，本次处理={total_to_process}")

    official_tuple = None
    if args.qwen_repo:
        try:
            official_tuple = init_official_transformers_and_utils(
                qwen_repo=args.qwen_repo,
                checkpoint_path=model_id,
                flash_attn2=args.flash_attn2,
                dtype_opt=args.dtype,
                max_memory_str=mem_str,
                offload_folder=args.offload_folder,
                quantize_str=args.quantize,
                device_map_opt=device_map_opt,
            )
            print("[INFO] 使用官方 Transformers 推理路径。")
        except Exception as e:
            print(f"[WARN] 官方 Transformers 初始化失败：{e}；将尝试 AutoModel 远程代码。")

    if official_tuple is not None:
        model, processor, process_mm_info_fn = official_tuple
    else:
        if args.force_gpu and torch.cuda.is_available():
            os.environ["FORCE_GPU"] = "1"
        model, processor = init_model_and_processor(model_id, args.device, args.dtype, mem_str, args.offload_folder, args.quantize, device_map_opt)
        process_mm_info_fn = None
    if args.device == "cuda" and args.equal_shard and torch.cuda.is_available():
        model = redispatch_uniform(model, torch.cuda.device_count())
    model = apply_audio_device(model, args.audio_device)


    for idx, it in enumerate(items_to_process, 1):
        audio_path = it["audio"]
        audio_path = rewrite_path_prefix(audio_path, remap)
        prompt_text = it.get("prompt") or "请对该人声片段进行音乐分析与描述。"
        messages = build_messages(audio_path, prompt_text)
        print(f"[{idx}/{total_to_process}] 处理：{it.get('id')} -> {audio_path}")
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
            print(f"[ERROR] 推理失败 {it.get('id')}：{e}")
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
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(out_payload, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[WARN] 实时写入文件失败: {e}")

    print(f"[OK] 全部处理完成，最终结果已写入：{output_path}")

    if torch.cuda.is_available():
        torch.backends.cuda.matmul.allow_tf32 = True
        try:
            torch.set_float32_matmul_precision("high")
        except Exception:
            pass

if __name__ == "__main__":
    main()