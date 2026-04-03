---
title: "Session Crash Recovery"
artifact: SPIKE-051
track: container
status: Complete
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

**Go — build a pre-runtime `swain` script as the structural crash recovery layer.**

Terminal multiplexer persistence (tmux-resurrect, Zellij) solves the wrong problem — session *context* matters more than terminal *layout*, and swain is moving away from tmux anyway (SPEC-177, INITIATIVE-015). The real finding: agentic runtimes (especially Claude Code) already persist rich session data locally, and swain's git-committed state (bookmark, focus, SESSION-ROADMAP.md, tk tasks) survives any crash. The missing piece is a pre-runtime structural layer that detects crashed sessions, cleans debris (git locks, stale tk locks, dangling worktrees), and composes resume context for the runtime — all in bash, before any LLM starts. Proposes 5 SPECs: pre-runtime script (A), shell function refactor (B), debris checks (C), DESIGN-004 persistence requirements (D), Zellij deferred (E).

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

**ADR-024 (Merge Tickets To Trunk, amended):** Originally declared tickets ephemeral; caused data loss when `ExitWorktree discard_changes: true` silently discarded unmerged commits. **Amended:** tickets are now committed coordination state. `ExitWorktree` must use `discard_changes: false` (default). Crash recovery should never auto-discard worktree state.

**ADR-018 (Structural Not Prosaic Session Invocation):** Session initialization is structural (CLI args), not prosaic (markdown directives). Crash recovery must also be structural — triggered by detectable state on disk, not by hoping the LLM reads a directive.

### Area 8: Pre-runtime structural layer (architectural implication of ADR-018)

ADR-018 mandates structural session invocation — but today, all crash detection and session state checks happen *inside* the agentic runtime (in swain-session skill code). This creates a fundamental problem: the runtime must be running before crash recovery can happen, but the crashed runtime's debris may block the new runtime from starting cleanly.

**The insight:** Crash detection, session resume selection, and debris cleanup must happen **before** the agentic runtime starts. This implies a separation:

**`swain` script (project root, checked into repo):**
- Runs *before* any agentic runtime — the single entry point for all swain sessions
- **Phase 1 — Pre-runtime structural checks:**
  - Detect crashed sessions (scan `~/.claude/sessions/`, `~/.copilot/session-state/`, etc.)
  - Clean crash debris (git locks, stale tk locks, dangling worktrees) with operator confirmation
  - Detect available runtimes installed on the system
- **Phase 2 — Session selection:**
  - If previous sessions exist (crashed or cleanly closed), present the operator with options: resume a specific session, start fresh, or enter a dangling worktree with unmerged work
  - Compose an initial prompt based on the operator's choice (e.g., if resuming: pass context about the crashed session, bookmark, focus lane, and in-progress tasks to the runtime's initial prompt so `/swain-session` can act on it)
- **Phase 3 — Runtime invocation:**
  - Resolve runtime preference: per-project (`swain.settings.json → runtime`) > global (`~/.config/swain/settings.json → runtime`) > auto-detect from installed runtimes (per ADR-017)
  - Launch with correct flags per ADR-017 support tiers (e.g., `claude --dangerously-skip-permissions`, `gemini -y -i`, `codex --full-auto`)
  - Pass `/swain-init` (fresh start) or `/swain-session` with resume context (crash recovery) as the initial prompt
  - For Partial-tier runtimes (Crush) that can't accept an initial prompt, start bare and rely on AGENTS.md
- Pure bash — no LLM dependency, no skill system, works even if the runtime is broken, testable independently

**`swain` shell function (user dotfiles, installed by swain-init):**
- Sole responsibility: find and run the project-root `swain` script
- Looks for the script at: `./swain`, `./.agents/bin/swain`, then falls back
- If no script found, falls back to the current behavior (detect runtimes, invoke with `/swain-init`) — graceful degradation for projects that haven't adopted the script yet
- No crash detection, no debris cleanup, no session selection — all that lives in the script
- Passes through any CLI arguments to the script (e.g., `swain --fresh` to skip resume)

**Why this matters for crash recovery:**
- Crash debris cleanup happens in bash, not in an LLM session — deterministic, fast, no token cost
- Session resume selection happens interactively in the terminal — the operator chooses before the runtime starts, not after the LLM has already initialized with a default context
- The script can be tested and versioned independently of the skill system
- Other runtimes (Gemini, Codex, Copilot, Crush) get crash recovery for free because it runs before runtime-specific code

