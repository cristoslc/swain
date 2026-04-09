---
layout: post.njk
title: "Why Swain Exists"
description: "AI agents ship code fast. Swain ensures they ship what actually matters."
date: 2026-03-08T12:00:00
published: 2026-03-08T12:00:00
series: "Steering the Machine"
seriesOrder: 1
tags:
  - post
  - introduction
  - swain
  - steering-the-machine
---

AI coding agents have a fundamental problem: they're fast, stateless, and uncritical. They'll implement whatever you ask — or whatever they infer from incomplete context — with real credentials and real consequences.

The result isn't immediate failure. It's slower: architectural drift that compounds silently. Decisions made in week one are forgotten by week twelve. Constraints get violated under speed pressure. The reasoning behind past choices evaporates when the conversation ends.

## The core insight

**Artifacts are the single source of truth.** If it's not written down, it wasn't decided.

Swain captures your decisions as markdown files in git: specs, ADRs, architectural constraints, component boundaries. These artifacts become the context that agents read before acting. When agents make decisions, those get captured too — visible for review, versioned for audit.

## The methodology

Swain structures everything around a four-phase loop:

**Intent → Execution → Evidence → Reconciliation**

1. **Intent**: You declare what should be true. Human-authored specs, constraints, goals.
2. **Execution**: Agents implement the intent. Swain provides the context but doesn't control how agents work.
3. **Evidence**: Swain observes what actually happened — git history, test results, dependency graphs. Verifiable, not declared.
4. **Reconciliation**: Swain compares intent against evidence and surfaces divergence. Sometimes execution drifted. Sometimes intent was wrong.

The loop is continuous. Most often you fix the code. Sometimes you fix the decision.

## What this gives you

- **Session continuity** — Every session picks up where the last left off. No re-explaining context.
- **Decision preservation** — What was decided lives in artifacts, not memory.
- **Bounded risk** — Agents run in isolated worktrees. Mistakes have limited blast radius.
- **Automated integrity** — Downstream work is checked against prior decisions automatically.

## Quick start

```bash
npx skills add cristoslc/swain
```

Then run `/swain-init` in your first session and ask:

```
/swain-roadmap
```

This shows active epics, decisions waiting on you, implementation-ready work, blockers, and GitHub issues — all in one view.

## Who this is for

**The operator**: A solo developer who makes decisions and delegates implementation to AI agents. Swain is your decision-support system. You steer; Swain keeps the record.

**The agent**: Any AI that reads markdown. Swain provides alignment context and verifies outcomes. The agent runtime is interchangeable.

## What's next

Swain is in early development — actively used but expect rough edges. The core is stable: design artifacts, task tracking, sync, and releases.

Coming soon: drift detection, automated reconciliation reports, better GitHub integration.

---

*Named for the swain in boat**swain**, the officer who keeps the rigging tight.*

[Read the documentation →](https://github.com/cristoslc/swain)
