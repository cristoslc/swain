# MCP as Distribution Layer — Research Trove

## Sources

- [MCP Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) — accessed 2026-03-18
- [MCP 2025-11-25 Spec Update — WorkOS](https://workos.com/blog/mcp-2025-11-25-spec-update) — accessed 2026-03-18
- [MCP Transport Future — MCP Blog](https://blog.modelcontextprotocol.io/posts/2025-12-19-mcp-transport-future/) — accessed 2026-03-18
- [TypeScript MCP SDK — GitHub](https://github.com/modelcontextprotocol/typescript-sdk) — accessed 2026-03-18
- [Python MCP SDK — GitHub](https://github.com/modelcontextprotocol/python-sdk) — accessed 2026-03-18
- [The MCP Registry](https://modelcontextprotocol.io/registry/about) — accessed 2026-03-18
- [Distribute your MCP server — Speakeasy](https://www.speakeasy.com/mcp/distributing-mcp-servers) — accessed 2026-03-18
- [MCP Registry GitHub](https://github.com/modelcontextprotocol/registry) — accessed 2026-03-18
- [MCP Session Management — Codesignal](https://codesignal.com/learn/courses/developing-and-integrating-an-mcp-server-in-typescript/lessons/stateful-mcp-server-sessions) — accessed 2026-03-18
- [State, long-lived vs. short-lived connections — MCP Discussions](https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/102) — accessed 2026-03-18
- [Everything Wrong with MCP — sshh.io](https://blog.sshh.io/p/everything-wrong-with-mcp) — accessed 2026-03-18
- [MCP Key Limitations — Medium/aimonks](https://medium.com/aimonks/model-context-protocol-mcp-key-limitations-for-regulated-industries-fb351cfae1a1) — accessed 2026-03-18
- [MCP Growing Pains — The New Stack](https://thenewstack.io/model-context-protocol-roadmap-2026/) — accessed 2026-03-18
- [Claude Code MCP Integration Docs](https://code.claude.com/docs/en/mcp) — accessed 2026-03-18
- [Claude Code Skills Docs](https://code.claude.com/docs/en/skills) — accessed 2026-03-18
- [Skills Explained — Claude Blog](https://claude.com/blog/skills-explained) — accessed 2026-03-18
- [Claude Skills vs. MCP — IntuitionLabs](https://intuitionlabs.ai/articles/claude-skills-vs-mcp) — accessed 2026-03-18
- [Claude Code Skills vs MCP vs Plugins — MorphLLM](https://www.morphllm.com/claude-code-skills-mcp-plugins) — accessed 2026-03-18
- [Spec Workflow MCP — GitHub](https://github.com/Pimzino/spec-workflow-mcp) — accessed 2026-03-18
- [Lifecycle MCP Server — GitHub](https://github.com/heffrey78/lifecycle-mcp) — accessed 2026-03-18
- [JetBrains MCP Support](https://www.jetbrains.com/help/ai-assistant/mcp.html) — accessed 2026-03-18
- [VS Code Full MCP Spec Support](https://code.visualstudio.com/blogs/2025/06/12/full-mcp-spec-support) — accessed 2026-03-18

---

## Findings

### MCP Specification Overview

**Current version:** 2025-11-25 (latest stable as of this research)

**Architecture:** MCP uses JSON-RPC 2.0 as its wire format. Three actor roles:
- **Hosts** — LLM applications that initiate connections (e.g., Claude Desktop, VS Code Copilot)
- **Clients** — connectors within the host, one per server connection
- **Servers** — services that provide context and capabilities

The design is explicitly inspired by LSP (Language Server Protocol): a universal adapter standard across an ecosystem rather than point-to-point integrations.

**Core server-side primitives:**

| Primitive | Purpose |
|-----------|---------|
| **Tools** | Executable functions the model calls. Typed inputs via JSON Schema, async handlers. |
| **Resources** | Structured data/context the model or user reads. URI-addressed, can be dynamic. |
| **Prompts** | Reusable message templates that surface as `/commands` in clients. |

**Core client-side primitives (servers can request these of clients):**

| Primitive | Purpose |
|-----------|---------|
| **Sampling** | Server asks the client to run an LLM completion. Enables server-side agent loops. Requires user approval. |
| **Roots** | Server queries the filesystem/URI boundaries it's allowed to operate within. |
| **Elicitation** | Server requests structured user input mid-task (form fields or OAuth browser flows). |

**Additional utility features:** progress tracking, cancellation, error reporting, logging, configuration negotiation.

**2025-11-25 notable additions:**
- **Tasks primitive (experimental):** Any request can return a task handle instead of blocking. Tasks move through `working → input_required → completed/failed/cancelled`. Enables true async long-running workflows and "call now, fetch later" patterns.
- **Sampling with Tools (SEP-1577):** Servers can now initiate agentic reasoning loops — previously sampling had no tool use, which was a major agentic gap.
- **Extensions framework:** Standardizes optional capability additions without bloating core spec.
- **OAuth 2.1 overhaul:** Client ID Metadata Documents (CIMD) replace Dynamic Client Registration. Machine-to-Machine OAuth added for headless agents. Cross App Access (XAA) enables enterprise IdP policy enforcement.
- **URL-Mode Elicitation:** Out-of-band flows for credentials/payments that keep secrets away from the client.

**Forthcoming (Q1–Q2 2026):** The Transport Working Group is moving sessions to the data model layer — making the protocol stateless at the transport level while applications handle stateful semantics explicitly (cookie-like mechanism). Targeted for June 2026 spec update. This eliminates sticky routing requirements for distributed deployments.

---

### Server Development

**Official SDKs:**

| SDK | Status | Notes |
|-----|--------|-------|
| TypeScript/Node | v1.x stable; v2 in pre-alpha, stable expected Q1 2026 | Primary SDK; Zod v4 schema validation; supports Streamable HTTP, stdio, Express/Hono middleware |
| Python | 1.2.0+ required | `FastMCP` class uses type hints + docstrings to auto-generate tool definitions; fastest iteration path |

**Transport options:**
- **Streamable HTTP** — primary modern transport for remote servers; clients POST, server optionally streams via SSE
- **stdio** — for local process servers; simplest dev experience; dominant in current tooling
- **SSE (deprecated)** — legacy remote transport; still supported, HTTP preferred

**Development experience:**

For simple tools, the DX is excellent. `server.tool()` takes a name, description, Zod schema, and async handler. The Python `FastMCP` class is particularly ergonomic — add a decorator, write a function, done.

For complex implementations, there is no hard ceiling. An MCP tool handler is arbitrary code — it can call external APIs, spawn subprocesses, read/write to disk, maintain in-memory state, connect to databases, manage git repos, or implement a full state machine. The protocol places no restrictions on what happens inside a handler.

Key developer ergonomics to note:
- Tool descriptions become the model's only understanding of what a tool does — poor descriptions degrade AI behavior, not just UX
- No standard for tool governance, versioning, or lifecycle management within the spec
- Error handling is not standardized — each server implements its own patterns
- Testing infrastructure is limited compared to mature frameworks

**Complexity ceiling:** None imposed by the protocol. The `lifecycle-mcp` server demonstrates 22 MCP tools spanning 6 handler modules, backed by SQLite, with full ADR tracking, requirement state machines, and GitHub issue sync.

---

### Server Distribution

**Four distribution mechanisms, in increasing ease-of-use:**

1. **Open-source repository** — Ship source + build instructions. Target audience: technical developers comfortable with CLI. Users clone, build, and manually configure `~/.claude.json` or `.mcp.json`.

2. **npm/PyPI package** — Publish to package registry; users install via `npx -y your-package` or `uvx your-package`. Moderate friction; still requires config entry.

3. **MCPB file (formerly DXT)** — Anthropic's zip-archive installer format. One-click installation through Claude Desktop's Extensions interface. No config editing required. Best for non-technical end users.

4. **Remote hosted server** — HTTP endpoint requiring only a URL + optional OAuth. Best end-user experience; requires the author to run infrastructure.

**Official MCP Registry** (in preview as of this research):

- Centralized metadata repository backed by Anthropic, GitHub, PulseMCP, Microsoft
- Stores `server.json` metadata pointing to packages on npm, PyPI, Docker Hub, etc. — does not host code itself
- Namespace authentication via GitHub account or DNS verification (reverse-DNS format: `io.github.username/server`)
- REST API for client/aggregator consumption; not intended for direct host consumption — downstream aggregators (marketplaces) sit between registry and end users
- Does NOT support private servers; private registries must be self-hosted
- Security scanning delegated to underlying package registries and aggregators

**Claude Code Plugin distribution** (most relevant for swain):

Plugins are installable bundles that can include skills, MCP server configs, hooks, and commands. A plugin can bundle an MCP server via `.mcp.json` at the plugin root or inline in `plugin.json`, with `${CLAUDE_PLUGIN_ROOT}` for bundled files and `${CLAUDE_PLUGIN_DATA}` for persistent state. When the plugin is installed, the MCP server starts automatically — zero manual MCP configuration for the user. This is the cleanest distribution path for a tool like swain that is tightly coupled to Claude Code.

**Scope model for Claude Code MCP:**
- `local` (default) — private to current user, current project, stored in `~/.claude.json`
- `project` — committed to `.mcp.json` in project root, shared with all collaborators
- `user` — available across all projects for this user, stored in `~/.claude.json`

Project-scoped servers in `.mcp.json` are the natural fit for per-project artifact management. Support env var expansion (`${VAR:-default}`) for machine-specific paths.

---

### Statefulness and File System Access

This is the most critical section for swain's artifact lifecycle model.

**Short answer: MCP servers can be fully stateful, access the file system unrestricted, and maintain persistent data — but with important architectural caveats.**

**How statefulness works today:**

The current spec establishes stateful sessions at the transport level. When a client connects, a session is initialized and maintained for the duration of the connection. The server can accumulate in-memory state across tool calls within that session. Server code is arbitrary — it can:
- Read and write files anywhere on the filesystem (if permissions allow)
- Maintain SQLite or other embedded databases
- Keep in-memory caches/state machines
- Spawn subprocesses
- Access the network

The `lifecycle-mcp` server uses SQLite with full traceability for requirements, tasks, and ADRs across sessions — demonstrating exactly the kind of persistent artifact lifecycle management swain needs.

**The distributed deployment problem:**

Stateful sessions bind clients to specific server instances. This creates "sticky routing" — a client that connects to server A cannot transparently switch to server B mid-session because session state is not shared. This is fine for local `stdio` servers (one process per user). It is a problem for horizontally scaled cloud deployments, which is why the spec team is working on decoupling session state from transport.

**For swain's use case (local, per-project, stdio), this is a non-issue.** The server runs as a local process, has direct filesystem access to the project directory, and can maintain all the state it needs in SQLite or the working tree.

**Session lifecycle in detail:**
1. `initialize` request — client declares protocol version and capabilities; server responds with its own capabilities
2. Operation phase — client calls tools, reads resources, etc.; server maintains session context
3. Server can use `sampling` to request LLM completions from the client (with user consent)
4. Session ends when transport closes

**The 2026 direction:** Sessions will move to the data model layer. This will actually make stateful servers *more* explicit and *easier* to reason about — applications build stateful semantics intentionally rather than inheriting them from transport layer behavior.

---

### Client Support Matrix

MCP has achieved broad adoption. As of early 2026:

| Client | MCP Support | Notes |
|--------|-------------|-------|
| Claude Code (CLI) | Full | stdio, SSE, Streamable HTTP; Tool Search lazy loading; project/user/local scopes; plugin-bundled servers |
| Claude Desktop | Full | stdio and HTTP; MCPB one-click install; OAuth 2.0 |
| Claude.ai (web) | Full | HTTP remote servers via Connectors; syncs to Claude Code |
| VS Code (Copilot) | Full spec support | All primitives as of June 2025 |
| Cursor | Full | Same configuration as Claude Desktop |
| Windsurf | Full | HTTP and stdio |
| JetBrains IDEs | Full (2025.1+ as client, 2025.2+ as server) | IntelliJ, PyCharm, WebStorm, CLion, Rider, GoLand, RubyMine, PhpStorm, Android Studio |
| Cline (VS Code ext) | Full | |
| Zed | Supported | |
| Continue.dev | Supported | |
| Replit | Supported | |
| OpenAI (ChatGPT) | Emerging | MCP support announced; implementation ongoing |
| Google Gemini tooling | Emerging | MCP support in progress |

A server built once works across all compliant hosts. This is MCP's strongest distribution argument.

**Token management:** A typical setup with 5 MCP servers and 58 tools consumes ~55,000 tokens before any conversation begins. Claude Code's Tool Search feature (requires Sonnet 4+ or Opus 4+) lazy-loads tools on demand, reducing this overhead by up to 85–95%. Tool Search activates automatically when MCP tools would exceed 10% of the context window.

---

### Complex Workflow Examples

MCP servers implementing complex, multi-step workflows exist and are production-grade:

**Spec Workflow MCP** (`Pimzino/spec-workflow-mcp`):
- Enforces sequential progression through Requirements → Design → Tasks phases
- Prevents phase-skipping; requires approval at each transition
- Real-time dashboard (localhost:5000) + VS Code extension
- Docker deployment; enterprise security headers, rate limiting, audit logging
- Supports multiple AI tools (Claude, Augment, Continue IDE, etc.)
- Closest existing analog to what swain does

**Lifecycle MCP Server** (`heffrey78/lifecycle-mcp`):
- 22 MCP tools, 6 handler modules
- SQLite persistence with full requirement traceability
- ADR (Architecture Decision Record) tracking with decision drivers, options, consequences
- Requirement state machine: Draft → Under Review → Approved → Architecture → Ready → Implemented → Validated → Deprecated
- Task management with effort estimation and GitHub issue synchronization
- Project health dashboards

**Microsoft Dynamics 365 ERP MCP Server**:
- Dynamic tool catalog that adapts as business needs evolve
- Agents perform nearly any ERP function without custom code
- Enterprise production deployment

**Project Management MCP** (`tejpalvirk/project`):
- Knowledge graph for projects, tasks, milestones, resources, team members
- `getDecisionLog`, `getProjectHealth`, `getPriorityItems` tools
- Multi-step workflow support for risk management and resource allocation

These examples confirm that MCP can implement arbitrarily complex workflows. The protocol does not limit tool implementation depth.

---

### Known Limitations

**Protocol-level:**

1. **No tool risk categorization.** Read-only file access and irreversible deletions look identical to the protocol. No standard mechanism for grading or gate-keeping tools by risk level. Encourages dangerous "auto-confirm" patterns.

2. **"Rug pull" vulnerability.** Servers can dynamically redefine tool names and descriptions after users have confirmed them. The spec notes tool annotations are "hints that should not be relied upon for security decisions."

3. **Prompt injection surface.** MCP tools are often embedded in system prompts, giving a compromised server authority to override assistant behavior. This is a higher-privilege attack surface than user-level prompt injection.

4. **No standard error handling.** Error handling is per-server; clients cannot rely on consistent error semantics.

5. **No tool governance, versioning, or lifecycle management in spec.** No standard for deprecating, versioning, or migrating tools.

6. **Cost opacity.** No standard for signaling token costs of tool responses. Unstructured text responses can silently consume large context budgets.

7. **No rich async UI.** MCP transmits unstructured text, images, or audio only. The new Tasks primitive helps with async state, but there is no mechanism for rich interactive confirmation flows (e.g., "show me this diff before you apply it") at the protocol level.

8. **LLM reliability gap.** State-of-the-art models achieve only ~16% success on complex multi-step tool benchmarks (e.g., airline booking). The protocol's quality is bounded by the model's tool-use reliability. Model sensitivity to tool naming means identical implementations perform differently across LLM backends.

**Ecosystem-level:**

9. **Registry still in preview.** Breaking changes and data resets possible. Not yet GA.

10. **Distributed statefulness.** Stateful sessions resist horizontal scaling; sticky routing required. (Targeted for resolution in June 2026 spec update.)

11. **Compliance gaps.** No SOC 2, PCI DSS, FedRAMP certification. Audit logs do not meet GDPR/SOX standards. No SLA guarantees. A blocker for regulated industries but not relevant to swain's use case.

12. **Role separation absent in v1.** The spec did not originally standardize authorization — same person must both configure the server and use it. OAuth 2.1 work (2025-11-25) is resolving this for multi-user scenarios.

13. **No multi-tenancy primitive.** No built-in mechanism for enforcing different access levels for different agents. Must be implemented per-server.

---

### MCP vs Native Skills Comparison

This section focuses on what matters for swain: a tool that orchestrates artifact lifecycle in Claude Code sessions.

**What skills are:**

Claude Code skills are prompt-based conversation modifiers. A skill is a directory with a `SKILL.md` (YAML frontmatter + markdown instructions) and optional supporting files (templates, scripts, reference docs). When invoked, the skill content is injected into the conversation as enriched context — no separate process, no RPC, no transport layer.

Key capabilities:
- **Bundled scripts:** Skills can include and execute scripts in any language. Shell commands in `` !`command` `` syntax run before the skill content reaches Claude; output is injected inline.
- **Progressive disclosure:** Descriptions load at startup (~100 tokens); full content loads only when relevant (<5k tokens); supporting files load only when referenced. Token overhead is minimal.
- **Frontmatter control:** `disable-model-invocation`, `user-invocable`, `allowed-tools`, `model`, `context: fork`, `hooks` — fine-grained control over when and how skills run.
- **Subagent execution:** `context: fork` runs the skill in an isolated subagent with its own tool set. Supports parallel execution of multiple agents.
- **Dynamic context injection:** Shell command output, `${CLAUDE_SESSION_ID}`, `${CLAUDE_SKILL_DIR}` substitutions.
- **Scoping:** Enterprise > Personal > Project > Plugin levels; monorepo support via nested `.claude/skills/` discovery.
- **Distribution:** Committed to `.claude/skills/` in source control (project skills) or packaged in a plugin.

**Head-to-head for swain:**

| Capability | Native Skills | MCP Server |
|------------|--------------|------------|
| Workflow orchestration (multi-step, conditional) | Excellent — skill instructions + agent reasoning | Good — tools implement steps; model orchestrates |
| File system read/write | Via Claude's built-in tools (Read, Edit, Write, Bash) | Via custom tool handlers with direct Node.js/Python fs access |
| Persistent state across sessions | Not natively; must use files or external state | Native via in-process memory, SQLite, or any DB |
| Lifecycle state machines (e.g., SPEC states) | Encoded in instructions; enforced by model reasoning | Enforced programmatically in tool handlers; deterministic |
| Token overhead | ~100 tokens/skill description; <5k full load | 55k+ tokens for 5 servers/58 tools (before Tool Search); ~2-11k with Tool Search |
| Multi-client portability | Claude Code and compatible agents only | Any MCP-compliant host (VS Code, Cursor, JetBrains, etc.) |
| Cross-project reuse | Personal skills (`~/.claude/skills/`) or plugins | User-scoped config or plugin bundles |
| Installation friction | Zero — committed to `.claude/skills/`; auto-discovered | One command (`claude mcp add`) or bundled in plugin |
| Deterministic constraint enforcement | Weak — model can ignore instructions | Strong — tool handlers can refuse invalid transitions |
| Version control for business logic | Markdown in git | Code (TS/Python) in git |
| Testing | No standard framework | Standard unit/integration testing for handlers |
| Debugging | Inspect conversation context | Standard process debugging, logs, observability tools |
| Complexity ceiling | High — bundled scripts can do anything | Unlimited — arbitrary server code |
| Security surface | Lower — no external process | Higher — separate process with own permissions |

**Key asymmetries:**

Skills excel at encoding *how Claude should reason and act* — they are instructions with teeth. They are sovereign to Claude Code's own tool layer and leverage the model's native reasoning for orchestration. They are zero-overhead to install, impossible to misconfigure, and highly legible to operators (it's just markdown).

MCP servers excel at *enforcing constraints programmatically* — a tool handler can refuse an invalid state transition in a way that model reasoning cannot. They expose capabilities across multiple AI clients without re-implementation. They can maintain state that outlives the conversation.

The hybrid model — skills for orchestration logic and methodology, MCP for deterministic enforcement and persistence — is the pattern most often recommended by practitioners. This is explicitly how Claude Code itself is designed: skills use MCP tools internally when they need real external access.

**What swain would lose by going MCP-only:**
- The ergonomic skill invocation model (`/swain-design`, `/swain-do`, etc.)
- Inline context injection that keeps operator mental model coherent
- Zero-friction distribution (no server to run, configure, or auth)
- CLAUDE.md / AGENTS.md as the normative source of constraints (currently human-readable by operators)
- Skill chaining patterns (skills that chain to other skills)

**What swain would gain by going MCP-only:**
- Deterministic artifact state machine enforcement (no "model ignored the instruction" failures)
- Persistent lifecycle DB that survives conversation resets
- Multi-client support (Cursor, VS Code, etc.)
- Testable business logic (unit tests for state transitions)
- Structured data queries (e.g., "show all epics with all specs complete")

**What a hybrid architecture would look like:**
- Skills remain the operator-facing interface and orchestration layer
- An MCP server provides the persistence layer (SQLite artifact store) and deterministic enforcement (state machine transitions, tk integration)
- Skills call MCP tools when they need to read/write artifact state or enforce transitions
- This is already the natural direction of Claude Code's own plugin system, which explicitly supports bundling MCP servers alongside skills

---

## Key Takeaways

1. **MCP can fully implement swain's artifact lifecycle needs.** Stateful servers with SQLite persistence, file system access, ADR tracking, and state machine enforcement all exist in production MCP servers today (lifecycle-mcp, spec-workflow-mcp). The protocol places no ceiling on handler complexity.

2. **The strongest architecture for swain is hybrid, not a replacement.** Skills handle orchestration, methodology, and operator UX. An MCP server handles persistence, deterministic state enforcement, and data queries. Claude Code's plugin system was designed for exactly this pattern — bundle both in a single installable artifact.

3. **MCP's portability advantage is real but bounded.** An MCP server works in VS Code, Cursor, JetBrains, and any other compliant host. But swain's skills (the orchestration layer) would still be Claude Code-specific. If multi-client portability is a goal, both layers need multi-client paths.

4. **The MCP distribution story is maturing but not complete.** The registry is in preview. Plugin-bundled servers (the cleanest path for swain) are the right model. MCPB one-click install exists for Claude Desktop but Claude Code plugin distribution is the first-class path for swain's audience.

5. **Token overhead is a solved problem for Claude Code users, not for everyone.** Tool Search eliminates 85–95% of MCP context overhead in Claude Code (Sonnet 4+ only). For other clients that don't implement Tool Search, a large MCP server can consume significant context budget. This matters if swain targets non-Claude-Code clients.