**Relationship to existing architecture:**
- The `swain` shell function today (from EPIC-045) is a thin launcher that detects runtimes and passes `/swain-init` as the initial prompt
- The proposed `swain` script would replace the structural parts of swain-session's bootstrap (crash detection, worktree detection, session.json loading) with a pre-runtime equivalent
- swain-session would still handle in-session bookmarking, focus lane, and context management — but no longer be responsible for crash recovery

## Recommendation

**Build a pre-runtime structural layer for crash recovery. Separate the `swain` user CLI from structural state checks. Skip tmux plugins and Zellij.**

The research shows:
1. **The data is already there.** Between runtime session persistence (`~/.claude/sessions/`, `~/.copilot/session-state/`, etc.), swain's git-committed state (session.json, SESSION-ROADMAP.md), and tk's ticket files, nearly everything needed for crash recovery already exists on disk.
2. **The debris is real.** Crashes leave dangling worktrees, git lock files, stale tk claim locks, interrupted merge/rebase state, and orphaned processes. Today these are scattered across swain-doctor, swain-preflight, and manual intervention with no unified crash-aware flow.
3. **Crash recovery must happen before the runtime starts** (Area 8). The current approach — running crash detection inside swain-session skill code — is fundamentally wrong because the runtime must be running before the skill can execute, but crash debris may block the runtime from starting cleanly.
4. Per ADR-018, crash recovery must be structural (bash script, detectable state on disk), not prosaic (LLM reading markdown).
5. Per ADR-015, crash recovery must never auto-discard worktree state.
6. tmux-resurrect/continuum and Zellij solve the wrong problem (terminal layout, not session context) and add fragility.

The right architecture is four SPECs:

1. **Pre-runtime `swain` script** — crash detection, debris cleanup, session resume selection, runtime invocation
2. **`swain` shell function refactor** — find/run the script, fallback gracefully, respect runtime preferences
3. **Crash debris checks** — expand swain-doctor/swain-preflight for the pre-runtime script to call
4. **Persistence requirements for DESIGN-004** — so the browser-based workspace is crash-resilient by design

## Proposed SPECs

### SPEC A: Pre-runtime `swain` script (recommended — architectural, high value)

A bash script at the project root (or `.agents/bin/swain`) that is the single structural entry point for all swain sessions. Subsumes the runtime detection and invocation logic currently in the shell function, and adds crash recovery.

**Phase 1 — Pre-runtime structural checks:**
1. **Crash detection** — scan runtime session directories for orphaned PIDs associated with this project:
   - Claude Code: `~/.claude/sessions/*.json` → check `cwd`, verify PID alive
   - Copilot CLI: `~/.copilot/session-state/` → scan session files
   - Gemini CLI: `~/.gemini/tmp/<project_hash>/chats/` → check for stale sessions
   - Other runtimes: degrade gracefully to swain git state only
2. **Debris cleanup** — detect and offer to clean crash debris before the runtime starts:
   - Git lock files (`.git/index.lock`, `MERGE_HEAD`, `rebase-merge/`, `CHERRY_PICK_HEAD`)
   - Stale tk claim locks (`.tickets/.locks/`)
   - Dangling worktrees cross-referenced with dead sessions
   - Per ADR-015: never auto-discard — all destructive actions require operator confirmation

**Phase 2 — Session selection:**
- If crashed sessions are detected, present the operator with options:
  - Resume a specific crashed session (the script composes an initial prompt with crash context — bookmark, focus lane, in-progress tk tasks, conversation log path — so `/swain-session` receives it)
  - Enter a dangling worktree that has unmerged work
  - Start fresh (skip recovery)
- If no crashed sessions, proceed directly to runtime invocation

**Phase 3 — Runtime invocation:**
1. Resolve runtime preference: per-project (`swain.settings.json → runtime`) > global (`~/.config/swain/settings.json → runtime`) > auto-detect from installed runtimes (per ADR-017)
2. Launch with correct flags per ADR-017 support tiers:
   - Claude Code: `claude --dangerously-skip-permissions "<initial-prompt>"`
   - Gemini CLI: `gemini -y -i "<initial-prompt>"`
   - Codex CLI: `codex --full-auto "<initial-prompt>"`
   - Copilot CLI: `copilot --yolo -i "<initial-prompt>"`
   - Crush: `crush --yolo` (no initial prompt — Partial tier)
