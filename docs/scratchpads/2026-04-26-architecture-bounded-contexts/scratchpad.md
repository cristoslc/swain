# swain architecture — bounded-context layering

Status: thinking-in-progress. Not an artifact. Supersedes prior scratchpads at `2026-04-26-swain-box-bridge-realignment*` (deleted; preserved in git history).

This scratchpad consolidates the layered model the operator articulated. Earlier scratchpads were wrong about kernel placement (had it inside the container) and conflated chat-aware domain logic with the chat-transport layer. This one corrects both and bakes in the multi-host hierarchy.

## Glossary

| Name | What | Where | How many | Speaks |
|---|---|---|---|---|
| **Operator surface** | Bounded context that presents to humans. Includes TUI, web UI (`swain-stage`), chat adapter | host (today), separate node (eventually) | many surface processes | varies (chat APIs, HTTPS, terminal) |
| **Chat adapter** | Marshals chat-service messages to/from operator-surface event stream. Pluggable: Zulip / iMessage / Slack | operator-surface node | one process, internal backends per service | chat APIs outward; WSS to host adapter inward |
| **TUI** | Host operator terminal UI | operator-surface node | one per operator | terminal; WSS to host adapter |
| **swain-stage** | Web UI (future) | operator-surface node | one per operator | HTTPS to browser; WSS to host adapter |
| **Host adapter** | Caddy. Routing fabric for the host bounded context. TLS, hostname routing, WSS pass-through | host | singleton per host | TLS, HTTP/WS routing |
| **Host kernel** | Per-host orchestrator. Manages project lifecycle, project registry, container start/stop, project-kernel processes. Ex-watchdog, but more | host | singleton per host | WSS to host adapter; spawns project kernels and swain-boxes |
| **Project kernel** | Per-project domain logic. Owns worktree, session, conversation state. Stateful | host | one per project | ACP outward to harness ACLs; structured RPC to swain-box agent; WSS to host adapter for surface traffic |
| **Project state file** | Persisted kernel state | host, in project dir, **gitignored** (`<project>/.swain/state.*`) | one per project | (storage) |
| **MCP gateway** | Per-project MCP server pass-through, kernel-hosted, published to swain-box | host | one per project | MCP wire to runtimes-in-box; configurable upstream |
| **swain-box** | Per-project Docker container | host docker | one per project | n/a |
| **swain-box agent** | Deterministic-ops helper inside the container. Health, git, shell-with-allowlist | inside swain-box | one per swain-box | `docker exec` (MVP); structured RPC (future) |
| **Harness ACL** | Anti-corruption layer per active session. Spawns the runtime, normalizes its quirks, exposes clean ACP to the project kernel | inside swain-box | **one per active session** | ACP outward to kernel; ACP stdio to runtime |
| **Runtime ACP agent** | The actual AI coding tool: `gemini --acp`, `claude-code-acp`, `opencode acp`, `codex-acp` | inside swain-box, child of harness ACL | one process per session | ACP stdio |

The word "bridge" is retired (it overloaded with too many things — historical opencode bridge, generic ACP bridge, the chat connector, etc.). The kernel-on-host correction means the in-container "kernel" of earlier scratchpads is now just the swain-box agent + harness ACLs.

## Bounded context hierarchy

```
operator surface  (TUI, swain-stage, chat adapter)
        │
        ▼
host  (host kernel, host adapter, MCP gateways, project kernels)
        │
        ▼
project  (project kernel, swain-box)
        │
        ▼
worktree / branch  (within a project)
```

**Cross-context properties:**

- An operator surface can run on a different node than a host. (TUI on laptop → host on home server.)
- One operator surface can talk to multiple hosts. (Aggregate dashboard across machines.)
- Each host can manage multiple projects.
- Each project has multiple worktrees/branches.

This is the property that justifies splitting "chat adapter" out of the host into the operator surface: chat adapter coordinates *operator inputs* across services; it doesn't belong to any specific host. Today it'll co-locate with a host (no network configured), but the model permits separation.

## C4 — System context

