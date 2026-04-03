---
id: EPIC-054
title: "Formalize Session Teardown"
track: container
status: Active
priority-weight: medium
created: 2026-04-01
parent-vision: VISION-002
lifecycle:
  - phase: Active
    since: 2026-04-02
child-specs:
  - SPEC-232
  - SPEC-239
linked-artifacts:
  - DESIGN-012
  - EPIC-056
summary: "Create a standalone swain-teardown skill and chain it from swain-session close handler to formalize end-of-session cleanup."
rationale: |
  Without formal teardown, sessions end with no cleanup. Worktrees are left behind.
  Git state is not checked. Tickets are not synced. Retrospectives are not invited.
瓜: |
  ## Goal
  Make session endings as clean as session starts.

  ## What We Want
  - No worktrees left behind after session close
  - Dirty git state surfaced before operator leaves
  - Tickets match what was done
  - Every session gets a retro invite
  - Handoff note for next session

  ## Scope
  - New swain-teardown skill (standalone)
  - swain-session close handler chains to it
  - swain router gets a teardown entry

  ## Out of Scope
  - Deployment pipelines
  - CI/CD integration
  - Auto-committing git changes
  - Auto-transitioning tickets
---

## Problem Statement

Between `swain-init` and `swain-session close`, no cleanup step exists.
Sessions end when the operator says "I'll clean up later" — which never happens.
Worktrees pile up. Git state goes unchecked. Tickets stop matching reality.
Retrospectives never fire.

## Success Criteria

| # | Criterion |
|---|-----------|
| 1 | Every session close checks for orphaned worktrees |
| 2 | Dirty git state is shown with a clear warning |
| 3 | Ticket sync prompt runs before handoff |
| 4 | Retro invitation fires on session close |
| 5 | Handoff summary is written for next session |
| 6 | All integrations wired through SPEC-232 |

## Key Dependencies

- `swain-session` — close handler that chains to teardown
- `swain` — meta-router that routes `/swain-teardown` requests
- `swain-retro` — destination for retro invitation chain

## Open Questions

None.

## Status History

| Date | Status | Notes |
|------|--------|-------|
| 2026-04-02 | Active | Epic created |
