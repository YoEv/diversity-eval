#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path

def build_items(root: Path, genre: str, start: int, end: int, use_abs: bool, prompt: str, lang: str):
    items = []
    for i in range(start, end + 1):
        sub = f"{genre}.{i:05d}"
        wav = root / sub / f"{sub}_vocals.wav"
        if not wav.exists():
            print(f"[WARN] 缺失文件，跳过：{wav}")
            continue
        audio_path = str(wav.resolve()) if use_abs else str(wav)
        items.append({
            "id": sub,
            "audio": audio_path,
            "prompt": prompt,
            "language": lang,
        })
    return items

def main():
    parser = argparse.ArgumentParser(description="准备 Qwen Omni 的音频提示输入 JSON")
    parser.add_argument("--input-root", type=str,
                        default="data/output/separated/GTZAN_Dataset/blues",
                        help="分离结果的某个流派目录（包含 <genre>/<genre.xxxxx>/<genre.xxxxx>_vocals.wav）")
    parser.add_argument("--start", type=int, default=0, help="起始索引（包含）")
    parser.add_argument("--end", type=int, default=99, help="结束索引（包含）")
    parser.add_argument("--absolute", action="store_true",
                        help="输出音频路径使用绝对路径")
    parser.add_argument("--output-dir", type=str,
                        default="data/output/omni_prompt_input",
                        help="输出目录")
    parser.add_argument("--output-file", type=str,
                        default="omni_prompts.json",
                        help="输出文件名（JSON）")
    parser.add_argument("--model", type=str,
                        default="Qwen/Qwen3-Omni-30B-A3B-Instruct",
                        help="模型名称（记录到 JSON 顶层）")
    parser.add_argument("--prompt", type=str,
                        default="This is a vocal solo track from a source separated pop music, describe the tempo, rhythm pattern, style, emotions, main theme of the lyrics, and melodic contour of the piece.",
                        help="提示词内容（写入到每条记录）")
    parser.add_argument("--language", type=str, default="zh",
                        help="提示语言标记，例如 zh/en")

    args = parser.parse_args()

    input_root = Path(args.input_root).resolve()
    genre = args.input_root.strip().rstrip("/").split("/")[-1]
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / args.output_file

    items = build_items(
        root=input_root,
        genre=genre,
        start=args.start,
        end=args.end,
        use_abs=args.absolute,
        prompt=args.prompt,
        lang=args.language,
    )

    payload = {
        "model": args.model,
        "count": len(items),
        "items": items,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[OK] 已写入 {output_path}，条目数：{len(items)}")

if __name__ == "__main__":
    main()