# Pocket Universe — Repository Snapshot

> **Repository**: https://github.com/spoons-and-mirrors/pocket-universe  
> **Version**: 0.1.12  
> **License**: MIT  
> **Description**: Inter-agent messaging for OpenCode parallel subagents  
> **Runtime**: Bun + TypeScript (ESM), peer-dep on `@opencode-ai/plugin ^1.0.0`  
> **Snapshot date**: 2026-04-23

---

## 1. Project Structure

```
pocket-universe/
├── .gitignore
├── .npmignore
├── .opencode/
│   ├── TODO.md
│   └── command/pocket-universe/          # OpenCode command templates
│       ├── spawn.md
│       ├── spawn-02.md
│       ├── sibling-01.md
│       ├── sibling-02.md
│       └── session-resume.md
├── .repomixignore
├── bun.lock
├── package.json
├── README.md
├── tsconfig.json
└── src/
    ├── index.ts                    # Plugin entry point
    ├── config.ts                   # Feature flags + JSONC config loader
    ├── state.ts                    # All in-memory state, aliases, inboxes, cleanup
    ├── types.ts                    # TypeScript interfaces
    ├── logger.ts                   # Logging utility
    ├── agents.ts                   # Agent list cache (fetches from /agent endpoint)
    ├── worktree.ts                 # Git worktree creation for agent isolation
    ├── commands/
    │   ├── index.ts                # /pocket command parser + executor
    │   └── pocket.ts               # /pocket command implementation
    ├── injection/
    │   ├── index.ts                # Re-exports
    │   ├── inbox.ts                # Synthetic broadcast tool-result messages
    │   ├── session.ts              # Session hierarchy helpers (parentId, rootId)
    │   ├── subagent.ts             # Synthetic task-tool injection + completion marking
    │   └── summary.ts              # Pocket Universe Summary generation/injection
    ├── messaging/
    │   ├── index.ts                # Re-exports
    │   ├── core.ts                 # sendMessage, getUnhandledMessages, markMessagesAsHandled
    │   ├── resume.ts               # resumeSessionWithBroadcast, resumeWithSubagentOutput
    │   └── session-update.ts       # Ignored user messages to main session (event log)
    ├── plugin/
    │   ├── hooks.ts                # All OpenCode hooks (session.before.idle, etc.)
    │   └── registry.ts             # Tool registration + /pocket command + config transform
    ├── prompts/
    │   ├── broadcast.prompts.ts
    │   ├── injection.ts
    │   ├── pocket.prompts.ts
    │   ├── recall.prompts.ts
    │   ├── render.ts
    │   ├── subagent.prompts.ts
    │   └── system.ts               # Conditional system prompt template
    └── tools/
        ├── index.ts                # Re-exports
        ├── broadcast.ts            # broadcast tool
        ├── recall.ts               # recall tool
        └── subagent.ts             # subagent tool
```

---

## 2. Closed-Loop Async Agent Implementation

Pocket Universe solves the core problem of async fire-and-forget agents. It implements a **closed loop** where:

### 2.1 Spawning (Fire-and-Forget → Tracked)

The `subagent` tool (`src/tools/subagent.ts`) creates a new OpenCode session as a **sibling** (child of the same parent, not nested):

1. Calls `client.session.create({ parentID })` — creates a peer session, not a nested one
2. Registers the session immediately via `registerSession()` with alias (agentA, agentB, …)
3. Sets virtual depth (caller depth + 1) for spawn-chain limits
4. Optionally creates a git worktree for isolation
5. Injects a synthetic `task` tool result into the parent's message history (visible in TUI)
6. Fires `client.session.prompt()` — does NOT await; returns immediately to the caller
7. Tracks the pending subagent in `callerPendingSubagents` map

### 2.2 Output Piping (Result Delivery)

When the subagent completes, the `.then()` handler:

