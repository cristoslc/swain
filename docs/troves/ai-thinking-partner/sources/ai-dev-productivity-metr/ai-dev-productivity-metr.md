---
source-id: "ai-dev-productivity-metr"
title: "Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity"
type: web
url: "https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/"
fetched: 2026-03-29T00:00:00Z
hash: "91836d2fe5298e57fac5e116866966b40823e8135ae159318f8305483b56e1b5"
---

# Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity

**Authors:** Joel Becker, Nate Rush, Elizabeth Barnes, David Rein
**Organization:** METR (non-profit research org)
**Date:** July 10, 2025
**Reading time:** ~20 minutes
**Full paper:** [arXiv:2507.09089](https://arxiv.org/abs/2507.09089)

## Core Finding

In a randomized controlled trial, experienced open-source developers using AI tools took **19% longer** to complete tasks than without AI -- a significant slowdown that contradicts both developer beliefs and expert forecasts.

## Methodology

- **16 experienced developers** from large open-source repositories (averaging 22k+ stars, 1M+ lines of code)
- Developers contributed to these repos for multiple years
- **246 total issues** (bug fixes, features, refactors) -- real work valuable to the repository
- Each issue randomly assigned to allow or disallow AI use
- When AI allowed: any tools of choice (primarily Cursor Pro with Claude 3.5/3.7 Sonnet)
- Average task duration: ~2 hours
- Screen recording for verification
- Compensation: $150/hr

## The Perception Gap

The most striking finding is the disconnect between perception and reality:

| Metric | Value |
|--------|-------|
| Actual effect of AI | 19% slower |
| Developer pre-task forecast | 24% faster with AI |
| Developer post-task belief | 20% faster with AI |

Developers expected AI to speed them up by 24%, and **even after experiencing the slowdown**, they still believed AI had made them 20% faster.

## Factor Analysis

Five factors likely contribute to the slowdown:

1. **High codebase familiarity** -- developers already know these codebases deeply, reducing AI's comparative advantage in exploration
2. **High quality standards** -- PRs must pass code review including style, testing, documentation requirements
3. **Many implicit requirements** -- linting, formatting, documentation norms that take humans time to learn but AI doesn't automatically know
4. **Context switching overhead** -- time spent formulating prompts, reviewing AI output, and correcting mistakes
5. **Overreliance on AI suggestions** -- accepting AI output that requires subsequent correction

## What the Study Does NOT Claim

| Non-claim | Clarification |
|-----------|---------------|
| AI doesn't speed up most developers | Study population is specifically experienced devs on familiar codebases |
| AI doesn't help outside software development | Only software development was studied |
| Future AI won't speed up devs in this setting | Progress is rapid and difficult to predict |
| No way to use existing AI more effectively | Cursor doesn't sample optimally; domain-specific tuning could help |

## Reconciling with Other Evidence

The study presents three hypotheses for reconciling their results with impressive benchmarks and widespread anecdotal reports of AI helpfulness:

### Hypothesis 1: RCT underestimates capabilities
Benchmark results and anecdotes are basically correct; some unknown methodological issue or setting-specific property explains the discrepancy.

### Hypothesis 2: Benchmarks and anecdotes overestimate
RCT results are basically correct; benchmarks overestimate (well-scoped, algorithmically scorable tasks) and anecdotal reports are overoptimistic (now with strong evidence that self-reports of speedup can be very inaccurate).

### Hypothesis 3: Complementary evidence for different settings
All three methodologies are basically correct but measure different subsets of the real task distribution that are more or less challenging for models.

## Key Nuances

- Developers used **frontier models** (Claude 3.5/3.7 Sonnet) -- not outdated tools
- Developers had **dozens to hundreds of hours** of prior LLM prompting experience
- Quality of submitted PRs was **similar** with and without AI
- Slowdown persists across different outcome measures and estimator methodologies
- Cannot rule out learning effects beyond 50 hours of Cursor usage
- Developers may use AI for reasons beyond productivity (enjoyment, investment in future skills)

## Going Forward

METR plans to re-run similar studies to track trends, noting this methodology may be harder to game than benchmarks. If AI substantially speeds up developers in their setting in future, it could signal rapid acceleration of AI R&D progress.

## Relevance to AI as Thinking Partner

This is perhaps the single most important study for calibrating expectations about AI-assisted development:

1. **The productivity paradox is real.** Feeling faster while being slower is documented, not just anecdotal.
2. **Expertise matters in opposite ways.** Deep familiarity with a codebase may reduce AI's value -- AI helps more where the developer knows less.
3. **Self-assessment is unreliable.** Even experienced developers systematically overestimate AI's benefit to their own productivity.
4. **Quality has a cost.** On well-maintained projects with high standards, AI doesn't automatically save time -- it may add overhead.
