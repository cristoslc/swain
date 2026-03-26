---
source-id: "deepseek-671b-8xh100-benchmarks"
title: "DeepSeek-V3/R1 671B on 8xH100: Deployment and Throughput Benchmarks"
type: web
url: "https://github.com/dzhsurf/deepseek-v3-r1-deploy-and-benchmarks"
fetched: 2026-03-26T03:00:00Z
hash: "c1aca20ef58f58e04d68132b1f79cb8920cee5719a2d31c24f72a93ad6057ea3"
---

# DeepSeek-V3/R1 671B on 8xH100 Benchmarks

## Hardware Configuration

- **GPUs**: 8x NVIDIA H100 SXM5 (640 GB total VRAM)
- **CPU**: 104x Intel Xeon Platinum 8470 cores
- **RAM**: 1024 GB DDR5
- **Network**: 100 Gbps Ethernet
- **Software**: vLLM 0.7.3

## Model Configuration

- **Model**: cognitivecomputations/DeepSeek-V3-AWQ (4-bit AWQ quantization)
- **Weight storage**: ~335 GB (quantized from 8-bit)
- **Total VRAM consumption**: ~400 GB across 8 GPUs (~50 GB per GPU)
- **Sequence config**: Input=1024 tokens, Output=256 tokens, MAX_NUM_SEQS=128

## Throughput Benchmarks

| Concurrency | Output tok/s | Total tok/s | Notes |
|-------------|-------------|-------------|-------|
| 1 | **~33** | -- | Single user, interactive |
| 15 | **~250** | -- | ~50ms median inter-token latency |
| 100+ | **~620** | ~3,000 | Peak throughput |

### Key Finding: Single-User Performance
At concurrency 1 (single user, agentic coding scenario), the model produces **~33 tokens/second**. This is within the 50-100 tok/s target range only at the low end.

### Multi-Node Performance (2 nodes, 16 GPUs, no InfiniBand)
- Output tokens/sec: ~980 (1.58x improvement over single node)
- Total throughput: ~4,500 tok/s
- Bottleneck: Socket-based communication without InfiniBand

## FP8 vs AWQ Comparison

FP8 deployment achieves approximately **1.4x speedup** over AWQ:
- FP8 output throughput: ~821 tok/s on 8xH100
- But FP8 requires ~685 GB VRAM -- more than 8x H100 (640 GB) can provide without offloading

## SGLang vs vLLM

SGLang demonstrated significantly lower concurrent throughput compared to vLLM for this deployment, making vLLM the recommended serving framework.

## Agentic Coding Viability Assessment

For single-user agentic coding (concurrency 1):
- **33 tok/s** on 8xH100 with AWQ quantization
- This is below the 50-100 tok/s target for comfortable agentic use
- Achieving 50+ tok/s would require FP8 on a larger GPU cluster (10+ H100s) or next-gen hardware (H200/B200)
- Monthly cost for 8xH100 cloud rental: **$8,700-$17,500/month** depending on provider