3. Initial prompt is either `/swain-init` (fresh start) or `/swain-session` with resume context (crash recovery), composed by the script based on Phase 2 selection
4. For crash recovery, the initial prompt includes structured context: `"Resume session: bookmark='<note>', focus='<lane>', worktree='<path>', tasks='<in-progress-ids>'"`

**Pure bash** — no LLM dependency, no skill system, deterministic, fast, no token cost, testable independently.

**Acceptance criteria:**
1. Given a crash (kill -9, reboot), running `swain` detects the orphaned session and presents recovery options before the runtime starts
2. Given a normal session, `swain` starts the runtime with no visible delay (fast path — skip Phase 2 when no crash detected)
3. Crash debris (git locks, stale tk locks) is cleaned before the runtime sees it
4. Runtime selection respects per-project > global > auto-detect preference chain
5. The selected runtime receives the correct flags and initial prompt per ADR-017
6. Session resume context is passed structurally to the runtime so swain-session can act on it (not rely on the LLM reading a markdown note)
7. The script is testable independently of any runtime (pure bash, no LLM)

### SPEC B: `swain` shell function refactor (recommended — enables SPEC A)

Refactor the `swain` shell function (installed by swain-init into user dotfiles) to be a thin wrapper that finds and runs the project-root script.

**Behavior:**
1. If a `swain` script exists at the project root (or `.agents/bin/swain`), exec it — it handles everything (crash detection, runtime selection, invocation)
2. If no script exists, fall back to the current behavior (detect runtimes, invoke with `/swain-init`) — graceful degradation for projects that haven't adopted the script yet
3. Pass through any CLI arguments (e.g., `swain --fresh` to skip resume, `swain --runtime gemini` to override preference)
4. No crash detection, no debris cleanup, no session selection, no runtime preference resolution — all that lives in the script

**Acceptance criteria:**
1. `swain` in a project with the script runs the script (which handles everything)
2. `swain` in a project without the script falls back to direct runtime invocation (current behavior)
3. CLI arguments are forwarded to the script
4. The function remains a thin wrapper — under 20 lines of shell

### SPEC C: Crash debris detection checks (recommended — safety, enables SPEC A)

Implement the individual crash debris checks as standalone bash functions that the pre-runtime script (SPEC A) can call. Also callable by swain-doctor for in-session health checks.

**Checks:**

| Check | Detection | Action |
|-------|-----------|--------|
| Git index lock | `.git/index.lock` exists, creating PID not running | Offer to remove |
| Interrupted merge | `.git/MERGE_HEAD` exists | Offer `git merge --abort` |
| Interrupted rebase | `.git/rebase-merge/` exists | Offer `git rebase --abort` |
| Interrupted cherry-pick | `.git/CHERRY_PICK_HEAD` exists | Offer `git cherry-pick --abort` |
| Stale tk claim locks | `.tickets/.locks/{id}/` with dead PID or >1 hour old | Offer to remove |
| Dangling worktrees (crash-correlated) | Worktree branch matches dead session's cwd | Surface uncommitted changes, offer cleanup |
| Orphaned MCP servers | Process list matching MCP patterns for this project | Offer to kill |

**Acceptance criteria:**
1. Each check is a standalone function callable from the pre-runtime script or swain-doctor
2. Git lock files from dead processes are detected and removable with one confirmation
3. No crash debris silently blocks the next session's git operations
4. Per ADR-015, no worktree state is auto-discarded

### SPEC D: Persistence requirements for browser-based workspace (input to DESIGN-004)

Document persistence requirements for the new browser-based swain-stage, informed by this spike's findings. Key requirements:
- Workspace state must be serialized to disk at least every 60 seconds (Zellij's 1-second model as benchmark)
- Recovery must not depend on the browser process surviving — state must be on disk
- The pre-runtime script (SPEC A) should be able to trigger workspace reconstruction

This is a design input, not an implementation spec — it feeds into INITIATIVE-015/DESIGN-004.

### SPEC E: Zellij as workspace substrate (deferred)

Not recommended now. Version-upgrade session loss (#3420) and subprocess command capture bug (#4873) are blocking. More importantly, swain is moving to browser-based workspaces. Zellij's persistence model is useful as a *design reference* for DESIGN-004, not as an adoption target.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-28 | — | Initial creation |
| Complete | 2026-03-28 | — | Research complete; Go verdict; 5 proposed SPECs |
