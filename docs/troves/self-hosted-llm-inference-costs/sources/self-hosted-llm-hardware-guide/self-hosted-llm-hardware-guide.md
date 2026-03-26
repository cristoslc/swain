---
source-id: "self-hosted-llm-hardware-guide"
title: "Self-Hosted LLMs in 2026: Hardware Tiers, Cost, and the DeepSeek V4 Break-Even Analysis"
type: web
url: "https://wavespeed.ai/blog/posts/deepseek-v4-gpu-vram-requirements/"
fetched: 2026-03-26T03:00:00Z
hash: "27a39ecd9c5861e2dd750383b4d8bd213d71faf6d0ba55c80cd3c41b8fe9af83"
---

# Self-Hosted LLM Hardware Guide (2026)

## DeepSeek V4 / 671B MoE Memory Requirements

### Full Precision (BF16)
- Active path weights: ~74 GB (37B x 2 bytes)
- Full 671B resident: **~1.34 TB** for weights alone
- Total with overhead: impractical without 16+ enterprise GPUs

### Quantized Options
| Quantization | VRAM Required | Quality Impact |
|-------------|--------------|----------------|
| Q8 | ~42-46 GB per-GPU (multi-GPU) | 1-2 pt loss on knowledge tasks, minor code differences |
| Q4 | ~22-26 GB per-GPU (multi-GPU) | 3-6 pt loss on knowledge tasks, noticeable wobble on complex reasoning |
| AWQ/GPTQ | Comparable to Q4/Q8 | Optimized for GPU inference |

### Quality Trade-offs by Task Type

| Task | BF16 | Q8 | Q4 |
|------|------|-----|-----|
| Knowledge tasks | Baseline | 1-2 pt loss | 3-6 pt loss |
| Code generation | Baseline | Minor differences | Adequate for edits |
| Math/Reasoning | Baseline | Slight regression on long CoT | Noticeable wobble on complex problems |

**Q4 is recommended for drafting and retrieval-grounded tasks. Q8+ preferred for reasoning-heavy workloads like agentic coding.**

## Hardware Configurations

### Multi-Node (Full Precision)
- **8x H100 80GB or 8x A100 80GB minimum** for BF16
- 16-24 GPUs recommended for headroom with KV cache

### Single-Node with Quantization
- **8x H100**: Q8 with tensor parallel 2-4; Q4 with tensor parallel 1-2
- **4x 80GB node**: Q8 functional with small batches; Q4 comfortable

### Consumer GPU Feasibility
- **2x RTX 4090**: Q4 only, short interactive prompts, NOT production-ready
- **4x RTX 4090**: Q8 viable with 4-8k contexts and reasonable batch sizes
- Thermal throttling and PCIe bandwidth create hidden constraints
- Even 4x RTX 4090 produces only **1-15 tok/s** for 671B models

## Cost-Benefit Break-Even Analysis

### API vs Self-Hosting Thresholds
| Monthly Tokens | API Cost (DeepSeek) | Self-Host (H100 rental) | Winner |
|---------------|--------------------|-----------------------|--------|
| <5M | ~$15 | ~$8,700+ | **API** |
| 100M | ~$300 | ~$8,700+ | **API** |
| 500M | ~$1,500 | ~$8,700+ | **API** |
| 1B+ | ~$3,000 | ~$8,700+ | **API** |

### Hidden Self-Hosting Costs
- Engineering overhead for deployment, monitoring, updates
- Observability infrastructure
- Model update management
- Ops infrastructure and on-call burden

### Break-Even Reality
Self-hosting becomes economically viable only at **300M+ tokens/month** with **>50% GPU utilization** sustained across quarters. For a single-user agentic coding scenario, API usage is almost always cheaper.

## What RTX 4090 Actually Gets You

An RTX 4090 ($1,800) with 24 GB VRAM can comfortably run:
- **Up to 32B parameter models** (e.g., Qwen 2.5 Coder 32B at Q4)
- **Performance**: 30-40 tok/s on 70B Q4 models (on Apple M3 Max 128GB via llama.cpp)
- These smaller models are excellent for coding assistance

It CANNOT run 397B-671B models. Period.

## Consumer Hardware Tier Reality

| Tier | Hardware | Cost | Max Model Size |
|------|----------|------|----------------|
| Entry | RTX 4060 (8GB) | ~$300 | 7-8B |
| Mid | RTX 4090 (24GB) | ~$1,800 | 32B |
| High | 2x RTX 4090 (48GB) | ~$3,600 | 70B (Q4) |
| Extreme | 4x RTX 4090 (96GB) | ~$7,200+ | ~100B |
| 671B territory | 8x H100 (640GB) | $8,700+/mo rental | 671B (Q4) |
