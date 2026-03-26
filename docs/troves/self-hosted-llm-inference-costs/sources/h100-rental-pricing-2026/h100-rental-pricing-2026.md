---
source-id: "h100-rental-pricing-2026"
title: "H100 Rental Prices Compared: $1.49-$6.98/hr Across 15+ Cloud Providers (2026)"
type: web
url: "https://intuitionlabs.ai/articles/h100-rental-prices-cloud-comparison"
fetched: 2026-03-26T03:00:00Z
hash: "a1e12e92eaf1947aa92b21baae74bc532a7a95b0836a6dc35aadb1d981e88a40"
---

# H100 Rental Prices Compared (2026)

## Per-GPU Hourly Rates (On-Demand)

### Major Cloud Providers
| Provider | $/GPU-hr |
|----------|----------|
| Azure (NC H100 v5) | $6.98 |
| Paperspace | $5.95 |
| CoreWeave | $6.16 |
| AWS (P5) | $3.90 |
| Google Cloud (A3-High) | $3.00 |

### Specialist GPU Clouds
| Provider | $/GPU-hr |
|----------|----------|
| Lambda Labs | $2.99 |
| TensorDock | $2.25 |
| RunPod (community) | $1.99 |
| HPC-AI | $1.99 |
| Cudo Compute | $1.80 |
| NeevCloud | $1.79 |
| Vast.ai (marketplace) | $1.49-$1.87 |

### Spot/Preemptible
| Provider | $/GPU-hr |
|----------|----------|
| AWS spot | ~$2.50 |
| GCP preemptible | ~$2.25 |

### Reserved (1-3 year commitment)
| Provider | $/GPU-hr |
|----------|----------|
| AWS Savings Plans | $1.90-$2.10 |

## 8-GPU Configuration Costs (Monthly Estimate, 24/7)

For a 671B model you need minimum 5x H100 but realistically 8x H100. Monthly costs at 24/7 uptime (730 hours/month):

| Provider | 8x H100 $/hr | Monthly (730h) |
|----------|--------------|----------------|
| Vast.ai (low) | $11.92 | **$8,702** |
| RunPod | $15.92 | **$11,622** |
| Lambda Labs | $23.92 | **$17,462** |
| AWS (on-demand) | $31.20 | **$22,776** |
| AWS (spot) | $20.00 | **$14,600** |
| Azure | $55.84 | **$40,763** |

## Historical Context

- AWS cut H100 prices 44% in June 2025 (from ~$7.57/GPU-hr to ~$3.90)
- H100 supply increased substantially by late 2025
- H200 (Blackwell) expected to push H100 prices further down through 2026
- Projected: sub-$2/GPU-hr universally by mid-2026

## A100 Pricing (Cheaper Alternative)

| Provider | A100 80GB $/GPU-hr |
|----------|-------------------|
| Vast.ai | $0.67 |
| RunPod | $0.79-$1.19 |
| Lambda | ~$1.29 |

8x A100 80GB monthly (Vast.ai): ~$3,912 -- but only 640GB total VRAM, which is tight for 671B Q4 (~380GB weights + KV cache).
