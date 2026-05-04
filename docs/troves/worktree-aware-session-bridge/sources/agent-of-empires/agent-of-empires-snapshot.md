# Agent of Empires - Architecture Snapshot

**Repository:** https://github.com/njbrake/agent-of-empires
**License:** MIT (Copyright 2026 Nathan Brake)
**Language:** Rust (TUI/backend) + TypeScript/React (web dashboard)
**Author:** Nate Brake (@natebrake), Machine Learning Engineer at Mozilla.ai

## 1. Project Overview

Agent of Empires (AoE) is a **session manager for AI coding agents** (Claude Code, OpenCode, Codex CLI, Gemini CLI, Mistral Vibe, Cursor CLI, Copilot CLI, Pi.dev, Factory Droid). It provides a TUI, CLI, and web dashboard to create, monitor, and manage multiple agent sessions, each running in an isolated tmux session. Key features:

- **Multi-agent parallel sessions** in tmux
- **Git worktree isolation** per session
- **Docker sandboxing** (one container per session)
- **Status detection** (running, waiting, idle, error) from pane content
- **Web dashboard** with xterm.js terminal relay (PWA-installable)
- **Remote phone access** via Tailscale Funnel or Cloudflare Tunnel

## 2. Project Structure

```
├── src/
│   ├── main.rs              # Binary entrypoint (aoe)
│   ├── lib.rs               # Shared library
│   ├── agents.rs            # Agent definitions (Claude, OpenCode, etc.)
│   ├── terminal.rs           # Terminal handling
│   ├── cli/                 # Clap CLI handlers
│   ├── containers/          # Docker/Apple Container sandboxing
│   │   ├── mod.rs            # DockerContainer struct, runtime selection
│   │   ├── container_interface.rs  # ContainerRuntimeInterface trait
│   │   ├── runtime.rs        # ContainerRuntime (Docker vs Apple Container)
│   │   ├── runtime_base.rs   # Shared runtime logic (build args, create, start, stop)
│   │   └── error.rs          # DockerError enum
│   ├── git/                  # Git worktree operations
│   │   ├── mod.rs
│   │   ├── worktree.rs       # GitWorktree (create, remove, list, compute paths)
│   │   ├── template.rs       # Path template resolution ({repo-name}, {branch}, {session-id})
│   │   ├── cleanup.rs        # Orphaned worktree detection
│   │   ├── diff.rs           # Git diff operations
│   │   ├── remote.rs         # Git remote operations
│   │   └── error.rs
│   ├── hooks/                # Agent status hook system
│   ├── process/              # OS-specific process handling (macOS.rs, linux.rs)
│   ├── server/               # Web dashboard backend (axum, REST, WebSocket PTY, auth)
│   ├── session/              # Session storage, config, lifecycle
│   │   ├── builder.rs        # SessionBuilder (creates tmux session + optional container + worktree)
│   │   ├── instance.rs       # SessionInstance (runtime state, SandboxInfo, WorkspaceInfo)
│   │   ├── config.rs         # Config (TOML-based, profiles)
│   │   ├── container_config.rs # Container config builder (volume mounts, env vars, sandbox dirs)
│   │   ├── environment.rs    # Environment variable collection
│   │   ├── deletion.rs       # Session deletion logic
│   │   ├── groups.rs         # Session grouping
│   │   ├── civilizations.rs  # Named groups of sessions
│   │   ├── repo_config.rs    # Per-repo configuration (.agent-of-empires/)
│   │   ├── profile_config.rs # Profile-level config overrides
│   │   ├── storage.rs        # JSON-based session persistence
│   │   └── serde_helpers.rs
│   ├── tmux/                 # tmux integration
│   │   ├── mod.rs             # Session cache, batch_pane_metadata, agent detection
│   │   ├── session.rs        # Session struct (create, kill, attach, capture, send_keys)
│   │   ├── terminal_session.rs # TerminalSession + ContainerTerminalSession
│   │   ├── status_detection.rs # Status detection from pane content
│   │   ├── status_bar.rs      # tmux status bar integration
│   │   └── utils.rs           # Helper functions (sanitize, pane checks, mouse-on args)
│   ├── tui/                  # ratatui TUI app
│   ├── migrations/           # Schema versioned data migrations
│   ├── sound/                # Sound effects (idle, chain, spell, etc.)
│   └── update/               # Version checking against GitHub releases
├── web/                      # React 19 + Vite + Tailwind v4 + xterm.js v6
├── website/                  # Astro static site (marketing/docs)
├── docker/                   # Dockerfiles (sandbox images)
├── docs/                     # User-facing documentation
├── scripts/                  # Install, release, build scripts
├── tests/                    # Integration + E2E tests
├── xtask/                    # Build automation
├── theme/                    # TUI theme definitions
├── bundled_sounds/           # WAV sound effects
├── assets/                   # Logo and images
└── .github/                  # CI workflows, PR templates
```

