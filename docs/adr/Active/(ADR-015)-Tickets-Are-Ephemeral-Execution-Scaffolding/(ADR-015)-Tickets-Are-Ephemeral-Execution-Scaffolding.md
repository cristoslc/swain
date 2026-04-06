---
title: "Tickets Are Ephemeral Execution Scaffolding"
artifact: ADR-015
track: standing
status: Active
author: cristos
created: 2026-03-23
last-updated: 2026-03-23
linked-artifacts:
  - INITIATIVE-013
  - EPIC-043
  - SPIKE-043
depends-on-artifacts: []
trove: ""
---

# Tickets Are Ephemeral Execution Scaffolding

## Context

Swain uses `tk` (ticket) for execution tracking during SPEC implementation. Tickets live in `.tickets/` as markdown files with YAML frontmatter. They track task status, dependencies, notes, and claims — all the state an agent needs to resume work mid-session or across sessions.

The question arose: what happens to tickets after a SPEC completes? Currently, tickets accumulate across worktrees and sessions. They were treated as potentially archival — preserved during worktree exits, referenced during retros, and never explicitly cleaned up.

This creates three problems:

1. **Worktree cleanup friction.** ExitWorktree warns about "uncommitted files" that are just spent tickets, forcing the operator to confirm discarding them every time.
2. **Retro quality.** Tickets record *what tasks existed and their status* — not *what decisions were made, what pivoted, or why*. Retros built from tickets produce checklists, not narratives. The session log (`.agents/session.json` JSONL) captures the actual conversation — decisions, pivots, rationale, operator feedback — which is what a retro needs.
3. **Stale ticket noise.** Old tickets from completed SPECs clutter `tk ready` and `ticket-query` output, requiring filters to exclude closed work.

## Decision

**Tickets are ephemeral execution scaffolding.** They exist to help agents track and resume work during implementation. Once the parent SPEC transitions to a terminal state (Complete, Abandoned), its tickets may be discarded.

Specific rules:

1. **Tickets are not committed to trunk.** `.tickets/` stays in `.gitignore`. Tickets live in the worktree for the duration of implementation and are discarded with the worktree.
2. **Retros use session logs, not tickets.** The swain-retro skill reconstructs the narrative from `.agents/session.json` (JSONL), which captures decisions, pivots, and rationale. Tickets are not an input to retrospectives.
3. **Worktree exit discards tickets silently.** When ExitWorktree runs after a SPEC completes, `.tickets/` files should not trigger the "uncommitted files" warning. They are expected ephemeral state, not work product.
4. **`tk` remains the execution tracker.** This decision does not change how tickets are created or used during implementation — only their lifecycle after completion.

## Alternatives Considered

**A. Commit tickets to trunk as archival records.** Rejected — tickets duplicate information that exists in better form elsewhere (spec verification tables, session logs, git history). Committing them adds noise to the repo without adding retrievable value.

**B. Archive tickets to a separate directory on completion.** Rejected — same problem as (A) but with extra complexity. If we need to reconstruct what happened, session logs and git history are more complete and more reliable.

**C. Keep tickets but exclude from retro input.** Partially adopted — the retro change stands regardless, but keeping tickets around with no consumer is pure accumulation.

## Consequences

**Positive:**
- Worktree cleanup is clean — no false warnings about "uncommitted files"
- Retros produce better narratives from richer source material (session logs)
- `tk ready` / `ticket-query` stay uncluttered
- Reduces cognitive load: tickets are clearly scoped to "during implementation" with no ambiguity about their shelf life

**Negative:**
- If an agent needs to resume a partially-complete SPEC in a *new* worktree (not the original), it can't read the old tickets. Mitigation: the SPEC's verification table and the plan file (`docs/superpowers/plans/`) provide enough context to reconstruct task state. This is a rare scenario — most SPECs complete within their originating worktree.

**Downstream changes required:**
- **swain-do SKILL.md**: Add a note that tickets are ephemeral and scoped to the worktree's lifetime
- **swain-retro SKILL.md**: Change evidence source from tickets to session logs (`.agents/session.json`)
- **swain-do worktree exit**: `.tickets/` should not block ExitWorktree removal
- **.gitignore**: Ensure `.tickets/` is listed (already the case in most repos)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-23 | — | User-requested; formalizes observed practice |
