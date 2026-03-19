---
title: "Claude Web & Desktop Extension Model"
artifact: SPIKE-028
track: container
status: Complete
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
question: "What capabilities do Claude web (Projects) and Claude desktop offer for extending agent behavior, and how much of swain's value can be projected onto each?"
gate: Pre-MVP
parent-initiative: INITIATIVE-014
risks-addressed:
  - Investing in a packaging approach that the target surfaces can't support
  - Assuming capabilities that don't exist or are about to change
evidence-pool: ""
---

# Claude Web & Desktop Extension Model

## Summary

**Conditional Go.** Claude web (via Connectors/MCP) and Claude desktop (via Desktop Extensions + Code tab) provide enough extensibility to deliver a meaningful subset of swain's value. The full agentic experience remains Claude Code-only, but a two-tier strategy — read/advisory via web, full capability via Code tab — is feasible. The primary gap is that the web surface cannot execute scripts, write files, or run agentic loops; Connectors bridge some of this via remote MCP servers but cannot replace local filesystem access.

## Question

What capabilities do Claude web (Projects) and Claude desktop offer for extending agent behavior, and how much of swain's value can be projected onto each?

## Go / No-Go Criteria

- **Go**: At least one Claude surface (web or desktop) supports enough extensibility to deliver swain's core decision-support loop (artifact awareness, lifecycle guidance, structured recommendations) without requiring CLI access
- **No-Go**: Both surfaces are limited to static system prompts with no file access, tool use, or persistent state — making swain's artifact-driven model infeasible

## Pivot Recommendation

If Claude web/desktop extensibility is too limited, pivot to MCP-first approach (SPIKE-030) targeting Claude desktop's MCP support as the primary surface, treating web as a degraded-mode fallback with prompt-only packaging.

## Findings

Evidence pool: [claude-web-desktop-extensions.md](../../troves/claude-web-desktop-extensions.md)

### Claude Web (claude.ai)

**Projects** provide a system-prompt-equivalent ("Project Instructions") with no documented character limit, a 30 MB knowledge base with RAG on paid plans, and project-scoped memory summaries. Projects are siloed — no cross-project references. Sharing requires Team/Enterprise.

**Connectors** (launched January 26, 2026) are the MCP integration surface. 50+ pre-built integrations plus custom remote MCP servers (1 free, unlimited on paid plans). Connectors support read, write, and action execution via MCP tools, plus "MCP Apps" that render interactive UIs inline. **Critical limitation:** the API connector supports only MCP tools — not prompts or resources.

**What this means for swain:** A Claude web Project could package swain's decision-support patterns as Project Instructions (the lifecycle rules, artifact conventions, routing logic) with knowledge base files for templates and reference material. A custom MCP Connector could expose artifact state queries (chart, status) and lifecycle transitions. The read/advisory loop works; the full write loop (file creation, phase transitions with git moves) requires a remote MCP server with repo access.

### Claude Desktop

Two architecturally separate modes:
- **Chat tab** — mirrors claude.ai with the addition of Desktop Extensions (.mcpb bundles for local MCP servers)
- **Code tab** — full Claude Code with GUI. Skills, plugins, hooks, MCP — everything works

Desktop Extensions (.mcpb) are ZIP archives with a `manifest.json` that package MCP servers for one-click install. They support Node.js, Python, and binary runtimes. Sensitive config stored in OS keychain. Developer tooling: `npx @anthropic-ai/mcpb init/pack`.

**What this means for swain:** The Code tab already runs swain perfectly. The Chat tab could use a Desktop Extension packaging swain's MCP server for local artifact queries and transitions — a richer experience than the web Connector because the local MCP server has filesystem access.

### Capability Gap

| Swain Capability | Claude Code | Claude Web | Claude Desktop Chat |
|-----------------|------------|-----------|-------------------|
| Artifact creation (file writes) | Native | Via remote MCP only | Via local MCP (.mcpb) |
| Phase transitions (git mv) | Native | Not feasible | Via local MCP (.mcpb) |
| Lifecycle state machine | Skill instructions | Project Instructions (advisory) | Skill instructions (Code tab) or MCP (Chat tab) |
| Status/chart queries | Scripts | Via MCP Connector | Via MCP (.mcpb) |
| Skill chaining | Native | Not available | Code tab only |
| Session management | swain-session skill | Project memory (limited) | Code tab only |

### Recommended Architecture

**Three-tier delivery:**
1. **Claude Code** (full) — skills + MCP server (hybrid). No changes needed to current model.
2. **Claude Desktop Chat** — Desktop Extension (.mcpb) packaging a local MCP server with filesystem access. Provides artifact queries, status, and transitions. No skill chaining but deterministic enforcement.
3. **Claude Web** — Project with instructions encoding swain's decision-support patterns + a remote MCP Connector for artifact state queries. Advisory mode — recommends but doesn't enforce. Lowest capability, broadest access.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-18 | | Initial creation |
| Complete | 2026-03-18 | | Research complete, findings documented |
