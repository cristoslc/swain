# Synthesis: OpenHands Documentation

**Trove:** openhands-docs · 9 sources · created 2026-05-05

---

## Key Findings

### Product Architecture

OpenHands is a multi-layered AI-driven development platform with four main offerings:

1. **Software Agent SDK** — A composable Python library that serves as the engine powering all other OpenHands products. Enables defining agents in code, running locally or scaling to thousands in the cloud.

2. **CLI** — A terminal-based interface similar to Claude Code or Codex, supporting Claude, GPT, and other LLMs.

3. **Local GUI** — A laptop-based solution with REST API and React SPA, comparable to Devin or Jules.

4. **Cloud/Enterprise** — Hosted infrastructure with source-available features including GitHub/GitLab/Bitbucket integrations, Slack/Jira/Linear connectivity, RBAC, multi-user support, and budgeting enforcement.

### SDK Architecture (Four-Package System)

The SDK is organized into four distinct Python packages:

| Package | Purpose | Required |
|---------|---------|----------|
| `openhands.sdk` | Core agent framework + base workspace classes | Always |
| `openhands.tools` | Pre-built tools (bash, file editing, etc.) | Optional |
| `openhands.workspace` | Extended workspace implementations (Docker, remote) | Optional |
| `openhands.agent_server` | Multi-user API server | Optional |

**Deployment Modes:**
- **Mode 1: Local Development**: Just `openhands-sdk` + `openhands-tools`, LocalWorkspace included, no Docker required
- **Mode 2: Production/Sandboxed**: All 4 packages, RemoteWorkspace auto-spawns agent-server in containers

### Agent Architecture Core

The Agent implements a **stateless, event-driven reasoning-action loop**:

1. **Step Execution**: Each `step()` call processes one reasoning cycle
2. **Condensation**: Compresses history when token limits approach
3. **LLM Query**: Queries LLM with messages from event history
4. **Response Parsing**: Tool calls → ActionEvent(s), Messages → MessageEvent
5. **Confirmation Check**: High-risk actions wait for user approval
6. **Action Execution**: Tools execute, create ObservationEvent(s)

**Key Characteristics:**
- Stateless: No mutable state between steps
- Event-Driven: Reads from event history, writes new events
- Interruptible: Each step is atomic and can be paused/resumed

### Tool System Design

The Tool System follows a **strict Action-Observation pattern** with two definition patterns:

**Pattern 1: Direct Instantiation** (Simple Tools)
- For stateless tools: `finish`, `think`
- Components: Action, Observation, ToolExecutor, ToolDefinition

**Pattern 2: Subclass with Factory** (Stateful Tools)
- For tools needing runtime config: `execute_bash`, `file_editor`, `glob`
- Components: Action, Observation, Stateful ToolExecutor, Factory method

**MCP Integration:**
- External tools via Model Context Protocol
- Async MCP bridge with sync wrapper
- Dynamic schema generation from MCP `inputSchema`
- Tools auto-discovered and added during agent initialization

**Tool Annotations (MCP spec):**
- `readOnlyHint`: Doesn't modify state
- `destructiveHint`: May delete/overwrite data
- `idempotentHint`: Repeated calls are safe
- `openWorldHint`: Interacts beyond closed domain

### Core Components

**SDK Package Components:**
- **Agent**: Implements reasoning-action loop
- **Conversation**: Manages conversation state and lifecycle
- **LLM**: Provider-agnostic language model interface with retry and telemetry
- **Tool System**: Action/Observation/Executor pattern with MCP integration
- **Events**: Typed event framework
- **Workspace**: Base classes (Workspace, LocalWorkspace, RemoteWorkspace)
- **Skill**: Reusable prompts with trigger-based activation
- **Condenser**: Conversation history compression for token management
- **Security**: Action risk assessment and validation before execution

### CLI Installation Options

Three installation methods:

1. **Using uv (Recommended)**
   ```bash
   uv tool install openhands --python 3.12
   ```

2. **Executable Binary**
   ```bash
   curl -fsSL https://install.openhands.dev/install.sh | sh
   ```

3. **Using Docker**
   - Full Docker command with environment variables
   - Requires `SANDBOX_USER_ID=$(id -u)` for permission matching

### swain-helm Implementation

Part of **INITIATIVE-018: Remote Operator Interaction** and **VISION-006: Untethered Operator**.

**Core Files:**
- `protocol.py` — Protocol definitions for bridge communication
- `provision.py` — Provisioning logic
- `plugin_process.py` — Plugin process management
- `session_registry.py` — Session registry for tracking active sessions
- `watchdog.py` — Watchdog for monitoring and health checks
- `worktree_scanner.py` — Scans worktrees for active projects
- `opencode_discovery.py` — OpenCode server discovery

**Subdirectories:**
- `adapters/` — Bridge adapters for different platforms
- `bridges/` — Bridge implementations
- `plugins/` — Plugin implementations

**Key Capabilities:**
- Project bridge kernel implementation
- Zulip integration for chat-based agent control
- OpenCode server management
- Session persistence and recovery
- Multi-project worktree scanning
- Plugin system for extensibility

---

## Points of Agreement

- Documentation clearly separates product lines (SDK vs CLI vs Web App)
- LiteLLM serves as the universal LLM interface abstraction
- Sandboxing is flexible with multiple runtime options (Docker, Apptainer, API, Process, Remote)
- Enterprise features are clearly delineated from open source
- Same agent code works in both local and production modes—just swap workspace type
- Stateless design enables reproducibility and debugging

## Points of Distinction

- **ACP vs MCP**: ACP (Agent Client Protocol) is for delegating to agent servers; MCP (Model Context Protocol) is for dynamic tool integration
- **Task vs Sub-Agent**: Tasks run synchronously; sub-agents run in parallel
- **Condenser vs Context**: Condenser compresses history; context management handles active state
- **Direct vs Confirmation Execution**: Direct for development; Confirmation for production with high-risk actions
- **LocalWorkspace vs RemoteWorkspace**: Local for prototyping; Remote for sandboxed production

## Gaps

- No detailed API reference coverage in trove (only high-level architecture)
- Limited information on evaluation infrastructure
- Chrome extension and Theory-of-Mind module only mentioned, not detailed
- Pricing details for Cloud/Enterprise not covered in documentation
- Advanced security analyzer implementation details not fully documented
- Performance benchmarks and comparison data not captured

---

## Related Resources

- [OpenHands Docs](https://docs.openhands.dev)
- [OpenHands GitHub](https://github.com/OpenHands/OpenHands)
- [Software Agent SDK](https://github.com/OpenHands/software-agent-sdk)
- [Product Roadmap](https://github.com/orgs/openhands/projects/1)
- [Community Slack](https://openhands.dev/joinslack)
- [OpenHands Cloud](https://app.all-hands.dev)
- [Enterprise Site](https://openhands.dev/enterprise)
- [swain-helm Implementation](https://github.com/cristoslc/swain/tree/epic/initiative-018-swain-helm-implementation/src/swain_helm)
