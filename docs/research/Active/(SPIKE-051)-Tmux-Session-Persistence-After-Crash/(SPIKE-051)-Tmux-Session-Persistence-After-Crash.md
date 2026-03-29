---
title: "Session Crash Recovery"
artifact: SPIKE-051
track: container
status: Active
author: cristos
created: 2026-03-28
last-updated: 2026-03-28
question: "After a system crash, what state is lost, what survives, and how should swain detect and recover from abnormal session termination?"
gate: Pre-MVP
risks-addressed:
  - Session context lost on system crash or power failure
  - Dangling worktrees and stale git state left behind by crashed sessions
  - Stale locks, orphaned processes, and interrupted git operations block the next session
  - Operator must manually diagnose and clean up crash debris before resuming work
parent-epic: EPIC-039
evidence-pool: "agent-session-persistence@450cb05"
---

# Session Crash Recovery

## Summary

## Question

After a system crash, what state is lost, what survives, and how should swain detect and recover from abnormal session termination?

## Go / No-Go Criteria

- **Go**: swain can detect a crashed session, surface enough context for the operator to resume within 30 seconds, and clean up crash debris (stale locks, dangling worktrees, interrupted git operations) automatically or with minimal operator confirmation.
- **No-Go**: The crash debris landscape is too varied to handle reliably, or existing tools (swain-doctor, git worktree prune) already cover enough that a dedicated recovery flow adds no value.

## Pivot Recommendation

If a unified crash recovery flow is too complex, improve the existing piecemeal detection (swain-doctor for worktrees, swain-preflight for stale locks) with better crash-specific messaging, rather than building a new recovery system.

## Research Areas

### 1. Terminal multiplexer persistence (tmux, Zellij)

- Can tmux-resurrect/continuum or Zellij's native persistence restore terminal state after a hard crash?
- What survives vs. what's lost?

### 2. Agentic runtime session data

- What does Claude Code (and other runtimes) persist locally that survives a crash?
- Can crashed sessions be identified and mapped back to a project directory?

### 3. swain's own persistence layer

- What git-committed state (session.json, SESSION-ROADMAP.md, artifacts) survives?
- What about tk task state in `.tickets/`?

### 4. Crash debris — what breaks

- Dangling worktrees left by crashed sessions
- Git lock files (`.git/index.lock`, `MERGE_HEAD`, `rebase-merge/`)
- Stale tk claim locks
- Orphaned MCP server processes
- Stale status caches
- Hook state referencing dead processes

### 5. Relevant architectural decisions

- How do existing ADRs constrain crash recovery design?

## Findings

### Area 1: tmux-resurrect + tmux-continuum

**What they save:** All sessions, windows, panes, layouts, working directories, and a conservative list of running programs (vi, vim, nvim, emacs, man, less, top, htop, etc.). Stored as tab-delimited plaintext in `~/.tmux/resurrect/` with timestamped files and a `last` symlink.

**Crash resilience:** tmux-continuum auto-saves every 15 minutes (configurable down to 1 minute) by piggy-backing on the tmux `status-right` refresh. Save files survive hard crashes since they're regular files on disk. Edge case: crash *during* a save can produce a truncated file, but the `last` symlink usually still points to the previous good save.

