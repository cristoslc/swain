---
name: swain-teardown
description: "End-of-session hygiene checks — orphan worktree detection, git dirty-state warning, ticket sync prompt, retro invitation, and handoff summary. Triggers on: 'teardown', 'clean up', 'wrap up', 'session end', 'end session', 'close session', 'log off', 'sign off', or automatically via swain-session close handler."
user-invocable: true
license: MIT
allowed-tools: Bash, Read, Glob
metadata:
  short-description: Session teardown hygiene checks before closing
  version: 1.0.0
  author: cristos
  source: swain
---
<!-- swain-model-hint: haiku, effort: low -->

# Session Teardown

<!-- session-check: SPEC-121 -->
Before running checks, verify an active session exists — unless `--session-chain` is passed (which means swain-session already confirmed session state):

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$REPO_ROOT/.agents/bin/swain-session-check.sh" 2>/dev/null
```
If `session-chain` is NOT passed and the JSON output has `"status"` other than `"active"`, inform the operator: "No active session to tear down." Exit cleanly with code 0.

---

## What this skill does

Session teardown runs a sequence of hygiene checks before a session closes:

1. Orphan worktree detection — finds worktrees with no corresponding session bookmark
2. Git dirty-state check — surfaces uncommitted changes before the operator leaves
3. Ticket sync prompt — prompts the operator to verify tickets match what was done
4. Retro invitation — invites the operator to capture session learnings via swain-retro
5. Handoff summary — appends a session summary to SESSION-ROADMAP.md

---

## Step 1 — Orphan worktree check

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Get all worktrees
git worktree list --porcelain 2>/dev/null | grep "^worktree " | while read -r line; do
  wt_path="${line#worktree }"
  wt_branch="$(git -C "$wt_path" rev-parse --abbrev-ref HEAD 2>/dev/null)"

  # Check if this worktree has a session bookmark
  bookmark_file="$REPO_ROOT/.agents/bookmarks.txt"
  if [ -f "$bookmark_file" ] && grep -q "$wt_path" "$bookmark_file" 2>/dev/null; then
    echo "linked: $wt_path ($wt_branch)"
  else
    echo "orphan: $wt_path ($wt_branch)"
  fi
done
```

If orphan worktrees are found, display them as findings with the message: "The following worktrees have no active session bookmark — consider removing them."

If `--session-chain` is passed, skip the orphan worktree check (worktrees are managed during session lifecycle).

---

## Step 2 — Git dirty-state check

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

cd "$REPO_ROOT"
git_status=$(git status --porcelain 2>/dev/null)

if [ -n "$git_status" ]; then
  echo "WARN: Dirty git working tree — uncommitted changes detected."
  echo "Changes:"
  echo "$git_status" | head -20
else
  echo "OK: Working tree is clean."
fi
```

Report findings with an actionable recommendation.

---

## Step 3 — Ticket sync prompt

Ask the operator to verify ticket state:

> "Before closing, verify that tickets match what was done. Run `tk issue list` and confirm open tickets are accurate. Any tickets to close or update?"

Wait for a response. Do not modify tickets automatically.

---

## Step 4 — Retro invitation

Invoke swain-retro for session learnings capture:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SWAIN_RETRO_SKILL="$REPO_ROOT/.claude/skills/swain-retro/SKILL.md"

# Invoke retro invitation via Skill tool
Skill("$SWAIN_RETRO_SKILL", "Manual retro invite — session has closed. Run /swain-retro to capture session learnings and invite the operator to reflect on what was accomplished.")
```

If swain-retro is not available, note the skip in the findings and continue.

---

## Step 5 — Handoff summary

Append a session summary to SESSION-ROADMAP.md:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SROADMAP="$REPO_ROOT/SESSION-ROADMAP.md"
session_id="$(jq -r '.session_id // empty' "$REPO_ROOT/.agents/session-state.json" 2>/dev/null)"
focus_lane="$(jq -r '.focus_lane // empty' "$REPO_ROOT/.agents/session-state.json" 2>/dev/null)"

if [ -n "$session_id" ]; then
  {
    echo ""
    echo "## Session $session_id Handoff"
    echo ""
    echo "**Focus lane:** ${focus_lane:-none}"
    echo "**Closed:** $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo ""
    echo "### Findings"
    echo ""
    echo "_(Populated from teardown checks above)_"
  } >> "$SROADMAP"
fi
```

If SESSION-ROADMAP.md does not exist, create it with a header first, then append.

---

## Step 6 — Report findings

After all checks, display a summary:

```
=== Session Teardown Summary ===

Worktree state:     {clean | N orphan worktrees found}
Git state:          {clean | dirty — see uncommitted changes above}
Ticket sync:        {confirmed | pending operator check}
Retro:              {invited | skipped (not available)}
Handoff summary:    {written to SESSION-ROADMAP.md | skipped}

Session teardown complete.
```

Exit with code 0 unless a critical error occurred.

---

## Error handling

| Situation | Response |
|-----------|----------|
| No active session (without --session-chain) | Report cleanly, exit 0 |
| Git unavailable | Skip git check, note in report |
| Worktree list fails | Skip worktree check, note in report |
| Session state file missing | Note absence, continue with available checks |
| SESSION-ROADMAP.md missing | Create with header, append summary |
| Retro not available | Note skip, continue with remaining checks |

---

## Integration with swain-session

swain-session calls this skill from the close handler after progress-log.sh and before committing SESSION-ROADMAP.md:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SWAIN_TEARDOWN_SKILL="$REPO_ROOT/.claude/skills/swain-teardown/SKILL.md"

# Run teardown as session chain (swain-session already confirmed session state)
Skill("$SWAIN_TEARDOWN_SKILL", "Session teardown — --session-chain flag passed from swain-session close handler.")
```

The `--session-chain` flag is embedded in the prompt args. The skill checks for this flag and skips the redundant session-active check.
