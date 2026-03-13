---
title: "swain-dispatch Skill"
artifact: SPEC-025
status: Proposed
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
type: feature
parent-epic: EPIC-010
linked-artifacts:
  - SPIKE-016
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: "github:cristoslc/swain#18"
swain-do: required
---

# swain-dispatch Skill

## Problem Statement

swain currently has no way to offload work to background agents. When a SPEC or task is ready for implementation, the operator must be in an active session. SPIKE-016 confirmed that `anthropics/claude-code-action@v1` provides a reliable mechanism to trigger Claude Code from GitHub Issues. swain needs a skill that creates properly-structured GitHub Issues and triggers the dispatch workflow.

## External Behavior

### `/swain dispatch SPEC-NNN`

1. Reads the artifact content from disk
2. Creates a GitHub Issue with:
   - Title: `[dispatch] {artifact title}`
   - Body: Full artifact content (frontmatter + spec body) wrapped in a code block
   - Labels: `agent-dispatch`, `swain`
   - Optional: `@claude` mention to trigger the action (configurable)
3. Triggers the dispatch via `repository_dispatch` event:
   ```bash
   gh api repos/{owner}/{repo}/dispatches \
     -f event_type="agent-dispatch" \
     -f client_payload[artifact]="SPEC-NNN" \
     -f client_payload[issue_number]="<created-issue-number>"
   ```
4. Reports the issue URL to the operator

### GitHub Actions workflow

A workflow file `.github/workflows/agent-dispatch.yml` that:
- Triggers on `repository_dispatch` (event_type: `agent-dispatch`)
- Also triggers on `issue_comment` containing `@claude` (manual fallback)
- Checks out the repo
- Runs `anthropics/claude-code-action@v1` with the artifact as context
- Uses model from `client_payload` or defaults to `claude-sonnet-4-6`

### Configuration

In `swain.settings.json`:
```json
{
  "dispatch": {
    "model": "claude-sonnet-4-6",
    "maxTurns": 15,
    "labels": ["agent-dispatch", "swain"],
    "autoTrigger": true
  }
}
```

## Acceptance Criteria

- **Given** `/swain dispatch SPEC-NNN`, **when** the artifact exists, **then** a GitHub Issue is created with the spec content and a `repository_dispatch` event is fired
- **Given** the dispatch workflow runs, **when** triggered by `repository_dispatch`, **then** Claude Code Action executes with the artifact context and posts results back to the issue
- **Given** `@claude` is mentioned in an issue comment, **when** the workflow triggers, **then** Claude Code Action responds to the comment
- **Given** the dispatch settings in `swain.settings.json`, **when** model or maxTurns are configured, **then** the workflow uses those values
- **Given** `gh` CLI is not authenticated or unavailable, **when** dispatch is attempted, **then** a clear error is shown with setup instructions

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Only dispatches to GitHub (no other backends in this spec)
- Does not implement model routing logic (that's a separate spec under EPIC-010)
- Requires `ANTHROPIC_API_KEY` as a GitHub Actions secret
- Requires the Claude GitHub App installed on the repo

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-13 | PENDING | Initial creation |
