---
source-id: "mem0-memory-layer"
title: "Mem0 — Universal Memory Layer for AI Agents"
type: web
url: "https://docs.mem0.ai/overview"
fetched: 2026-03-23T00:00:00Z
hash: "b15c5b08dab6d67233645c71426011800a2e36e1a470873444b96f67fbf954c5"
---

# Mem0 — Universal Memory Layer for AI Agents

Mem0 ("mem-zero") is a memory engine that keeps conversations contextual so users never repeat themselves and agents respond with continuity. Available as both open-source (Apache 2.0, 37k+ GitHub stars) and a managed platform.

## Core Architecture

Mem0 operates as a memory layer that sits between AI applications and language models. It captures and stores relevant information from user interactions, then retrieves it contextually when needed.

### Memory Pipeline

1. **Extraction Phase**: The system ingests three context sources — the latest exchange, a rolling summary, and the m most recent messages — and uses an LLM to extract a concise set of candidate memories
2. **Consolidation**: New memories are reconciled against existing ones — deduplicating, merging, and updating as needed
3. **Storage**: Memories are stored in a vector database with metadata for retrieval
4. **Retrieval**: At query time, memories are retrieved via semantic similarity search, optionally with metadata filtering

### Memory Types

Mem0 supports three scopes of memory:

- **User memory**: Preferences, facts, and context specific to a user
- **Agent memory**: Knowledge specific to an agent's role or domain
- **Session memory**: Context within a single conversation session

## Graph Memory (Mem0^g)

An enhanced variant that layers a graph-based store on top of the vector memory to capture richer, multi-session relationships.

### How It Works

- Mem0's extraction LLM identifies entities, relationships, and timestamps from conversation data
- Embeddings land in the configured vector database
- Nodes and edges flow into a graph backend (Neo4j, Memgraph, Neptune, Kuzu, or Apache AGE)
- Retrieval combines vector similarity with graph traversal for multi-hop reasoning

### Graph Memory Results

On the LOCOMO benchmark, Mem0 with graph memory achieves ~2% higher overall score than base configuration, and 26% relative improvement over OpenAI's memory in the LLM-as-a-Judge metric.

## Integration Model

### Code Interface

```python
from mem0 import Memory

memory = Memory()

# Add memories from conversation
memory.add("I work at Acme Corp in the ML team", user_id="alice")

# Search memories
results = memory.search("Where does Alice work?", user_id="alice")
```

### Framework Support

Works with OpenAI, LangGraph, CrewAI, Vercel AI SDK, and any MCP-compatible client. Available in Python and JavaScript.

### OpenMemory MCP Server

A persistent MCP memory server for coding agents (Cursor, Windsurf, VS Code). Tags memories by type (user preference, implementation pattern) for automatic context retrieval.

## Platform vs Open Source

| Feature | Open Source | Platform |
|---------|-----------|----------|
| Vector store | Self-managed | Managed |
| Graph memory | Self-managed Neo4j | Managed |
| Rerankers | Manual setup | Built-in |
| SOC 2 / GDPR | N/A | Included |
| Scaling | Manual | Automatic |
| Webhooks | N/A | Available |

## Key Design Characteristics

- **LLM-powered extraction**: Uses an LLM (default: GPT-4.1-nano) to extract memories, not rule-based
- **Multi-provider**: Supports OpenAI, Anthropic, Google, Ollama for extraction
- **Dual storage**: Vector + optional graph for complementary retrieval strategies
- **Intelligent compression**: Compresses chat history into optimized memory representations to minimize token usage
- **Entity resolution**: Graph memory deduplicates entities across conversations
- **Temporal awareness**: Graph edges can capture time-dependent relationships

## Research Paper

"Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory" (arXiv:2504.19413). Demonstrates consistent outperformance across single-hop, temporal, multi-hop, and open-domain questions.
