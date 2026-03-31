---
source-id: "monitoring-distributed-systems"
title: "Monitoring Distributed Systems"
type: web
url: "https://sre.google/sre-book/monitoring-distributed-systems/"
fetched: 2026-03-29T00:00:00Z
hash: "2d88037b5c7cc04692057881637cb14e094bde1290efa2764f9280f02aa2e1b2"
---

# Monitoring Distributed Systems

**Authors:** Rob Ewaschuk (writer), Betsy Beyer (editor)
**Source:** Google SRE Book, Chapter 6
**License:** CC BY-NC-ND 4.0
**Capability:** Cap 4 -- Think in Production

## Content

Google's SRE teams have basic principles and best practices for building successful monitoring and alerting systems. This chapter offers guidelines for what issues should interrupt a human via a page, and how to deal with issues that aren't serious enough to trigger a page.

### Definitions

- **Monitoring**: Collecting, processing, aggregating, and displaying real-time quantitative data about a system
- **White-box monitoring**: Based on metrics exposed by system internals (logs, profiling interfaces, internal statistics)
- **Black-box monitoring**: Testing externally visible behavior as a user would see it
- **Dashboard**: A web application providing a summary view of a service's core metrics
- **Alert**: A notification pushed to a human -- classified as tickets, email alerts, or pages
- **Root cause**: A defect that, if repaired, instills confidence the event won't recur in the same way

### Why Monitor?

- **Analyzing long-term trends**: How big is my database and how fast is it growing?
- **Comparing over time or experiment groups**: Are queries faster with the new configuration?
- **Alerting**: Something is broken and somebody needs to fix it right now
- **Building dashboards**: Answer basic questions about your service using the four golden signals
- **Retrospective analysis (debugging)**: Our latency just shot up; what else happened?

### Symptoms Versus Causes

The monitoring system should address two questions: what's broken, and why? "What's broken" is the symptom; "why" is the cause. Writing good monitoring with maximum signal and minimum noise requires maintaining this distinction.

### Black-Box Versus White-Box

- Black-box monitoring is symptom-oriented and represents active problems
- White-box monitoring allows detection of imminent problems, failures masked by retries, etc.
- For paging: black-box forces discipline to only alert when problems are both ongoing and producing real symptoms
- For debugging: white-box is essential

### The Four Golden Signals

If you can only measure four metrics of your user-facing system, focus on these:

1. **Latency**: Time to service a request. Distinguish between successful and failed request latency.
2. **Traffic**: How much demand is placed on the system (e.g., HTTP requests/second)
3. **Errors**: Rate of requests that fail -- explicitly, implicitly, or by policy
4. **Saturation**: How "full" your service is, emphasizing the most constrained resources

### Choosing Appropriate Resolution

Different aspects need different granularity. Per-second CPU measurements may be expensive but reveal spikes. Per-minute probing may suffice for availability monitoring. Balance cost against insight.

### As Simple as Possible, No Simpler

- Rules that catch real incidents should be simple, predictable, and reliable
- Data collection rarely exercised should be candidates for removal
- Signals collected but never exposed in dashboards or alerts are candidates for removal
- Keep the critical path (problem onset -> page -> triage -> debugging) simple and comprehensible

### Tying Principles Together

Questions for evaluating alerts:
- Does this rule detect an otherwise undetected condition that is urgent, actionable, and user-visible?
- Will I ever be able to ignore this alert?
- Does this alert definitely indicate users are being negatively affected?
- Can I take action in response? Is the action urgent?
- Are other people getting paged for this issue?

Philosophy on pages:
- Every page should require a sense of urgency
- Every page should be actionable
- Every page response should require intelligence
- Pages should be about novel problems

### Monitoring for the Long Term

- Decisions about monitoring should be made with long-term goals in mind
- Taking a controlled, short-term decrease in availability is often a strategic trade for long-run stability
- Pages with rote, algorithmic responses should be a red flag -- automate them

### Bigtable Case Study

The Bigtable team was over-alerting based on mean performance SLOs. They used a three-pronged approach: improved performance, temporarily relaxed SLO targets (using 75th percentile), and disabled email alerts. This breathing room allowed fixing long-term problems instead of constantly fighting tactical fires.

### Gmail Case Study

Early Gmail monitoring fired alerts when individual tasks were de-scheduled. With thousands of tasks, this was unmaintainable. The team built a tool to "poke" the scheduler, but debated whether to fully automate the workaround vs. waiting for a proper fix. This tension between short-term patches and long-term fixes is common.

## Relevance to Intent-Evidence Loop

This chapter is the definitive guide to the **Evidence** phase of the loop when applied to production systems. The four golden signals provide a concrete framework for what evidence to collect. The symptoms-vs-causes distinction maps directly to the difference between evidence (what's observable) and reconciliation (comparing evidence against intent to find root causes).

The Bigtable case study illustrates how reconciliation (comparing SLO intent against monitoring evidence) can reveal that the intent itself needs revision -- a key feedback loop.