## 3. tmux Multi-Session Management

### Architecture

Each AI agent session maps to a **tmux session** with the naming convention `aoe_{title}_{id8}` (e.g., `aoe_My_Project_abc12345`). A separate `aoe_term_{title}_{id8}` session is created for paired terminal access, and `aoe_cterm_{title}_{id8}` for container terminals.

### Key Details

- **Session creation** (`src/tmux/session.rs`): Uses `tmux new-session -d -s {name} -c {working_dir}` with `remain-on-exit on`, `pane-base-index 0`, and `mouse on` options.
- **Session caching** (`src/tmux/mod.rs`): A global `SESSION_CACHE` (RwLock) with 2-second TTL avoids redundant `tmux list-sessions` calls. `batch_pane_metadata()` fetches all pane status in one subprocess.
- **Status detection** (`src/tmux/status_detection.rs`): Parses tmux pane content (with ANSI stripped) to detect Running/Waiting/Idle/Error. Claude Code uses file-based hooks instead; OpenCode looks for "esc to interrupt", spinner chars, permission prompts.
- **Secrets handling**: Environment variables are injected via `export KEY='secret'; exec agent_cmd` compound commands so secrets don't appear in `ps` output. After `exec`, the original shell is replaced.
- **Multi-window safety**: Uses `^{.0` tmux target format to always hit window 0 pane 0 (the agent pane), regardless of base-index settings or split panes.
- **Terminal sessions** (`src/tmux/terminal_session.rs`): A `PairedTerminal` abstraction shared between `TerminalSession` (host, prefix `aoe_term_`) and `ContainerTerminalSession` (prefix `aoe_cterm_`).

## 4. Git Worktree Integration

### Architecture (`src/git/worktree.rs`)

The `GitWorktree` struct provides:

- **`create_worktree(branch, path, create_branch)`**: Creates a new worktree. Fetches from origin, resolves branch references (local or remote), and runs `git worktree add`. Converts `.git` files from absolute to relative paths for Docker portability.
- **`remove_worktree(path, force)`**: Runs `git worktree remove`.
- **`list_worktrees()`**: Lists all worktrees using `git2::Repository::worktrees()`.
- **`compute_path(branch, template, session_id)`**: Resolves path templates (`{repo-name}`, `{branch}`, `{session-id}`) into concrete paths.
- **`detect_default_branch()`**: Checks local/remote branches for "main" or "master".
- **`find_main_repo(path)`**: Resolves from worktree `.git` files back to the main repo root. Handles bare repos, linked worktrees, `.bare/` patterns, and sibling bare repos.
- **`is_bare_repo(path)`**: Detects bare repos for template selection.
- **`convert_git_file_to_relative()`**: Converts absolute `gitdir:` paths in worktree `.git` files to relative paths for container mounts.
- **`prune_worktrees()`**: Cleans stale worktree references before creation.

### Configuration

```toml
[worktree]
enabled = false
path_template = "../{repo-name}-worktrees/{branch}"  # non-bare repos
bare_repo_path_template = "./{branch}"               # bare repos
auto_cleanup = true
show_branch_in_tui = true
delete_branch_on_cleanup = false
```

### Worktree + Sandbox Interaction

When using worktrees inside Docker containers, AoE detects the worktree layout and mounts the correct volumes:
- **Bare repo worktrees**: Mounts the entire repo root (container sees `.bare/` as a sibling).
- **Sibling worktrees**: Mounts both the main repo and worktree as separate volumes under `/workspace/`.
- **Non-git paths**: Mounts directly to `/workspace/{dir_name}`.

## 5. Docker Sandboxing Code

### Architecture (`src/containers/`)

**`ContainerRuntimeInterface` trait** (`container_interface.rs`): Defines the full lifecycle: `is_available()`, `is_daemon_running()`, `create_container()`, `start_container()`, `stop_container()`, `remove()`, `exec_command()`, `batch_running_states()`.

**`ContainerRuntime`** (`runtime.rs`): Dispatches between `RuntimeKind::Docker` and `RuntimeKind::AppleContainer`. Differences:
- Docker: `docker container inspect` for existence, `docker container inspect -f {{.State.Running}}` for status, `docker rm -v` for cleanup.
- Apple Container: `container logs` for existence (inspect returns 0 even for missing containers), `container inspect` (JSON with `/0/status` field) for status, `container delete` for cleanup. Commands wrapped in `sh -c` for PATH resolution.

**`RuntimeBase`** (`runtime_base.rs`): Shared logic for both runtimes. `build_create_args()` constructs the `docker run` command with `-d`, volume mounts (`-v`), env vars (`-e`), CPU/memory limits, and port mappings. Secrets use `EnvEntry::Inherit` (only key in argv, value in process env) to avoid leaking into `ps`.

