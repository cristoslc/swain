---
title: "Session Startup Time Instrumentation"
artifact: SPIKE-001
track: container
status: Active
author: cristos
created: 2026-03-30
last-updated: 2026-03-30
question: "Where does session startup wall time actually go — LLM inference, tool-call overhead, script execution, or file I/O — and what is the achievable floor?"
gate: Pre-MVP
risks-addressed:
  - Optimizing the wrong layer (e.g., scripts when inference dominates)
  - Setting unrealistic success criteria for EPIC-048
evidence-pool: ""
---

# Session Startup Time Instrumentation

## Summary

<!-- Populated at completion -->

## Question

Where does session startup wall time actually go — LLM inference, tool-call overhead, script execution, or file I/O — and what is the achievable floor?

## Go / No-Go Criteria

- **Go (proceed with SPEC-194/196):** LLM round-trips account for >60% of wall time, confirming that chain collapse and greeting split are the highest-leverage changes.
- **Go (pivot to script optimization):** Script execution accounts for >40% of wall time, suggesting we should optimize specgraph/GitHub API calls before touching the skill chain.
- **No-Go (rethink approach):** Wall time is dominated by a single unavoidable operation (e.g., EnterWorktree git clone) that can't be deferred or backgrounded.

## Pivot Recommendation

If script execution dominates, pivot to background/async execution of expensive collectors (specgraph, GitHub API) rather than restructuring the skill chain. If a single unavoidable operation dominates, focus on making that operation faster rather than reorganizing the chain.

## Method

1. **Add timestamps to shell scripts** — instrument `swain-session-bootstrap.sh`, `swain-status.sh`, `swain-preflight.sh` with `date +%s%N` at entry/exit of each major section.
2. **Log skill invocation boundaries** — add a lightweight timing wrapper in the shell launcher that records when each `/skill` invocation starts and ends.
3. **Run 5 cold starts and 5 warm starts** — capture timing data for both scenarios.
4. **Categorize time** into: shell launcher overhead, LLM inference (skill read + reasoning), tool-call round-trip, script execution, file I/O, network I/O (GitHub API).
5. **Calculate achievable floor** — sum only the unavoidable operations (git rev-parse, session.json read, tmux rename) to establish the theoretical minimum.

## Findings

<!-- Populated during Active phase -->

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-30 | -- | Initial creation; operator-requested |
