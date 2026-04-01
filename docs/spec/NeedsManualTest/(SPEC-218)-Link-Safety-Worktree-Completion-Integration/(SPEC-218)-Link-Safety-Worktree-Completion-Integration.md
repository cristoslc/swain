---
title: "Link Safety Worktree Completion Integration"
artifact: SPEC-218
track: implementable
status: NeedsManualTest
author: cristos
created: 2026-03-31
last-updated: 2026-03-31
priority-weight: high
type: bug
parent-epic: EPIC-051
parent-initiative: ""
linked-artifacts:
  - EPIC-051
  - SPEC-216
  - SPEC-217
  - DESIGN-007
  - ADR-011
depends-on-artifacts:
  - SPEC-216
  - SPEC-217
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Link Safety Worktree Completion Integration

## Problem Statement

Even with detection ([SPEC-216](../(SPEC-216)-Worktree-Relative-Link-Detection-Script/(SPEC-216)-Worktree-Relative-Link-Detection-Script.md)) and resolution ([SPEC-217](../(SPEC-217)-Worktree-Link-Resolution-on-Merge/(SPEC-217)-Worktree-Link-Resolution-on-Merge.md)) scripts available, nothing calls them during worktree completion. Suspicious links still reach trunk unless the operator remembers to run the tools manually.

## Desired Outcomes

The worktree completion workflow — whether driven by `finishing-a-development-branch` or `swain-sync` — automatically runs the link detector on changed files before the merge commit. If suspicious links are found, the resolver runs automatically. UNRESOLVABLE items block the merge and surface to the operator with clear guidance.

## External Behavior

**Hook point:** After `git fetch origin && git merge origin/main` (per [ADR-011](../../../adr/Active/(ADR-011)-Worktree-Landing-Via-Merge-With-Retry.md) step 2) and before `git push`.

**Behavior:**
1. Identify changed files in the worktree branch vs. merge base (`git diff --name-only MERGE_BASE HEAD`)
2. Run `detect-worktree-links.sh` on those files
3. If exit 0 (no issues): proceed to push
4. If exit 1 (issues found): run `resolve-worktree-links.sh` on the flagged files
   - If all resolved (exit 0): stage the fixes, amend the merge commit, proceed to push
   - If any UNRESOLVABLE (exit 1): print each UNRESOLVABLE item with its file and line, abort push, surface to operator

**Operator surface:**
```
[link-safety] Found 2 suspicious links. Resolving automatically...
[link-safety] Fixed: docs/spec/Active/(SPEC-216)-foo/(SPEC-216)-foo.md:14 ../../../tmp -> ../design/
[link-safety] UNRESOLVABLE: docs/spec/Active/(SPEC-216)-foo/(SPEC-216)-foo.md:22 /tmp/worktree-abc/missing.sh
[link-safety] Merge aborted. Fix the UNRESOLVABLE link before pushing.
```

## Acceptance Criteria

- Given a worktree with no suspicious links in changed files, when completion runs, then no link-safety output appears and push proceeds normally
- Given a worktree with auto-resolvable suspicious links, when completion runs, then they are fixed and committed automatically before push
- Given a worktree with at least one UNRESOLVABLE link, when completion runs, then push is aborted and the operator sees which file/line to fix
- The integration does not re-scan unchanged files (only diffs vs. merge base)
- The hook runs in both `finishing-a-development-branch` skill and `swain-sync` skill at the same logical step
- Integration adds no more than 3 seconds to the completion workflow on a typical repo

## Reproduction Steps

1. Create a worktree, write a markdown file with a `../` link that goes past the repo root
2. Commit and attempt worktree completion
3. Without this spec: push succeeds, broken link reaches trunk
4. With this spec: link is detected, resolved or blocked before push

## Severity

high

## Expected vs. Actual Behavior

**Expected:** Worktree completion automatically detects and resolves worktree-specific links before merge.

**Actual:** Completion has no link-safety step — broken links reach trunk silently.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| Clean worktree completes without link-safety output | `test_integration.sh`: "clean files — no output" | Pass |
| Auto-resolvable links fixed before push | `test_integration.sh`: "auto-resolvable — FIXED in output" + "file clean after resolve" | Pass |
| UNRESOLVABLE blocks push with clear message | `test_integration.sh`: "UNRESOLVABLE — hook exits 1" + "abort message shown" | Pass |
| Only changed files scanned | Hook uses `git diff --name-only MERGE_BASE HEAD` to scope inputs | Pass |
| Hook present in both finishing-a-development-branch and swain-sync | `grep -c "link-safety"` → 4 hits in each SKILL.md | Pass |

## Scope & Constraints

- Modify `finishing-a-development-branch` skill and `swain-sync` skill — add the link-safety step at the correct hook point
- Do not modify `detect-worktree-links.sh` or `resolve-worktree-links.sh` behavior (those are owned by SPEC-216/217)
- The auto-amend on resolution must not re-sign or alter the merge commit message beyond adding a `[link-safety: fixed N links]` trailer

## Implementation Approach

1. In `finishing-a-development-branch`: after the merge step (before push), add a link-safety block calling the two scripts
2. In `swain-sync`: same hook point, same block
3. Use `git diff --name-only $(git merge-base HEAD origin/main) HEAD` to scope the scan
4. On auto-fix: `git add <fixed-files> && git commit --amend --no-edit -m "$(git log -1 --pretty=%B)\n\n[link-safety: fixed $N links]"`
5. On UNRESOLVABLE: print itemized list, `exit 1` to abort push

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | a5f0def | Initial creation |
| NeedsManualTest | 2026-03-31 | -- | All tasks complete; 7 tests passing |
