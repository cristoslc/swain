---
title: "Swain v2 as Tool, Not Skill — CLI + MCP Architecture Exploration"
artifact: SPIKE-073
track: container
status: Proposed
author: cristos
created: 2026-05-01
last-updated: 2026-05-01
question: "What would swain v2 look like as a standalone tool (CLI binary, MCP server, or both) instead of an injected skill overlay?"
gate: Pre-Vision
parent-vision: ""
parent-initiative: ""
risks-addressed:
    - Skill-injected methodology has no deterministic enforcement — agents can ignore instructions.
    - Skill files consume context window tokens even with progressive disclosure.
    - Skills are surface-specific (Claude Code, Codex, Gemini CLI each need adaptation).
    - Operator cannot directly invoke swain outside an agent session.
    - Agent-as-router problem: both skills AND MCP tools depend on the agent choosing to invoke them correctly and at the right moments.
trove: "skills-as-tools@1d55769"
linked-artifacts:
  - SPIKE-030
  - EPIC-033
  - SPEC-319
authored-by: deepseek-v4-pro:cloud
---

# Swain v2 as Tool, Not Skill — CLI + MCP Architecture Exploration

## Summary

This SPIKE explores the design space for swain v2 as a standalone tool rather than a skill overlay injected into agent context windows. It maps four architectural options (CLI-only, MCP-only, full hybrid, ACP-integrated), evaluates each against swain's core requirements, and recommends a phased hybrid approach starting with an MCP server and thin CLI wrapper. The key insight: tools provide deterministic enforcement that skills cannot — lifecycle state machines become code gates, not text suggestions.

## Question

What would swain v2 look like as a standalone tool — a CLI binary, an MCP server, or both — instead of the current skill-injected pattern?

## Scope

**This SPIKE explores what *could* be built.** It does not set scope for building it. The exploration informs a future VISION artifact for swain v2 tooling.

### What Changes from Swain v1 (Skills)

| Aspect | v1 (Skills) | v2 (Tools) |
|--------|------------|-----------|
| Delivery | `.md` files in `.claude/skills/` or `.agents/skills/` | `swain` binary + optional MCP server |
| Invocation | Skill chaining (`/swain-design`, `/swain-do`) | `swain design "..."`, MCP tool calls |
| Enforcement | Advisory ("should") via injected text | Deterministic ("must") via code checks |
| State | Ephemeral (context window) | Persistent (SQLite/JSON on disk) |
| Operator access | Only through agent | Independent CLI for direct use |
| Distribution | `npx skills add cristoslc/swain` | `brew install swain` / `npx swain` / plugin |
| Portability | Per-runtime adaptation | Any MCP client or any tool-calling agent |
| Readability | Operator reads markdown | Operator reads CLI output and MCP dashboards |
| Testing | No standard framework | Standard unit/integration tests for all logic |
| Context cost | 30–50 tokens/skill until loaded (progressive) | Tool definitions in context window (~1–10k for 10–15 tools) |

### Design Axes

The tool-vs-skill question splits into four architectural axes:

1. **CLI tool** — a `swain` binary that agents invoke via `bash` (like git, npm, cargo).
2. **MCP server** — an MCP server exposing swain primitives as Tools, Prompts, and Resources.
3. **Full hybrid** — a CLI binary *and* an MCP server, one codebase, two interfaces.
4. **ACP agent** — swain as an ACP (Agent Client Protocol) agent, participating in sessions as a peer.

## Options Analysis

### Option 1: CLI-Only (`swain` binary)

A standalone executable that agents call through their `bash` tool.

```
swain design "Create a spec for user authentication"
swain do "Claim task T15 from SPEC-082"
swain status --roadmap
swain session start
```

**What it looks like:**
- A Go, Rust, or Python binary distributed via `brew install swain`, npm, or pip.
- Agents invoke `swain <subcommand>` as they would `git log` or `npm test`.
- Subcommands map to current skill workflows: `design`, `do`, `status`, `session`, `search`, `sync`, `release`, `retro`, `teardown`.
- Output is structured (JSON for agents, human-readable for operators).
- State persists in `~/.swain/` or `./.swain/` per project.

