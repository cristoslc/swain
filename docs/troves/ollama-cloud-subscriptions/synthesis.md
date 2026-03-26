# Synthesis: Ollama Cloud Subscription Tiers and Throughput

## Key Findings

### Tier structure is clear; limits are deliberately opaque

Ollama Cloud offers three tiers: Free ($0), Pro ($20/month or $200/year), and Max ($100/month). The pricing is straightforward. What is not straightforward is what you actually get. Usage is measured in **GPU time** rather than token counts or request quotas. Ollama explicitly designs plans around "use case intensity rather than hard token caps" -- confirmed both on the pricing page and via direct support email. (ollama-pricing-page, reddit-cloud-token-limitations)

The only quantitative multipliers published are:
- **Pro**: 50x more usage than Free
- **Max**: 5x more usage than Pro (250x Free)

But since the base unit (Free tier's actual capacity) is undefined, these multipliers are relative to an unknown quantity.

### Concurrency is the one hard number that matters for dispatch workers

The only concrete, published limit is concurrent cloud model slots:

| Plan | Concurrent Models | Monthly Cost |
|------|-------------------|--------------|
| Free | 1 | $0 |
| Pro | 3 | $20 |
| Max | 10 | $100 |

For dispatch workers running parallel agent sessions, **this is the binding constraint**. A single Pro subscription supports 3 simultaneous cloud model requests; Max supports 10. Requests beyond the limit are queued, and if the queue fills, they are rejected. (ollama-pricing-page)

### Session and weekly limits create unpredictable throttling

All plans have **session limits that reset every 5 hours** and **weekly limits that reset every 7 days**. At 90% of the plan limit, Ollama sends an email notification. Community reports indicate:

- Free tier: ~3M tokens/day, ~6M tokens/week (one estimate), or roughly 1-2 hours of coding per day before hitting limits
- Pro tier: One user reported "only 20 premium model requests per month" (possibly model-specific for larger models like Gemini 3 Pro Preview)
- Max tier ($100/month): A user reported usage filling up during professional work and couldn't find exact caps
- Weekly limit: One user was "locked at 97.6% for my weekly usage... been waiting on a cool down period well over 26 hours of no use and still at 97.6%"

(reddit-cloud-pro-usage-limits, reddit-cloud-token-limitations)

### Throughput performance is adequate but not competitive

From the `ollama-cloud-dispatch-workers` trove: shared inference delivers 42-95 tok/s; dedicated A100 endpoints reach 210 tok/s. The official pricing page says only that they "target and monitor for low time-to-first-token and high throughput" and that "priority tiers with faster performance may be available in the future." Crucially, **no tier currently guarantees higher throughput than another** -- all tiers share the same inference pool. (ollama-pricing-page, checkthat-ollama-pricing-2026)

### Reliability is a serious concern for production dispatch

A March 2026 incident documented **29.7% failure rate** on Qwen3.5 models lasting over a week, with 500 errors on tool-calling requests and 3,500+ errors in a single production session. Max tier subscribers still hit throttling after 5 days of usage. There is no status page, no incident communication, and support tickets went unanswered for 2+ weeks. (gh-issue-14673-reliability)

### The Max tier is specifically positioned for agent workloads

Ollama's own marketing positions Max for "continuous agent tasks, multiple concurrent agents, large models over extended sessions." The Efficienist coverage confirms Max is "aimed at heavier sustained usage like coding agents and batch processing." This is the right tier for dispatch workers, but the lack of published limits means you cannot predict when you'll be throttled. (ollama-pricing-page, efficienist-pro-annual-billing)

## Points of Agreement

All sources confirm:
- Three tiers: Free / Pro ($20) / Max ($100)
- GPU-time-based usage measurement, not token counts
- Session limits (5h reset) and weekly limits (7d reset)
- No published numeric quotas for any tier
- Local model execution remains free and unlimited regardless of cloud tier
- Concurrency: 1 / 3 / 10 models across tiers

## Points of Disagreement

- **Pro multiplier**: The pricing page says "50x more than Free"; older docs and community reports cite "20X+" -- the number may have changed or the older figure referred to a different metric
- **Production viability**: CheckThat's TCO analysis treats the $20-100/month tiers as cost-competitive with commercial APIs at scale; community reports say limits are hit too quickly for sustained production use
- **Structured output support**: One user claims cloud models don't support structured outputs "even if the actual model does"; Ollama's pricing FAQ says tool calling is tested and supported -- these may refer to different capabilities (structured outputs vs tool calling)

## Gaps

- **No published rate limits**: The single biggest gap. Without knowing what "50x Free" means in absolute terms (tokens, requests, GPU-seconds), dispatch worker capacity planning is impossible
- **No SLA**: No uptime guarantee, no response time commitment, no incident communication channel
- **No per-tier throughput differentiation**: All tiers share the same inference infrastructure at the same speed; paying more buys capacity (concurrency + GPU time budget) but not performance
- **No overage pricing yet**: "Additional usage at competitive per-token rates, including cache-aware pricing, is coming" -- but not available today; hitting the limit means waiting for reset
- **No status page**: Dispatch workers cannot implement graceful degradation based on service health
- **Premium model allocation unclear**: "Premium model requests" are separate from general cloud usage but the allocation per tier is not documented

## Cross-Reference: ollama-cloud-dispatch-workers Trove

The companion trove covers API compatibility, tool calling reliability, and model quality. Combined findings for SPIKE-045:

1. **Authentication**: Simple bearer token -- viable for headless dispatch (dispatch-workers trove)
2. **Tool calling**: Works for qwen3.5 and glm-5 but is fragile and model-dependent (dispatch-workers trove)
3. **Pricing**: $20/month Pro gives 3 concurrent slots; $100/month Max gives 10 (this trove)
4. **Throughput**: 42-95 tok/s shared, no tier differentiation (both troves)
5. **Reliability**: 29.7% failure rate incident, no SLA, no status page (this trove)
6. **Limits**: Opaque GPU-time-based, session/weekly resets, no published numbers (this trove)

**Bottom line for dispatch workers**: The Max tier's 10 concurrent model slots and "heavy, sustained usage" positioning makes it the right choice on paper. But the absence of published limits, lack of SLA, and documented reliability incidents mean dispatch workers need local-model fallback and aggressive retry logic to be viable in production.
