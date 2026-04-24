# OpenCode Pilot - Code Snapshot

**Repository**: https://github.com/athal7/opencode-pilot
**Author**: Andrew Thal
**License**: MIT
**Version**: 0.27.0
**Snapshot Date**: 2026-04-23

---

## Project Overview

opencode-pilot is an automation daemon for OpenCode that **polls for work** (GitHub issues, Linear tickets, custom sources) and **spawns sessions** via the OpenCode HTTP API. It evaluates issue readiness, manages session lifecycle, supports git worktree isolation, and provides built-in presets for common workflows.

## Project Structure

```
opencode-pilot/
├── service/
│   ├── server.js           # HTTP server + service lifecycle (~202 lines)
│   ├── poll-service.js     # Polling orchestration loop (~459 lines)
│   ├── poller.js           # MCP polling + state tracking (~1305 lines)
│   ├── actions.js          # Session creation, reuse, messaging (~1178 lines)
│   ├── session-context.js  # SessionContext value object (~83 lines)
│   ├── worktree.js         # Worktree management via OpenCode API (~277 lines)
│   ├── repo-config.js      # YAML config loading + repo discovery (~462 lines)
│   ├── readiness.js         # Issue readiness evaluation (~432 lines)
│   ├── logger.js           # Logging utility
│   ├── utils.js            # Shared utilities
│   ├── version.js          # Version constant
│   ├── presets/
│   │   ├── index.js        # Preset expansion (github/my-issues, etc.)
│   │   ├── github.yaml     # GitHub preset definitions
│   │   └── linear.yaml     # Linear preset definitions
├── plugin/
│   └── index.js            # OpenCode plugin entry point
├── bin/
│   └── opencode-pilot      # CLI binary
├── test/
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── examples/
│   ├── config.yaml         # Example configuration
│   └── templates/          # Prompt templates (default.md, review.md, etc.)
├── Formula/
│   └── opencode-pilot.rb   # Homebrew formula
├── package.json            # NPM package (opencode-pilot v0.27.0)
├── README.md
├── AGENTS.md
├── .releaserc.cjs          # Semantic release config
└── .devcontainer/          # Dev container config
```

## Daemon Management Code

### Service Lifecycle (`service/server.js`)

- **HTTP server**: Listens on port 4097 (configurable via `config.yaml` `server_port`)
- **Health check endpoint**: `GET /health` returns `{ status: "ok", version }`
- **Startup**: `startService()` creates HTTP server + starts polling if config exists
- **Shutdown**: `stopService()` stops polling interval + closes HTTP server
- **Signal handlers**: `SIGTERM` and `SIGINT` trigger graceful shutdown
- **Error handling**: Uncaught exceptions and unhandled rejections exit process

### Polling Orchestration (`service/poll-service.js`)

**`pollOnce()` - Single poll cycle**:
1. Loads config, gets all sources
2. For each source: fetches items via MCP or CLI
3. Enriches items (comments, mergeable status, branch refs, attention labels)
4. Evaluates readiness (labels, dependencies, fields)
5. Sorts by priority
6. Detects PR stacks for session reuse
7. Deduplicates across sources
8. Executes actions (creates sessions or reuses existing)
9. Tracks processed items, marks unseen items

**`startPolling()` - Continuous loop**:
- Configurable interval (default 5 minutes)
- Startup delay (default 10s) for server initialization
- Cleans up expired state entries on start
- Returns `{ interval, poller, stop }` for external control

**Configuration priority resolution** (`buildActionConfigFromSource`):
- Explicit source fields > repo config > defaults

### Polling Engine (`service/poller.js`)

**MCP Integration** (`pollGenericSource`):
- Creates `@modelcontextprotocol/sdk` Client
- Supports `StdioClientTransport`, `StreamableHTTPClientTransport`, `SSEClientTransport`
- Connects to MCP server from `opencode.json` config
- Calls tool, parses JSON response, applies field mappings
- 30-second timeout with race condition

**CLI Command Sources** (`pollCliSource`):
- Executes shell commands (e.g., `gh api ...`)
- Substitutes arguments into command templates
- Parses JSON output

**State Tracking** (`createPoller`):
- Persists processed items to `~/.config/opencode/pilot/poll-state.json`
- Deduplication key index for cross-source deduplication (e.g., Linear issue + GitHub PR)
- `markProcessed()`, `isProcessed()`, `shouldReprocess()`, `clearProcessed()`
- Reappearance detection: tracks `wasUnseen` flag for re-triggering on reopened issues
- TTL-based cleanup: removes entries older than configurable days
- Source-specific cleanup: removes items no longer in source results

**GitHub Comment Enrichment** (`fetchGitHubComments`):
- Fetches PR review comments, issue comments, and PR reviews via `gh api`
- Supports bot filtering via `hasNonBotFeedback()`
- Computes attention labels (Conflicts, Feedback, Conflicts+Feedback)

