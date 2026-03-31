---
source-id: "service-level-objectives"
title: "Service Level Objectives"
type: web
url: "https://sre.google/sre-book/service-level-objectives/"
fetched: 2026-03-29T00:00:00Z
hash: "f417ec909501c84ee83b6c9ae040bee834be319af3672068ac8e49f4e8d10745"
---

# Service Level Objectives

**Authors:** Chris Jones, John Wilkes, Niall Murphy, Cody Smith (writers), Betsy Beyer (editor)
**Source:** Google SRE Book, Chapter 4
**License:** CC BY-NC-ND 4.0
**Capability:** Cap 4 -- Think in Production

## Content

It's impossible to manage a service correctly without understanding which behaviors really matter and how to measure and evaluate those behaviors. SLIs, SLOs, and SLAs define basic properties of metrics that matter, target values, and consequences of meeting or missing them.

### Service Level Terminology

**SLI (Service Level Indicator)**: A carefully defined quantitative measure of some aspect of the level of service provided. Common SLIs include request latency, error rate, system throughput, and availability. Measurements are often aggregated into rates, averages, or percentiles.

**SLO (Service Level Objective)**: A target value or range of values for a service level measured by an SLI. Structure: SLI <= target, or lower bound <= SLI <= upper bound. Example: "99% of Get RPC calls will complete in less than 100 ms."

**SLA (Service Level Agreement)**: An explicit or implicit contract with users that includes consequences of meeting or missing the SLOs. If there is no explicit consequence, you're almost certainly looking at an SLO, not an SLA.

### Indicators in Practice

Services fall into broad categories:
- **User-facing serving**: availability, latency, throughput
- **Storage systems**: latency, availability, durability
- **Big data systems**: throughput, end-to-end latency
- **All systems**: correctness

### Aggregation

Most metrics are better thought of as distributions rather than averages. Using percentiles allows considering the shape of the distribution. The 99th percentile shows plausible worst-case values while the 50th shows typical experience.

### Objectives in Practice

**Start from user needs, not from what's easy to measure.** Working backward from desired objectives to specific indicators works better than choosing indicators then coming up with targets.

Key guidance for choosing targets:
- **Don't pick a target based on current performance** -- may lock you into heroic efforts
- **Keep it simple** -- complicated aggregations obscure changes
- **Avoid absolutes** -- "always available" is unrealistic and expensive
- **Have as few SLOs as possible** -- just enough for good coverage
- **Perfection can wait** -- start loose, tighten over time

### SLOs as Control Loops

1. Monitor and measure SLIs
2. Compare SLIs to SLOs, decide if action is needed
3. If action needed, figure out what to do
4. Take that action

Without the SLO, you wouldn't know whether or when to take action.

### Setting Expectations

- **Keep a safety margin**: Use a tighter internal SLO than what's advertised
- **Don't overachieve**: Users build on actual performance, not stated SLOs. Chubby introduced planned outages to prevent over-dependence.

### The Chubby Planned Outage

Google's Chubby lock service was so reliable that service owners added dependencies assuming it would never go down. SRE now ensures Chubby meets but does not significantly exceed its SLO. If no true failure occurs in a quarter, a controlled outage is synthesized. This flushes out unreasonable dependencies shortly after they're added.

### Error Budgets

It's unrealistic to insist SLOs are met 100% of the time. An error budget -- a rate at which SLOs can be missed -- is tracked daily or weekly. The SLO violation rate compared against the error budget informs deployment decisions.

## Relevance to Intent-Evidence Loop

SLOs are the canonical example of **Intent encoded as measurable specifications**. SLIs provide the **Evidence** (measured behavior). The SLO control loop (measure -> compare -> decide -> act) IS the Intent-Evidence-Reconciliation loop applied to production systems.

The Chubby planned outage story illustrates a profound reconciliation insight: when evidence consistently shows the system exceeds its intent (overperformance), that itself is a problem because it creates invisible coupling. Reconciliation must detect both under-delivery AND over-delivery relative to intent.

Error budgets formalize the reconciliation threshold -- how much divergence between intent and evidence is acceptable before action is required.
