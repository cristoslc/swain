# opencode-worktree Snapshot

> Cloned from https://github.com/kdcokenny/opencode-worktree on 2026-04-23

## 1. Project Structure

```
opencode-worktree/
├── .git/
├── LICENSE                    # MIT License, Copyright (c) 2026 Kenny
├── README.md                  # Full documentation (254 lines)
└── src/
    └── plugin/
        ├── worktree.ts        # Main plugin entry point (1106 lines)
        ├── worktree/
        │   ├── launch-context.ts   # OCX/plain launch mode detection (153 lines)
        │   ├── state.ts            # SQLite session/pending-op state (502 lines)
        │   └── terminal.ts          # Cross-platform terminal spawning (1375 lines)
        └── kdco-primitives/
            ├── index.ts             # Barrel exports (26 lines)
            ├── get-project-id.ts    # Git root commit → project ID (172 lines)
            ├── log-warn.ts         # OpenCode client or console warning (51 lines)
            ├── mutex.ts            # Promise-based mutex (122 lines)
            ├── shell.ts            # Bash/AppleScript/Batch escaping (138 lines)
            ├── temp.ts             # Symlink-aware temp dir (36 lines)
            ├── terminal-detect.ts  # tmux detection via TMUX env var (34 lines)
            ├── types.ts            # OpencodeClient type alias (13 lines)
            └── with-timeout.ts     # Promise timeout wrapper (84 lines)
```