**`ContainerConfig`** (`container_interface.rs`): Holds `working_dir`, `volumes` (Vec<VolumeMount>), `anonymous_volumes`, `environment` (Vec<EnvEntry>), `cpu_limit`, `memory_limit`, `port_mappings`.

### Sandbox Configuration Builder (`src/session/container_config.rs`)

`build_container_config()` orchestrates the full setup:
1. Resolves volume paths (worktree-aware, bare-repo-aware).
2. Mounts project directory to `/workspace/{name}`.
3. Syncs host agent credentials into per-agent sandbox directories (e.g., `~/.claude/sandbox/`).
4. Mounts shared sandbox dirs read-write into containers.
5. Seeds home-level files (`.claude.json` onboarding skip, `.sandbox-gitconfig` with GitHub credential helper).
6. Handles macOS Keychain credential extraction for Claude OAuth.
7. Preserves container-created files on restart (skips general copy if `projects/` exists).
8. Installs agent hooks into sandbox settings.
9. Deduplicates volumes by container path (user extras override automatic).
10. Builds anonymous volumes from `volume_ignores` config (e.g., `target/`, `node_modules/`).

### Agent Config Table

| Agent | Host Dir | Keychain | Seed Files | Copy Dirs |
|-------|----------|----------|------------|-----------|
| claude | .claude | Yes (Claude Code-credentials) | .claude.json, .sandbox-gitconfig | plugins/, skills/ |
| opencode | .local/share/opencode, .config/opencode | No | None | None |
| codex | .codex | No | None | None |
| gemini | .gemini | No | None | None |
| vibe | .vibe | No | None | None |
| cursor | .cursor | No | None | None |
| copilot | .copilot | No | None | None |
| pi | .pi | No | None | None |
| droid | .factory | No | None | None |

### Container Lifecycle

1. **Create**: `docker run -d --name aoe-sandbox-{id8} -v ... -e ... sleep infinity`
2. **Start**: `docker start {name}`
3. **Execute agent**: `docker exec -it {name} {agent_cmd}` via tmux
4. **Status**: `docker ps -a --filter name=aoe-sandbox- --format {{.Names}}\t{{.State}}`
5. **Cleanup**: `docker rm -v {name}` (removes anonymous volumes; named auth volumes persist)

### Default Sandbox Image

`ghcr.io/njbrake/aoe-sandbox:latest` (includes all supported agents, git, ripgrep, fzf). Dev image adds Rust, uv, Node.js, gh CLI.

## 6. License

**MIT License** - Copyright (c) 2026 Nathan Brake. Full text in `/tmp/agent-of-empires-sources/LICENSE`.

## 7. Key Configuration Files

| File | Purpose |
|------|---------|
| `~/.agent-of-empires/config.toml` | Global config (theme, worktree, sandbox, session, tmux, diff, sound, web) |
| `~/.agent-of-empires/profiles/<profile>/sessions.json` | Session storage per profile |
| `.agent-of-empires/` (repo-local) | Per-repo config overrides |
| `Cargo.toml` | Rust workspace config, dependencies |
| `deny.toml` | Cargo deny configuration |
| `rust-toolchain.toml` | Rust toolchain pin |
| `flake.nix` | Nix flake for development |
| `docker/Dockerfile` | Production sandbox image |
| `docker/Dockerfile.dev` | Dev sandbox image (Rust, Node, gh) |
| `web/package.json` | Frontend dependencies |
| `theme/` | TUI theme definitions |

## 8. Session Configuration Structure

```rust
struct Config {
    default_profile: String,
    theme: ThemeConfig,
    claude: ClaudeConfig,
    updates: UpdatesConfig,
    worktree: WorktreeConfig,     // enabled, path_template, bare_repo_path_template, auto_cleanup, show_branch_in_tui, delete_branch_on_cleanup
    sandbox: SandboxConfig,       // enabled_by_default, default_image, auto_cleanup, cpu_limit, memory_limit, environment, volume_ignores, extra_volumes, mount_ssh, container_runtime
    tmux: TmuxConfig,
    session: SessionConfig,       // sort_order, group_by, custom_agents, yolo_mode_default, agent_status_hooks
    diff: DiffConfig,
    hooks: HooksConfig,
    sound: SoundConfig,
    app_state: AppStateConfig,
    web: WebConfig,
}
```

## 9. Source Files Copied to /tmp/agent-of-empires-sources/

27 files covering the core modules:
- `src/tmux/` (6 files): Session management, status detection, terminal sessions
- `src/git/` (5 files): Worktree operations, path templates, cleanup, diff, remote
- `src/containers/` (5 files): Container abstraction, runtime dispatch, base runtime, interface
- `src/session/` (5 files): Config, container config builder, instance, environment, builder
- Root: `agents.rs`, `lib.rs`, `Cargo.toml`, `LICENSE`, `AGENTS.md`
- Docs: `worktrees.md`, `sandbox.md`