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

## Post 2: Specs Steer Humans. Tests Constrain Agents. (draft, revised)

Framed as hypothesis + research-adjusted plan. Opens with the initial thesis (TDD constrains agents, fitness functions are the missing layer) grounded in the VISION-006 experience. Then introduces the survey of 20 testing practices and three changes the research prompted: (1) verification and exploration are different practices — the loop gains an exploration phase, (2) BDD traceability overhead exceeds its value for a solo developer — simplify from 7 specs to 3, (3) the loop needs adaptive convergence tracking, not a fixed failure limit. Cuts BDD traceability to three specs. Adds the verification/exploration split from Marick's testing quadrants. Ends at "the testing vocabulary is larger than I assumed, and the vocabulary changes what to build."

Key structural requirement: the opening must name the hypothesis and VISION-006 evidence, then the research survey adjusts the plan — the correction comes from the methodology survey, not just from more experience.

## Post 3: Problem Space, Solution Space, Intent Space (planned)

The synthesis. Three-space model:
- Problem space — what users need (behavioral tests, user journeys, exploratory testing).
- Solution space — what we built (unit tests, integration tests, contract tests).
- Intent space — what we decided to build and why (specs, ADRs, architecture docs, fitness functions).

When a test fails, which space drifted? This reframes the argument: it's not artifacts-vs-tests, it's that different test types illuminate different spaces. Contract testing (from the trove research) illuminates the drift between spec and implementation — consumers and providers drift, just like intent and solution drift. The `[contracts-with]` relationship type makes this trackable.

Rehabilitates specs. Post 1 oversold them. Post 2 nearly discarded them. Post 3 puts them in their proper role: intent-space documentation that humans need but agents can't follow. The test suite translates intent into enforceable constraints. Different test types illuminate different kinds of drift.

## Post 4: The Minimum Viable Test Suite (planned)

The practical post — the one a reader can act on. Uses Justin Searls' criterion (endorsed by Martin Fowler) as the organizing principle: write tests that "establish clear boundaries, run quickly and reliably, and only fail for useful reasons." Then uses mutation testing as the quality metric — not "what percentage of code is covered" but "what percentage of introduced bugs does the suite catch."

Grounds the series in something actionable. Posts 1-3 are conceptual; Post 4 is "here's what to actually write first." Uses the trove's testing-quadrants framework to organize the minimum viable suite: behavioral tests (unit, integration) for solution-space, fitness functions for intent-space, and charter-based exploration sessions for problem-space.

## Post 5: Evidence-First Spec Generation (planned)

The most speculative idea. Can specs be auto-generated from code + tests, then corrected by the operator? This inverts the loop from Post 1: instead of Intent → Execution → Evidence, it's Evidence → Intent → Reconciliation.

The trove research makes this more concrete than the original outline suggested. Reconciliation doesn't just correct existing intent against evidence — it also generates new intent when exploration discovers problems no spec covers (the "discovery" severity from the trove recommendations). The loop already runs in both directions: intent specifies what should be true, evidence reveals what is true, and exploration reveals what nobody thought to specify. Evidence-first generation is the loop running backwards, not replacing the forward direction.

Frame as an experiment, not a conclusion. The riskiest post — it might be wrong.

## Editorial notes

- Post 2 must not discard Post 1 entirely. A single sentence — "Specs still matter for human thinking; they just can't steer agents" — prevents the reader from over-correcting.
- Minimize swain jargon. Use swain as the case study but translate internal references for a general audience.
- Bold sparingly. Reserve for 2-3 moments per post where the skimmer should stop.
- Inline links sparingly. Use endnotes/references section for internal retro links.
- Each post should stand alone while rewarding sequential reading.