No `package.json`, `tsconfig.json`, or build configuration files in the repo — this is a source-only facade repo. The build/publish pipeline lives in the [OCX monorepo](https://github.com/kdcokenny/ocx).

## 2. How It Manages Git Worktrees

### Auto-Spawning Terminals

The plugin exposes two tools to the OpenCode AI agent:

1. **`worktree_create(branch, baseBranch?)`** — Creates an isolated git worktree and opens a terminal with OpenCode running inside it:
   - Validates branch name (blocks shell metacharacters, git ref violations)
   - Detects launch context: **OCX mode** (with `OCX_CONTEXT`, `OCX_BIN`, `OCX_PROFILE` env vars) or **plain mode** (bare `opencode --session`)
   - Calls `git worktree add` to create the worktree at `~/.local/share/opencode/worktree/<project-id>/<branch>`
   - Syncs configured files/symlinks from the main worktree
   - Runs `postCreate` hook commands (e.g., `pnpm install`)
   - Forks the current OpenCode session (copies plan.md and delegations)
   - **Spawns a new terminal** with OpenCode already running in the worktree directory

2. **`worktree_delete(reason)`** — Marks the worktree for deletion on session idle:
   - Sets a pending delete operation in SQLite
   - On `session.idle` event: runs `preDelete` hooks, `git add -A` + `git commit`, `git worktree remove --force`, clears state

### Terminal Detection & Spawning

Detection priority (`terminal.ts:329-340`):

1. **tmux** — If `TMUX` env var is set → creates a new tmux window (mutex-serialized to prevent socket races)
2. **cmux** — If `CMUX_WORKSPACE_ID` or (`CMUX_SOCKET_PATH` + `CMUX_SOCKET_MODE=allowAll`) → uses `cmux new-workspace`
3. **Platform detection** — Falls back to OS-specific terminal:
   - **macOS**: Ghostty (inline command), iTerm2 (AppleScript), Kitty (`@ launch` tab → new window), Alacritty, Warp (launch config YAML), Terminal.app
   - **Linux**: Kitty, WezTerm, Alacritty, Ghostty, Warp, Foot, GNOME Terminal, Konsole, XFCE4 Terminal, xterm — with `xdg-terminal-exec` and `x-terminal-emulator` fallbacks
   - **Windows/WSL**: Windows Terminal (`wt.exe`) → `cmd.exe` fallback

All detached spawns use self-cleaning scripts (`trap 'rm -f "$0"' EXIT`) to avoid temp file leaks.

### File Syncing

Configured via `.opencode/worktree.jsonc` (auto-created on first use):

- **`sync.copyFiles`** — Copy specific files (e.g., `.env`, `.env.local`) from main worktree
- **`sync.symlinkDirs`** — Symlink directories (e.g., `node_modules`) to save disk space
- **`sync.exclude`** — Patterns to exclude from copying (reserved for future use)
- Path traversal protection: rejects `..`, absolute paths, and resolved paths outside base dir

### Cleanup on Exit

- **Database-backed state**: SQLite at `~/.local/share/opencode/plugins/worktree/<project-id>.sqlite` with WAL mode and `busy_timeout=5000`
- **Process cleanup handlers**: `SIGTERM`, `SIGINT`, `beforeExit` trigger WAL checkpoint + DB close
- **Pending operations**: Singleton row in `pending_operations` table — `setPendingDelete` replaces any existing pending op (spawn or delete)
- **Session tracking**: `sessions` table with columns for id, branch, path, createdAt, launchMode, profile, ocxBin
- **Migration-safe**: `ensureSessionLaunchMetadataColumns()` adds columns idempotently

### Session Forking

When creating a worktree, the plugin:
1. Forks the current OpenCode session via `client.session.fork()`
2. Copies `plan.md` from `~/.local/share/opencode/workspace/<project-id>/<rootSessionId>/`
3. Copies delegation data from `~/.local/share/opencode/delegations/<project-id>/<rootSessionId>/`
4. On fork failure: cleans up forked session, workspace dir, and delegations dir
5. Builds launch argv based on mode: `[opencode, --session, <id>]` or `[ocxBin, opencode, -p, profile, --session, <id>]`

## 3. License

**MIT License** — Copyright (c) 2026 Kenny. Full text available in `LICENSE`.

Key points:
- Permissive commercial use, modification, distribution, sublicense
- Must include copyright notice and permission notice in copies
- Provided AS IS, no warranty

## 4. Key Configuration Files

### `.opencode/worktree.jsonc` (auto-created)

```jsonc
{
  "$schema": "https://registry.kdco.dev/schemas/worktree.json",
  "worktreePath": "~/my-worktrees",  // optional, supports ~
  "sync": {
    "copyFiles": [],      // files to copy from main worktree
    "symlinkDirs": [],    // directories to symlink
    "exclude": []          // patterns to exclude (future)
  },
  "hooks": {
    "postCreate": [],      // commands after creation (e.g., "pnpm install")
    "preDelete": []         // commands before deletion (e.g., "docker compose down")
  }
}
```

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `OCX_CONTEXT=1` | Marks OCX launch mode |
| `OCX_BIN` | Path to OCX binary (required if `OCX_CONTEXT=1`) |
| `OCX_PROFILE` | OCX profile name (required if `OCX_CONTEXT=1`) |
| `CMUX_WORKSPACE_ID` | cmux workspace context (triggers cmux terminal) |
| `CMUX_SOCKET_PATH` + `CMUX_SOCKET_MODE` | cmux socket control |
| `TMUX` | tmux session detection |

### Project ID Resolution

- Primary: first git root commit SHA (40-char hex) — stable across renames
- Fallback: SHA-256 hash of project path (16-char hex) — for non-git repos
- Cached in `.git/opencode` (or shared `.git` for worktrees)

### Data Paths

| Path | Purpose |
|------|---------|
| `~/.local/share/opencode/worktree/<project-id>/<branch>/` | Worktree checkout |
| `~/.local/share/opencode/plugins/worktree/<project-id>.sqlite` | Session state DB |
| `~/.local/share/opencode/workspace/<project-id>/<sessionId>/` | OpenCode workspace (plan.md) |
| `~/.local/share/opencode/delegations/<project-id>/<sessionId>/` | Delegation data |

## 5. Architecture Highlights

- **Result type pattern**: Uses `OkResult<T> | ErrResult<E>` instead of exceptions for git operations, with explicit error handling at call sites
- **Boundary validation**: Zod schemas validate all external input (branch names, config, session data, env vars)
- **Security**: Shell metacharacters blocked in branch names, path traversal blocked in file sync, shell escaping uses `escapeBash`/`escapeAppleScript`/`escapeBatch`
- **Concurrency**: Mutex-serialized tmux operations, WAL-mode SQLite with `busy_timeout=5000`, singleton pending operations
- **Cross-platform**: 7 macOS terminals, 10 Linux terminals, Windows Terminal + cmd.exe, WSL interop, cmux native workspace
- **Self-cleaning scripts**: All spawned terminals use trap-based cleanup (`trap 'rm -f "$0"' EXIT`) or batch `goto` self-delete