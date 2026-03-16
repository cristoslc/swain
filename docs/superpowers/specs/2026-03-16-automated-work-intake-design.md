# Automated Work Intake — Initiative Design

**Date:** 2026-03-16
**Artifact:** INITIATIVE-008
**Status:** Active

## Problem

swain-dispatch is operator-push only. There is no mechanism for agents to discover and pick up work autonomously from external sources. For swain to support polling agents, messaging bots, and webhook-triggered work, it needs a secure intake surface with deterministic pre-filtering so agents never see unvetted input.

## Design Decisions

### Two-Tier Intake Model

Work enters through one of two paths:

- **Fast path (authenticated):** Issue contains a valid auth token (mechanism TBD per SPIKE-025). Bypasses structural and content filters, proceeds directly to artifact creation.
- **Slow path (filtered):** No valid auth token. Must pass all deterministic gates: label filter, author allowlist, content pattern matching.

### Artifact Creation (Not Re-Dispatch)

Filtered issues become swain artifacts — not GitHub dispatch events. The intake pipeline's output is a SPEC, EPIC, or SPIKE on disk, linked to the source issue URL via `linked-artifacts`. This avoids circular dispatch (issue → GitHub → issue) and integrates directly into the swain-do execution path.

### Artifact Type Classification

An agent determines artifact type *after* deterministic filtering has approved the issue:
- Explicit markers in the issue (e.g., `[SPIKE]` prefix, `type: epic` label)
- Content heuristics (research questions → SPIKE, deliverable scope → EPIC, implementable unit → SPEC)
- Agent judgment as fallback

The boundary: **deterministic filter decides IF work enters the system; agent decides WHAT kind of artifact it becomes.**

### Channel Strategy: MVP First

GitHub Issue polling is the first and only channel. No abstraction for multiple channels until a second channel exists. Messaging bots (Slack/Discord) and external webhooks (Linear, Jira) are future work — designed when there's demand.

### Deterministic Filter Chain

1. Fetch open issues by label from configured repos
2. Dedup against already-processed issues
3. Auth check — valid token → fast path (skip to artifact creation)
4. Author allowlist gate
5. Content pattern matching (required + excluded patterns)
6. Agent classifies and creates artifact
7. Mark issue as processed, comment with artifact link

### Configuration

Per-project in `swain.settings.json`:

```json
{
  "intake": {
    "repos": ["owner/repo"],
    "pollLabel": "agent-intake",
    "processedLabel": "intake-processed",
    "authMethod": "totp",
    "authors": ["cristoslc"],
    "contentPatterns": {
      "required": ["SPEC-\\d+"],
      "excluded": ["\\[question\\]", "\\[discussion\\]"]
    },
    "cronSchedule": "*/15 * * * *"
  }
}
```

### Trigger Mechanisms

- Cron-scheduled GitHub Action (configurable interval)
- `workflow_dispatch` for manual sweeps

## Dependencies

- **SPIKE-025:** Auth mechanism for public channels must be resolved before EPIC-024 implementation
- **SPEC-052:** Vision-Rooted Chart Hierarchy — specifically its URL-based `linked-artifacts` data model extension, required for source issue linking

## Delivery Order

1. SPIKE-025 — resolve auth question
2. SPEC-052 — needs to land (or frontmatter contract stabilized)
3. EPIC-024 — GitHub Issue polling with deterministic pre-filtering
4. Future channels when there's demand

## Out of Scope

- Trust boundaries / agent sandboxing (INITIATIVE-004)
- What agents do with work after intake (swain-dispatch + swain-do)
- Code-level security scanning (EPIC-017, EPIC-023)

## Artifacts Created

| Artifact | Title | Status |
|----------|-------|--------|
| INITIATIVE-008 | Automated Work Intake | Active |
| SPIKE-025 | Authentication for Public Intake Channels | Proposed |
| EPIC-024 | GitHub Issue Polling with Deterministic Pre-Filtering | Proposed |
