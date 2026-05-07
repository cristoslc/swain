---
title: Goose Subagents - Parallel Task Execution with Isolated Sessions
url: https://www.nickyt.co/blog/advent-of-ai-day-11-goose-subagents-2n2/
source-type: web-page
fetched: 2026-05-05
transcript-source: web-page
---

# Goose Subagents

## Overview

Goose supports subagents for parallel task execution. Each subagent runs in its own isolated session.

## How Subagents Work

When you ask for subagents, goose:

1. **Creates task definitions** and stores them in a TasksManager
2. **Spawns separate goose instances** for execution (each in its own isolated session)
3. **Aggregates results** back to the parent

This prevents sessions from stepping on each other.

## Architecture

Goose has a modular architecture with a core Rust codebase:
- **Agent class**: Handles agent logic
- **Extension management**: Tool discovery and execution
- **Tool execution**: Running MCP tools
- **LLM provider communication**: Multi-provider support

### Key Tools for Subagents

The main agent uses tools like:
- `platform__create_task`
- `platform__execute_tasks`

## Use Cases

### Summary Mode
```
"Use a subagent to research this topic and summarize the key findings"
```
This gives you just the final result to keep your conversation clean.

### Parallel File Processing
```
"Use 2 subagents to create hello.html and goodbye.html in parallel"
```

### Video Processing Recipe
A recipe that spawns 4 parallel subagents for video processing with real-time progress updates.

## Session Management

- Each subagent runs in its own isolated session
- Only task results make it back to parent
- All noisy details stay quarantined in separate sessions
- Can spin up with natural language

## Best Practices

From PulseMCP recommendations:

1. **Don't overload subagents**: Give only the tools needed for the specific job
2. **Start linear**: Automate straightforward workflows first
3. **Compose agents**: Turn individual agents into subagents of a main agent
4. **Isolate by concern**: Keep sensitive data away from MCP client/server

## Benefits

- **Parallel execution**: Multiple tasks at once
- **Context isolation**: Prevents context poisoning
- **Token efficiency**: Save LLM tokens
- **Tool accuracy**: More accurate tool selection
- **Clean parent conversation**: Only results return

## Future Development

GitHub discussion #4389 about moving to a more consistent architecture where:
- Each session gets its own agent instance
- (Currently server mode shares a single Agent)

## Quote

"With subagents, only the task results make it back while all the noisy details stay quarantined in separate sessions."

---

Sources:
- https://www.nickyt.co/blog/advent-of-ai-day-11-goose-subagents-2n2/
- https://dev.to/nickytonline/what-makes-goose-different-from-other-ai-coding-agents-2edc
- https://www.pulsemcp.com/building-agents-with-goose