**Strengths:**
- Zero protocol dependency — works with any agent that can run bash.
- Operator can use the CLI directly without an agent session.
- Familiar UX (like git or npm).
- Deterministic enforcement: code gates at every subcommand.
- Easy distribution: any package manager.
- No token overhead from tool definitions (agent sees CLI output, not tool schemas).
- Testable with standard integration tests.

**Weaknesses:**
- Agent must parse CLI output to understand state — no structured tool discovery.
- Each call is a fresh process — no persistent connection.
- No slash-command ergonomics (`/swain-design` becomes `swain design` through bash).
- Methodology loading is implicit (agent reads manpages/help) rather than explicit skill chaining.
- Operator needs to learn CLI commands (though git-like familiarity helps).

**Verdict:** Viable standalone. Best for operators who want direct access. Weak as the *only* agent interface — agents benefit from structured tool descriptions.

### Option 2: MCP-Only (MCP Server)

A Python or TypeScript MCP server exposing swain's full capability surface.

```
# Agent sees:
Tools: design, do_status, chart_query, lifecycle_transition, load_methodology, ...
Prompts: design, do, status, session
Resources: artifact-graph://current, artifact://SPEC-082
```

**What it looks like:**
- MCP server (`swain-mcp`) using FastMCP (Python) or TypeScript SDK.
- 10–15 Tools covering artifact CRUD, lifecycle transitions, chart queries, status, task tracking.
- MCP Prompts for `design`, `do`, `status`, `session` (surfaced as `/mcp__swain__design` slashes).
- MCP Resources for artifact definitions, templates, and artifact content (URI-addressable).
- SQLite persistence for artifact state across sessions.
- Deterministic lifecycle state machine (refuses invalid transitions).
- `load_methodology` tool returns instructional text — the portable skill-chaining bridge.

**Strengths:**
- Structured tool discovery — agent knows exactly what swain can do.
- Deterministic enforcement at every tool handler.
- Persistent state across sessions.
- Multi-client portability (Claude, Codex, Copilot, Gemini CLI, VS Code, Cursor, JetBrains).
- MCP Prompts replace slash commands.
- `load_methodology` provides skill-chaining-equivalent behavior.
- MCP Resources make artifact content queryable.
- Server-controlled orchestration via Sampling (long-term).

**Weaknesses:**
- Token overhead from tool definitions (1–10k tokens for 10–15 tools, 85% reducible with Tool Search).
- Separate process lifecycle — server must be running.
- No operator-facing interface without an agent.
- Auth complexity (OAuth2 setup for remote, stdio fine for local).
- "Rug pull" vulnerability (servers can redefine tool descriptions).
- MCP Prompts UX gap vs native slash commands (improving but not solved).

**Verdict:** Strong primary interface. Best for agent ergonomics. Weak for direct operator access. Already decomposed in EPIC-033 with 9 child SPECs.

### Option 3: Full Hybrid (CLI + MCP)

One codebase exposing both a CLI and an MCP server. The CLI wraps the MCP server's logic or shares a common core library.

```
# Operator direct use:
swain design --title "New Auth" --parent EPIC-033
swain do claim T15
swain status --roadmap

# Agent MCP use:
Tool call: swain__design(title="New Auth", parent="EPIC-033")
Tool call: swain__do_claim(task_id="T15")
Tool call: swain__chart_query(kind="roadmap")
```

**What it looks like:**
- A shared Python or TypeScript library implementing swain's domain logic.
- `swain` CLI binary: thin command dispatch over the library.
- `swain-mcp` server: MCP tools wrapping the same library calls.
- One codebase, one test suite, two interfaces.
- CLI for operators, MCP for agents.

**Strengths:**
- Best of both worlds: operator CLI + agent MCP.
- Single source of truth for domain logic.
- Single test suite covering both interfaces.
- Operator can test workflows directly.
- Agents get structured tool discovery.

**Weaknesses:**
- Heaviest implementation load (both interfaces to build and maintain).
- Distribution complexity (CLI + MCP server = two install targets).
- Token overhead from MCP tool definitions still applies.
- Risk of CLI/MCP interface divergence over time.

**Verdict:** Ideal end-state. Full coverage. Highest implementation cost. Staged rollout recommended.

