---
source-id: "gh-issue-14673-reliability"
title: "Service Reliability Degradation: High Timeout Rates on Ollama Cloud (GitHub #14673)"
type: web
url: "https://github.com/ollama/ollama/issues/14673"
fetched: 2026-03-25T18:00:00Z
hash: "b3e2c2626d1ee98dfec9cfb418bd8f3842d85e2899c9cae72bc161659b22412f"
---

# Service Reliability Degradation: High Timeout Rates on Ollama Cloud

GitHub issue #14673 documenting systematic reliability issues with Ollama Cloud, filed 2026-03-06. Cross-references a separate Reddit report of 29.7% failure rate.

## Incident Timeline

Over a 4-hour window (09:14-13:09 EST, 2026-03-06), multiple agent services experienced systematic timeouts:

- **Scout service**: 3 timeout attempts during inbox checks
- **Ledger service**: Market prep timeout (resolved on retry), plus 3 consecutive Google Search Console timeouts
- **Smith service**: 2 separate timeouts during investigation tasks

## Root Cause

"Ollama Cloud API service overload as root cause of timeouts." Network connectivity to ollama.com confirmed healthy (0% packet loss, 12ms avg RTT).

## Confirmed Failure Modes

1. **29.7% failure rate** on Qwen3.5 models — ongoing for 1+ week at time of filing
2. **API routing errors**: 404s during model switching
3. **Tool calling failures**: 500 errors when tools enabled on cloud models
4. **Rate limiting issues**: $100/month (Max tier) subscribers hitting 4-day throttles after only 5 days of usage

## Community Impact

- A separate Reddit thread documented **3,500+ errors in one session** for a production content moderation workflow
- Support tickets ignored for 2+ weeks
- No incident communication from Ollama team

## Implications for Dispatch Workers

This issue is directly relevant to dispatch worker viability:

- Agent workflows that depend on cloud inference are brittle during capacity events
- No status page or incident communication means dispatch workers cannot implement graceful degradation based on service status
- The 29.7% failure rate on Qwen3.5 specifically is concerning since that model is a primary candidate for dispatch work
- Max tier ($100/month) subscribers still hit throttles, suggesting the tier system does not guarantee throughput

## Ollama Team Response

No documented response in the issue thread. The reporter requested:
1. Acknowledgment of service status
2. Incident timeline
3. ETA for resolution
4. Rate-limiting guidance
5. Qwen3.5 stability clarification

All remained unanswered at time of fetch.
