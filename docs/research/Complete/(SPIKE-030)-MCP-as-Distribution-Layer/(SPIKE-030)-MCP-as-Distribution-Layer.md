---
title: "MCP as Distribution Layer"
artifact: SPIKE-030
track: container
status: Complete
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
question: "Can MCP (Model Context Protocol) serve as swain's primary distribution layer — packaging skill capabilities as MCP tools/resources that any MCP-compatible client can consume?"
gate: Pre-MVP
parent-initiative: INITIATIVE-014
risks-addressed:
  - Building on a protocol that doesn't have sufficient adoption or stability
  - MCP's tool model being too narrow for swain's workflow-oriented patterns
evidence-pool: ""
linked-artifacts:
  - EPIC-033
---

# MCP as Distribution Layer

## Summary

**Go.** MCP can serve as swain's primary distribution layer. All three MCP primitives (Tools, Prompts, Resources) map to swain's skill capabilities, and Sampling with Tools (SEP-1577) enables server-controlled orchestration that is strictly more powerful than skill chaining. The initial report understated MCP's capability — skill chaining is replicable via tool-returned instructional content and MCP Prompts. The recommended near-term architecture is **hybrid** (skills for Claude Code ergonomics, MCP for persistence + portability), transitioning to **MCP-primary** as Sampling client support matures.

## Question

Can MCP (Model Context Protocol) serve as swain's primary distribution layer — packaging skill capabilities as MCP tools/resources that any MCP-compatible client can consume?

## Go / No-Go Criteria

- **Go**: MCP's tool + resource model can express swain's core capabilities (artifact CRUD, lifecycle transitions, status queries, chart navigation), AND at least 3 clients support MCP (Claude desktop, Claude web, plus one non-Anthropic client)
- **No-Go**: MCP's model is too primitive for stateful workflows (e.g., no session persistence, no file system access, no multi-step tool chaining), or adoption is limited to a single client

## Pivot Recommendation

If MCP is insufficient, fall back to surface-specific packaging: system prompts for Claude web, native skills for Claude Code, and AGENTS.md for runtimes that support it. Accept fragmentation and minimize per-surface maintenance via shared markdown source.

## Findings

Evidence pool: mcp-distribution-layer (trove archived)

### MCP Can Do Everything Swain Needs

Production MCP servers demonstrate swain-equivalent complexity:

- **lifecycle-mcp**: 22 tools, 6 handler modules, SQLite persistence, ADR tracking, requirement state machines (Draft → Under Review → Approved → ... → Validated → Deprecated), task management with GitHub issue sync
- **spec-workflow-mcp**: Sequential phase enforcement (Requirements → Design → Tasks), approval gates, real-time dashboard, Docker deployment, cross-tool support (Claude, Augment, Continue IDE)

The protocol places no ceiling on handler complexity. A tool handler is arbitrary code — it can manage git repos, run state machines, maintain persistent databases, and enforce lifecycle constraints programmatically.

### The Hybrid Architecture

| Layer | Skills (orchestration) | MCP Server (persistence) |
|-------|----------------------|-------------------------|
| Role | How Claude should reason and act | What's allowed and what state exists |
| Enforcement | Model reasoning (advisory) | Programmatic (deterministic) |
| Distribution | `.claude/skills/` or `.agents/skills/` | Plugin-bundled or standalone |
| Portability | Claude Code + compatible runtimes | Any MCP-compliant client |
| Testing | No standard framework | Standard unit/integration tests |

