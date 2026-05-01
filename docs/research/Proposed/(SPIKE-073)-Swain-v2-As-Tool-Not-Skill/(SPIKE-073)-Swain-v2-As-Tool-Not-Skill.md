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

## Decision Matrix

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

### 1. Tools Solve the Enforcement Gap

The fundamental weakness of skill-injected methodology is that it's advisory. [skills-as-tools trove] establishes this as the industry's shared diagnosis. Skills say "you should follow this workflow." Tools say "this transition is invalid — refused." The AI coding agents deconstructed analysis [ai-coding-agents-deconstructed] identifies modes without hard permissions as the key limitation: plan mode is just a prompt, and agents routinely drift from methodology under context pressure.

Swain v2 as a tool eliminates this gap. Lifecycle state machines become code. Phase transitions become validated gate conditions. Methodology becomes a constraint, not a suggestion.

### 2. The Industry Trajectory Favors Tools Over Skills

SPIKE-030 (Complete) already established that MCP can serve as swain's distribution layer. The skills-as-tools trove adds new evidence:
- MCP is now under the Linux Foundation with formal governance.
- 2026 roadmap addresses auth, context bloat, and enterprise readiness.
- Tools-as-methodology is a growing pattern (lifecycle-mcp, spec-workflow-mcp).
- ACPX demonstrates headless agent orchestration as a practical cross-harness pattern.

The "skills killed MCP" narrative has been rebutted: both layers coexist in 2026 architecture.

### 3. A Phased Approach Minimizes Risk

A single "build everything" approach is too risky. Recommended phasing:

**Phase 1 — MCP Server (6-8 weeks)**
- Implement EPIC-033 (already decomposed into 9 SPECs).
- 10–15 tools covering core swain operations.
- SQLite persistence, deterministic lifecycle state machine.
- `load_methodology` tool for skill-chaining bridge.
- Claude Code plugin packaging (bundles MCP + existing skills).
- npm distribution for any MCP client.
- Existing skills continue to work unchanged (hybrid coexistence).

**Phase 2 — Thin CLI Wrapper (2–4 weeks)**
- Wrap the MCP server's domain library in a CLI.
- `swain design`, `swain do`, `swain status`, `swain session`, etc.
- JSON output mode for agent consumption.
- Human-readable output for operator direct use.
- Same persistence layer as MCP (operators and agents see the same state).

**Phase 3 — Skills Become Thin Wrappers (ongoing)**
- As agents adopt MCP-native invocation, skill files shrink to routing instructions.
- Example: `/swain-design` skill becomes: "Use the swain__design tool. Here's how to interpret its output."
- Eventually, skills may be removed entirely for MCP-native clients.

**Phase 4 — ACP Integration (post-VISION, speculative)**
- If multi-agent workflows become a priority, add ACP support.
- Swain participates as a methodology agent in multi-agent sessions.
- acpx-compatible for headless orchestration.

### 4. What Happens to Existing Skills?

Skills do not disappear in v2. They evolve:
- **Phase 1**: skills coexist with MCP tools (hybrid architecture from SPIKE-030).
- **Phase 2**: skills become thin wrappers calling `swain` CLI or MCP tools.
- **Phase 3**: skills are optional — agents can use MCP natively or fall back to skills.
- **End-state**: skills exist for agents without MCP support; MCP tools are primary for compatible agents.

The operator never loses the readable governance that skills provide. CLI output and MCP resource URIs replace `SKILL.md` as the documentation surface.

### 5. Token Economics Are Acceptable

A 10–15 tool MCP server consumes ~1–10k tokens of context. With Tool Search (Claude Code Sonnet 4+), this drops ~85% to ~150–1,500 on-demand tokens. For agents without Tool Search, the full cost applies — but swain's lean tool count (not one tool per artifact operation) keeps it manageable.

The CLI path has no tool-definition overhead at all. Agents see only the output of `swain status`, not the schema of every possible command. This is a meaningful advantage for context-constrained sessions.

### 6. Operator Experience Changes Significantly

**Current (skills):**
- Operator reads `SKILL.md` files to understand swain's methodology.
- Operator invokes skills through slash commands in agent sessions.
- Operator cannot interact with swain outside an agent.

**v2 (tools):**
- Operator runs `swain status` directly in terminal.
- Operator transitions artifacts via `swain design transition SPEC-082 Active`.
- Operator reads CLI help (`swain --help`, `swain design --help`) instead of `SKILL.md`.
- Operator can script swain operations (CI/CD, git hooks, automation).
- Agent sessions still invoke swain, but operator has a parallel direct path.

### 7. Existing Artifacts to Leverage

| Artifact | Status | Relevance |
|----------|--------|-----------|
| SPIKE-030 | Complete, Go | MCP viability proven; hybrid architecture recommended. |
| EPIC-033 | Proposed, 9 child SPECs | Full MCP server decomposed and ready for implementation. |
| SPIKE-047 | Active | All 5 runtimes compatible with CLI invocation via swain's shell launcher. |
| SPEC-319 | Active | swain-helm CLI pattern (subcommand groups, shell scripts) as reference. |
| SPEC-293 | — | swain-search CLI tool research pattern as reference. |

## Recommendations

### Go (Staged Hybrid)

Swain v2 as a tool is viable and recommended. The phased approach:

1. **Start with MCP server** (Phase 1). All 9 SPECs under EPIC-033 are ready. Implementation is straightforward with FastMCP + SQLite. Distribute as Claude Code plugin + npm package. Existing skills coexist.

2. **Add thin CLI wrapper** (Phase 2). Share the MCP server's domain library. The CLI provides operator access and reduces token overhead for agents that prefer bash to MCP tool calls.

3. **Evolve skills into routing shims** (Phase 3). As MCP-native clients dominate, skills shrink to one-liners delegating to tools.

4. **Defer ACP integration** to post-VISION exploration. The use case is multi-agent setups, which swain's solo-operator model does not currently require.

### Not Recommended

- **CLI-only** as the sole interface: loses structured tool discovery for agents.
- **MCP-only** as the sole interface: loses operator direct access.
- **ACP agent** as v2 launch scope: ecosystem too new, overengineering for current needs.
- **Big-bang rewrite**: implementing all three interfaces simultaneously is unnecessary risk.

### Open Questions for a Future VISION

1. **Language choice**: Python (FastMCP) for fastest iteration, or Rust/Go for a single binary? Current skills are shell, scripts are Python. MCP ecosystem favors Python/TypeScript.
2. **Distribution channel**: brew for CLI, npm for MCP, plugin.json for Claude Code? How many channels to maintain?
3. **Skill sunset timeline**: when can skills be removed for MCP-native clients? What's the trigger?
4. **Backward compatibility**: how long must the hybrid mode persist? What happens to projects using swain v1 skills?
5. **Auth model**: local stdio (no auth) is fine for personal use. What does auth look like for team MCP servers?
6. **MCP Apps UI**: should swain provide interactive dashboards via MCP Apps (Jan 2026 spec), or stay text-output?

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-05-01 | | Auto-drafted exploratory SPIKE for proposed VISION. |
