# Agent Session Persistence — Synthesis

Cross-runtime analysis of local session persistence for the five runtimes supported by swain (per ADR-017).

## Key Findings

### All five runtimes persist session data locally

Every supported runtime writes session state to disk. The storage mechanisms differ but the pattern is consistent: conversations are logged locally and can (to varying degrees) be resumed.

| Runtime | Storage mechanism | Location | Project-scoped | Crash-safe writes |
|---------|------------------|----------|---------------|-------------------|
| Claude Code | Append-only JSONL | `~/.claude/` | Yes (`cwd` in session metadata, path-encoded project dirs) | Yes (append-only, per-message) |
| Codex CLI | JSONL + named sessions | `~/.codex/` | No (global) | Partial (transport failures can prevent persistence) |
| Gemini CLI | Files per session | `~/.gemini/tmp/<project_hash>/chats/` | Yes (project hash) | Partial (crash recovery not yet implemented) |
| Copilot CLI | JSON files + SQLite | `~/.copilot/session-state/` + `session-store.db` | Unclear (not documented) | Yes (incremental writes + reindexing fallback) |
| Crush (OpenCode) | SQLite | `~/.local/share/opencode/opencode.db` | Unclear (likely via CWD metadata) | Yes (ACID guarantees) |

### Claude Code has the richest local persistence

Claude Code is the only runtime that provides all of:
- Per-PID session metadata with explicit `cwd` mapping (`sessions/{pid}.json`)
- Append-only conversation logs (crash-safe by design)
- File edit snapshots at message boundaries
- Shell environment snapshots
- A global history index (`history.jsonl`) cross-referencing sessions to projects

This makes it the only runtime where swain can reliably detect a crashed session and map it back to a specific project directory.

### Project-to-session mapping varies widely

- **Claude Code**: Explicit — `sessions/{pid}.json` contains `cwd`, `projects/` uses path-encoded slugs
- **Gemini CLI**: Explicit — `project_hash` in the storage path
- **Codex CLI**: Not project-scoped — sessions are global
- **Copilot CLI**: Not documented — may be in session files but not exposed
- **Crush**: Not documented — likely in SQLite records

### Crash recovery maturity varies

- **Claude Code**: Mature — append-only JSONL means data survives crashes; `/resume` works
- **Copilot CLI**: Good — incremental writes to session files; reindexing recovers data missed by SQLite flush
- **Crush**: Good at data layer (SQLite ACID) — but no documented crash detection or recovery UX
- **Codex CLI**: Improving but fragile — transport failures can leave sessions unrecoverable
- **Gemini CLI**: Weakest — crash recovery explicitly requested as a feature ([#11758](https://github.com/google-gemini/gemini-cli/issues/11758)) but not yet implemented

## Points of Agreement

1. **Local-first persistence**: All runtimes store session data on the local filesystem, not cloud-only
2. **Resume capability**: All support some form of session resume (varying reliability)
3. **Append-only or transactional writes**: The more mature runtimes use crash-safe write patterns (JSONL append or SQLite transactions)

## Points of Disagreement

1. **Project scoping**: Claude Code and Gemini scope sessions to projects; others are global or undocumented
2. **Crash detection**: Only Claude Code provides enough metadata (PID files, cwd mapping) for an external tool to detect and identify crashed sessions
3. **Storage format**: Split between JSONL (Claude Code, Codex) and SQLite (Copilot, Crush), with Gemini using plain files

## Gaps

1. **No runtime exposes a "session crashed" signal**: All detection must be inferred from orphaned PIDs, stale files, or missing close markers
2. **Cross-runtime session discovery**: No standard for finding sessions across different runtimes for the same project
3. **Crash debris cleanup**: No runtime handles stale git locks, dangling worktrees, or interrupted operations left by the crash
4. **Session-to-task mapping**: No runtime links sessions to external task trackers — this is swain-specific state

## Implications for SPIKE-051

1. **Claude Code is the only viable target for crash detection** — the PID-to-cwd mapping in `sessions/{pid}.json` is the key enabler. Other runtimes would need runtime-specific adapters that may not be feasible given their storage designs.
2. **A pluggable detection interface is the right design** — implement Claude Code first, add others as their crash recovery matures. Gemini's `project_hash` path structure could work once crash recovery ships.
3. **swain's value-add is the crash debris layer** — no runtime handles git locks, worktree cleanup, or task state recovery. This is uniquely swain's responsibility regardless of which runtime is used.