```mermaid
flowchart TB
    Op(("Operator"))
    Browser(("Browser"))
    ChatSvc[("Zulip / iMessage / Slack")]

    subgraph OS["Operator surface (one node, eventually movable)"]
        TUI["TUI"]
        Stage["swain-stage<br/>(web UI, future)"]
        ChatA["Chat adapter<br/>(pluggable backends)"]
    end

    subgraph Host1["Host machine 1"]
        HA1["Host adapter<br/>(Caddy)"]
        HK1["Host kernel<br/>(orchestrator)"]
        K1A["Project kernel A"]
        K1B["Project kernel B"]
        Box1A["swain-box A<br/>(container)"]
        Box1B["swain-box B<br/>(container)"]
    end

    HostN["Host machine 2..N<br/>(same shape)"]

    Op <--> TUI
    Op <--> Browser
    Browser <--> Stage
    Op <-->|"chat"| ChatSvc
    ChatSvc <--> ChatA

    TUI <-->|"WSS"| HA1
    Stage <-->|"WSS"| HA1
    ChatA <-->|"WSS"| HA1
    TUI <-.->|"WSS"| HostN
    Stage <-.->|"WSS"| HostN
    ChatA <-.->|"WSS"| HostN

    HA1 <--> HK1
    HA1 <--> K1A
    HA1 <--> K1B
    HK1 -.->|"manages"| K1A
    HK1 -.->|"manages"| K1B
    HK1 -.->|"manages"| Box1A
    HK1 -.->|"manages"| Box1B
    K1A <--> Box1A
    K1B <--> Box1B
```

## C4 — Inside one host

```mermaid
flowchart TB
    subgraph Host["Host machine"]
        HA["Host adapter (Caddy)<br/>TLS + hostname routing<br/>+ WSS pass-through"]
        HK["Host kernel<br/>· project registry<br/>· container lifecycle<br/>· project-kernel lifecycle<br/>· health"]

        subgraph Project["Project A (host-side processes + container)"]
            K["Project kernel A<br/>· worktree mgmt<br/>· session mgmt<br/>· conversation mgmt<br/>· chat-shape coalescing<br/>· serializes commands"]
            State[("state file<br/>.swain/state.* in project<br/>(gitignored)")]
            MCP["MCP gateway A<br/>(pass-through MVP)"]

            subgraph Box["swain-box A (container)"]
                ACL_S1["Harness ACL: session 1"]
                ACL_S2["Harness ACL: session 2"]
                R1["claude-code-acp<br/>session 1"]
                R2["gemini --acp<br/>session 2"]
                SBA["swain-box agent<br/>(docker exec MVP)"]
                ProjFS[("project FS bind mount")]
            end
        end

        OtherProj["Project B<br/>(same shape)"]
    end

    HA <-->|"hostname route<br/>to project A"| K
    HK -.->|"start/stop/health"| K
    HK -.->|"start/stop/health"| Box
    K <-->|"ACP"| ACL_S1
    K <-->|"ACP"| ACL_S2
    K -->|"docker exec"| SBA
    K <-->|"reads/writes"| State
    ACL_S1 <-->|"ACP stdio"| R1
    ACL_S2 <-->|"ACP stdio"| R2
    R1 -->|"MCP wire"| MCP
    R2 -->|"MCP wire"| MCP
    R1 <--> ProjFS
    R2 <--> ProjFS
```

## Seams (canonical list)

Categorized by which bounded contexts they cross. "BC" = bounded context.

### Operator surface ↔ host (BC crossing — networked even when co-located)

1. **TUI ↔ host adapter** — WSS, ACP-shaped events for runtime traffic + side channel for swain events (worktree, project list)
2. **swain-stage ↔ host adapter** — WSS, same protocols as TUI
3. **Chat adapter ↔ host adapter** — WSS, same protocols
4. **Chat adapter ↔ chat service** — chat-service-specific (Zulip API long-poll, iMessage, etc.)

### Within host: between host kernel and host adapter

5. **Host kernel ↔ host adapter** — host kernel registers project routes, configures Caddy, listens for control commands

### Within host: project kernel boundaries (BC crossing — process boundary)

6. **Host adapter ↔ project kernel** — WSS routed by hostname; surface traffic flows here
7. **Host kernel ↔ project kernel** — lifecycle: start, stop, health, restart, registration

### Project kernel ↔ container

8. **Project kernel ↔ harness ACL** — ACP over WSS or local TCP; one connection per active session
9. **Project kernel ↔ swain-box agent** — docker exec (MVP) or structured RPC (future)
10. **Runtime (in box) ↔ MCP gateway (on host)** — MCP wire over network into the container

### Within container

11. **Harness ACL ↔ runtime ACP agent** — ACP JSON-RPC over stdio; the ACL spawns the runtime
12. **swain-box agent ↔ container OS** — runs allowlisted shell, reads logs, checks state
13. **Runtime ↔ project filesystem** — bind mount

## Persistence

**Project state file**: `<project-root>/.swain/state.*` on the host filesystem. Gitignored.

