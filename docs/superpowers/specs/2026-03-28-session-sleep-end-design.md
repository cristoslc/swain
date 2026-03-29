# Session Sleep and End Operations

## Summary

Extend swain-session with two new operations — **sleep** and **end** — completing the session lifecycle. Sleep enables supervised autonomous work while the operator is away. End provides a graceful shutdown checklist that prevents entropy accumulation across sessions.

Both operations live in swain-session (not new skills) because they are the natural other end of the lifecycle that swain-session already manages (start, bookmark, focus, preferences).

## Design Decisions

- **Risk-tiered autonomy** over scope-locked autonomy. During sleep, the agent classifies actions by reversibility rather than requiring an explicit task list. Reversible actions proceed; irreversible actions are deferred.
- **Break enforcement via hook** over behavioral-only. A `UserPromptSubmit` hook code-blocks operator input before the agreed return time. The operator said they'd be away — the agent holds them to it. Ctrl-C is the only override. (Connects to operator sustainability — agentic addiction intervention.)
- **Deterministic scripts for deterministic work.** Time comparison, git merge detection, and session state management live in scripts. Risk classification and work prioritization live in skill prose.
- **Stop hook for time injection** over agent self-checking. The agent has no internal clock. A `Stop` hook evaluates checkpoint status deterministically and injects either "continue" or "checkpoint reached" — the agent doesn't interpret timestamps.
- **Claude Code first.** Hooks (`UserPromptSubmit`, `Stop`, `SessionEnd`) are Claude Code-specific. Other runtimes degrade to behavioral-only enforcement per ADR-017.

## Sleep Operation

### Trigger

Operator says "sleep", "I'm stepping away", "work while I'm gone", "keep going, back in 2 hours."

### Entry Sequence

1. Ask: "When will you be back?" Accept natural language ("2 hours", "tomorrow morning", "10pm"). Resolve to absolute ISO timestamp.
2. Record to `session.json`: `sleep: { start: "<ISO>", returnBy: "<ISO>", checkpointDone: false, deferredActions: [] }`
3. Acknowledge: "Got it. Working until `<time>`. Safe to walk away."

### Risk Tiers

| Tier | Actions | Behavior |
|------|---------|----------|
| **Autonomous** | Write code, run tests, commit to worktree, transition artifacts, claim/close tk tasks, create worktrees, bookmark updates, create files | Proceed without pause |
| **Deferred** | Push, merge to trunk, create PRs, create/close GitHub issues, post external comments, delete branches | Log to `sleep.deferredActions` in session.json, surface on return |

### Work Prioritization (soft constraints)

1. Finish current in-progress tk tasks
2. Claim and execute ready tasks in the current plan
3. If plan exhausts, pick up ready specs in the focus lane
4. If focus lane exhausts, idle with checkpoint

### Checkpoint Behavior

At `returnBy` time (detected via Stop hook — see below), the agent:

1. Writes a checkpoint summary to `docs/swain-retro/sleep-summary-<date>.md`
2. Opens it for the operator (it will be waiting when they return)
3. Continues working on autonomous-tier actions
4. If context window approaches exhaustion, stops and bookmarks

### Break Enforcement (`UserPromptSubmit` hook)

When `session.json` has `sleep.returnBy` and current time < `returnBy`:
- Hook outputs a message: "You said you'd be back at `<time>`. It's `<now>`. Session is in sleep mode — close this tab and come back later. Ctrl-C to force-override."
- Hook returns exit code 2 (blocks the prompt)

When current time >= `returnBy`:
- Clear sleep state from session.json
- Allow prompt through normally

### Stop Hook (checkpoint evaluator)

On every turn during sleep mode, the hook:

1. Reads `session.json` for sleep state
2. If no sleep state, outputs nothing (no-op)
3. If sleep state exists, runs `date` and compares to `returnBy`
4. If before `returnBy`: injects `{"decision": "continue"}` into context
5. If at or past `returnBy` and `checkpointDone` is false: injects `{"decision": "checkpoint", "returnBy": "<time>", "elapsed": "<duration>"}` and sets `checkpointDone: true` in session.json
6. If at or past `returnBy` and `checkpointDone` is true: injects `{"decision": "continue"}` (checkpoint already written, keep working)

### Graceful Degradation

On runtimes without `UserPromptSubmit` hooks (all except Claude Code), break enforcement is behavioral only — the SKILL prose instructs the agent to refuse operator input before `returnBy`. The Stop hook also degrades to behavioral (agent must remember to run `date`).

## End Operation

### Trigger

