---
source-id: observability-driven-testing
trove: testing-practices-beyond-unit
type: web-article
title: "Observability-Driven Testing: Using Production Telemetry to Drive Test Selection"
author: "Charity Majors; Liz Fong-Jones; George Miranda; Rouan Wilsenach; Martin Fowler"
fetched: 2026-04-20
freshness-ttl: 365
url: "https://www.honeycomb.io/blog/observability-driven-development"
tags: [observability, production-testing, telemetry, logs-metrics-traces, qa-in-production, honeycomb, instrumentation, o11y]
---

# Observability-Driven Testing: Using Production Telemetry to Drive Test Selection

## What Observability-Driven Testing Is

Observability-driven testing (ODT) is the practice of using production telemetry — logs, metrics, and traces — to decide what to test, how to test it, and whether what you tested is working. It inverts the traditional model. Instead of writing tests in advance of production behavior, you observe production behavior first, then write tests that codify what you learned.

This is not testing in production. It is testing *from* production. The difference matters. Testing in production means running your test suite against live users. Testing from production means using production data to understand what tests you need, what assertions matter, and what failure modes actually occur.

## The Three Pillars

Charity Majors, Liz Fong-Jones, and George Miranda's *Observability Engineering* (O'Reilly, 2022) defines three pillars of observability:

1. **Logs** — structured event records that capture discrete occurrences. A log entry tells you what happened at a specific moment: a request failed, a cache expired, a user clicked a button. Logs are the raw material for understanding individual events.

2. **Metrics** — numeric measurements aggregated over time. A metric tells you how often something happens, how long it takes, or how much resource it consumes. Metrics are the raw material for understanding trends and setting thresholds.

3. **Traces** — causal chains that connect events across service boundaries. A trace tells you the full journey of a request through a distributed system. Traces are the raw material for understanding latency, bottlenecks, and cross-service failures.

ODT uses all three. Logs tell you what broke. Metrics tell you how often. Traces tell you why. Test selection starts from the traces, narrows with logs, and prioritizes with metrics.

## QA in Production

Rouan Wilsenach's "QA in Production" article on martinfowler.com (2020) makes the argument that production is the only environment that matches production. Staging, canary, and integration test environments approximate production, but they differ in data, traffic, configuration, and timing. Tests that pass in staging may fail in production. Tests that fail in staging may have been testing the wrong thing.

Wilsenach's key insight: QA in production does not mean running automated test suites against live users. It means:

- **Monitoring real user behavior** to discover defects you did not anticipate.
- **Synthetic monitoring** (see Martin Fowler's "Synthetic Monitoring" bliki, 2020) to exercise known critical paths at regular intervals. Synthetic monitoring is a production test: it asserts that the health check returns 200, that the login flow completes in under 2 seconds, that the checkout process succeeds end-to-end.
- **Observability-driven assertions** that codify production invariants. If "95th percentile checkout latency is under 500ms" has been true for the last 30 days, that invariant becomes a production test. When it breaks, you know something changed before any user reports it.

This reframes the question from "did our tests pass?" to "is our system behaving correctly right now?" The latter is strictly more useful because it accounts for configuration drift, data shape changes, dependency failures, and traffic patterns that no test environment replicates.

## The Observability-Resilience Loop

ODT forms a loop with resilience engineering:

1. **Observe.** Instrument everything. Collect logs, metrics, and traces at high cardinality and high dimensionality. Honeycomb's approach (high-cardinality events with arbitrary key-value attributes) is the reference model.
2. **Detect.** Set alerts on production invariants — not on infrastructure thresholds. An alert on "CPU above 80%" tells you something is busy. An alert on "checkout latency above 500ms" tells you something is wrong.
3. **Diagnose.** Use traces to find the root cause. Logs confirm the diagnosis. Metrics quantify the blast radius.
4. **Codify.** Write a test that would have caught the defect before it reached production. This test is derived from production behavior, not from speculation about what might break.
5. **Validate.** Run the new test in CI. If it passes in CI and the production invariant is still healthy, the loop closes. If the test proves insufficient (the defect recurs in production despite the CI test), go back to step 1 with better instrumentation.

This loop is where ODT gets its name. Observability drives test selection. Test selection drives CI coverage. CI coverage catches regressions before production. Production observability catches what CI missed. The loop tightens over time.

## Martin Fowler's Synthetic Monitoring Bliki

Fowler's bliki entry on synthetic monitoring (2020) describes the practice of running automated transactions against a production system at regular intervals. These are not unit tests. They are not integration tests. They are production tests that assert behavioral invariants:

- The health endpoint returns 200.
- The login flow completes within 2 seconds.
- The search results page contains results.

Synthetic monitoring is a subset of ODT. It tests known paths at known intervals. It does not discover unknown paths or unknown failures. For that, you need real-user observability.

But synthetic monitoring has an advantage over real-user monitoring: it runs even when no real users are active. At 3 AM on a Sunday, synthetic monitoring tells you the system is healthy. Real-user monitoring tells you nothing because no one is using it. Synthetic monitoring is the canary for production invariants.

## Relationship to Other Practices

- **Dogfooding** (see companion source) generates real-user traffic that ODT consumes. Without users generating traffic, there is less telemetry to observe. Dogfooding and ODT are synergistic: dogfooding provides the traffic, ODT provides the instrumentation and analysis.
- **Compliance testing** (see companion source) verifies policies. ODT can verify that policies are being followed in production — for example, that PII is not leaking into logs, that S3 buckets are not publicly accessible. Policy compliance in production is a production invariant, observable and testable.
- **Testing quadrants** (see companion source) place ODT in Q3 (business-facing, critiquing team) and Q4 (technology-facing, critiquing team). Synthetic monitoring is Q3 (it tests user-facing behavior). Trace-based testing is Q4 (it tests system properties like latency and error rates).
- **Shift-left testing** (see companion source) moves testing earlier. ODT moves some testing later — into production — but uses production data to inform earlier testing. They are not in tension. Shift-left prevents predictable failures. ODT catches unpredictable ones.

## Practical Takeaways

1. **Instrument before you test.** You cannot observe what you do not instrument. Add structured logging, metrics, and traces before writing tests. The instrumentation tells you what tests to write.
2. **Codify production invariants as assertions.** If "checkout latency under 500ms" has been true for 30 days, it is a test. Encode it in synthetic monitoring. Alert when it breaks.
3. **Use traces for root cause, logs for confirmation, metrics for prioritization.** Each pillar has a distinct role in the ODT loop.
4. **Close the loop.** Every production failure should produce a CI test. If it does not, the loop is open and the same failure will recur.
5. **Prefer high-cardinality observability over threshold alerting.** Thresholds on CPU, memory, and disk are weak proxies for user impact. Observability on request latency, error rates, and user-visible behavior is direct. Alert on what users experience, not what servers consume.