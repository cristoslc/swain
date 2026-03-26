# Synthesis: Self-Hosted LLM Inference Costs

## The Core Finding

**The "$55/month RTX 4090 build" claim in SPIKE-045 is off by two orders of magnitude for 397B-671B models.** A single RTX 4090 has 24 GB VRAM. A 671B model at Q4 quantization needs ~386 GB. You would need 16 RTX 4090s ($28,800+ in GPUs alone) just for weights, and the result would still be impractically slow (1-15 tok/s) due to PCIe bandwidth bottlenecks.

The realistic minimum for running qwen3.5:397b or deepseek-v3.1:671b at usable speeds is **8x H100 80GB GPUs**, which costs **$8,700-$17,500/month** in cloud rental.

## Theme 1: Memory Requirements Are Non-Negotiable

671B parameter models have irreducible memory requirements regardless of MoE architecture:

| Precision | VRAM for 671B | Minimum GPUs |
|-----------|--------------|--------------|
| FP16 | ~1,543 GB | 20x H100 80GB |
| FP8 | ~685 GB | 9x H100 80GB |
| Q4 (AWQ) | ~335-386 GB | 5x H100 80GB |
| Q2 (dynamic) | ~131-226 GB | 2-3x H100 80GB |

The MoE architecture (37B active parameters per token) reduces **compute** per token but does NOT reduce **memory** -- all 671B parameters must be resident in GPU memory because any token might route to any expert.

Q4 quantization is the practical floor for usable quality. Below Q4, code generation and reasoning quality degrade noticeably -- exactly the tasks agentic coding demands.

*Sources: deepseek-v3-gpu-requirements, deepseek-v3-vram-quantization, self-hosted-llm-hardware-guide*

## Theme 2: Actual Performance on Real Hardware

The best available benchmark for this exact scenario (DeepSeek 671B on 8xH100 with AWQ quantization via vLLM):

| Metric | Value | Target for Agentic Coding |
|--------|-------|--------------------------|
| Single-user tok/s | **~33** | 50-100 |
| Peak concurrent tok/s | ~620 | N/A (single user) |
| Inter-token latency (1 user) | Minimal | <50ms |

**33 tok/s falls short of the 50-100 tok/s target** for comfortable agentic coding. Achieving 50+ tok/s would require either FP8 on 10+ H100s or next-gen hardware (H200/B200).

On consumer hardware, the picture is far worse:
- **RTX 4090 (24GB)**: Cannot load the model at all
- **4x RTX 4090 (96GB)**: Still cannot load 671B Q4 (~386 GB)
- **Consumer CPU-only (96GB RAM, NVMe)**: ~2 tok/s -- unusable for agentic work
- **4x Mac Studio M3 Ultra (512GB unified)**: Theoretically possible, ~$12,000 hardware, speed unknown

*Sources: deepseek-671b-8xh100-benchmarks, self-hosted-llm-hardware-guide*

## Theme 3: Cloud GPU Rental Costs

Monthly costs for running 671B models 24/7 (730 hours/month):

| Configuration | Cheapest Provider | Monthly Cost |
|--------------|-------------------|-------------|
| 8x A100 80GB | Vast.ai ($0.67/GPU-hr) | **$3,913** |
| 8x H100 80GB | RunPod ($1.50/GPU-hr) | **$8,760** |
| 8x H100 80GB | Lambda ($2.99/GPU-hr) | **$17,462** |
| 5x H100 80GB (tight) | RunPod ($1.50/GPU-hr) | **$5,475** |

H100 prices have fallen significantly (AWS cut 44% in June 2025), and are projected to reach sub-$2/GPU-hr universally by mid-2026. But even optimistic projections put 8xH100 monthly at $8,000+.

For intermittent use (e.g., 8 hours/day, 5 days/week = ~173 hours/month):
- 8x H100 on RunPod: ~$2,076/month
- 8x A100 on Vast.ai: ~$928/month

*Sources: h100-rental-pricing-2026, gpu-cloud-pricing-comparison*

## Theme 4: Cost Comparison -- The Brutal Math

### Ollama Cloud vs Self-Hosted for 671B Models

| Option | Monthly Cost | 671B Model Access | Speed | Reliability |
|--------|-------------|-------------------|-------|-------------|
| Ollama Cloud Max | **$100** | Yes (cloud-hosted) | Varies (timeout issues reported) | Questionable (see dispatch-workers trove) |
| Ollama Cloud Pro | **$25** | Yes (rate-limited) | Varies | Questionable |
| Self-hosted 8xH100 (cloud) | **$8,760-$17,500** | Yes | ~33 tok/s single-user | You manage it |
| Self-hosted 8xA100 (cloud) | **$3,913-$4,614** | Tight fit, slower | ~20 tok/s estimated | You manage it |
| DeepSeek API direct | **~$15-300** (by usage) | Yes | Fast | Good |

### Break-Even Analysis

Self-hosting only makes economic sense at **300M+ tokens/month** with **>50% GPU utilization** sustained over quarters. A single agentic coding user generating even 10M tokens/month would pay:
- DeepSeek API: ~$3-11/month
- Ollama Cloud Max: $100/month (unlimited within plan)
- Self-hosted 8xH100: $8,760/month

**Self-hosting 671B models is 87-292x more expensive than Ollama Cloud Max for a single user.**

*Sources: gpu-cloud-pricing-comparison, self-hosted-llm-hardware-guide; cross-ref: ollama-cloud-subscriptions trove*

## Theme 5: What $55/Month Actually Gets You

The "$55/month" figure from SPIKE-045 corresponds roughly to the amortized cost of a single RTX 4090 build (~$2,000 hardware / 36 months + electricity). That hardware can run:

- **Qwen 2.5 Coder 32B** at Q4: fits in 24GB, excellent coding performance
- **Llama 3.3 70B** at heavy quantization: marginal fit, degraded quality
- **DeepSeek-R1-Distill-32B**: good reasoning in a small package

These are **32B-70B models**, not 397B-671B. They are useful for coding assistance but represent a fundamentally different capability tier than the frontier 671B models.

*Sources: self-hosted-llm-hardware-guide; cross-ref: ollama-cloud-dispatch-workers trove*

## Implications for SPIKE-045 Pivot B

1. **Pivot B as stated is not viable.** Self-hosting qwen3.5:397b or deepseek-v3.1:671b requires $3,900-$17,500/month in GPU rental -- not $55/month.
2. **The RTX 4090 path works only for smaller models** (up to ~70B with quantization). These models are useful but are not the "frontier dispatch workers" SPIKE-045 envisions.
3. **Ollama Cloud Max at $100/month is dramatically cheaper** than self-hosting for 671B model access, despite its reliability problems.
4. **DeepSeek's own API** ($0.27-$1.10/M tokens) is the cheapest way to access 671B-class models for low-to-moderate usage.
5. **The only scenario where self-hosting 671B makes sense** is a team of 10+ developers sharing the same GPU cluster, amortizing $8,700/month across many users -- and even then, API access is likely cheaper and simpler.

## Confidence Assessment

- **VRAM requirements**: High confidence. Multiple independent sources converge on ~386 GB for 671B Q4.
- **Cloud pricing**: High confidence. Cross-validated across 5+ providers with March 2026 data.
- **Performance benchmarks**: Medium-high confidence. Based on one detailed benchmark repo (8xH100) corroborated by community reports.
- **Break-even analysis**: Medium confidence. Depends on usage patterns and assumes current pricing holds.
