---
source-id: tick-md-coordination
type: web-page
title: "tick-md: How We Coordinate Multiple AI Agents with a Markdown File"
url: "https://purplehorizons.io/blog/tick-md-multi-agent-coordination-markdown"
fetched: 2026-03-20
content-hash: "--"
---

# tick-md: How We Coordinate Multiple AI Agents with a Markdown File

## File Locking Mechanism

The core collision prevention strategy relies on Git-based file locking. When an agent claims a task, the system locks the file to prevent concurrent edit conflicts. This eliminates merge conflicts by ensuring only one agent can modify the TICK.md file at a time.

## Coordination Protocol

1. **Task claiming**: agents connect via MCP server to claim available tasks, triggering an immediate file lock
2. **Progress tracking**: while working, agents append comments and status updates directly to task entries
3. **Completion and unblocking**: task completion automatically unblocks dependent tasks
4. **Audit trail**: Git records every claim, status change, and completion as timestamped commits

## Collision Prevention

- **Exclusive locking**: when an agent claims a task, it locks the file — only the claiming agent can modify entries during work
- **Race condition handling**: real-world testing uncovered and resolved race conditions when two agents tried to claim tasks simultaneously

## Design Philosophy

The developers chose Markdown + Git because "every LLM understands Markdown" natively, requiring no custom parsers or API integrations. This AI-native design enables agents to read and write tasks as naturally as code.

## Relevance to Multi-Agent Coordination

tick-md demonstrates a practical pattern for task-level coordination between AI agents using file-based state. The exclusive locking mechanism prevents task-level collisions but does not address code-level collisions (two agents editing the same source file). It solves the orchestration layer but not the integration layer.