### Option 4: ACP Agent

Swain as a peer agent communicating via the Agent Client Protocol (ACP), participating in multi-agent sessions alongside Claude, Codex, etc.

```
# Agent invokes swain as an ACP peer:
acpx swain 'transition SPEC-082 to Active'
acpx swain exec 'create trove for auth-patterns research'
```

**What it looks like:**
- Swain runs as an ACP-compatible server process.
- Other agents discover and invoke it through the ACP protocol.
- Swain maintains its own state, session memory, and methodology enforcement.
- Acts as a specialized "methodology agent" in a multi-agent setup.

**Strengths:**
- Clean separation of concerns — swain is a peer, not an overlay.
- Headless, non-interactive sessions with permission profiles.
- Cross-harness compatibility (any ACP agent can call swain).
- Sessions survive restarts.
- The acpx pattern already proves viability.

**Weaknesses:**
- ACP ecosystem is newer and smaller than MCP.
- Requires agents to support ACP (growing but not universal).
- Adds protocol complexity on top of MCP.
- Operator access still indirect (through ACP agent or separate CLI).
- Unclear value-add over MCP for single-operator workflows.

**Verdict:** Forward-looking. Interesting for multi-agent setups. Overengineering for the primary solo-operator use case. Defer to post-VISION exploration.

## The Agent-as-Router Problem

MCP tools and skills share a fundamental weakness: both depend on the agent choosing to invoke them. The agent is the router. The tool does not decide when it runs — the agent does.

### Three Layers of Enforcement

| Layer | What enforces it | When it fires | Agent can skip? |
|-------|-----------------|---------------|-----------------|
| **Skill** | Agent's own reasoning | Agent decides to follow instructions | Yes — entirely advisory |
| **MCP tool** | Code gate in handler | Agent decides to call the tool | Yes — tool is never called |
| **Hooks / pre-commit / CI** | External trigger | Automatically on events | No — fires regardless of agent intent |

Skills and MCP tools only differ at layer 2: what happens *after* invocation. Neither improves layer 1: whether invocation happens at all.

### What Swain Actually Needs Enforcement For

Consider SPEC-073's lifecycle transitions. The current skill says "when a spec is implemented, transition it to Complete." The agent decides whether to do that. An MCP tool `swain__lifecycle_transition(spec="SPEC-073", phase="Complete")` checks that tasks are done before allowing the transition. But the agent still decides whether to call the tool.

The enforcement chain has two links:
1. **The agent must initiate the transition.**
2. **The transition must be valid.**

An MCP server hardens link 2. It does nothing for link 1.

### Where the Router Problem Hurts Most

| Swain ceremony | Router risk | Severity |
|---------------|------------|----------|
| Phase transitions (spec/epic lifecycle) | Agent forgets to transition after finishing work | High — state drifts from reality |
| Task tracking (claim, close, depend) | Agent does work without tracking | High — no visibility into progress |
| ADR compliance checks | Agent skips checking ADRs before changes | Medium — constraint violations accumulate |
| Session bookmarks | Agent doesn't bookmark context | Low — operator can still resume manually |
| Retrospectives | Agent doesn't reflect after completion | Medium — learning lost |

Skills fail at these because the agent ignores them under context pressure. An MCP server fails at these for the same reason: the agent must still *choose* to call `swain__transition` or `swain__task_claim`.

### What Actually Escapes the Router: External Triggers

The only interventions that bypass the agent's routing decision are mechanisms that fire independently:

