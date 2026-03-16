---
title: "GitHub Issue Polling with Deterministic Pre-Filtering"
artifact: EPIC-024
track: container
status: Proposed
author: cristos
created: 2026-03-16
last-updated: 2026-03-16
parent-initiative: INITIATIVE-008
depends-on:
  - SPIKE-025
  - SPEC-052
success-criteria:
  - A scheduled GitHub Action polls configured repos for new issues matching intake criteria
  - Issues with valid auth tokens are fast-tracked without structural/content filtering
  - Issues without auth tokens pass deterministic label, author, and content filters before intake
  - Filtered issues are converted to swain artifacts (SPEC, EPIC, or SPIKE) with source URL in linked-artifacts
  - Manual sweep is available via workflow_dispatch
  - Processed issues are marked to prevent re-processing
linked-artifacts:
  - INITIATIVE-008
  - SPIKE-025
  - SPEC-052
---

# GitHub Issue Polling with Deterministic Pre-Filtering

## Problem

swain-dispatch is push-only — the operator must explicitly invoke it. There is no mechanism for agents to poll external sources for actionable work. GitHub Issues are the most natural first source: issues arrive on public or private repos, and agents should be able to discover, filter, and intake them autonomously.

## Solution

A GitHub Action workflow that runs on a cron schedule (and manually via `workflow_dispatch`), polls configured repos for open issues, applies a deterministic filter chain, and creates swain artifacts from issues that pass.

## Filter Chain

All filtering is deterministic — no LLM involvement in the triage path.

1. **Fetch** — query open issues from configured repo(s) via GitHub API, filtered by configurable label (e.g., `agent-intake`)
2. **Dedup** — skip issues already processed (tracked via a label like `intake-processed`)
3. **Auth check** — scan issue body for auth token (mechanism per SPIKE-025)
   - Valid → mark as authenticated, skip to step 6
   - Missing/invalid → continue to slow path
4. **Author allowlist** — is the issue author in the configured allowed list?
5. **Content pattern match** — does the title/body match required patterns and not match excluded patterns?
6. **Classify & create artifact** — an agent reads the filtered issue and determines artifact type (SPEC, EPIC, SPIKE) based on:
   - Explicit markers in the issue (e.g., `[SPIKE]` prefix, `type: epic` label)
   - Content heuristics (research questions → SPIKE, deliverable scope → EPIC, implementable unit → SPEC)
   - Agent judgment as fallback
   - Artifact is created following swain-design conventions with source issue URL in `linked-artifacts`
7. **Mark processed** — add `intake-processed` label to the issue, post a comment linking back to the created artifact

## Configuration

Extends `swain.settings.json`:

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

## Trigger Mechanisms

- **Cron** — GitHub Action runs on configurable schedule (default: every 15 minutes)
- **Manual** — `workflow_dispatch` for on-demand sweeps

## Key Dependencies

- **SPIKE-025:** Auth mechanism must be resolved before the auth check step can be implemented
- **SPEC-052:** Vision-Rooted Chart Hierarchy — specifically its URL-based `linked-artifacts` data model extension, required for source issue linking

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-16 | — | Created during INITIATIVE-008 brainstorming |
