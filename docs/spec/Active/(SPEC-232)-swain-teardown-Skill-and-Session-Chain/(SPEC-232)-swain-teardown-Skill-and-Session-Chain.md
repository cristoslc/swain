---
id: SPEC-232
title: "swain-teardown Skill and Session Chain"
status: Active
parent-epic: EPIC-054
swain-do: required
created: 2026-04-01
lifecycle:
  - phase: Active
    since: 2026-04-02
linked-artifacts:
  - EPIC-054
  - DESIGN-012
summary: "Create the swain-teardown skill with worktree orphan check, git dirty-state warning, ticket sync prompt, retro invitation, and handoff summary. Chain it from swain-session close handler and add router entry in swain."
implementationOwner: agent
testStrategy: manual
---

## Problem Statement section.

Sessions currently end without any formal teardown step between start and end. The operator often says they will clean up later, but cleanup rarely happens. As a result, worktrees accumulate unchecked. Git state diverges from tickets. Retrospective invitations are skipped entirely. No cleanup checks run automatically at session close.

## Solution Overview section.

The solution creates a standalone swain-teardown skill that runs end-of-session hygiene checks. The skill is chained from the swain-session close handler and is also available as a standalone invocation. The routing entry is added to the swain meta-skill. All checks produce a clear findings report with recommendations.

## Acceptance Criteria section.

The following acceptance criteria define when this implementation is complete.

| # | Criterion | Verified By |
|---|-----------|-------------|
| AC1 | swain-teardown skill exists at .claude/skills/swain-teardown/SKILL.md | Skill discovery |
| AC2 | Skill checks for orphan worktrees and reports findings | Manual test |
| AC3 | Skill checks git working tree state and warns on dirty state | Manual test |
| AC4 | Skill prompts for ticket sync check before closing | Manual test |
| AC5 | Skill sends retro invitation via swain-retro chain | Manual test |
| AC6 | Skill generates handoff summary and writes to SESSION-ROADMAP.md | Manual test |
| AC7 | swain-session close handler chains to swain-teardown | Session close test |
| AC8 | swain meta-router routes /swain-teardown requests | Router test |
| AC9 | All artifact IDs in this spec resolve to correct relative paths | Link check |

All acceptance criteria must pass verification before the spec is marked complete.

## Scope of Implementation section.

The implementation scope is divided into two clear categories: included and excluded items.

### Included Scope section.

The included scope contains the new swain-teardown skill, the session-chain integration, and the router entry. The new skill is located at .claude/skills/swain-teardown/SKILL.md. The session-chain integration is added to the swain-session SKILL.md file. The router entry is added to the swain SKILL.md file. No new scripts are created. The skill logic is self-contained in the SKILL.md file.

### Excluded Scope section.

The excluded scope prevents accidental scope creep into sensitive areas. Worktrees are not auto-removed; the operator must confirm any removal. Git changes are not auto-committed or auto-pushed. Tickets are not auto-transitioned; operator confirms all transitions. Changes are not made to swain-init, swain-do, or swain-design. Backend scripts such as session-state.sh and progress-log.sh are not modified.

---

## Technical Approach section.

The implementation follows a three-step approach guided by writing-skills TDD methodology.

### Step 1: Create swain-teardown Skill section.

The first step establishes the skill and validates baseline failures before the skill exists.

RED phase failures describe what breaks before the skill exists.

| # | Failure description |
|---|--------|
| 1 | swain-teardown skill is not found in skill discovery |
| 2 | /swain-teardown returns unknown intent from swain router |
| 3 | Session close leaves orphan worktrees without detection |
| 4 | Session close does not warn about dirty git state |
| 5 | Session close does not prompt for ticket sync |
| 6 | Session close does not invite retrospective participation |
| 7 | Session close does not generate any handoff summary |

Green phase describes the seven-step skill implementation that resolves all failures. The skill detects teardown trigger words to identify when it should run. The skill checks for active session state before running checks. The skill runs worktree orphan check using git worktree list output with session markers. The skill runs git dirty-state check using git status porcelain output. The skill runs ticket sync check comparing session log against tk issue list. The skill sends retro invitation using swain-retro invite with session id. The skill writes handoff summary to SESSION-ROADMAP.md. The skill reports findings with clear recommendations for operator action.

### Step 2: Update swain-session Close Handler section.

The second step modifies the swain-session close handler to chain the teardown skill after mechanical close steps. After session-state.sh close, session-digest.sh, progress-log.sh, and commit, the handler runs the teardown chain. The --session-chain flag skips the redundant session-active check since the handler already confirmed session state. The edit adds a single command in the close handler after the progress-log.sh call.

### Step 3: Update swain Router section.

The third step adds a routing entry in the swain meta-skill to route /swain-teardown requests to the new skill. The routing entry follows the existing pattern used for other skill invocations. The teardown routing is placed alongside other skill routing entries in the case structure.

---

## File Inventory section.

All files modified or created as part of this implementation are listed here.

| File | Action | Notes |
|------|--------|-------|
| .claude/skills/swain-teardown/SKILL.md | Create | New standalone skill for session teardown |
| .claude/skills/swain-session/SKILL.md | Edit | Add teardown chain in close handler after progress-log.sh |
| .claude/skills/swain/SKILL.md | Edit | Add teardown routing entry in skill case structure |

---

## Integration Details section.

### swain-session Close Handler Chain section.

The current close handler sequence runs four steps before the session ends. The first step runs session-state.sh close. The second step runs session-digest.sh. The third step runs progress-log.sh. The fourth step commits SESSION-ROADMAP.md. The new sequence inserts the teardown chain as a new step after progress-log.sh and before the commit. The full new sequence is: session-state.sh close, session-digest.sh, progress-log.sh, teardown chain, commit SESSION-ROADMAP.md.

---

## Error Handling section.

The skill handles four distinct error situations with appropriate responses.

| Situation | Response |
|-----------|----------|
| No active session found | Report cleanly with no-session message, exit with code 0 |
| Git command unavailable | Skip git check entirely, note the unavailability in the report |
| Worktree list command fails | Skip worktree check, note the failure in the report |
| Retro API call fails | Note failure as non-blocking, continue with remaining checks |

SESSION-ROADMAP.md missing is handled by creating the file with a header before appending the summary.

---

## Manual Test Scenarios section.

Four test scenarios cover the main cases for this implementation.

| Scenario | Steps | Expected Result |
|----------|-------|----------------|
| Clean session close | Start session. Make no changes. Close session. | Teardown shows clean state with no warnings |
| Dirty git state close | Start session. Make changes without committing. Close session. | Teardown warns about dirty state with actionable message |
| Orphan worktrees detected | Create orphan worktree. Start new session. Close session. | Teardown lists the orphan worktree as a finding |
| Standalone no-session invocation | No active session. Run /swain-teardown. | Clean no-session response with graceful exit |

---

## Open Questions section.

There are no open questions for this specification at this time. All concerns have been resolved during design and spec review.

## Status History section.

| Date | Status | Notes |
|------|--------|-------|
| 2026-04-02 | Active | Initial spec created and marked active |
