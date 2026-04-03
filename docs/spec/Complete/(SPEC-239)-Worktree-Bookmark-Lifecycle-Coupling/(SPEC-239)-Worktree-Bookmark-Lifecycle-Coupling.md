---
title: "Worktree-Bookmark Lifecycle Coupling"
artifact: SPEC-239
track: implementable
status: Complete
author: cristos
created: 2026-04-02
priority-weight: medium
type: enhancement
parent-epic: EPIC-054
swain-do: required
---

# Worktree-Bookmark Lifecycle Coupling

## The Problem Statement Section.

swain-teardown detects orphan worktrees but cannot act on them. The teardown report surfaces three accumulated orphan worktrees with no path to resolution. Orphan detection without orphan resolution is an incomplete feature. Worktrees continue to pile up across sessions. The session ends and nothing changes in the worktree inventory. Each subsequent session starts with more cleanup debt than the last. This pattern repeats indefinitely without intervention.

## The Desired Outcomes Section.

Every worktree created during a session has a corresponding session bookmark. When a session closes, all worktrees created during that session are removed or marked for cleanup. No worktree exists without a session bookmark unless the operator explicitly kept it. Next session teardown finds zero orphan worktrees. The teardown skill graduates from diagnostic to actionable. The operator leaves each session with a clean worktree inventory and a clear record of what was removed.

## The External Behavior Section.

### The Current Behavior Sub-section.

The teardown skill currently operates as a diagnostic tool only. It lists all worktrees and checks the `session.json` worktrees array for each worktree path. Worktrees without session bookmarks are flagged as orphans. The teardown reports findings and exits. No changes are made to the worktree inventory. The diagnostic output is accurate but useless for cleanup.

### The Desired Behavior Sub-section.

The teardown skill should operate as an actionable cleanup tool. It lists all worktrees and checks the `session.json` worktrees array for each worktree path. Worktrees without session bookmarks are flagged as orphans. The teardown evaluates each orphan against safety criteria. Safe orphans are offered for operator confirmation. Removed worktrees are logged in the teardown summary. The teardown report reflects both detected orphans and completed removals.

### The Safety Constraints Sub-section.

The teardown skill must never auto-remove worktrees without operator confirmation. The trunk worktree must never be offered for removal regardless of its state. Worktrees with uncommitted changes must never be removed. Worktrees that are the current working directory must never be removed. Worktrees with unmerged branches must be flagged but not offered for removal. These constraints protect the operator from accidental data loss. The safety rules are absolute and non-negotiable.

### The New Inputs Sub-section.

| Input | Source | Description |
|-------|--------|-------------|
| `WTLIST` | `git worktree list --porcelain` | All worktrees and their current states |
| `BOOKMARKS` | `session.json` worktrees array | Session bookmarks containing worktree paths |
| `OPERATOR_CONFIRM` | stdin | y/n confirmation response per orphan worktree |
| `WT_BRANCH` | `git -C "$wt" rev-parse --abbrev-ref HEAD` | Branch name for each worktree |
| `WT_STATUS` | `git -C "$wt" status --porcelain` | Dirty state of each worktree |
| `MERGE_STATUS` | `git merge-base --is-ancestor` | Whether branch is merged into trunk |

### The New Outputs Sub-section.

| Output | Destination | Description |
|--------|-------------|-------------|
| `orphan_worktrees` | teardown report | Orphan worktrees with their safety assessment |
| `removal_candidates` | operator prompt | Orphans that meet all safety criteria |
| `removal_summary` | SESSION-ROADMAP.md | Worktrees removed during this teardown session |

## The Acceptance Criteria Section.

Given an orphan worktree exists without a corresponding session bookmark entry:

AC1 establishes that uncommitted changes block removal offers. When the orphan worktree has uncommitted changes, the teardown skill flags it as unsafe to remove and does not offer it for operator removal. The teardown continues to the next orphan without prompting for this one.

AC2 establishes that unmerged branches block removal offers. When the orphan worktree branch is not fully merged into trunk, the teardown skill flags it as unsafe to remove and does not offer it for operator removal. The teardown continues to the next orphan without prompting for this one.

AC3 establishes that the current directory blocks removal offers. When the orphan worktree is the current working directory, the teardown skill flags it as unsafe to remove. The teardown continues to the next orphan without prompting for this one.

AC4 establishes that safety criteria enable removal offers. When the orphan worktree meets all safety criteria (clean, merged, not current directory), the teardown skill prompts the operator to confirm removal. The prompt shows the worktree path and branch name.

AC5 establishes that operator confirmation triggers removal. Upon operator confirmation, the teardown skill removes the worktree using `git worktree remove`. The removal is immediate and the worktree directory is deleted.

AC6 establishes that removals are logged in SESSION-ROADMAP.md. The teardown summary appended to SESSION-ROADMAP.md includes each removed worktree with its path and branch name. The log entry is human-readable and timestamped.

AC7 establishes that trunk is never removable. The trunk worktree is never offered for removal regardless of its state. Even if trunk appears as an orphan, the teardown skill explicitly excludes it from removal offers. This is a hardcoded safety rule.

AC8 establishes that successful removal clears the orphan. After teardown with operator approvals, running teardown again shows zero orphan worktrees. The removed worktrees no longer appear in `git worktree list`. New orphans can accumulate in future sessions.