1. **Hooks** (Claude Code's PreToolUse/PostToolUse). Fires before/after tool calls. Can block or augment behavior. Example: a PostToolUse hook on `Write` that checks `git diff` and warns if no spec tracking matches the changed files. The agent cannot skip this — the hook fires regardless.

2. **Git hooks** (pre-commit, pre-push). Runs `swain validate` before commits. Refuses commits that violate ADR constraints or reference unparented artifacts. The agent cannot commit without passing validation.

3. **CI/CD gates**. Runs `swain check --all` in CI. Blocks merge if lifecycle state doesn't match branch content. Works across agents and sessions.

4. **Operator-manual enforcement**. The operator runs `swain check` and sees violations. This doesn't prevent anything but creates visibility.

5. **Shell wrapper / shim**. A `swain-shell` that wraps the agent's tool execution, intercepting bash calls and refusing ones that violate process constraints. More invasive but more powerful.

### Where MCP Actually Helps vs Skills

MCP's value is not in solving the router problem. It's in:

| Value | MCP provides | Skills also provide? |
|-------|-------------|---------------------|
| Structured state query | Yes (chart_query, artifact_content as Resources) | No |
| Persistent state across sessions | Yes (SQLite) | No |
| Deterministic gate-check (if called) | Yes (lifecycle state machine) | No |
| Cross-client portability | Yes (any MCP client) | Partial (Claude + Codex + Gemini CLI) |
| Testable logic | Yes (standard test frameworks) | No |
| Operator CLI access | Only with wrapper | No |
| Automatic invocation | No | No |

The right framing: MCP makes swain a *usable resource* that enforces rules when consulted. It doesn't make swain a *proactive enforcer* that prevents process violations.

## Revised Decision Matrix

Adding "escapes router problem" as a criterion changes the analysis:

| Criterion | CLI-Only | MCP-Only | Full Hybrid | Hook/Gate | Shell Wrapper |
|-----------|----------|----------|-------------|-----------|---------------|
| Deterministic enforcement (if called) | ++ | ++ | ++ | ++ | ++ |
| Escapes agent-as-router | - | - | - | ++ | ++ |
| Operator direct access | ++ | - | ++ | -- | - |
| Agent ergonomics | - | ++ | ++ | -- | + |
| Cross-runtime portability | + | ++ | ++ | - | - |
| Structured tool discovery | - | ++ | ++ | - | - |
| Token overhead | ++ | + | + | ++ | ++ |
| Implementation complexity | + | + | - | + | - |
| Distribution simplicity | ++ | + | - | + | - |
| State persistence | + | ++ | ++ | - | - |
| Blocks invalid actions | - | - | - | ++ | ++ |
| Visibility into state | + | ++ | ++ | - | - |

(Hook/Gate = pre-commit hooks + CI gates + Claude Code hooks; Shell Wrapper = shim intercepting agent tool calls)


| Criterion | CLI-Only | MCP-Only | Full Hybrid | ACP Agent |
|-----------|----------|----------|-------------|-----------|
| Deterministic enforcement | ++ | ++ | ++ | ++ |
| Operator direct access | ++ | - | ++ | - |
| Agent ergonomics | - | ++ | ++ | + |
| Cross-runtime portability | + | ++ | ++ | + |
| Structured tool discovery | - | ++ | ++ | + |
| Token overhead | ++ | + | + | + |
| Implementation complexity | + | + | - | - |
| Distribution simplicity | ++ | + | - | - |
| State persistence | + | ++ | ++ | ++ |
| Testability | ++ | ++ | ++ | ++ |
| Slash-command ergonomics | - | + | + | - |

## Findings

### 1. MCP Does Not Escape the Agent-as-Router Problem

This is the critical finding. Skills fail at enforcement because the agent decides whether to follow instructions. MCP tools fail at enforcement for the identical reason: the agent decides whether to call the tool. A lifecycle state machine that refuses invalid transitions is worthless if the agent never calls the transition tool.

The value of MCP over skills is real but narrow:
- Once called, MCP provides deterministic gate-checking (skills provide advisory text).
- MCP provides persistent, queryable state (skills provide only current context).
- MCP provides cross-client portability (skills need per-runtime adaptation).

But none of this addresses *whether the ceremony happens at all*. [See Agent-as-Router Problem above.]

### 2. The Persistence Fork: Files-in-Repo vs SQLite Authority

EPIC-033 and SPIKE-030 assume SQLite persistence for the MCP server. But artifact state currently lives in `.md` files under `docs/` — the same files specgraph parses to build the graph. This creates a fork with three paths:

**Path A: Files stay in the repo. MCP is a pass-through.**
- Artifacts remain `.md` files under `docs/` (exactly as today).
- MCP tools read/write frontmatter directly in those files (using existing parsers).
- specgraph works unchanged — reads files from disk, builds graph from frontmatter.
- MCP server has no persistent store of its own; it's a thin wrapper over the filesystem + specgraph.
- Git tracks everything. Operator reads files directly. No duplication risk.

**What this looks like in practice:**
```
Agent calls: swain__lifecycle_transition(spec="SPEC-073", phase="Complete")
MCP handler:
  1. Reads docs/spec/Proposed/(SPEC-073)*/SPEC-073.md
  2. Parses frontmatter → checks tasks resolved, valid transition
  3. Edits status: Proposed → Complete
  4. Moves file: docs/spec/Proposed/... → docs/spec/Complete/...
  5. Returns success or error with reason

Agent calls: swain__chart_query(kind="roadmap")
MCP handler:
  1. Runs specgraph --build if stale
  2. Calls specgraph overview --json
  3. Returns structured output
```

**Strengths:**
- No second source of truth. Files ARE the state.
- specgraph works unchanged. Zero migration of existing parsers.
- Operator can still read/edit files directly. MCP is not mandatory.
- Git diffs are meaningful — see exactly what changed.
- Phase changes are git-tracked (file moves between phase directories).
- No synchronization risk between SQLite and files.

**Weaknesses:**
- No SQL-level structured queries on artifact state. Every query parses files or reads specgraph cache.
- MCP state (task tracking, sessions, bookmarks) has nowhere to live except .md files or separate files.
- Concurrent access from multiple agents could conflict (write races on same file).
- specgraph cache invalidation adds latency on every query that touches changed files.
- No transaction guarantees — file moves + frontmatter edits are not atomic.

**Path B: Lift state into SQLite. Files become a mirror or disappear.**
- Artifact state lives in SQLite as the authority.
- MCP tools read/write SQLite exclusively.
- `.md` files under `docs/` are either generated from SQLite (sync script) or abandoned entirely.
- specgraph would need to read from SQLite instead of file frontmatter (rewrite parser).
- Git tracks generated files (diverge risk) or they're gitignored (lose git history).

**What this looks like in practice:**
```
Agent calls: swain__lifecycle_transition(spec="SPEC-073", phase="Complete")
MCP handler:
  1. SQL query: SELECT status, depends_on FROM artifacts WHERE id='SPEC-073'
  2. Checks all depends_on targets are Complete
  3. UPDATE artifacts SET status='Complete', phase_dir='Complete' WHERE id='SPEC-073'
  4. Regenerate markdown file at new location (or defer to sync)
  5. Returns success or error

Agent calls: swain__chart_query(kind="roadmap")
MCP handler:
  1. Runs SQL queries joining artifacts, edges, statuses
  2. Assembles graph in-memory
  3. Returns structured output
```

**Strengths:**
- Structured queries are fast and powerful — "all specs with phase=Proposed AND parent_epic=EPIC-033".
- Concurrent access handled by SQLite's WAL mode.
- Task tracking, sessions, bookmarks live naturally alongside artifacts.
- Transactional — phase transitions are atomic (SQL file move + status update in one commit).
- specgraph becomes a SQL reader, not a filesystem parser.

**Weaknesses:**
- specgraph parser must be rewritten to read SQLite instead of YAML frontmatter (significant migration).
- Git loses meaningful diffs — SQLite binary blobs or generated markdown (divergence risk).
- Operator cannot directly edit artifact state without a tool (`swain edit SPEC-073 --field status=Active`).
- Two sources of truth if files are kept: SQLite + generated files must stay in sync.
- If files are abandoned, all existing scripts (design-check.sh, adr-check.sh, renumber-artifact.sh, relink.sh) must be rewritten for SQLite.
- Loss of git history for artifact changes — SQL commits replace git commits.

**Path C: Hybrid — SQLite for operational state, files for artifact truth.**
- Artifact definitions and lifecycle remain authoritative in `.md` files.
- specgraph continues to read files as today (unchanged).
- MCP server adds SQLite only for operational state: task tracking, session state, bookmarks, decision logs.
- MCP tools read files for artifact queries (via specgraph), use SQLite for session-scoped state.
- No second source of truth for artifacts — files are always canonical.
- SQLite is disposable (session scratch space), not authoritative.

**What this looks like in practice:**
```
Agent calls: swain__task_claim(task_id="T15", spec="SPEC-073")
MCP handler:
  1. Checks SQLite session_tasks for conflicts
  2. INSERT INTO session_tasks (task_id, spec, status, claimed_at)
  3. No file touched — tasks are session-scoped

Agent calls: swain__lifecycle_transition(spec="SPEC-073", phase="Complete")
MCP handler:
  1. Reads SQLite session_tasks to verify all tasks done
  2. Reads .md file, validates transition
  3. Edits frontmatter, moves file (filesystem operation)
  4. No SQLite artifact write — files are the authority

Agent calls: swain__session_start()
MCP handler:
  1. Creates session row in SQLite
  2. Loads last session's bookmark from SQLite
  3. Returns current specgraph overview (read from files)
```

**Strengths:**
- Files remain the single source of truth for artifacts. specgraph unchanged.
- Operational state (tasks, sessions, bookmarks) gets SQL benefits without contaminating artifact truth.
- No migration of file-based scripts.
- SQLite session data can be gitignored or ephemeral.
- Phase transitions remain git-tracked.
- Implementation is incremental — add SQLite for operational state, keep files for artifacts.

**Weaknesses:**
- Artifact queries still go through specgraph cache (same latency as today).
- Task state is not git-tracked (unless session_tasks.db is committed).
- Two stores to manage (files + SQLite), though with clear ownership boundaries.
- Less structurally clean than Path B (single store), but preserves existing investment.

### Which Path Aligns With Swain's Identity?

Swain's core value is artifacts on disk that encode decisions, scope, and constraints. This is in AGENTS.md: *"Artifacts on disk — specs, epics, spikes, ADRs — live under docs/ and encode what was decided, what to build, and what constraints apply."*

Path A (files in repo, MCP pass-through) or Path C (hybrid, files authoritative) preserve this identity. Path B (SQLite authority, files optional) changes what swain IS — from a documentation discipline to a database application.

Path C is the recommended starting point. It adds operational state (tasks, sessions, bookmarks) — the things that currently have no structured persistence — without changing what artifacts are. Path B is a valid long-term direction but changes swain's fundamental nature and needs its own evaluation separate from the tool-vs-skill question.

### 3. Solving the Router Problem Requires External Triggers

Mechanisms that bypass agent routing:
- **Hooks** fire on tool execution events — agent cannot skip them.
- **Git hooks** fire on git operations — agent cannot commit without passing checks.
- **CI gates** fire on push/PR — process violations block merge.
- **Shell wrappers** intercept agent tool calls — refuse invalid operations before they execute.

These are the complement to tools, not an alternative to them. A swain tool provides the enforcement logic; a hook or gate provides the trigger that ensures the tool is consulted.

### 4. The Design Space Splits Along the Router Line

| Approach | Solves call-side | Solves check-side | Overhead |
|----------|-----------------|-------------------|----------|
| Skills-only | No (agent decides) | No (advisory) | Lowest |
| MCP-only | No (agent decides) | Yes (code gates) | Medium |
| MCP + hooks | Partially (hooks fire on events) | Yes (code gates) | Medium-high |
| MCP + git hooks | Yes (commit/push gates) | Yes (code gates) | Medium-high |
| Shell wrapper | Yes (intercepts tool calls) | Yes (code gates) | High |
| Full CI/CD | Yes (merge gates) | Yes (code gates) | Highest |

The best approach depends on which ceremonies need enforcement most.

### 5. Phase Transitions Are the Hardest Problem

The ceremonies that matter most — artifact phase transitions — are the hardest to enforce automatically. They happen at moments with no obvious trigger event. "I finished implementing SPEC-073" has no hook-compatible signal. The agent must initiate the transition voluntarily.

Options that address this:
- **Hooks on `git commit`**: check if changed files belong to active specs; prompt transition.
- **Hooks on `Write` + `Edit`**: track which specs' files are modified; suggest transition on session end.
- **Operator manual**: the operator runs `swain status` and sees stale artifacts; transitions manually.
- **Convention**: agent is *expected* to call the transition tool; violations are visible but not blocked.

No fully automated solution exists for phase transitions without an explicit trigger event. This is not a swain-specific limitation — it's inherent to voluntary ceremonies.

### 6. Token Economics Are Less Relevant to the Real Problem

The token overhead debate (skills 30–50 tokens vs MCP 1–10k) is secondary. The primary design questions are: what's the enforcement surface, and where does state live? A 30-token skill that the agent ignores is worse than a 10k-token MCP tool that the agent ignores — both fail equally. Token overhead only matters once we've solved the invocation question and the persistence question.

### 7. Existing Artifacts to Leverage

| Artifact | Status | Relevance |
|----------|--------|-----------|
| SPIKE-030 | Complete, Go | MCP viability proved; hybrid architecture recommended. Router problem not examined. |
| EPIC-033 | Proposed, 9 child SPECs | Full MCP server decomposed. Needs router-problem analysis added. |
| SPIKE-047 | Active | All 5 runtimes compatible with CLI invocation. Relevant for hook/shim portability. |
| SPEC-319 | Active | swain-helm CLI pattern as reference. |
| SPEC-293 | — | swain-search CLI tool research pattern as reference. |

## Recommendations

### Go on Staged Tool Architecture — Path C for Persistence

Swain v2 as a tool is viable and recommended, with two critical constraints:
1. **Tools alone don't solve enforcement** — the agent is still the router.
2. **Files remain authoritative** — adopt Path C (SQLite for operational state, files for artifact truth).

Phase 1 starts with Path C. Path B (full SQLite authority) would change swain's fundamental nature and needs its own evaluation.

#### Phase 1 — MCP Server + Path C Persistence (6-8 weeks)

Build the MCP server with Path C architecture:
- **Artifact tools** (CRUD, lifecycle transitions, chart queries, status) operate on `.md` files under `docs/`, using existing specgraph as the query layer. No SQLite for artifacts.
- **Operational tools** (task tracking, session state, bookmarks, decision logs) use SQLite. This data is session-scoped and optionally git-tracked.
- 10–15 tools total. Deterministic gate-checking in handlers. `load_methodology` for portable method delivery.
- Claude Code plugin packaging (bundles MCP + existing skills).
- npm distribution for any MCP client.

```python
# Example: artifact transition (filesystem path)
@mcp.tool()
def lifecycle_transition(artifact_id: str, new_phase: str) -> dict:
    filepath = resolve_artifact_path(artifact_id)      # finds .md file under docs/spec/etc
    frontmatter = parse_frontmatter(filepath)
    validate_transition(frontmatter["status"], new_phase)  # code gate
    update_frontmatter(filepath, {"status": new_phase})
    move_to_phase_directory(filepath, new_phase)       # git-tracked file move
    return {"status": "ok", "new_phase": new_phase}

# Example: task claim (SQLite path)
@mcp.tool()
def task_claim(task_id: str, spec_id: str) -> dict:
    db.execute("INSERT INTO session_tasks (task_id, spec, status) VALUES (?, ?, 'claimed')",
               (task_id, spec_id))
    return {"status": "ok", "task": task_id}
```

**What Phase 1 solves:** persistent operational state, cross-session visibility, deterministic gate-checking (when called), cross-client portability. Files remain authoritative; specgraph works unchanged.
**What Phase 1 does not solve:** whether the agent calls the tools at the right moments.

#### Phase 2 — Git Hooks for Passive Enforcement (2-3 weeks)

Add git hook integration that runs `swain check` without agent involvement:
- `pre-commit` hook: validates that changed artifact files follow lifecycle rules. Warns (or blocks, opt-in) on stale artifacts, unparented references, ADR violations.
- `post-commit` hook: updates artifact indexes, stamps lifecycle hashes.
- Agent cannot skip these — git hooks fire regardless.

**What Phase 2 adds:** automatic visibility into process violations. Operator sees warnings even if agent skipped ceremonies.

#### Phase 3 — Claude Code Hooks for Active Enforcement (2-3 weeks)

Implement Claude Code PreToolUse/PostToolUse hooks:
- `PreToolUse(Write)`: checks if the file being written belongs to an active spec. Prompts the agent to confirm phase transitions.
- `PostToolUse(Edit)`: tracks which specs are being modified. Suggests task claim updates.
- `SessionStart`: loads current artifact state, flags stale items.
- `PostToolUse(Commit)`: prompts for `swain sync` after commits touch artifact files.

**What Phase 3 adds:** hooks fire automatically on specific trigger events — agent cannot skip them. This partially addresses the router problem for ceremonies with detectable trigger signals (file writes, commits, session starts).

#### Phase 4 — Thin CLI Wrapper (2-4 weeks)

Wrap the MCP server's domain library in a CLI for operator direct use:
- `swain design`, `swain do`, `swain status`, `swain check`, `swain session`.
- JSON output mode for scripting and CI.
- Human-readable output for operator direct use.
- Operator fills the enforcement gap manually — sees `swain check` violations and addresses them.

**What Phase 4 adds:** operator access. Not automatic enforcement, but visibility into what the agent missed.

#### Phase 5 — Shell Wrapper (exploratory, post-VISION)

A `swain-shell` shim that wraps the agent's `bash` tool, intercepting commands and refusing ones that violate process constraints. This is the most invasive approach but the only one that provides proactive, real-time enforcement across all tool calls.

**Deferred** as a post-VISION exploration. The implementation complexity is high and the user experience impact is unknown.

### Phases 1-4 Combined Enforce This

| Ceremony | Router risk | Phase 1 (MCP) | Phase 2 (git hooks) | Phase 3 (CC hooks) | Phase 4 (CLI) |
|----------|------------|---------------|---------------------|--------------------|-------------------|
| Phase transitions | High | Gate-checks work *if called* | Warns on stale artifacts at commit | Prompts on Write/Edit of spec files | Operator sees violations |
| Task tracking | High | Claim/close tools work *if called* | — | Prompts on file changes matching active specs | Operator sees untracked work |
| ADR compliance | Medium | Check tool works *if called* | Blocks commits violating ADRs | Prompts on ADR-touching changes | Operator runs `swain check --adr` |
| Session bookmarks | Low | Session tools work *if called* | — | SessionStart loads state | Operator runs `swain session` |
| Retrospectives | Medium | Retro tool works *if called* | — | — | Operator runs `swain retro` |
| Sync workflow | Medium | Sync tools work *if called* | — | PostToolUse(Commit) triggers sync | Operator runs `swain sync` |

### What Remains Unsolved

Phase transitions are the hardest problem. No automatic trigger exists for "I finished implementing this spec." The combination of git hooks (warn), Claude Code hooks (prompt), and CLI visibility (operator catch) makes violations visible — but doesn't prevent them.

The only architectural solution to this is the shell wrapper (Phase 5), which would need to understand enough about what the agent is doing to know when ceremonies are due. That's an open research question.

### Not Recommended

- **MCP-only as a standalone solution**: doesn't address the router problem.
- **CLI-only as a standalone solution**: same issue, plus loses structured tool discovery.
- **ACP agent as v2 launch scope**: ecosystem too new, same router problem.
- **Skills-only status quo**: advisory-only enforcement is the root problem.
- **Path B (SQLite authority for artifacts)**: changes what swain IS. Artifacts-on-disk is swain's defining property. This belongs in a separate evaluation, not as a dependency of tool-vs-skill.

### Open Questions for a Future VISION

1. **What ceremonies actually need automatic enforcement vs visibility?** Some violations (stale phase tracking) are visible to the operator without blocking. Others (ADR violations in committed code) might warrant hard blocking.
2. **Shell wrapper feasibility**: can a shim reliably detect when ceremonies are due without excessive false positives?
3. **Hook portability**: Claude Code hooks don't work on other runtimes. How important is cross-runtime hook support?
4. **Language choice**: Python (FastMCP) for fastest iteration, or Rust/Go for a single binary? Current skills are shell, scripts are Python.
5. **Distribution channel**: brew for CLI, npm for MCP, plugin.json for Claude Code? How many channels to maintain?
6. **MCP Apps UI**: should swain provide interactive dashboards via MCP Apps (Jan 2026 spec), or stay text-output?
7. **Path B re-evaluation trigger**: under what conditions would lifting artifacts into SQLite become the right call? (e.g., scale beyond what filesystem parsing handles, multi-operator teams, CI/CD automation needs).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-05-01 | | Auto-drafted exploratory SPIKE for proposed VISION. |
