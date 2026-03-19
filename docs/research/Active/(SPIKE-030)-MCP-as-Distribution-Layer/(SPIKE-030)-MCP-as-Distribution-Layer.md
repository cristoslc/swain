---
title: "MCP as Distribution Layer"
artifact: SPIKE-030
track: container
status: Active
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
---

# MCP as Distribution Layer

## Summary

**Conditional Go.** MCP can technically express swain's full artifact lifecycle (proven by lifecycle-mcp and spec-workflow-mcp in production). However, the strongest architecture is **hybrid**: skills for orchestration and operator UX, MCP server for persistence and deterministic enforcement. Going MCP-only would lose skill chaining, inline context injection, and zero-friction distribution. Going skills-only keeps the current Claude Code lock-in. The hybrid model — bundled as a Claude Code plugin — is the recommended path, with the MCP server portable to other clients independently.

## Question

Can MCP (Model Context Protocol) serve as swain's primary distribution layer — packaging skill capabilities as MCP tools/resources that any MCP-compatible client can consume?

## Go / No-Go Criteria

- **Go**: MCP's tool + resource model can express swain's core capabilities (artifact CRUD, lifecycle transitions, status queries, chart navigation), AND at least 3 clients support MCP (Claude desktop, Claude web, plus one non-Anthropic client)
- **No-Go**: MCP's model is too primitive for stateful workflows (e.g., no session persistence, no file system access, no multi-step tool chaining), or adoption is limited to a single client

## Pivot Recommendation

If MCP is insufficient, fall back to surface-specific packaging: system prompts for Claude web, native skills for Claude Code, and AGENTS.md for runtimes that support it. Accept fragmentation and minimize per-surface maintenance via shared markdown source.

## Findings

Evidence pool: [mcp-distribution-layer.md](../../troves/mcp-distribution-layer.md)

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

**What skills do better:** Encoding methodology and decision trees, inline context injection, zero-friction installation, operator-readable governance (it's just markdown), skill-to-skill chaining.

**What MCP does better:** Deterministic constraint enforcement (refuse invalid transitions), persistent state across sessions (SQLite), structured data queries (all epics with specs complete), multi-client portability, testable business logic.

**The sweet spot:** Skills remain the operator-facing interface. The MCP server is the persistence and enforcement layer. Skills call MCP tools when they need to read/write artifact state. This is exactly how Claude Code's own plugin system is designed — `plugin.json` bundles skills alongside MCP server config.

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

**Conditional Go** with the following conditions:
1. Build the MCP server as the persistence/enforcement layer, NOT as a full replacement for skills
2. Bundle as a Claude Code plugin for the primary audience
3. Separately package as .mcpb for Claude Desktop Chat and npm for other MCP clients
4. Keep tool count under 15 for token budget reasons
5. Defer remote hosting (Claude web Connector) until local MCP proves value

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-18 | | Initial creation |
