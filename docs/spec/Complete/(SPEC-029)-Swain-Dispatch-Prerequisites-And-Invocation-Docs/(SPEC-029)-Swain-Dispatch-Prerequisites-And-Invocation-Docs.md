---
title: "swain-dispatch Prerequisites and Invocation Docs"
artifact: SPEC-029
status: Complete
type: enhancement
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
source-issue: "github:cristoslc/swain#41"
parent-epic: EPIC-010
swain-do: required
addresses: []
linked-artifacts:
  - SPEC-025
depends-on-artifacts: []
implementation-commits: 78c1ca6
---

# swain-dispatch Prerequisites and Invocation Docs

## Problem Statement

swain-dispatch has basic prerequisite checks but lacks comprehensive setup documentation, clear error messages with step-by-step instructions, and doesn't cover the timing gotcha (body mention at creation vs follow-up comment). Users encountering setup issues don't get enough guidance to self-serve.

Source: [GitHub Issue #41](https://github.com/cristoslc/swain/issues/41)

## Acceptance Criteria

1. swain-dispatch checks for workflow file before dispatch and gives setup instructions if missing
2. swain-dispatch checks for API key secret before dispatch and gives setup instructions if missing
3. Clear error messages with copy-paste setup instructions for each missing prerequisite
4. Invocation docs cover the timing gotcha (body `@claude` vs comment `@claude`)
5. Prerequisites section in SKILL.md documents all three requirements (Claude App, workflow, API key)

## Verification

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Workflow file check with instructions | PASS | Step 0 in SKILL.md |
| 2 | API key secret check with instructions | PASS | Step 0 in SKILL.md |
| 3 | Clear error messages | PASS | Numbered setup guide in preflight |
| 4 | Timing gotcha documented | PASS | "Trigger timing" section in SKILL.md |
| 5 | All prerequisites documented | PASS | Prerequisites section with all 3 |

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Complete | 2026-03-13 | 78c1ca6 | Enhancement — direct to Complete |