**PR Stack Detection** (`detectStacks`):
- Groups PRs by repo
- Matches headRefName/baseRefName chains using union-find
- Returns map of itemId -> sibling itemIds for session reuse

**Deduplication** (`computeDedupKeys`):
- Generates canonical keys (e.g., `linear:ENG-123`, `github:org/repo#456`)
- Extracts issue references from title/body (e.g., "Fixes ENG-123" -> `linear:ENG-123`)

### Session Management (`service/actions.js`)

**Session Creation** (`createSessionViaApi`):
- `POST /session?directory=X` to create session
- `PATCH /session/:id` to set title
- `POST /session/:id/message` or `POST /session/:id/command` to send prompt
- Slash command detection: routes `/command` to `/command` endpoint
- Model override: `provider/model` format split into `providerID` + `modelID`
- 60-second header timeout for long-running commands

**Session Reuse** (`findReusableSession`, `selectBestSession`):
- Queries `GET /session?directory=X&roots=true`
- Filters archived sessions
- Prefers idle sessions, then most recently updated

**Server Discovery** (`discoverOpencodeServer`):
- Scans all running OpenCode server ports via `lsof`
- Matches sessions to directories using `GET /project/current`
- Priority: configured `server_port` > exact sandbox match > worktree match > global server

**Worktree Isolation** (invariant C):
- Worktree sessions skip `findReusableSession` entirely
- Each PR/issue in its own worktree gets its own session
- Prevents cross-PR contamination

**Prompt Templates**:
- Loads from `~/.config/opencode/pilot/templates/{name}.md`
- Expands `{field}` and `{field.nested}` placeholders with item data
- Fallback: combines `title` + `body` if template not found

### Worktree Management (`service/worktree.js`)

- `resolveWorktreeDirectory()`: Resolves working directory from config
  - `"new"`: Creates fresh worktree via `POST /experimental/worktree?directory=X`
  - Named worktree: Looks up existing sandbox
  - Sandbox reuse: Checks existing sandboxes by name
- `listWorktrees()`: `GET /experimental/worktree?directory=X`
- `createWorktree()`: `POST /experimental/worktree` with optional name
- `getProjectInfoForDirectory()`: Finds server matching target directory

### Readiness Evaluation (`service/readiness.js`)

Multi-factor readiness checking:

1. **Label constraints**: Exclude labels, required labels, any_of labels
2. **Dependency references**: "blocked by #123", "depends on #456", unchecked task lists
3. **Bot comment filtering**: Only trigger on human (non-bot) feedback
4. **Merge conflict detection**: `enrich_mergeable` flag + `require_conflicts` filter
5. **Attention detection**: Combined conflicts + feedback check
6. **Field matching**: Generic `readiness.fields` config for required field values
7. **Priority scoring**: Label weights + age bonus

### Configuration (`service/repo-config.js`)

- YAML config at `~/.config/opencode/pilot/config.yaml`
- **Presets**: `github/my-issues`, `github/review-requests`, `github/my-prs-attention`, `linear/my-issues`
- **GitHub shorthand**: `github: "assignee:@me is:open"` syntax
- **Auto-discovery**: Scans `repos_dir` for git remotes (origin + upstream for fork support)
- **Defaults layering**: source > repo > defaults (with `_explicit` tracking)
- **Tool provider config**: Merges user config with preset defaults

## Key Files

| File | Lines | Purpose |
|------|-------|---------|
| `service/actions.js` | 1178 | Session creation, reuse, server discovery, prompt building |
| `service/poller.js` | 1305 | MCP polling, state tracking, deduplication, stack detection |
| `service/poll-service.js` | 459 | Polling orchestration loop, readiness evaluation |
| `service/repo-config.js` | 462 | YAML config loading, preset expansion, repo discovery |
| `service/readiness.js` | 432 | Multi-factor issue readiness evaluation |
| `service/worktree.js` | 277 | Worktree management via OpenCode API |
| `service/server.js` | 202 | HTTP server, polling startup, signal handling |
| `service/session-context.js` | 83 | Value object tracking project + working directories |

## Dependencies

- `@modelcontextprotocol/sdk` ^1.25.1 (MCP client)
- `yaml` ^2.8.2 (config parsing)
- Dev: `semantic-release` + plugins for automated versioning

## Key Design Decisions

1. **HTTP API-first**: Creates sessions via OpenCode's REST API, not CLI spawning
2. **MCP + CLI hybrid polling**: Supports both MCP tool calls and shell command sources
3. **Cross-source deduplication**: Dedup keys prevent Linear+GitHub double-triggers
4. **Worktree isolation**: Each PR/issue gets its own session via git worktrees
5. **Session reuse**: Prefers idle sessions over busy ones, respects archived status
6. **Slash command routing**: Detects `/command` prompts and routes to `/command` endpoint
7. **State persistence**: JSON file tracks processed items with dedup key index
8. **Config layering**: Presets < defaults < repo config < source config < explicit overrides