**What is NOT restored:**
- Shell history (removed in PR #308)
- Scrollback buffer (optional but causes crashes on macOS — [#416](https://github.com/tmux-plugins/tmux-resurrect/issues/416))
- Environment variables ([#109](https://github.com/tmux-plugins/tmux-resurrect/issues/109))
- Running process state (programs are re-launched fresh, not resumed)
- SSH connections, background jobs

**macOS-specific risks:**
- Pane content capture (`@resurrect-capture-pane-contents`) causes tmux crashes on macOS — must leave OFF
- `reattach-to-user-namespace` wrappers with `&&`/`||` break pane restoration (modern tmux 3.2+ eliminates this need)
- Continuum auto-start requires macOS Accessibility permission grant

**Setup:** 3-5 lines in `~/.tmux.conf` plus TPM. **Critical fragility:** theme plugins that overwrite `status-right` silently break auto-save. Status-line must be enabled.

**Known reliability issues:** Empty/corrupt save files ([#115](https://github.com/tmux-plugins/tmux-resurrect/issues/115), [#403](https://github.com/tmux-plugins/tmux-resurrect/issues/403)), restore silently does nothing ([#513](https://github.com/tmux-plugins/tmux-resurrect/issues/513)), re-save corrupts restored sessions ([#392](https://github.com/tmux-plugins/tmux-resurrect/issues/392)).

**Verdict:** Protects tmux *layout* (panes, directories). Does NOT protect session *state* (what was running, environment, scrollback). Fragile on macOS. For swain, the layout is the least valuable part — and tmux-based swain-stage is being removed (SPEC-177) in favor of a browser-based workspace (INITIATIVE-015).

### Area 2: Agentic runtime session persistence (what already survives)

**Trove:** [`agent-session-persistence`](../../../troves/agent-session-persistence/manifest.yaml) — cross-runtime analysis of local session persistence for all five ADR-017 runtimes.

All five supported runtimes (Claude Code, Codex CLI, Gemini CLI, Copilot CLI, Crush) persist session data locally. The storage mechanisms differ but the pattern is consistent. See [synthesis](../../../troves/agent-session-persistence/synthesis.md) for the full comparison.

**Cross-runtime comparison:**

| Runtime | Storage | Location | Project-scoped | Crash-safe writes | Crash detection feasible |
|---------|---------|----------|---------------|-------------------|------------------------|
| Claude Code | Append-only JSONL | `~/.claude/` | Yes (`cwd` in PID files) | Yes | **Yes** — orphaned PID + cwd mapping |
| Codex CLI | JSONL + named sessions | `~/.codex/` | No (global) | Partial | No — no PID/project mapping |
| Gemini CLI | Files per session | `~/.gemini/tmp/<project_hash>/chats/` | Yes (project hash) | Partial | Maybe — when crash recovery ships |
| Copilot CLI | JSON + SQLite | `~/.copilot/session-state/` | Unclear | Yes | Partial — session files exist but no PID mapping |
| Crush | SQLite | `~/.local/share/opencode/` | Unclear | Yes (ACID) | No — no documented metadata |

**Claude Code is the only runtime where swain can reliably detect a crashed session and map it back to a project directory.** The PID-to-cwd mapping in `sessions/{pid}.json` is the key enabler.

**Claude Code session storage (`~/.claude/`):**

| Data | Location | Crash-safe | Maps to project |
|------|----------|------------|-----------------|
| Session metadata (PID, sessionId, cwd, startedAt) | `sessions/{pid}.json` | Yes | Yes — `cwd` field |
| Full conversation history | `projects/{path-slug}/{sessionId}.jsonl` | Yes | Yes — path-encoded slug |
| Global history log | `history.jsonl` | Yes | Yes — `project` + `sessionId` fields |
| File edit snapshots | `file-history/{sessionId}/` | Yes | Via sessionId lookup |
| Shell environment | `shell-snapshots/snapshot-zsh-{ts}.sh` | Yes | Indirect |
| Task execution cursor | `tasks/{sessionId}/.highwatermark` | Yes | Via sessionId |

**Crash detection pattern:** Scan `~/.claude/sessions/*.json` for orphaned PIDs (process no longer running but session file not cleaned up). Each file contains `{pid, sessionId, cwd, startedAt}` — enough to identify which project was active and link to the full conversation.

**Recovery path:**
```
Orphaned PID in sessions/{pid}.json
  → sessionId + cwd (project path)
  → projects/{encoded-path}/{sessionId}.jsonl (full conversation)
  → file-history/{sessionId}/ (file snapshots at message boundaries)
  → .agents/session.json (bookmark + focus lane)
```

**swain's git-committed state (also survives any crash):**

| Data | Source | Recovery |
|------|--------|----------|
| Last working branch | `session.json → lastBranch` | Bootstrap reads on start |
| Focus lane | `session.json → focus_lane` | Bootstrap reads on start |
| Context bookmark | `session.json → bookmark` | Bootstrap displays on start |
| Session goal + decisions | `SESSION-ROADMAP.md` | Git-committed, readable |
| Full artifact graph | `docs/` | Intact |
| Recent activity | `git log` | Intact |

**tk (ticket) task state — also crash-safe:**

All tk state lives in `.tickets/*.md` files (YAML frontmatter + markdown body). tk has no internal persistent state — it's a pure CLI that reads/writes these files.

| Data | Location | Survives crash | Recovery |
|------|----------|---------------|----------|
| Task status (open/in_progress/closed) | `.tickets/*.md` frontmatter | Yes | `tk ready` lists unblocked tasks |
| Task notes/history | `.tickets/*.md` body | Yes | Read directly |
| Task dependencies | `.tickets/*.md` `deps` field | Yes | `tk dep tree <id>` |
| Spec cross-references | `.tickets/*.md` `tags: [spec:SPEC-NNN]` | Yes | Query by tag |
| Claim locks | `.tickets/.locks/{id}/` | Partial — stale on crash | Manual cleanup needed |

**Key per ADR-015:** Tickets are *ephemeral*, scoped to worktree lifetime — not committed to trunk. They're discarded with worktree exit. But within a worktree, they survive crashes because they're regular files on disk.

**The gap with tk:** swain-session's bookmark captures a high-level note ("working on SPEC-174") but not which specific tk task was active. After a crash, the operator must run `tk ready` to see in-progress tasks. swain-do could update the bookmark with the current task ID when claiming work, enabling swain-session to surface it on recovery.

**Other runtimes:** OpenCode stores config at `~/.config/opencode/opencode.json` but no local conversation history (cloud-first). Gemini CLI, Codex, and Copilot CLI session storage not confirmed — likely cloud-first as well. Claude Code is the only runtime with rich local session persistence.

**The gap — what swain doesn't yet leverage:**
- swain-session doesn't read `~/.claude/sessions/` to detect crashed sessions
- No mapping from swain's session.json to Claude Code's sessionId (they're independent)
- No explicit session lifecycle marker (SPEC-119 will add start/close)
- swain-do doesn't write the active tk task ID to the bookmark
- Stale tk claim locks after crash (mkdir-based, no automatic cleanup)
- Terminal workspace layout (tmux-based swain-stage being removed per SPEC-177; browser-based replacement not yet available)

**Key insight:** The "continuity feel" comes primarily from *session context* (what was I working on? what's next? what decisions were made?) — not from terminal layout. Between Claude Code's local session persistence and swain's git-committed state, nearly everything needed for crash recovery already exists on disk. The missing piece is *detection and presentation* — swain-session needs to find the crashed session and surface the recovery context.

### Area 3: Hybrid approach analysis

The hybrid approach (tmux-continuum for layout + swain git state for context) adds complexity without proportional benefit:

- tmux-based swain-stage is being removed (SPEC-177), so there's no swain-managed tmux layout to persist
- The fragility of continuum on macOS (status-right hijacking, pane content crashes, theme conflicts) creates maintenance burden
- Two recovery paths (tmux plugin + swain native) means two things to debug when recovery fails
- Investing in tmux layout persistence is counter-directional when the workspace is moving to browser-based (INITIATIVE-015)

**Verdict:** Not recommended. The maintenance cost exceeds the marginal benefit over pure swain-native recovery.

### Area 4: Zellij as alternative

**Persistence model:** Zellij serializes session state to disk every 1 second (vs. tmux-continuum's 15-minute default). Stored as human-readable KDL layout files in `~/Library/Caches/org.Zellij-Contributors.Zellij/` on macOS. Survives hard reboots.

**Critical difference from tmux:** Zellij *replays commands* on resurrection (with a safety "Press ENTER to run..." banner), while tmux keeps live PTYs across detach/attach. For crash recovery specifically, this doesn't matter — tmux loses live PTYs on crash too.

**Advantages over tmux:**
- Built-in 1-second persistence (no plugin needed)
- Declarative KDL layouts (cleaner than shell-scripted tmux layouts)
- Native floating panes, WASM plugin system
- CLI returns pane IDs and supports `--json` output (better for scripting)
- `zellij action override-layout` for runtime layout changes

**Risks:**
- Sessions lost across Zellij version upgrades — no migration tool ([#3420](https://github.com/zellij-org/zellij/issues/3420))
- Multi-child command capture bug ([#4873](https://github.com/zellij-org/zellij/issues/4873)) — directly relevant if panes run `claude` or `nvim` with subprocesses
- 1,571 open issues vs. tmux's 67 — larger unresolved surface area
- 6 years old vs. tmux's 19 — less battle-tested
- Alt/Option key requires terminal-specific config on macOS

**Verdict:** Zellij's persistence is genuinely better than tmux's for crash recovery. But the version-upgrade session loss and the subprocess command capture bug are blocking. More importantly, swain is moving away from terminal multiplexer-managed workspaces entirely (INITIATIVE-015 → browser-based). Zellij is a data point for the persistence design of the new workspace, not a migration target.

### Area 5: Dangling worktrees

When a session crashes before `ExitWorktree` runs, the worktree directory and its git branch persist on disk indefinitely.

**Current detection (SPEC-044, Complete):** swain-doctor detects three classes at session start:

| Class | Detection | Current action |
|-------|-----------|---------------|
| Orphaned (directory missing, git ref dangling) | `git worktree list --porcelain` + `[ ! -d "$path" ]` | Warn, suggest `git worktree prune` |
| Stale (merged into trunk, directory exists) | `git merge-base --is-ancestor "$branch" origin/trunk` | Warn, suggest `git worktree remove` |
| Active (unmerged commits) | Branch has commits not in trunk | INFO only — may contain valuable work |

**The gap:** swain-doctor reports these as advisories but takes no action. After a crash, the operator must manually run cleanup commands. There's no distinction between "this worktree was left by a crashed session" vs. "this worktree belongs to a session running in another terminal."

**What's needed:** Cross-reference dangling worktrees with orphaned runtime sessions. If a worktree's branch name matches a dead session's working directory, it's crash debris. If it has uncommitted changes, surface them prominently — they may be the operator's last unsaved work.

### Area 6: Crash debris — git state and locks

A crash can leave several types of stale state that blocks the next session:

**Git lock files:**

| File | Created during | Effect if stale | Current swain handling |
|------|---------------|-----------------|----------------------|
| `.git/index.lock` | `git add`, `git commit` | Blocks ALL git operations | None — requires manual `rm` |
| `.git/MERGE_HEAD` | In-progress merge | Git thinks a merge is active | None — requires `git merge --abort` |
| `.git/rebase-merge/` | In-progress rebase | Git thinks a rebase is active | None — requires `git rebase --abort` |
| `.git/CHERRY_PICK_HEAD` | In-progress cherry-pick | Git thinks a cherry-pick is active | None — requires `git cherry-pick --abort` |

**None of these are detected by swain-doctor or swain-preflight today.** They're particularly likely after a crash during swain-sync (which runs git merge, commit, and push operations).

**tk claim locks:**

| File | Created during | Effect if stale | Current swain handling |
|------|---------------|-----------------|----------------------|
| `.tickets/.locks/{id}/` | `tk claim` | Prevents re-claiming the task | swain-preflight warns on locks >1 hour old |

**Orphaned processes:**

| Process | Created by | Effect if orphaned | Current swain handling |
|---------|-----------|-------------------|----------------------|
| MCP servers | Claude Code | May hold ports, consume resources | None |
| Pre-commit hooks | git commit | Stale lock files possible | None |
| File watchers (specwatch, trovewatch) | swain skills | Stale log files | None — logs recreated on restart |

### Area 7: Relevant ADRs

Four active ADRs constrain crash recovery design:

**ADR-011 (Worktree Landing Via Merge With Retry):** Worktree branches merge to trunk (not rebase). If a crash interrupts the merge-with-retry loop, the worktree may have a partial merge state. Recovery: `git merge --abort` in the worktree, then retry the sync.

**ADR-012 (Lifecycle Hashes Must Be Reachable From Main):** Bans squash-merge, force-push to main, and git filter-branch. Ensures lifecycle commit hashes in artifact tables survive any recovery operation. Crash recovery must not use destructive git operations.

**ADR-015 (Merge Tickets To Trunk, amended):** Originally declared tickets ephemeral; caused data loss when `ExitWorktree discard_changes: true` silently discarded unmerged commits. **Amended:** tickets are now committed coordination state. `ExitWorktree` must use `discard_changes: false` (default). Crash recovery should never auto-discard worktree state.

**ADR-018 (Structural Not Prosaic Session Invocation):** Session initialization is structural (CLI args), not prosaic (markdown directives). Crash recovery must also be structural — triggered by detectable state on disk, not by hoping the LLM reads a directive.

## Recommendation

**Build a unified crash recovery flow in swain-session that detects, cleans, and presents. Skip tmux plugins and Zellij.**

The research shows:
1. **The data is already there.** Between Claude Code's local session persistence (`~/.claude/sessions/`, `projects/`, `file-history/`), swain's git-committed state (session.json, SESSION-ROADMAP.md), and tk's ticket files, nearly everything needed for crash recovery already exists on disk.
2. **The debris is real.** Crashes leave dangling worktrees, git lock files, stale tk claim locks, interrupted merge/rebase state, and orphaned processes. Today these are scattered across swain-doctor, swain-preflight, and manual intervention with no unified crash-aware flow.
3. **The missing piece is detection + orchestration.** swain-session needs to: (a) detect that the previous session crashed, (b) clean up debris, (c) surface recovery context — as a single structural flow at session start.
4. tmux-resurrect/continuum and Zellij solve the wrong problem (terminal layout, not session context) and add fragility.
5. Per ADR-018, crash recovery must be structural (triggered by detectable state on disk), not prosaic.
6. Per ADR-015, crash recovery must never auto-discard worktree state.

The right move is three SPECs:

1. **Crash detection + context recovery** in swain-session bootstrap
2. **Crash debris cleanup** expanding swain-doctor/swain-preflight to handle git locks, dangling worktrees cross-referenced with dead sessions, and stale tk locks
3. **Persistence requirements for DESIGN-004** so the browser-based workspace is crash-resilient by design

## Proposed SPECs

### SPEC A: Crash Detection + Context Recovery in swain-session (recommended — high value)

On session start, swain-session detects whether a previous session for this project ended abnormally and surfaces recovery context.

**Detection mechanism (structural, per ADR-018):**
1. Scan `~/.claude/sessions/*.json` for entries where `cwd` matches the current project path (or a worktree under it)
2. Check if the PID is still running — if not, the session crashed or was killed
3. Cross-reference with swain's session.json for bookmark/lifecycle markers
4. Check for dangling worktrees whose branch names correlate with dead sessions (cross-reference `git worktree list` with orphaned PIDs)

**Recovery presentation:**
- Display the last bookmark and focus lane from `.agents/session.json`
- Show SESSION-ROADMAP.md summary (session goal, decisions, walk-away signal)
- Show in-progress tk tasks (`tk ready` or query for `status: in_progress`) so the operator knows exactly where they left off
- Show recent git log for "what was I doing?"
- Identify the crashed session's conversation log (`~/.claude/projects/{slug}/{sessionId}.jsonl`) and offer to reference it
- List dangling worktrees with uncommitted changes — these may contain the operator's last unsaved work
- Offer to re-enter the last worktree if it still exists and has unmerged work

**Runtime-agnostic design:** The detection mechanism should be pluggable. Claude Code's `sessions/` directory is the first implementation, but the interface should allow other runtimes to register their own session discovery paths (per ADR-017/ADR-018 multi-runtime support).

**Acceptance criteria:**
1. Given a crash (kill -9, reboot), when the next session starts, swain-session detects the orphaned session and displays recovery context
2. Given a normal session close, the next session starts normally (no false positive crash detection)
3. Recovery presents enough context that the operator can resume work within 30 seconds
4. Detection works for Claude Code sessions; other runtimes degrade gracefully (fall back to swain git state only)
5. In-progress tk tasks are surfaced as part of recovery context
6. Dangling worktrees correlated with dead sessions are identified and surfaced

### SPEC B: Crash Debris Cleanup in swain-doctor (recommended — safety)

Expand swain-doctor and swain-preflight to detect and clean crash debris that blocks the next session. Per ADR-015, never auto-discard worktree state — all destructive actions require operator confirmation.

**New checks:**

| Check | Detection | Action |
|-------|-----------|--------|
| Git index lock | `.git/index.lock` exists, creating PID not running | Offer to remove (safe — PID is dead) |
| Interrupted merge | `.git/MERGE_HEAD` exists | Offer `git merge --abort` |
| Interrupted rebase | `.git/rebase-merge/` exists | Offer `git rebase --abort` |
| Interrupted cherry-pick | `.git/CHERRY_PICK_HEAD` exists | Offer `git cherry-pick --abort` |
| Stale tk claim locks | `.tickets/.locks/{id}/` with dead PID or >1 hour old | Offer to remove |
| Dangling worktrees (crash-correlated) | Worktree branch matches dead session's cwd | Surface uncommitted changes, offer cleanup |
| Orphaned MCP servers | Process list matching MCP patterns for this project | Offer to kill |

**Integration with SPEC A:** swain-session's crash detection triggers debris cleanup before presenting recovery context. The operator sees a clean slate, not error messages from stale state.

**Acceptance criteria:**
1. Git lock files from dead processes are detected and removable with one confirmation
2. Interrupted git operations (merge, rebase, cherry-pick) are detected and abortable
3. Stale tk claim locks are detected and removable
4. No crash debris silently blocks the next session's git operations
5. Per ADR-015, no worktree state is auto-discarded — operator confirms all destructive actions

### SPEC C: Persistence requirements for browser-based workspace (input to DESIGN-004)

Document persistence requirements for the new browser-based swain-stage, informed by this spike's findings. Key requirements:
- Workspace state must be serialized to disk at least every 60 seconds (Zellij's 1-second model as benchmark)
- Recovery must not depend on the browser process surviving — state must be on disk
- swain-session's crash detection (SPEC A) should be able to trigger workspace reconstruction

This is a design input, not an implementation spec — it feeds into INITIATIVE-015/DESIGN-004.

### SPEC D: Zellij as workspace substrate (deferred)

Not recommended now. Version-upgrade session loss (#3420) and subprocess command capture bug (#4873) are blocking. More importantly, swain is moving to browser-based workspaces. Zellij's persistence model is useful as a *design reference* for DESIGN-004, not as an adoption target.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-28 | — | Initial creation |
