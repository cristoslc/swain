---
layout: post.njk
title: "Introducing Swain"
description: "A decision-capture system for solo developers working with AI coding agents."
date: 2026-04-07
tags:
  - post
  - introduction
  - swain
---

AI coding agents are fast, stateless, and uncritical. They'll build whatever they're told — or whatever they infer from incomplete context. Left unsupervised, they produce code that passes tests but silently violates architectural constraints, drifts from prior decisions, and accumulates structural debt that no test suite can detect.

Swain solves this by capturing your **decisions** as artifacts in git: what was decided, why, and what constraints apply. When the AI makes decisions, Swain makes those visible too, so you can review and course-correct.

## The core problem

The gap between human decisions and agent execution widens silently over time. Decisions made in week one are forgotten by week twelve. The reasoning behind past choices evaporates when the conversation ends.

You end up re-explaining context that should already be settled. Agents drift because the reasoning isn't there on disk. And you're constantly firefighting instead of steering.

## How Swain works

Swain structures everything around a four-phase loop:

**Intent** → **Execution** → **Evidence** → **Reconciliation**

1. **Intent**: You declare what should be true — specs, ADRs, architectural constraints, component boundaries. These live as markdown files in `docs/`, versioned in git.

2. **Execution**: Agents implement the specs. Swain provides the alignment context (what constraints apply, what decisions govern this work) but doesn't control how agents work internally.

3. **Evidence**: Swain observes what actually happened — git history, test results, dependency graphs, drift reports. Evidence is derived from verifiable sources, not declarations.

4. **Reconciliation**: Swain compares intent against evidence and surfaces divergence. Sometimes execution drifted and needs correction. Sometimes intent was wrong and needs updating.

## What you get

- **Session continuity** — Every session picks up where the last left off. No re-explaining context.
- **Decision preservation** — What was decided lives in artifacts, not conversations or memory.
- **Bounded risk** — Agents run in isolated worktrees. Mistakes have bounded blast radius.
- **Automated integrity** — Once you've made a call, downstream work is checked against that decision automatically.

## Quick start

```bash
npx skills add cristoslc/swain
```

After installing, run `/swain-init` in your first session to set up governance rules and task tracking. Then ask:

```
/swain-roadmap
```

This shows active epics with progress, decisions waiting on you, implementation-ready items, blocked work, tasks, and GitHub issues — all in one view with clickable links.

## Who this is for

**The operator** — a solo developer who makes decisions and delegates implementation to AI coding agents. Swain is your decision-support system: it captures intent, surfaces what needs attention, and preserves the reasoning behind choices. You steer; Swain keeps the record.

**The agent** — any AI coding agent that reads markdown. Swain provides alignment context (acceptance criteria, scope boundaries, constraints, dependency graphs) and verifies outcomes against that context. How the agent works internally is irrelevant. Any agent that reads structured text can participate.

## What's next

Swain is in early development. It's actively used in production by its author, but expect rough edges and shifting APIs. The core pieces are stable:

- **swain-design** — Create and evolve artifacts (Visions, Initiatives, Epics, Specs, ADRs)
- **swain-do** — Turn approved specs into tracked implementation plans with tasks
- **swain-sync** — Fetch, rebase, commit with conventional messages
- **swain-release** — Changelog, version bump, git tag

More coming soon: drift detection, automated reconciliation reports, and better integration with GitHub issues.

---

*Named for the swain in boat**swain**, the officer who keeps the rigging tight.*

[Read the full documentation →](https://github.com/cristoslc/swain)
