---
title: "Introducing Swain"
description: "A decision-capture system for solo developers working with AI coding agents."
date: 2026-04-07
tags:
  - post
  - introduction
  - swain
---

## The problem

AI coding agents are fast, stateless, and uncritical. They build whatever they're told — or whatever they infer from incomplete context. They operate with real credentials, real filesystem access, and real consequences.

Left unsupervised, agents produce code that passes tests but silently violates architectural constraints, drifts from prior decisions, and accumulates structural debt that no test suite can detect. Left uncontained, a confused or compromised agent can cause damage far beyond its intended scope.

The gap between human decisions and agent execution widens silently over time. Decisions made in week one are forgotten by week twelve. The reasoning behind past choices evaporates when the conversation ends.

## What swain does

Swain captures the operator's decisions as artifacts in git: what was decided and why. When the AI makes decisions, swain makes those visible too, so you can review and course-correct.

You bring judgment and vision. The AI brings throughput and execution.

The result is a project that maintains **intent**, not just one that accumulates code. The AI doesn't drift because the reasoning is right there on disk — and swain actively protects it.

## The alignment loop

Swain's architecture rests on a four-phase loop:

**Intent** — What has been decided. Specs, ADRs, architectural constraints, component boundaries, goals. Human-authored declarations of what should be true.

**Execution** — Where intent meets reality. Agents implementing specs, building features, running migrations. Swain provides the alignment context (what constraints apply, what decisions govern this work) and verifies outcomes.

**Evidence** — What can be observed. Git history, test results, dependency graphs, drift reports, agent session outputs. Evidence is derived from verifiable sources, not from declarations.

**Reconciliation** — The structured comparison of intent against evidence. Drift reports, retrospectives, ADR compliance checks. Reconciliation surfaces divergence so the operator can decide what to do about it.

The loop is continuous. Most often, execution has drifted from intent and needs correction. But sometimes the drift reveals that intent was wrong — a boundary that agents repeatedly violate may be poorly drawn, a constraint that every implementation works around may be outdated.

## Foundational principles

**Artifacts are the single source of truth.** What was decided lives in artifacts — not in conversations, not in memory. If it's not in an artifact, it wasn't decided.

**Git is the persistence layer.** Swain does not maintain its own database. Everything is markdown files in a git repository. Version history, blame, and diff are the audit trail.

**Agents are black boxes.** Swain provides inputs (intent, context, constraints) and verifies outputs (evidence, compliance, completion). The agent runtime is interchangeable.

**Intent and evidence are separate things.** Source code tells you what exists; intent declares what should exist. These must not be collapsed.

**Intent is malleable.** Decisions are hypotheses, not commandments. When evidence repeatedly contradicts intent, that's a signal. Reconciliation doesn't just enforce intent — it challenges it.

## What a session looks like

Two skills auto-run at the start of every session:

1. **swain-doctor** checks project health and repairs what it finds
2. **swain-init** restores your context, proposes a focus lane, and generates a session roadmap

Then you ask what's going on:

```
/swain-roadmap
```

This shows active epics with progress, decisions waiting on you, implementation-ready items, blocked work, tasks, and GitHub issues — all in one view with clickable links.

From there, the core loop is:

- **Design** (`/swain-design`) — create and evolve artifacts: Visions, Initiatives, Epics, Specs, Spikes, ADRs, Personas, Runbooks, Journeys, and Designs
- **Execute** (`/swain-do`) — turn approved specs into tracked implementation plans with tasks and dependencies
- **Ship** (`/swain-sync`, `/swain-release`) — fetch, rebase, commit with conventional messages, cut versioned releases

Artifacts are markdown files in `docs/`. Phases are subdirectories. Transitions are commits. Everything is inspectable, diffable, and version-controlled.

## Install

```bash
npx skills add cristoslc/swain
```

The installer detects which agent platforms you have (Claude Code, Cursor, Codex, etc.) and installs skills only for those platforms. Built on the [skills standard](https://github.com/anthropics/skills).

After installing, run `/swain-init` in your first session to set up governance rules and task tracking.

## Who this is for

**The operator** — a solo developer who makes decisions and delegates implementation to AI coding agents. Swain is the operator's decision-support system: it captures intent, surfaces what needs attention, and preserves the reasoning behind choices. The operator steers; swain keeps the record.

**The agent** — any AI coding agent that reads markdown. Swain provides alignment context (acceptance criteria, scope boundaries, constraints, dependency graphs) and verifies outcomes against that context. How the agent works internally is irrelevant. Any agent that reads structured text can participate.

## What swain is not

- **Not a team tool.** Solo operator with AI agents. Team coordination is a different problem.
- **Not an agent runtime.** Alignment and verification, not execution. Swain works with any agent that reads markdown.
- **Not a replacement for git.** Git is the foundation. Swain is an opinionated layer on top of it.
- **Not prescriptive about agent choice.** Swap runtimes freely. Swain doesn't care which agent you use.

---

*Named for the swain in boat**swain**, the officer who keeps the rigging tight.*
