---
title: "Reconcile Doctor Script and Skill"
artifact: SPEC-288
track: implementable
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
type: enhancement
parent-epic: EPIC-068
linked-artifacts: []
depends-on-artifacts: []
addresses: []
swain-do: required
---

# Reconcile Doctor Script and Skill

## Problem Statement

`swain-doctor.sh` and `swain-doctor/SKILL.md` have drifted apart. The script has 6 checks not documented in SKILL.md. SKILL.md has 3 checks with inline detection logic that don't exist in the script. swain-init Phase 2.5 contains a branch model recommendation that belongs in swain-doctor. The result is inconsistent behavior and wasted agent tokens parsing redundant detection instructions.

## Desired Outcomes

Agents parse a slim SKILL.md that says "run the script, then look up remediation by check name." No detection logic in SKILL.md. No undocumented checks in the script.

## External Behavior

- `swain-doctor.sh` gains 3 new check functions: `check_branch_model`, `check_platform_dotfolders`, `check_skill_gitignore`.
- swain-init Phase 2.5 (branch model recommendation) is removed (already done this session).
- SKILL.md is restructured as: (1) how to run the script, (2) preflight integration, (3) remediation lookup table keyed by check name, (4) summary report format.

## Acceptance Criteria

- Given the script runs, when it completes, then every check name in its JSON output has a corresponding remediation section in SKILL.md.
- Given SKILL.md, when an agent reads it, then there is zero inline detection logic (no bash check commands outside the "run the script" invocation).
- Given a project without trunk or release branches, when swain-doctor runs, then the branch_model check emits an advisory.
- Given swain-init runs on a fresh project, when Phase 2.5 would have fired, then no branch model recommendation appears (it comes from doctor instead).
- Given a consumer project with unignored swain skill folders, when swain-doctor runs, then check_skill_gitignore emits a warning.
- Given platform dotfolder stubs exist for uninstalled platforms, when swain-doctor runs, then check_platform_dotfolders reports them.

## Scope & Constraints

- Do not change what existing checks detect or remediate — only move detection to the script and remediation to SKILL.md.
- Platform dotfolder check requires `jq`. If unavailable, skip with status `skipped`.
- The duplicate "Artifact index health" section in SKILL.md should be removed (already done this session).

## Implementation Approach

1. Add `check_branch_model`, `check_platform_dotfolders`, `check_skill_gitignore` to `swain-doctor.sh`.
2. Rewrite SKILL.md as a lookup table: frontmatter + intro + "run the script" section + one `##` per check name with remediation-only content.
3. Add remediation entries for the 6 script-only checks: `commit_signing`, `ssh_readiness`, `crash_debris`, `agents_bin_symlinks`, `flat_artifacts`, `swain_symlink`.
4. Verify the script's check list matches SKILL.md's section list.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-06 | _pending_ | Partial work already in progress (branch model move, duplicate removal). |
