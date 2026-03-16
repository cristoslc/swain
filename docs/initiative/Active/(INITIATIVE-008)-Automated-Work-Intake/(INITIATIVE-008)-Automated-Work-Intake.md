---
title: "Automated Work Intake"
artifact: INITIATIVE-008
track: container
status: Active
author: cristos
created: 2026-03-16
last-updated: 2026-03-16
parent-vision: VISION-001
priority-weight: high
success-criteria:
  - Agents can discover and pick up work autonomously from external sources
  - All inbound work passes deterministic pre-filtering before any agent sees it
  - TOTP-authenticated issues are fast-tracked; unauthenticated issues go through structural + content filters
  - Per-project intake configuration supporting one or more repos
linked-artifacts:
  - EPIC-024
  - SPIKE-025
  - SPEC-052
---

# Automated Work Intake

## Strategic Focus

Secure the interaction surface for automated work. Today, swain-dispatch is operator-push only — the operator explicitly invokes `/swain dispatch SPEC-NNN`. There is no way for agents to discover and pick up work autonomously from external sources. For swain to support polling agents, messaging bots, and webhook-triggered work, it needs a secure intake surface with deterministic pre-filtering so agents never see unvetted input.

## Scope Boundaries

**In scope:** Deterministic pre-filtering of external work sources (no LLM in the triage path), two-tier intake model (TOTP-authenticated fast path + filtered slow path), channel adapters for GitHub Issue polling (first), messaging bots and external webhooks (future), per-project configuration.

**Out of scope:** Trust boundaries and agent sandboxing (INITIATIVE-004 territory), what agents do with work once they receive it (existing swain-dispatch + swain-do), code-level security scanning (EPIC-017, EPIC-023).

## Two-Tier Intake Model

Work enters the system through one of two paths:

- **Fast path (authenticated):** Issue contains a valid auth token (mechanism TBD per SPIKE-025). Skips structural and content filters, proceeds directly to artifact creation.
- **Slow path (filtered):** No valid auth token. Must pass all deterministic gates: label filter, author allowlist, content pattern matching (required and excluded patterns).

Once an issue passes either path, an agent classifies it (SPEC, EPIC, or SPIKE) based on explicit markers, content heuristics, and agent judgment, then creates the artifact following standard swain-design conventions with the source issue URL in `linked-artifacts`.

## Child Epics

- EPIC-024: GitHub Issue Polling with Deterministic Pre-Filtering (Proposed)

## Child Spikes

- SPIKE-025: Authentication for Public Intake Channels (Proposed)

## Small Work (Epic-less Specs)

None.

## Future Channels (Not Yet Designed)

- Messaging bot intake (Slack/Discord)
- External webhook intake (Linear, Jira, etc.)

## Key Dependencies

- EPIC-024 depends on SPIKE-025 (auth mechanism informs filter design)
- EPIC-024 depends on SPEC-052 (Vision-Rooted Chart Hierarchy — specifically URL-based linked-artifacts for source issue linking)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-16 | — | Created during brainstorming session; first deliverable is GitHub Issue polling |
