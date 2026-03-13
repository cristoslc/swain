---
title: "Background Agent Invocation Via GitHub"
artifact: SPIKE-016
status: Planned
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
question: "How can swain invoke Claude Code (or other agents) to work on tasks in the background via GitHub Issues, and what are the mechanics of @claude mentions, webhooks, or API triggers?"
gate: Pre-EPIC-010-specs
risks-addressed:
  - Building a dispatch system without understanding the invocation mechanics
  - Assuming @claude works a certain way without testing
depends-on: []
linked-artifacts:
  - EPIC-010
evidence-pool: ""
---

# Background Agent Invocation Via GitHub

## Question

How can swain invoke Claude Code (or other agents) to work on tasks in the background via GitHub Issues, and what are the mechanics of `@claude` mentions, webhooks, or API triggers?

## Go / No-Go Criteria

- **GO:** A reliable mechanism exists to trigger agent work via GitHub Issues with predictable behavior (agent picks up the issue, works on it, posts results)
- **NO-GO:** No reliable invocation mechanism exists or the latency/reliability is too poor for practical use

## Pivot Recommendation

If GitHub-native invocation is unreliable, explore alternative dispatch surfaces:
- GitHub Actions with Claude API calls
- Direct Claude Code CLI invocation via SSH to a dev machine
- Queue-based dispatch (e.g., a watched directory or webhook endpoint)

## Findings

(Populated during Active phase)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-13 | 6a5e1ac | Initial creation |
