---
title: "Fix swain-dispatch functional bugs"
artifact: SPEC-074
track: implementable
status: Abandoned
author: cristos
created: 2026-03-18
last-updated: 2026-03-25
type: bug
parent-epic: EPIC-031
linked-artifacts:
  - SPEC-079
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Fix swain-dispatch functional bugs

## Problem Statement

Two high-severity functional bugs prevent swain-dispatch from working correctly:

1. **Broken autoTrigger:** Step 5 fires a `repository_dispatch` event, but the embedded GitHub Actions workflow YAML only listens on `issues.opened`, `issue_comment`, and `pull_request_review_comment` — never `repository_dispatch`. The auto-trigger feature is non-functional.

2. **Broken heredoc variable expansion:** Step 4 uses `cat <<'EOF'` (single-quoted delimiter) which suppresses shell variable expansion. `${ARTIFACT_ID}` and `${ARTIFACT_CONTENT}` are written literally instead of expanded.

## Acceptance Criteria

**AC-1:** The embedded workflow YAML template includes `repository_dispatch` with `types: [agent-dispatch]` as a trigger event.

**AC-2:** The heredoc in Step 4 uses unquoted `EOF` (or equivalent) so that `${ARTIFACT_ID}` and `${ARTIFACT_CONTENT}` are expanded by the shell.

**AC-3:** Existing non-auto-trigger flow (manual issue creation) is not broken by the fix.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC-1 | Grep workflow YAML for repository_dispatch | |
| AC-2 | Test variable expansion in heredoc | |
| AC-3 | Manual walkthrough of issue creation flow | |

## Scope & Constraints

**In scope:** `skills/swain-dispatch/SKILL.md` only.

**Out of scope:** Adding references/, settings schema, or other medium/low findings — those are addressed by SPEC-079.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-18 | — | Two high-severity bugs from audit |
| Abandoned | 2026-03-25 | -- | swain-dispatch deprecated — requires API billing (ANTHROPIC_API_KEY); may revisit when non-API billing supported |