## The Verification Section.

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1 | Manual test: create orphan with dirty state, run teardown, verify no removal offer appears | |
| AC2 | Manual test: create orphan with unmerged branch, run teardown, verify no removal offer appears | |
| AC3 | Manual test: from within orphan worktree directory, run teardown, verify no removal offer appears | |
| AC4 | Manual test: create orphan meeting all safety criteria, run teardown, verify removal prompt appears | |
| AC5 | Manual test: confirm removal prompt, verify `git worktree list` no longer shows the worktree | |
| AC6 | Manual test: after removal completes, check SESSION-ROADMAP.md for removal entry with path and branch | |
| AC7 | Manual test: attempt to trigger trunk removal offer, verify trunk is excluded from offers | |
| AC8 | Manual test: remove all orphans, run teardown again, verify zero orphan worktrees reported | |

## The Scope and Constraints Section.

### The In Scope Items Sub-section.

| Item | Description |
|------|-------------|
| Safety checks | Validate orphan worktrees before offering removal |
| Interactive confirmation | Prompt operator and parse y/n response |
| Removal logging | Append removed worktrees to SESSION-ROADMAP.md |
| Skill update | Modify swain-teardown SKILL.md step 1 and step 5 |

The scope covers all changes needed to make teardown actionable for orphan worktrees. The updates are confined to the teardown skill. No other skills or scripts require modification.

### The Out of Scope Items Sub-section.

| Item | Rationale |
|------|-----------|
| Auto-removal without confirmation | Operator must always approve worktree removal |
| Bookmark creation during worktree creation | Belongs in swain-session worktree flow |
| Bookmark cleanup during worktree removal | Separate concern requiring its own spec |
| External git host integration | Not applicable to local worktree management |
| Bulk removal modes | Interactive confirmation is the intended workflow |

These items are explicitly excluded to keep this spec focused. Each out-of-scope item could be a separate spec if needed.

## The Implementation Approach Section.

Three modifications are required in the swain-teardown SKILL.md file. Each modification targets a specific step in the existing teardown flow.

### The Step 1 Update Sub-section.

Extend the orphan worktree detection loop to include safety assessment. The loop iterates over all worktrees from `git worktree list`. For each worktree, it checks whether a bookmark exists. Orphan worktrees proceed through three safety checks: current directory, dirty state, and merge status. The safety assessment is stored in a `reason` variable and echoed alongside the orphan report.

```bash
for wt_path in $(git worktree list --porcelain | grep "^worktree " | cut -d' ' -f2-); do
  wt_branch="$(git -C "$wt_path" rev-parse --abbrev-ref HEAD 2>/dev/null)"
  is_orphan=true
  reason=""

  # Skip trunk worktree
  if [ "$wt_path" = "$REPO_ROOT" ]; then
    echo "protected: $wt_path (trunk)"
    continue
  fi

  # Check bookmark via session.json worktrees array
  if [ -f "$session_json" ] && jq -e -r '.worktrees[]?.path' "$session_json" 2>/dev/null | grep -qx "$wt_path"; then
    is_orphan=false
  fi

  if [ "$is_orphan" = true ]; then
    # Safety checks
    if [ "$wt_path" = "$(pwd)" ]; then
      reason="current directory"
    elif [ -n "$(git -C "$wt_path" status --porcelain)" ]; then
      reason="uncommitted changes"
    elif ! git merge-base --is-ancestor "$wt_branch" trunk 2>/dev/null; then
      reason="branch not fully merged"
    else
      reason="safe to remove"
    fi
    echo "orphan: $wt_path ($wt_branch) — $reason"
  fi
done
```

### The Step 1b Update Sub-section.

After the orphan report is displayed, collect safe orphans and prompt for confirmation. Safe orphans are those with `reason="safe to remove"`. The operator sees a list of removal candidates and enters y or n per worktree. The parsed responses are stored in an array for later execution.

```bash
removed_worktrees=()
for wt_info in $(git worktree list --porcelain | grep "^worktree " | cut -d' ' -f2-); do
  # Skip trunk and non-orphan worktrees
  if [ "$wt_info" = "$REPO_ROOT" ]; then continue; fi

  # Check via session.json worktrees array
  if [ -f "$session_json" ] && jq -e -r '.worktrees[]?.path' "$session_json" 2>/dev/null | grep -qx "$wt_info"; then continue; fi

  wt_branch="$(git -C "$wt_info" rev-parse --abbrev-ref HEAD 2>/dev/null)"
  if [ -n "$(git -C "$wt_info" status --porcelain)" ]; then continue; fi
  if ! git merge-base --is-ancestor "$wt_branch" trunk 2>/dev/null; then continue; fi

  echo "> Remove orphan worktree $wt_info ($wt_branch)? [y/N]"
  read -r response
  if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
    git worktree remove "$wt_info" 2>/dev/null && removed_worktrees+=("$wt_info ($wt_branch)")
  fi
done
```

### The Step 5 Update Sub-section.

Extend the SESSION-ROADMAP.md append to include removed worktrees. If the removal array has entries, a new subsection is added after the existing findings section. Each removed worktree is logged with its path and branch name.

```bash
if [ ${#removed_worktrees[@]} -gt 0 ]; then
  echo "" >> "$SROADMAP"
  echo "### Worktrees Removed During This Teardown" >> "$SROADMAP"
  echo "" >> "$SROADMAP"
  echo "The following orphan worktrees were removed with operator confirmation." >> "$SROADMAP"
  echo "" >> "$SROADMAP"
  for wt in "${removed_worktrees[@]}"; do
    echo "- $wt" >> "$SROADMAP"
  done
fi
```

### The Step 6 Update Sub-section.

Update the teardown summary template to reflect removals. The worktree state line now shows both orphan count and removal count. The format is "N orphan worktrees, M removed" or "clean" if no orphans remain.

## The Lifecycle Section.

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-02 | | Initial spec created |
| Complete | 2026-04-03 | | Implementation verified — swain-teardown v2.0.0, orphan detection with safety checks, session.json integration, operator confirm, SESSION-ROADMAP logging |
