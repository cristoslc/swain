# OpenCode Agent Tmux (opentmux) - Code Snapshot

**Repository**: https://github.com/AnganSamadder/opencode-agent-tmux
**Author**: Angan Samadder
**License**: MIT
**Version**: 1.5.7
**Snapshot Date**: 2026-04-23

---

## Project Overview

opentmux is an OpenCode plugin providing **smart tmux integration** for viewing agent execution in real-time. It automatically spawns tmux panes for subagent sessions, streams agent output via `opencode attach`, and manages terminal workspace layouts including zombie process reaping.

## Project Structure

```
opencode-agent-tmux/
├── src/
│   ├── index.ts                  # Plugin entry point (~81 lines)
│   ├── tmux-session-manager.ts   # Core session lifecycle manager (~334 lines)
│   ├── spawn-queue.ts            # Queue for serial pane spawning with retry (~269 lines)
│   ├── zombie-reaper.ts          # Zombie process detection and cleanup (~528 lines)
│   ├── layout.ts                 # Pure layout computation functions (~262 lines)
│   ├── types.ts                  # Plugin interface types (~19 lines)
│   ├── bin/
│   │   └── opentmux.ts           # CLI entry point / smart wrapper (~627 lines)
│   ├── utils/
│   │   ├── index.ts              # Barrel export
│   │   ├── logger.ts             # Logging utility
│   │   ├── process.ts            # Process management utilities
│   │   ├── config-loader.ts      # Config loading from JSON files
│   │   ├── layout.test.ts        # Layout tests
│   │   └── tmux.ts               # Tmux command execution & pane management (~557 lines)
│   └── __tests__/                # Unit tests
├── package.json                  # NPM package (opentmux v1.5.7)
├── tsconfig.json
├── tsup.config.ts                # Build config
├── AGENTS.md                     # Agent guidelines
├── README.md
├── MULTI_PORT.md                 # Multi-port documentation
├── TMUX_LAUNCHER.md              # Launcher documentation
├── PLAN.md
└── SISYPHUS-PROMPT.md
```

## Session/Daemon Management Code

### Plugin Entry Point (`src/index.ts`)

- Initializes `TmuxSessionManager` with config from `loadConfig()`
- Detects server URL from `OPENCODE_PORT` env var or defaults to `localhost:4096`
- Guards against duplicate initialization with `isInitialized` flag
- Listens for `session.created` events to spawn panes

### TmuxSession Manager (`src/tmux-session-manager.ts`)

Core lifecycle manager for agent tmux panes:

**Session Tracking** (`TrackedSession` interface):
- Tracks `sessionId`, `paneId`, `parentId`, `title`, `createdAt`, `lastSeenAt`, `missingSince`

**Session Creation** (`onSessionCreated`):
- Listens for `session.created` events with `info.id` and `info.parentID`
- Deduplicates via `sessions` Map and `pendingSessions` Set
- Enqueues pane spawn via `SpawnQueue`
- Starts polling if first session

**Polling** (`pollSessions`):
- Periodic health check via `client.session.status()`
- Closes sessions that are: idle, missing too long (> `SESSION_MISSING_GRACE_MS`), or timed out
- Auto-stops polling when no sessions remain

**Shutdown Handling** (`registerShutdownHandlers`, `handleShutdown`, `cleanup`):
- Catches `SIGINT`, `SIGTERM`, `SIGHUP`, `SIGQUIT`, `beforeExit`
- Closes all panes, stops polling, shuts down spawn queue and reaper

### Spawn Queue (`src/spawn-queue.ts`)

Serial pane-spawning queue with:
- **Coalescing**: Duplicate enqueues for same sessionId return existing promise
- **Exponential backoff retry**: 250ms base, configurable max retries
- **Stale item detection**: Items waiting >30s are skipped
- **Queue drain notification**: `onQueueDrained` callback triggers deferred layout application

### Zombie Reaper (`src/zombie-reaper.ts`)

Two-mode cleanup system:

**Plugin Mode** (periodic scan):
- Scans for `opencode attach` processes matching this server's URL
- Marks processes as zombie candidates after `minZombieChecks` detections + `gracePeriodMs`
- Kills zombies (SIGTERM, then SIGKILL)
- **Auto-self-destruct**: If no clients for `selfDestructTimeoutMs`, kills the server itself

**CLI Mode** (`reapAll`):
- Scans all OpenCode server ports for inactive processes
- Kills zombie attach processes and stale servers
- Used via `opentmux --reap` command

**Process Classification** (`findAllAttachProcesses`):
- Finds PIDs running `opencode attach`
- Extracts session ID from `--session` flag
- Extracts target URL from arguments

### Smart Wrapper (`src/bin/opentmux.ts`)

CLI entry point that acts as an `opencode` wrapper:
- **Multi-port support**: Scans ports 4096-4106 for available servers
- **Port reclaiming**: Kills stale non-tmux processes on occupied ports
- **Session rotation**: `rotate_port` config kills oldest session when all ports busy
- **CLI passthrough**: Detects non-TUI commands (`auth`, `config`, `plugins`, etc.) and bypasses tmux
- **Tmux launch**: If not in tmux, creates a new tmux session with opencode

### Layout System (`src/layout.ts`)

Pure functions for multi-column agent pane distribution:
- `computeColumnCount()`: Calculates needed columns from agent count
- `distributeAgentsRoundRobin()`: Distributes agents across columns evenly
- `groupAgentsByColumn()`: Groups agent IDs by column
- `mainPanePercentForColumns()`: Adaptive main pane sizing (1 col: 60%, 2 col: 45%, 3+: 30%)
- `buildMainVerticalMultiColumnLayoutString()`: Generates tmux layout strings with checksum

## Key Files

| File | Lines | Purpose |
|------|-------|---------|
| `src/tmux-session-manager.ts` | 334 | Core session lifecycle, polling, cleanup |
| `src/spawn-queue.ts` | 269 | Queued pane spawning with retry |
| `src/zombie-reaper.ts` | 528 | Zombie process detection and killing |
| `src/utils/tmux.ts` | 557 | Tmux command execution, pane spawn/close, layout |
| `src/layout.ts` | 262 | Pure layout computation functions |
| `src/bin/opentmux.ts` | 627 | CLI wrapper with multi-port support |
| `src/index.ts` | 81 | Plugin entry point |
| `src/types.ts` | 19 | Plugin interface types |

## Dependencies

- `proper-lockfile` ^4.1.2
- `zod` ^3.24.1 (config validation)
- Dev: `@types/bun`, `@types/node`, `tsup`, `typescript`

## Key Design Decisions

1. **Event-driven pane management**: Listens for `session.created` events to spawn panes
2. **Zombie reaping**: Dual-mode killer (plugin periodic scan + CLI manual reap) with configurable thresholds
3. **Multi-port support**: Scans port range, reclaims stale processes, optional port rotation
4. **Layout computation**: Pure functions generate tmux layout strings; debounced after queue drain
5. **Coalescing spawn queue**: Prevents duplicate spawns for same sessionId
6. **Smart CLI wrapper**: `opentmux` command wraps `opencode` with tmux detection and port management