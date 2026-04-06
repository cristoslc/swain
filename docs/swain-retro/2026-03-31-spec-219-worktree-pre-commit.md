---
title: "Retro: SPEC-219 Worktree Pre-Commit Artifact Flush"
artifact: RETRO-2026-03-31-spec-219-worktree-pre-commit
track: standing
status: Active
created: 2026-03-31
last-updated: 2026-03-31
scope: "SPEC-219 implementation and swain-do audit"
period: "2026-03-31"
linked-artifacts:
  - SPEC-219
  - SPEC-193
---

# Retro: SPEC-219 Worktree Pre-Commit Artifact Flush

## Summary

[SPEC-219](../spec/Complete/(SPEC-219)-Worktree-Pre-Commit-Artifact-Flush/(SPEC-219)-Worktree-Pre-Commit-Artifact-Flush.md) was created, implemented, and closed in a single session. The bug: new artifact files created before entering a worktree were invisible inside the worktree because the branch was cut before the files were committed. The fix added a pre-commit step to swain-do's worktree isolation preamble. A subsequent skill-creator audit caught a behavioral bug in the fix itself and repaired it, along with four other issues in SKILL.md and the cheatsheet.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| [SPEC-219](../spec/Complete/(SPEC-219)-Worktree-Pre-Commit-Artifact-Flush/(SPEC-219)-Worktree-Pre-Commit-Artifact-Flush.md) | Worktree Entry Must Commit Staged Artifacts First | Complete |
| [SPEC-193](../spec/Complete/(SPEC-193)-Artifact-ID-allocation-must-check-all-local-branches/(SPEC-193)-Artifact-ID-allocation-must-check-all-local-branches.md) | Artifact ID allocation must check all branches | Annotated (related finding) |

## Reflection

### What went well

The bug was caught organically — SPEC-219 itself was the first artifact to experience the bug it described. The session committed SPEC-219 before entering the worktree, which is exactly what the fix prescribes. The fix-then-verify loop closed cleanly within the same session.

The skill-creator audit immediately after implementation caught a behavioral regression in the fix. Running the audit as part of the delivery rather than deferring it paid off — the window between "fix committed" and "fix audited" was minutes, not sessions.

### What was surprising

The first implementation of the fix used `git add -A`, which stages all dirty files — both untracked new files and modified tracked files. The spec's own Implementation Approach section described this behavior ("subject to `.gitignore`") but framed it as correct. It wasn't: only untracked files need committing before worktree creation, because modified tracked files are already in git history and appear in the worktree regardless. The audit caught this; the spec did not.

This is a case where the Implementation Approach in the SPEC contained a bug that survived into the committed fix. The spec review step (ADR compliance, scope check) doesn't validate whether the proposed approach is technically correct — it validates whether it's in scope.

### What would change

The SPEC-219 spec's Implementation Approach section should have distinguished between untracked files (the actual problem) and dirty tracked files (not a problem for worktree visibility). A cleaner problem statement would have led to a cleaner first implementation.

More broadly: when an Implementation Approach includes bash snippets, those snippets deserve the same scrutiny as code. Reading them at spec authoring time would have caught the `git add -A` over-reach before it shipped.

### Patterns observed

This is the second session where a fix required a follow-up fix caught by an audit (cf. SPEC-214 symlink auto-repair). The pattern: first-pass fixes are often correct in intent but too broad in scope. Audit as a second pass is catching these, but the cost is two commits instead of one.

A related pattern: SPEC-193 (artifact ID allocation missing untracked files) and SPEC-219 share the same root — the committed/uncommitted boundary is leaky in swain workflows. Two separate bugs, same underlying assumption failure.

## Learnings captured

| Item | Type | Summary |
|------|------|---------|
| Spec Implementation Approach sections need bash-level review | SPEC candidate | swain-design should prompt for bash snippet review when the Implementation Approach contains shell commands |
| `git add -A` vs untracked-only is a recurring footgun | SPEC candidate | Document the committed/uncommitted boundary distinction in swain-do skill prose and SPEC template |
| Two consecutive fixes for same root cause (SPEC-193, SPEC-219) | SPEC candidate | Consider a unifying SPEC or ADR covering the committed/uncommitted boundary assumption across swain workflows |

## SPEC candidates

1. **Spec bash review gate** — When swain-design authors a SPEC whose Implementation Approach contains shell commands, flag them for review before the SPEC enters Active. The ADR compliance check doesn't cover correctness of proposed commands, only architectural alignment. A lightweight "does this command do what you think it does?" prompt at authoring time would catch `git add -A` vs `git ls-files --others` class errors before they ship.

2. **Committed/uncommitted boundary ADR** — SPEC-193 and SPEC-219 both stem from the assumption that the working tree and the latest commit are equivalent. This assumption breaks in multi-step sessions where artifact creation and worktree entry are sequential. An ADR documenting this boundary — and the expected behavior at each transition point — would prevent future bugs in the same class and give new skill authors a reference.