1. Fetches the subagent's final output via `fetchSubagentOutput()`
2. Marks the session as `idle` in `sessionStates`
3. Saves to `completedAgentHistory` for the `recall` tool
4. Marks the task as completed in the parent TUI
5. Delivers the output to the caller via one of two modes:
   - **forced_attention: true** (default) — adds to the caller's broadcast inbox; if caller is idle, resumes via `resumeSessionWithBroadcast()`
   - **forced_attention: false** — stores in `pendingSubagentOutputs` for hook-based delivery via `resumePrompt`

### 2.3 Session Completion Hook (`session.before.idle`)

The critical hook in `src/plugin/hooks.ts` implements the blocking loop:

1. Checks for pending subagents — waits via polling (`setInterval` every 100ms, timeout 5min)
2. Checks for pending subagent outputs (no forced attention mode)
3. Checks for unread broadcast messages
4. If any are found, sets `output.resumePrompt` to resume the session — **the session does NOT complete until all work is resolved**
5. Only after everything is resolved, checks if this is a first-level child returning to main session, and injects the **Pocket Universe Summary**

### 2.4 Main Thread Blocking

The main session (user's session) receives a **Pocket Universe Summary** — a persisted synthetic user message containing all agent statuses and worktree paths. This is only injected after ALL first-level children complete, tracked via `mainSessionActiveChildren`.

---

## 3. Coordination Between Parallel Subagents

### 3.1 Broadcast Messaging (`broadcast` tool)

- **Status update** (`broadcast(message="...")`): Updates the agent's status history. Passive visibility — other agents see it when they next broadcast. Does NOT wake agents.
- **Direct message** (`broadcast(send_to="agentB", message="...")`): Queues in the recipient's inbox AND resumes the recipient if idle.
- **Reply** (`broadcast(reply_to=1, message="...")`): Marks the original message as handled and auto-wires the recipient to the sender.

Messages are injected into each LLM turn via `experimental.chat.messages.transform` hook as a synthetic `broadcast` tool result containing:
  - `you_are`: the agent's alias
  - `agents`: list of sibling agents with status histories and worktree paths
  - `messages`: inbox messages (replyable)

### 3.2 Inbox System (`src/messaging/core.ts`)

- Per-session inboxes: `Map<sessionId, Message[]>`
- Messages have `handled` flag for deduplication
- `presentedMessages` tracks which messages were already shown to avoid double-delivery
- TTL: handled messages expire after 30 min, unhandled after 2 hours
- Max inbox size: 100 messages per session

### 3.3 Session Resumption (`src/messaging/resume.ts`)

When a broadcast targets an idle agent:
1. Message is stored in inbox
2. `resumeSessionWithBroadcast()` is called
3. Sends a prompt to the idle session via `client.session.prompt()` with a resume prompt
4. After completion, checks for more unread messages — loops until none remain

### 3.4 Pocket Universe Scoping

Each "pocket universe" is scoped to a main session via `sessionToRootId`. Agents from different main sessions are completely invisible to each other. This prevents cross-contamination between parallel user tasks.

### 3.5 `/pocket` Command

Users can send messages to any agent from the main session:
```
/pocket @agentB wrap it up
```
Messages appear as from "user" and resume idle agents.

### 3.6 Recall Tool (`recall`)

Agents can query past agent histories (including completed agents from prior pocket universes if `cross_pocket: true`):
- `recall()` — all agents' status histories
- `recall(agent_name="agentA")` — specific agent's history
- `recall(agent_name="agentA", show_output=true)` — include final output

---

## 4. Key Configuration

Config loaded from (priority order):
1. `.pocket-universe.jsonc` (project-local)
2. `~/.config/opencode/pocket-universe.jsonc` (global, auto-created)

| Flag | Default | Description |
|------|---------|-------------|
| `worktree` | `false` | Create isolated git worktrees per agent |
| `logging` | `false` | Debug logs to `.logs/pocket-universe.log` |
| `tools.broadcast` | `true` | Enable inter-agent messaging |
| `tools.subagent.enabled` | `true` | Enable subagent spawning |
| `tools.subagent.max_depth` | `3` | Max spawn chain depth (main=0) |
| `tools.subagent.forced_attention` | `true` | Subagent results in inbox (false=injected as user message) |
| `tools.recall.enabled` | `false` | Enable agent history query |
| `tools.recall.cross_pocket` | `true` | Access agents from prior pocket universes |
| `session_update.broadcast.status_update` | `false` | Notify main session on status updates |
| `session_update.broadcast.message_sent` | `false` | Notify main session on direct messages |
| `session_update.subagent.*` | `false` | Notify on subagent events |

---

## 5. Architecture Diagrams

### 5.1 Session Hierarchy

```
Main Session (user)
├── AgentA (child session, depth 0→1)
│   └── AgentC (subagent of AgentA, depth 1→2)
└── AgentB (child session, depth 0→1)

All children share the same parentId (main session).
Virtual depth limits prevent runaway spawning.
```

### 5.2 Message Flow

```
AgentA broadcasts → stored in AgentB's inbox
                    → AgentB is idle? → resume AgentB
                    → AgentB is active? → injected on next turn via messages.transform

AgentA spawns AgentC → fire-and-forget prompt()
                    → AgentC completes → output piped to AgentA
                    → AgentA idle? → resume AgentA with output
                    → AgentA active? → added to AgentA's inbox

All agents complete → Pocket Universe Summary injected to Main Session
```

### 5.3 Hook Pipeline

| Hook | Purpose |
|------|---------|
| `experimental.chat.system.transform` | Registers session, injects system prompt, tracks first-level children |
| `experimental.chat.messages.transform` | Injects synthetic broadcast inbox + subagent task messages |
| `session.before.idle` | Blocks completion until subagents finish, processes pending outputs/messages |
| `session.idle` | Marks session idle, marks subagent tasks completed |
| `tool.execute.before` | Captures task descriptions for agent status |
| `tool.execute.after` | Marks task sessions idle, resumes with unread messages |
| `command.execute.before` | Intercepts `/pocket` command and routes to agents |
| `config` | Registers tools + `/pocket` command + subagent_tools |

---

## 6. Key Files Copied

All source files are in `/tmp/pocket-universe-sources/`:

| File | Role |
|------|------|
| `index.ts` | Plugin entry point |
| `state.ts` | All in-memory state, aliases, inboxes, cleanup, agent history |
| `config.ts` | Feature flags, JSONC config loader |
| `types.ts` | TypeScript interfaces |
| `agents.ts` | Agent list cache from opencode API |
| `worktree.ts` | Git worktree management |
| `broadcast.ts` | Broadcast tool implementation |
| `subagent.ts` | Subagent tool implementation |
| `recall.ts` | Recall tool implementation |
| `core.ts` | Core messaging: send, queue, mark handled |
| `resume.ts` | Session resumption logic |
| `session-update.ts` | Main session event notifications |
| `hooks.ts` | All OpenCode lifecycle hooks |
| `registry.ts` | Tool + command registration |
| `inbox.ts` | Synthetic broadcast tool-result message creation |
| `summary.ts` | Pocket Universe Summary generation + injection |
| `subagent.ts` | Subagent task injection + completion marking in parent |
| `session.ts` | Session hierarchy helpers (parentId, rootId) |
| `system.ts` | Conditional system prompt template |

---

## 7. Dependencies

- **Runtime**: `@opencode-ai/plugin ^1.0.0` (peer dep)
- **Dev**: `@opencode-ai/plugin ^1.0.143`, `@types/node ^24.10.1`, `bun-types ^1.3.5`, `prettier ^3.7.4`, `typescript ^5.9.3`
- **Build**: `bun build` + `tsc --emitDeclarationOnly`

---

## 8. Pending Upstream PRs

Per README, this plugin requires:
1. **[opencode PR #9272](https://github.com/anomalyco/opencode/pull/9272)** — async subagents, session resumption, main thread block
2. **[opencode PR #7725](https://github.com/anomalyco/opencode/pull/7725)** — scoping tools to subagents only