Operator says "end", "wrap up", "done for today", "clean up session", "shut it down."

### Sequence

1. **Dirty check** — run `git status`. If uncommitted changes exist, warn loudly: "Uncommitted changes detected — this shouldn't happen. Commit or discard before ending." Don't block.

2. **Open work check** — run `tk ready` and `tk status` for in-progress tasks. If any exist, surface: "N tasks still open: [list]. These will persist in the worktree for next session."

3. **Deferred actions check** — if sleep mode accumulated deferred actions, surface: "N deferred actions from sleep mode: [list]. These need operator attention in the next session."

4. **Worktree decision** — check if the worktree branch has been merged to trunk (all commits reachable from trunk):
   - **Merged:** "Worktree branch is merged to trunk. Cleaning up." → `ExitWorktree` with discard.
   - **Not merged:** "Worktree has unmerged work. Keeping for next session." → bookmark, leave worktree.

5. **Session retro** — invoke swain-retro with session scope. If working under an EPIC, retro attaches there. If cross-cutting, produces standalone session retro doc. Captures learnings while context is fresh.

6. **Final bookmark** — write summary with what was accomplished, what's pending, and any deferred actions.

7. **Inform operator:** "Session cleaned up. Safe to `/exit` or close the terminal."

### `SessionEnd` Hook (fire-and-forget safety net)

If the operator quits without running end (closes terminal, ctrl-c, etc.), the `SessionEnd` hook runs `swain-bookmark.sh` with a generic "session ended without cleanup" note. This is a safety net, not the primary path.

### Script: `swain-session-end.sh`

Performs the deterministic checks for the end sequence:
- Checks git status (dirty/clean)
- Checks if worktree branch is merged to trunk (all commits reachable)
- Checks for deferred actions in session.json
- Checks tk for open tasks

Outputs JSON:
```json
{
  "dirty": false,
  "merged": true,
  "deferredActions": 0,
  "openTasks": 3
}
```

The skill prose interprets the JSON and takes action (retro, bookmark, ExitWorktree, inform operator).

## New Files

| File | Purpose |
|------|---------|
| `skills/swain-session/scripts/swain-session-sleep.sh` | Records sleep state to session.json (start time, return time). Clears sleep state on return. |
| `skills/swain-session/scripts/swain-session-end.sh` | Deterministic end checks: git dirty, merge status, deferred actions, open tasks. Outputs JSON. |
| `skills/swain-session/scripts/swain-sleep-checkpoint-hook.sh` | Stop hook: reads sleep state, compares time, outputs continue/checkpoint decision. |
| `skills/swain-session/scripts/swain-sleep-enforce-hook.sh` | UserPromptSubmit hook: blocks operator input before return time. |

## Modified Files

| File | Changes |
|------|---------|
| `skills/swain-session/SKILL.md` | Add sleep and end operations to manual invocation section. Add risk tier table. Add hook configuration instructions. Version bump. |
| `session.json` schema | Add `sleep` object with `start`, `returnBy`, `checkpointDone`, `deferredActions` fields. |

## Hooks Configuration (Claude Code)

```json
{
  "hooks": {
    "Stop": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "bash skills/swain-session/scripts/swain-sleep-checkpoint-hook.sh",
        "timeout": 5
      }]
    }],
    "UserPromptSubmit": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "bash skills/swain-session/scripts/swain-sleep-enforce-hook.sh",
        "timeout": 5
      }]
    }],
    "SessionEnd": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "bash skills/swain-session/scripts/swain-bookmark.sh 'session ended without cleanup'",
        "timeout": 5
      }]
    }]
  }
}
```

## SPEC Decomposition (for swain-design)

This design decomposes into two SPECs:

1. **SPEC: Session sleep operation** — sleep entry, risk tiers (prose), work prioritization (prose), checkpoint behavior, Stop hook, UserPromptSubmit hook, sleep state in session.json, `swain-session-sleep.sh`, hook scripts, SKILL.md updates.

2. **SPEC: Session end operation** — end sequence, dirty/merge/task checks, worktree decision, retro invocation, final bookmark, SessionEnd hook, `swain-session-end.sh`, SKILL.md updates.

## Open Questions

- **Hook installation:** Should swain-init install these hooks during onboarding, or should swain-session install them on first invocation? (Recommendation: swain-init, since hooks are infrastructure.)
- **Sleep checkpoint format:** Should the sleep summary be a standalone markdown file in `docs/swain-retro/`, or a section appended to the session retro? (Recommendation: standalone, since it's mid-session not end-of-session.)
