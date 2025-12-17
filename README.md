# diversity-eval

A system-level framework for evaluating **distributional diversity** in generative music models.
This repo contains the end-to-end pipeline (data processing → prompting/generation → analysis) and reports produced during development.

## Paper

* **A Framework for Evaluating Distributional Diversity in Generative Music Models (PDF)**
  [https://github.com/YoEv/diversity-eval/blob/snapshot1027/A%20Framework%20for%20Evaluating%20Distributional%20Diversity%20in%20Generative%20Music%20Models.pdf](https://github.com/YoEv/diversity-eval/blob/snapshot1027/A%20Framework%20for%20Evaluating%20Distributional%20Diversity%20in%20Generative%20Music%20Models.pdf)

* External snapshot link (for sharing):
  [https://github.com/YoEv/diversity-eval/blob/snapshot1027/A%20Framework%20for%20Evaluating%20Distributional%20Diversity%20in%20Generative%20Music%20Models.pdf](https://github.com/YoEv/diversity-eval/blob/snapshot1027/A%20Framework%20for%20Evaluating%20Distributional%20Diversity%20in%20Generative%20Music%20Models.pdf)

## What’s in this repo

At a high level, the project evaluates diversity through a unified pipeline that supports:

* In-distribution vs out-of-distribution comparisons
* Key-related diversity signals (distribution-level)
* Melody-related diversity signals (symbolic- and embedding-level)
* Scalable caption/prompt generation and batch processing

## Repository structure (snapshot1027)

```
Reports/      # writeups, notes, intermediate reports
data/         # datasets, manifests, intermediate outputs
examples/     # example configs / example runs
external/     # external tools or wrappers
logs/         # runtime logs
pipelines/    # core pipeline code (preprocess, generation, evaluation)
scripts/      # entry scripts / launchers / utilities
vllm/         # vLLM submodule
.cache/       # local caches (environment-dependent)
README_EXTERNAL.md
README_PIPELINE.md
A Framework for Evaluating Distributional Diversity in Generative Music Models.pdf
```

([GitHub][1])

## Quick start

This repo is organized around `pipelines/` (core logic) and `scripts/` (how you run it).
For detailed, step-by-step instructions, see:

* `README_PIPELINE.md`
* `README_EXTERNAL.md` ([GitHub][1])

## Citation

If you build on this work, please cite the paper PDF linked above (formal bibtex entry can be added here later).

## Contact

Xiaosha (Evelyne) Li
Georgia Institute of Technology

[1]: https://github.com/YoEv/diversity-eval/tree/snapshot1027 "GitHub - YoEv/diversity-eval at snapshot1027"
