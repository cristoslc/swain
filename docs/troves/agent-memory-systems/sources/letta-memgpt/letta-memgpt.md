---
source-id: "letta-memgpt"
title: "Letta (MemGPT) — Stateful Agents with Self-Editing Memory"
type: web
url: "https://docs.letta.com/concepts/memgpt/"
fetched: 2026-03-23T00:00:00Z
hash: "d8c04e7d46dd1896168786654d20a4b755f7b020b7f7fafa5bc5ac221b020201"
---

# Letta (MemGPT) — Stateful Agents with Self-Editing Memory

Letta is the platform for building stateful agents that remember, learn, and improve over time. It evolved from the MemGPT research paper, which introduced the concept of LLM-driven self-editing memory.

## MemGPT: The Core Idea

MemGPT (Memory-GPT) treats the LLM's context window like an operating system's virtual memory. The key insight: give the LLM tools to manage its own memory, rather than relying on external systems to decide what to remember.

### Memory Architecture

Letta agents have a multi-tiered memory system:

- **Core memory (in-context)**: Always loaded into the LLM's context window. Contains the agent's persona and key user information. The agent can edit this directly using memory tools.
- **Archival memory (out-of-context)**: A searchable database for information that shouldn't pollute the context window (instruction manuals, documentation, large knowledge bases). Read/write via tools.
- **Recall memory**: Complete conversation history, searchable but not loaded by default.

### Self-Editing Memory Tools

The agent has built-in tools to manage its own memory:

- `core_memory_append` / `core_memory_replace` — modify in-context memory blocks
- `archival_memory_insert` / `archival_memory_search` — read/write the out-of-context store
- `conversation_search` — search through past conversation history

The LLM decides when and how to use these tools based on the conversation, making memory management part of the agent's reasoning process rather than a separate system.

## Letta Platform Features

### Memory Blocks

Structured sections of core memory (persona, human, custom blocks). Each block has a label, value, and character limit. The agent sees all blocks in its context and can edit them.

### Shared Memory

Memory blocks can be shared across multiple agents. When one agent updates a shared block, all agents with access see the change. Useful for multi-agent systems that need common knowledge.

### Context Hierarchy

Letta provides a structured context hierarchy for organizing what the agent sees:

1. System instructions (immutable)
2. Memory blocks (agent-editable)
3. Recent conversation messages
4. Tool results

### Compaction

When the conversation exceeds the context window, Letta summarizes older messages and stores them in recall memory. The agent retains access via `conversation_search`.

## Letta Code

A terminal-based coding agent built on Letta, with:

- **Background memory subagents**: Improve prompts, context, and skills over time with experience
- **Memory palace**: Visual interface to view and modify agent memory
- **Skills**: Reusable procedures the agent can learn and invoke
- **Git-backed memory**: Memory changes tracked in git

### Sleep-Time Agents

An experimental architecture where memory processing happens between interactions ("sleep time"), similar to human memory consolidation during sleep. The agent reflects on recent conversations and updates its memory without blocking the user.

## Key Design Characteristics

- **Agent-driven memory**: The LLM itself decides what to remember, forget, and how to organize memory — not an external pipeline
- **Virtual memory paradigm**: Mirrors OS memory management (paging, swapping) for LLM context
- **Persistent state**: Agents maintain state across sessions as first-class entities, not ephemeral conversations
- **Model-agnostic**: Supports Opus 4.5, GPT-5.2, and many others
- **Self-improving**: Agents evolve their own instructions, memory, and skills over time

## Disambiguation

- **MemGPT**: Refers to the original research paper's design pattern (LLM OS with self-editing memory)
- **Letta**: The agent framework and company that maintains the open-source MemGPT pattern
- **Letta Code**: The terminal coding agent product built on the Letta platform
