---
title: "Steering the Machine — Series Outline"
description: "Editorial outline for the 5-post blog series on aligning AI agents through testing."
eleventyExcludeFromCollections: true
permalink: false
---

# Steering the Machine

A blog series on what it takes to keep AI agents aligned with your intent. Written from experience building swain — 730+ commits, 14 days, four models, sixteen skills.

## Arc

| # | Post | Stance | Register | Status |
|---|------|--------|----------|--------|
| 1 | Why Swain Exists | Artifacts are the answer | Confident, clean | Published 2026-03-08 |
| 2 | Specs Steer Humans. Tests Constrain Agents. | Artifacts failed; tests worked | Battle-scarred, honest | Draft, target 2026-04-08 |
| 3 | Problem Space, Solution Space, Intent Space | Both matter, in different roles | Synthetic, mature | Planned |
| 4 | The Minimum Viable Test Suite | Here's what to build first | Practical, grounded | Planned |
| 5 | Evidence-First Spec Generation | What if we invert the loop? | Speculative, open | Planned |

The arc moves from naive optimism → hard-won correction → synthesis → practical guidance → open speculation. It mirrors the reader's likely journey: they start thinking artifacts are enough, realize they're not, want a framework, then want to know what to do.

## Post 1: Why Swain Exists (published)

The "before" picture. Introduces the Intent → Execution → Evidence → Reconciliation loop. Claims artifacts are the single source of truth. Serves retroactively as the setup for the correction in Post 2.

## Post 2: Specs Steer Humans. Tests Constrain Agents. (draft)

The correction. Acknowledges the Intent → Execution → Evidence → Reconciliation loop from Post 1 is correct, but swain v1 over-invested in Intent (artifact hierarchy) and under-invested in Evidence and Reconciliation (tests, automated drift detection). 730 commits later, specs were written then ignored, hierarchy created ceremony debt, reconciliation stayed manual. VISION-006 is the case study: three architectural pivots in one session, TDD rescued it. Ends at "the fitness functions are missing." Experience report, not a roadmap.

Key structural requirement: the opening must name Post 1's thesis, affirm the loop, and identify the imbalance.

## Post 3: Problem Space, Solution Space, Intent Space (planned)

The synthesis. Three-space model:
- Problem space — what users need (behavioral tests, user journeys).
- Solution space — what we built (unit tests, integration tests).
- Intent space — what we decided to build and why (specs, ADRs, architecture docs).

When a test fails, which space drifted? This reframes the argument: it's not artifacts-vs-tests, it's that different artifacts serve different spaces, and tests keep the spaces aligned.

Rehabilitates specs. Post 1 oversold them. Post 2 nearly discarded them. Post 3 puts them in their proper role: intent-space documentation that humans need but agents can't follow. The test suite translates intent into enforceable constraints.

## Post 4: The Minimum Viable Test Suite (planned)

The practical post — the one a reader can act on. Unit tests are cheap. Integration tests are medium. Fitness functions are expensive. Where's the inflection point? What's the smallest suite that keeps drift bounded on a real project?

Grounds the series in something actionable. Posts 1-3 are conceptual; Post 4 is "here's what to actually write first."

## Post 5: Evidence-First Spec Generation (planned)

The most speculative idea. Can specs be auto-generated from code + tests, then corrected by the operator? This inverts the loop from Post 1: instead of Intent → Execution → Evidence, it's Evidence → Intent → Reconciliation.

Frame as an experiment, not a conclusion. The riskiest post — it might be wrong.

## Editorial notes

- Post 2 must not discard Post 1 entirely. A single sentence — "Specs still matter for human thinking; they just can't steer agents" — prevents the reader from over-correcting.
- Minimize swain jargon. Use swain as the case study but translate internal references for a general audience.
- Bold sparingly. Reserve for 2-3 moments per post where the skimmer should stop.
- Inline links sparingly. Use endnotes/references section for internal retro links.
- Each post should stand alone while rewarding sequential reading.
