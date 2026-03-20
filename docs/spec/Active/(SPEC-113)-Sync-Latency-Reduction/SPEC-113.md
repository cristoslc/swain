---
title: "Reduce swain-sync latency and context disruption"
artifact: SPEC-113
track: implementable
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: enhancement
parent-epic: ""
parent-initiative: INITIATIVE-005
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Reduce swain-sync latency and context disruption

## Problem Statement

swain-sync takes too long when delegated to a sub-agent, causing the operator to lose their context thread while waiting. The sync workflow involves fetch/rebase, staging, gitignore checks, ADR compliance, design drift, index rebuild, commit, and push — each step is sequential, and the sub-agent overhead adds latency on top. The operator experiences a 60-90 second pause that breaks flow.

## External Behavior

**Current:** Operator invokes /swain-sync, waits 60-90s for the sub-agent to complete all steps, loses train of thought.

**Desired:** Sync completes fast enough that the operator doesn't context-switch, OR runs reliably in the background so the operator can continue working.

## Acceptance Criteria

- **Given** a typical sync (< 20 changed files, no conflicts), **When** the operator invokes /swain-sync, **Then** the sync completes in under 20 seconds
- **Given** a background sync, **When** it completes, **Then** the operator is notified with a one-line summary (commit hash, files changed, push status)
- **Given** a background sync that encounters a conflict or hook failure, **Then** it surfaces the error clearly without losing the operator's staged changes
- The advisory checks (ADR compliance, design drift) should be parallelized or skipped for speed when the operator signals urgency (e.g., /push vs /swain-sync)

## Investigation Areas

1. **Reduce sub-agent overhead** — the sub-agent re-reads the full skill instructions every time. Could the sync steps be a shell script instead of agent-interpreted instructions?
2. **Parallelize advisory checks** — ADR compliance, design drift, and index rebuild can run concurrently with each other (they're all read-only until staging)
3. **Background-by-default** — sync could always run in background with a notification on completion, rather than blocking the conversation
4. **Fast path** — /push as a lightweight alternative that skips advisory checks (already exists but may need refinement)
5. **Incremental index rebuild** — only rebuild indexes for types that actually changed, not all types (partially implemented but may have overhead in the detection step)

## Scope & Constraints

- Must not sacrifice safety (gitignore checks, hook execution) for speed
- Must preserve the commit message quality (conventional commits, Co-Authored-By)
- Background sync must handle the case where the operator makes more changes while sync is running

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | | Initial creation |
