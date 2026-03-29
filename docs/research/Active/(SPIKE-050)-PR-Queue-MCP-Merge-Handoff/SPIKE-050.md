---
title: "PR Queue MCP for Merge Handoff"
artifact: SPIKE-050
track: container
status: Active
author: cristos
created: 2026-03-27
last-updated: 2026-03-27
question: "Can we build an MCP server that swain-sync leverages to merge completed work to trunk via a PR queue, enabling in-process agents to hand off merge+retro without blocking?"
gate: Pre-MVP
parent-initiative: INITIATIVE-013
risks-addressed:
  - Agent sessions blocked waiting for merge/review
  - Retro steps skipped when agents rush to complete
  - No structured handoff point between agent work and trunk integration
---

# PR Queue MCP for Merge Handoff

## Summary

<!-- Final-pass section: populated when transitioning to Complete. -->

## Question

Can we build an MCP server that swain-sync leverages to merge completed work to trunk via a PR queue, enabling in-process agents to hand off merge+retro without blocking?

Today when an agent finishes work in a worktree, swain-sync handles the commit+push, but the merge-to-trunk step is either manual or done inline by the same agent session. This creates two problems:
1. The agent blocks on merge (CI checks, conflicts, review) when it could move to the next task
2. Post-merge steps (swain-retro, bookmark update, worktree cleanup) are often skipped because the agent is already context-switching

The ideal flow: agent completes work → calls MCP to enqueue a merge → MCP handles PR creation, merge, retro trigger, and worktree cleanup asynchronously. The agent gets back a queue receipt and moves on.

## Go / No-Go Criteria

- **Go**: A working MCP prototype that can (a) accept a merge request from an agent via tool call, (b) create a PR, (c) merge on green CI (or immediately if no CI), and (d) trigger swain-retro post-merge. Round-trip from agent enqueue to merge must be < 5 minutes for a clean fast-forward.
- **No-Go**: If GitHub API rate limits, MCP server lifecycle management, or process isolation make the queue unreliable for a solo developer workflow (>20% failure rate on happy path).

## Pivot Recommendation

If a full MCP is too heavy, build a lightweight `swain-merge-queue.sh` daemon that runs in a tmux pane (managed by swain-stage), watches a local queue file, and processes merges sequentially. The agent writes to the queue file instead of calling an MCP tool. Loses the structured tool-call interface but keeps the async handoff benefit.

## Findings

### Architecture sketch

```
Agent Session                    MCP Server                     GitHub
     │                               │                            │
     ├─ mcp: enqueue-merge ──────────►                            │
     │   {branch, worktree, retro}   │                            │
     │                               ├─ gh pr create ─────────────►
     │◄── receipt {queue_id, pr_url} │                            │
     │                               │◄── CI status webhook ──────┤
     │   (agent continues work)      │                            │
     │                               ├─ gh pr merge ──────────────►
     │                               │                            │
     │                               ├─ swain-retro (if epic)     │
     │                               ├─ worktree cleanup          │
     │                               └─ bookmark update           │
```

### Investigation threads

1. **MCP server feasibility** — What's the simplest MCP server that can run locally, persist across agent sessions, and expose merge-queue tools? Options: Node.js (official SDK), Python, shell+socat.
2. **GitHub API integration** — Can we use `gh` CLI from within an MCP server? Or do we need direct API calls? Rate limit implications for a solo dev (5000 req/hr is plenty).
3. **Retro triggering** — swain-retro currently runs as a skill inside an agent session. Can it run headless from a script? Or does the MCP need to spawn a short-lived agent session for the retro?
4. **Queue semantics** — FIFO? Priority? What happens when two agents enqueue merges to trunk simultaneously? Do we need conflict detection or just sequential processing?
5. **Process lifecycle** — Who starts/stops the MCP server? swain-stage tmux integration? launchd? Docker container?
6. **swain-sync integration** — What changes to swain-sync to detect "MCP available" and route through the queue vs. direct merge?

### Prior art to evaluate

- GitHub merge queue (native) — overkill for solo dev? Or exactly right?
- Mergify — SaaS, probably too heavy
- Local CI tools (act, nektos/act) — for running checks locally before merge
- Claude Code remote triggers — could a scheduled trigger handle the queue?

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-27 | — | Initial creation |
