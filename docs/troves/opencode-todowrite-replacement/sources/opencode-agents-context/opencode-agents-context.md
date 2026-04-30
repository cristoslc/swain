---
source: https://opencode.ai/docs/agents/
type: web
title: "OpenCode Agents Documentation"
fetched: 2026-04-30
proxy-used: none
---

# OpenCode Agents Documentation (Relevant Excerpts)

## Built-in Agents

OpenCode includes two built-in agents switchable with Tab:
- **Build** (Plan mode): Disables file modification, suggests how to implement.
- **Plan** (Build mode): Full tool access for implementation.

## General Agent
"A general-purpose agent for researching complex questions and executing multi-step tasks. Has full tool access **(except todo)**, so it can make file changes when needed."

## Subagent Tool Denial
The `task` subagent type specifically excludes the todowrite tool. This is a deliberate design decision, but causes problems when the user instructs the agent to use todowrite and it can't.

## Custom Agents
Users can define custom agents with specific tool permissions. The `permission` block can grant or deny individual tools.
