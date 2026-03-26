---
source-id: "ollama-pricing-page"
title: "Ollama Pricing Page — Official Tier Comparison"
type: web
url: "https://ollama.com/pricing"
fetched: 2026-03-25T18:00:00Z
hash: "706fad4998ac1f932aaa85e27cd27cc99d57c9217dae51863b3b32801d30e987"
---

# Ollama Pricing Page — Official Tier Comparison

Primary source: the official Ollama pricing page at ollama.com/pricing, fetched 2026-03-25.

## Tiers

### Free ($0)

- Automate coding, document analysis, and other tasks with open models
- Keep your data private
- Run models on your hardware
- Access cloud models
- CLI, API, and desktop apps
- 40,000+ community integrations
- Unlimited public models
- **Concurrency**: 1 cloud model at a time
- **Usage level**: Light usage — chatting with models, evaluating larger models, coding and AI assistants with smaller models

### Pro ($20/month or $200/year)

Everything in Free, plus:

- **Concurrency**: Run 3 cloud models at a time
- **Usage**: 50x more cloud usage than Free
- Upload and share private models
- **Usage level**: Day-to-day work — larger models, coding automation, deep research

### Max ($100/month)

Everything in Pro, plus:

- **Concurrency**: Run 10 cloud models at a time
- **Usage**: 5x more usage than Pro (effectively 250x Free)
- **Usage level**: Heavy, sustained usage — continuous agent tasks, multiple concurrent agents, large models over extended sessions

## Usage Model

- Each plan has **session limits that reset every 5 hours** and **weekly limits that reset every 7 days**.
- Usage reflects actual utilization of Ollama's cloud infrastructure — primarily **GPU time**, which depends on model size and request duration.
- Shorter requests and prompts that share cached context use less.
- Ollama does **not** cap at a set number of tokens. As hardware and model architectures get more efficient, you get more out of your plan over time.
- At 90% of plan limit, Ollama sends an email reminder.
- Requests beyond concurrency limit are **queued** and processed as a slot opens. If the queue is full, the request is rejected.

## Overage / Additional Usage

"Soon. Additional usage at competitive per-token rates, including cache-aware pricing, is coming."

## Tool Calling

"Yes. Cloud models that are trained to support tools are tested for tool calling and with real agent workflows before they go live."

## Throughput

"Speed depends on model size, architecture, and hardware optimization. We target and monitor for low time-to-first-token and high throughput across all cloud models. Priority tiers with faster performance may be available in the future."

## Quantization

Native weights, as released by the model provider. On modern NVIDIA hardware, models may use accelerated data formats supported by Blackwell and Vera Rubin architectures (e.g. NVFP4).

## Privacy

- Hosted primarily in the United States; may route to Europe and Singapore.
- Prompt or response data is **never logged or trained on**.
- Ollama collaborates with NVIDIA Cloud Providers (NCPs) to host open models.