**What skills do better today:** Inline context injection at higher instruction authority (system-prompt-adjacent vs tool-result level), zero-friction installation, operator-readable governance (it's just markdown), Claude Code-native ergonomics (slash commands, chaining, hooks).

**What MCP does better:** Deterministic constraint enforcement (refuse invalid transitions), persistent state across sessions (SQLite), structured data queries (all epics with specs complete), multi-client portability, testable business logic, server-controlled orchestration via Sampling.

**The sweet spot (near-term):** Skills remain the operator-facing interface in Claude Code. The MCP server provides persistence and enforcement. Skills call MCP tools when they need to read/write artifact state. This is exactly how Claude Code's plugin system is designed — `plugin.json` bundles skills alongside MCP server config.

**The trajectory (medium-term):** As MCP Sampling with Tools matures and gains client support, the MCP server can absorb orchestration responsibilities. The `load_methodology` tool pattern (returning instructional text from the server) provides skill-chaining-equivalent behavior today. MCP Prompts surface as slash commands (`/mcp__swain__design`) — the direct analog of skill invocation. The long-term architecture is MCP-primary, not hybrid-forever.

### Corrected Capability Analysis (v2)

The initial analysis (v1) incorrectly listed "skill chaining" and "inline context injection" as capabilities MCP cannot replicate. Corrected mapping:

| Skill Capability | MCP Mechanism | Status |
|-----------------|---------------|--------|
| Methodology loading (SKILL.md injection) | Tool results returning instructional text | Works today |
| Slash-command invocation (`/swain-design`) | MCP Prompts as `/mcp__swain__design` | Works today in Claude Code |
| Skill-to-skill chaining | `load_methodology` tool returning next skill's instructions | Works today |
| Progressive context loading | Tool Search (deferred) + Prompts (on invocation) | Works today |
| Bundled scripts and templates | Server-side code + embedded Resources | Works today, more powerful |
| Cross-skill shared state | Single MCP server maintains state across all tools | Works today, stronger than skills |
| System-prompt-level instruction authority | Sampling `systemPrompt` parameter | Requires Sampling client support |
| `context: fork` (isolated subagent) | Sampling (separate LLM completion) | Requires Sampling client support |
| Conditional chains (check availability) | Tool logic checks server state | Works today |

**Key remaining gap:** Tool results have lower instruction-following authority than system-prompt-level injection. In practice, frontier models follow tool-returned instructions reliably, but the authority difference exists. Sampling's `systemPrompt` parameter resolves this — when client support arrives.

### Distribution Options

1. **Open-source repo** (current) — `npx skills add cristoslc/swain`. Works for Claude Code. MCP server requires manual `claude mcp add`.
2. **Claude Code Plugin** (recommended) — `plugin.json` bundles skills + MCP config. MCP server auto-starts on install. Zero manual config.
3. **Desktop Extension (.mcpb)** — packages the MCP server for Claude Desktop Chat tab. One-click install.
4. **Remote MCP server** — for Claude web Connectors. Requires hosting infrastructure. Best UX but highest maintenance.
5. **npm package** — `npx swain-mcp` for any MCP client. Standard distribution.

### Token Overhead

A typical MCP setup (5 servers, 58 tools) consumes ~55K tokens before conversation starts. Claude Code's Tool Search (Sonnet 4+) reduces this 85–95%. Other clients without Tool Search pay the full cost. Swain should keep its tool count lean — expose 10–15 high-value tools, not one tool per artifact operation.

### Risks

- MCP registry still in preview (not GA) — breaking changes possible
- No standard for tool versioning or deprecation in the protocol
- "Rug pull" vulnerability — servers can redefine tool descriptions post-confirmation
- Distributed statefulness requires sticky routing (being addressed in June 2026 spec update, but a non-issue for local stdio servers)
- Token overhead on non-Claude-Code clients without Tool Search

### Go / No-Go Assessment

**Go** with the following phasing:

**Near-term (hybrid):**
1. Build the MCP server with artifact CRUD, lifecycle transitions, chart queries, and a `load_methodology` tool for portable skill chaining
2. Bundle as a Claude Code plugin (skills + MCP) for the primary audience
3. Package the MCP server independently as .mcpb (Desktop) and npm (any client)
4. Keep tool count under 15 for token budget
5. Expose MCP Prompts for key workflows (`design`, `do`, `status`, `session`)

**Medium-term (MCP-primary):**
6. When Sampling with Tools has Claude Code support, migrate orchestration from skill instructions to server-controlled flows
7. Skills become thin wrappers or are replaced entirely by MCP Prompts
8. Remote hosting for Claude web Connector (only after local MCP proves value)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-18 | | Initial creation |
| Complete | 2026-03-18 | | Research complete, findings documented |
