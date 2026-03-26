---
source-id: "opencode-rules-context"
title: "OpenCode Rules and Context Persistence"
type: web
url: "https://opencode.ai/docs/rules/"
fetched: 2026-03-23T00:00:00Z
hash: "076d7f78cec1655d0c7369d06cfc1b4b1e464f422c1c68db8619fb652fcceee9"
notes: "OpenCode has no native cross-session memory. Content synthesized from official docs and community discussion."
---

# OpenCode Rules and Context Persistence

OpenCode provides instruction persistence via AGENTS.md files but has **no built-in cross-session memory system**. Persistent memory is only available through third-party plugins.

## AGENTS.md — Instruction Files

OpenCode uses `AGENTS.md` for custom instructions, similar to Cursor's rules. The file's contents are included in the LLM's context to customize behavior for a specific project.

### Locations

- **Project-specific**: `AGENTS.md` in project root
- **Global**: `~/.config/opencode/AGENTS.md`
- **Custom paths**: specified in `opencode.json` or global `~/.config/opencode/opencode.json`

### Features

- Custom instruction files can be specified in config to reuse existing rules
- Teams can share rules without duplicating them to AGENTS.md
- Supports custom agents with custom system prompt files
- Custom commands can target specific agents

## No Native Memory

As of early 2026, OpenCode has no built-in mechanism for:
- Automatic memory extraction from conversations
- Persistent fact storage across sessions
- Session summary or context carryover

A feature request for persistent session memory (GitHub issue #16077) proposes a `--memory-file` flag and config-based memory, but this has not been implemented natively.

## Community Memory Solutions

The OpenCode community has developed several third-party memory plugins:

- **true-mem**: Automatic memory plugin with 4-layer noise filtering, dual scope (global preferences + project-specific decisions), cognitive decay (episodic fades, preferences stay), and optional semantic embeddings
- **opencode-mem**: Plugin using local vector database (USearch) with SQLite as source of truth, web interface for browsing memories
- **MCP-based solutions**: Users connect external memory servers (CORE Memory, Basic Memory, mem0) via MCP configuration in `opencode.json`
- **Manual handoff docs**: Some users create handoff documents at session end and load them at session start

## Context Compaction

OpenCode does have a built-in compaction system: when context limit is reached, a hidden system agent compacts long context into a smaller summary. The agent receives a special system prompt instructing it to respond with a summarization of its work and recommended remaining tasks. This is in-session only — it does not persist across sessions.

## Key Design Characteristics

- **Instructions only, no memory**: AGENTS.md provides instructions but not learned facts
- **Plugin ecosystem**: memory is delegated to the community via MCP and plugins
- **No automatic extraction**: no autonomous memory formation from conversations
- **No consolidation or forgetting**: third-party plugins implement varying approaches
- **Active demand**: persistent memory is one of the most-requested features
