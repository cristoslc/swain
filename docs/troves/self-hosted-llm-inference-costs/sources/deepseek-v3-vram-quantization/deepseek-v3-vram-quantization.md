---
source-id: "deepseek-v3-vram-quantization"
title: "Understanding the Requirements for DeepSeek V3 Inference"
type: web
url: "https://blogs.novita.ai/what-are-the-requirements-for-deepseek-v3-inference/"
fetched: 2026-03-26T03:00:00Z
hash: "79f75e72f7f18823a53d8b27f8067dd51d8a557a52d2d86258d26ee2f2a1b83c"
---

# DeepSeek V3 Inference Requirements

## VRAM Requirements by Precision

| Precision | VRAM Required | Notes |
|-----------|--------------|-------|
| FP16 (full) | ~1,543 GB | 671B x 2 bytes + overhead |
| FP8 | ~685 GB | Requires 8x H100 minimum |
| 4-bit (Q4) | ~386 GB | Minimum practical quantization |
| 2-bit (dynamic) | ~131-226 GB | Significant quality loss |

## Architecture Efficiency

DeepSeek V3 is a Mixture-of-Experts model:
- **671B total parameters** but only **37B activated per token**
- 256 routed experts + 1 shared expert
- Each token interacts with 8 specialized experts + 1 shared expert
- This means compute scales with 37B, but memory must hold all 671B parameters resident

The MoE architecture makes the model cheaper to *run* per token (compute-wise) but does NOT reduce memory requirements since all expert weights must be loaded.

## Consumer Hardware Reality

The source explicitly states: "Running the full 671B parameter model locally requires significant computational power, often exceeding the capabilities of standard laptops or desktops."

Even with 4-bit quantization (386 GB), you need:
- At minimum 5x H100 80GB GPUs (400 GB usable)
- Or 8x A100 80GB GPUs (640 GB total, allowing room for KV cache)
- Or theoretically 16x RTX 4090s (384 GB total) -- but PCIe bandwidth and multi-GPU overhead make this impractical

## The RTX 4090 Myth

A single RTX 4090 has 24 GB VRAM. The 671B Q4 model needs ~386 GB.
That is **16 RTX 4090s** just for weights -- before any KV cache for context.
At ~$1,800/card, that is **$28,800 in GPUs alone**, plus a server chassis, motherboard, PSUs, and cooling that can handle 16 GPUs. Real builds like this cost $35,000-$50,000+.