Contents:
- Active sessions per worktree, with runtime + ACP session-id mapping
- Conversation history references (which Zulip topic / TUI buffer corresponds to which session)
- Worktree map snapshot
- Per-conversation defaults (preferred runtime, etc.)

The state file lives **in the project**, not in the swain-box volume, because:
- Operator can inspect / back up via normal filesystem tools
- Survives container destroy/recreate cleanly
- Co-located with project metadata (CLAUDE.md, etc.) is conceptually right

The kernel reads state on start, writes on every meaningful change. Probably SQLite or JSON-with-fsync depending on traffic; SQLite for the typical case.

**Host kernel state**: project registry (which projects are registered, hostnames, container references). Lives at `~/.swain/host/registry.*`. Not gitignored (operator-level, not project-level).

**Why kernel can't live in container**: a kernel that lives inside its own swain-box can't kill, restart, or manage the lifecycle of that swain-box (the kernel goes down with the container). Lifecycle management requires an outside-the-container controller. Either the host kernel does it directly, or the project kernel does it (and lives on host). Both put the project kernel on the host.

## Multi-runtime: ACP everywhere, ACL per session

ACP (Agent Client Protocol) is the wire format inside the container, between the harness ACL and the runtime ACP agent. JSON-RPC 2.0 over stdio, designed for "external thing controls AI coding agent." Industry standard governed by Zed's working group.

Runtimes that speak ACP:
- **gemini**: native (`gemini --acp`)
- **claude-code-acp**: official Zed adapter wrapping the Anthropic SDK
- **opencode acp**: native (`opencode acp` subcommand). Has open issues — see "known integration friction" below
- **codex-acp**: community adapter (v2 — wait for stability)

**One harness ACL per active session.** Reasons:
- claude can't multiplex sessions in one process (verified empirically: SPIKE 2026-04-26 showed `session_id` field in stream-json input is ignored by the CLI; one process = one conversation)
- Per-session ACL is a clean isolation boundary — one session's quirks/bugs don't bleed
- Process count = active session count (acceptable cost; sessions are typically <10)

