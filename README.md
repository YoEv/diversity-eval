**Distributional Diversity Evaluation for Generative Music Models**

A system-level, model-agnostic framework for evaluating **distributional diversity** in generative music systems, with a focus on tonal and melodic properties under in-distribution and out-of-distribution settings.

## Paper

* **[A Framework for Evaluating Distributional Diversity in Generative Music Models](https://github.com/YoEv/diversity-eval/blob/snapshot1027/A%20Framework%20for%20Evaluating%20Distributional%20Diversity%20in%20Generative%20Music%20Models.pdf)**

## Method at a glance

This project evaluates diversity as a **corpus-level property**, rather than a sample-level reconstruction objective.
The framework operates by:

1. Mapping real and generated audio into musically meaningful representations (e.g., key labels, symbolic main-melody features, learned embeddings).
2. Constructing feature distributions over real and generated corpora.
3. Comparing these distributions using appropriate diversity and divergence measures to quantify coverage, concentration, and drift.
4. Analyzing robustness under domain shift (in-distribution vs out-of-distribution) and stability across repeated generations.

Pairwise similarity measures are used only for stability or controllability analysis and are explicitly separated from distributional diversity evaluation.

## Pipeline overview

![Diversity evaluation pipeline](https://github.com/YoEv/diversity-eval/blob/snapshot1027/pipeline_figure.png)

The pipeline integrates waveform processing, representation extraction, optional caption-based prompting and regeneration, and distribution-level analysis, while remaining agnostic to the underlying generative model architecture.

## What’s in this repo

At a high level, the repository contains:

* Data processing and evaluation pipelines for key and melodic diversity
* Scripts for large-scale generation, captioning, and analysis
* Reports and intermediate artifacts produced during development

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
pipeline_figure.png
A Framework for Evaluating Distributional Diversity in Generative Music Models.pdf
```

## Citation

If you use this framework or build upon this work, please cite this repo.

## Contact

Xiaosha Evelyne Li
Georgia Institute of Technology