**The harness ACL is the runtime-side anti-corruption layer.** It:
- Spawns the runtime subprocess with the right flags (e.g. `--yolo`, `--dangerously-skip-permissions`, `--full-auto`)
- Filters known runtime quirks (e.g., opencode #17282 ANSI-escape leak in JSON-RPC)
- Translates runtime-specific events into normalized ACP that the kernel can consume uniformly
- Auto-allows `session/request_permission` (sandbox-level approval, not per-tool)

**Sandbox-level approval, not per-tool.** Operator approval at session level (start/kill); container is the safety boundary. Each runtime launched in its most permissive mode. ACP `session/request_permission` is auto-allowed.

### Known integration friction (sampled 2026-04-26)

Per-runtime issues the harness ACL must defend against:

- **opencode acp**: `#22795` (server exits immediately on startup), `#17282` (ANSI escapes corrupt JSON-RPC), `#24494` (`end_turn` returned on errors), `#21013` (no `session_info_update`), `#17019` (oversized payload crashes). Defensive parsing + retry on startup + payload-size guard required.
- **claude-code-acp**: third-party (Zed-maintained) — version pinning + soak testing before bumps.
- **gemini --acp**: less battle-tested than the others; verify headless container behavior without a display server.
- **codex-acp**: deferred to v2; SDK still experimental.

## MCP gateway: per-project on host, pass-through MVP

One MCP gateway process per project, hosted by (or alongside) the project kernel on the host. Published to the swain-box container via a network socket / port mount. Runtimes inside the container connect to it.

**MVP behavior**: pass-through to the upstream MCP servers configured for the project. No filtering, no caching, no rewriting.

**Future**: kernel can intercept (rate-limit, audit-log, redact) without changing the runtime-facing wire.

**Why per-project**: each project has different MCP needs (different toolsets, different upstreams). Per-project also means a misbehaving MCP server in one project can't take down others.

**Why on host**: kernel hosts it because the kernel is where project domain logic lives, including "which MCP servers does this project use." Putting it in the container would couple it to container lifecycle (restart on rebuild), which we don't want.

## swain-box agent: docker exec MVP, designed for RPC future

The kernel needs to run deterministic operations *inside* the container — health checks, git operations on the project mount, log inspection. Two implementations:

**MVP — docker exec.** Kernel shells out: `docker exec <container> <command>`. Each call is a separate process. Simple, no extra long-running processes inside the container. Latency-OK for the volume of calls expected.

**Future — RPC daemon.** A small in-container daemon (`swain-box-agentd`) listening on a unix socket or local TCP. Kernel sends structured RPC requests over a long-lived connection. Lower latency, cleaner observability, structured surface. Required if call volume grows or if we need streaming responses (e.g., live log tailing).

**Design constraint**: build the kernel-side abstraction so swapping MVP for RPC is purely an implementation detail of one module. The kernel's call sites use a `BoxAgent` interface; the implementation today shells out, the implementation later RPCs. Same verbs.

**RPC surface (deferred)**: small allowlisted set — health, git status/log, read project file, restart-runtime, inspect-runtime-state, stream logs. Explicit verbs only. No arbitrary shell.

## Coordination concerns

**Multiple operator surfaces don't know about each other.** A TUI says "kill session X" while chat says "send prompt to session X" — both arrive at the project kernel. Kernel serializes its command intake (actor-style). Last-arriving wins for conflicting commands; non-conflicting commands compose naturally.

**Read access multiplexes naturally.** All operator surfaces subscribe to the project kernel's event stream. Each renders events in its own way. No coordination required for reads.

**Multi-host operator surface.** When the TUI talks to two hosts, it shows projects from both. Each host kernel knows only its own projects. Aggregation happens in the operator surface (or in a future operator-surface-side aggregator). No host-to-host communication required.

## Two stream types into the runtime: ACP and terminal

Operators need both structured-conversation access (chat, web) AND direct interactive access (sign-in, native runtime TUI, attach). Both are operator-surface concerns and both flow through the same routing stack:

> **operator surface → host adapter → project kernel → swain-box agent**

What differs is the stream type carried over that stack:

- **ACP stream**: structured JSON-RPC, kernel mediates and tracks runtime sessions. Used by chat, web, and any read-only dashboard view.
- **Terminal stream**: bidirectional bytes, kernel routes but doesn't interpret. Used for any time-sliced operator interaction with a runtime CLI or shell.

Both diverge only at the swain-box agent: ACP streams go on to harness ACL → runtime; terminal streams go to a PTY allocated in the container.

### Why TTY is a surface concern, not a bypass

A prior draft modeled TTY as `docker exec -it` from the operator's shell. That:

- violated the bounded-context hierarchy (operator activity skipping host adapter)
- broke multi-node operation (operator surface on a different node than the host has no docker access)
- couldn't be rendered by web UIs

Correcting: terminal access is just another operator-surface stream. Same routing, same auth boundary, same multi-node story as ACP and read-only dashboard streams.

### Use cases unified

Every interactive-runtime case becomes "operator surface opens a terminal stream":

| Case | Surface action | Stream content |
|---|---|---|
| First-time auth (Claude OAuth device flow) | TUI: "auth claude in project A" | `pty_attach('claude', ['/login'])` — operator types device code, watches polling output |
| Native claude TUI | TUI: "open claude TUI in project A, session X" | `pty_attach('claude', ['--resume', 'X'])` |
| Remote-control / attach existing TUI | TUI: "attach to TUI session in project A" | `pty_attach('claude', ['--resume', 'X'])` (or runtime-specific attach mech) |
| Ad-hoc shell | TUI: "shell into project A's box" | `pty_attach('bash', [])` |
| opencode auth bootstrap | TUI: "auth opencode in project A" | `pty_attach('opencode', ['auth', 'login'])` |

Same path for all. No "you must be on the host" caveat.

### What the swain-box agent surface looks like

The agent exposes both stream types over its single connection back to the project kernel:

- **Structured RPC** (request/response): `health_check`, `git_status`, `read_log`, `restart_runtime`, list-active-PTYs, kill-PTY, etc.
- **Streaming** (long-lived bidirectional): `pty_attach(command, args, env)` returns a stream-id; bytes flow both ways keyed to that id

Implementation transport: WebSocket (or local TCP) carrying JSON frames for RPC + binary frames for PTY streams, multiplexed. MVP can ride atop `docker exec -i` for the structured RPC and `docker exec -it` for PTY (same docker-exec abstraction in code). Future RPC daemon supports both natively.

### Which surfaces render terminals

| Surface | Renders terminal? | How |
|---|---|---|
| TUI (host operator TUI) | Yes | Pass-through to operator's terminal, or sub-pane |
| swain-stage (web UI) | Yes | xterm.js |
| Chat adapter | **No** | Auth/shell don't fit chat shape; chat is ACP-only |

Chat being ACP-only is a deliberate scope decision. Anyone who needs to authenticate or directly TUI uses the TUI surface or the web UI.

### Kernel involvement in terminal streams

Kernel is in the routing path; doesn't parse bytes. It tracks:

- Which terminal streams are open against which sessions (state visibility — chat can show "operator is currently in a TUI session" if useful)
- Per-session lock: if a TTY stream is held against session X, kernel refuses parallel ACP spawn for X. Resolves the same-session-conflict concern from earlier drafts. Need a small SPIKE to verify the lock semantics work for runtimes whose attach is process-spawn (claude `--resume` spins a fresh process; another `--resume` for the same id while one's running races at the session-file level — kernel's lock is the cleaner gate)

### What this means for the operator-local `swain-box` CLI

The CLI doesn't bypass the surface model. Commands like `swain-box shell <project>` become **thin clients** — they connect to a TUI surface (or directly to the host adapter as a one-shot ACP/terminal client) and open a terminal stream just like the full TUI would. Same path; just a CLI shape instead of an interactive UI.

### State sharing across both stream types

Credentials and session files live on disk in the container's volumes:

- `/root/.claude/.credentials.json`
- `/root/.claude/projects/<project>/<session-id>.jsonl`
- `/root/.opencode/...`

Both stream types read and write the same disk:

- Auth done over a terminal stream → credentials persisted → next ACP-mode runtime spawn reads them
- TTY-started session → claude writes to its session-files dir → ACP's `session/list` (queried via the runtime) sees it
- No kernel coordination needed for state propagation; runtimes are stateless about who's calling

### Open concerns

- **Concurrent same-session conflict** — addressed by kernel-side locking (above), with a SPIKE to verify under real claude/opencode behavior.
- **OAuth flows that require a real browser** (no device flow). Operator does auth on a host with a browser, then a tooling step copies credentials into the container's volume. Per-runtime case work; document as needed.
- **Persistent detached TUI** (operator disconnects without killing). Out of scope for swain core. Operators who want this run `tmux` inside the container themselves.

## Open decisions deferred

- **Auth between layers.** Bearer tokens? mTLS? Caddy basic auth? Defer until model is finalized; will come with a security-minded ADR.
- **Single chat adapter process or one per service.** Operationally minor; design adapter so either works.
- **Kernel discovery.** When chat adapter receives "user X says hi in project A topic Y", how does it find project A's kernel? Likely Caddy hostname routing — chat adapter targets `https://swain-projecta.localhost`, hostname is in its registration record. Fully resolved during host-kernel definition.
- **swain-box agent RPC verb list** (when we move past MVP).
- **Session persistence semantics across kernel restart.** ACP `session/list` + `session/resume` is the mechanism; what we replay on the chat surface side is a UX decision.
- **Capability bridges for host tmux.** Per-project mount of host tmux socket into the swain-box. Mostly just config; no architectural moving parts beyond the mount.

## What this scratchpad commits to

- Bounded contexts: operator surface → host → project → worktree
- Project kernel runs on host, one per project, stateful
- Host kernel is a real component (more than a watchdog) — ex-watchdog promoted to orchestrator
- Operator surface can move off-host eventually
- ACP is the wire inside the container, ACL per session
- MCP gateway: per-project, host-side, pass-through to start
- swain-box agent: docker exec MVP, RPC-shaped abstraction in code from day one
- Persistence: project state in `.swain/` (gitignored), host registry in `~/.swain/host/`
- Sandbox-level approval, not per-tool; auto-allow ACP permission requests

## What this throws away from prior scratchpads

- "Kernel-in-container" — wrong placement; kernel is host-side
- Generic "ACP proxy in container" framing — replaced by harness ACLs (per session) + swain-box agent (deterministic ops) + (no proxy as a separate component)
- "swain-bridge" as one host process bundling chat adapter + chat-shape domain logic — split into chat adapter (transport, in operator surface) + project kernel (domain, on host)
- Singular "WSS endpoint per swain-box" — replaced by per-session ACP connections from kernel to harness ACL; runtime traffic doesn't traverse the host adapter
- Mixed glossary in v1/v2/multiruntime variants — superseded by this single scratchpad

## What needs to happen before this becomes an ADR

1. Operator review and sign-off on this layered model
2. Decide host kernel naming (use "host kernel" or different?)
3. Settle the still-open decisions above (auth, kernel discovery details)
4. Verify the integration-friction issues actually behave as described under load (read existing worktree code; dispatch a small SPIKE per runtime)
5. Promote to ADR(s): probably one per bounded context (operator-surface ADR, host ADR, project-kernel ADR) — or one big ADR with sections

The current ADR-048 (Container-Per-Project Topology) sits at the host-and-project-container layer; it stays valid. The new ADRs would extend it upward (operator surface) and inward (kernel/ACL split).
