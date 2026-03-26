---
source-id: "basic-memory-mcp"
title: "Basic Memory — Markdown Knowledge Graph MCP Server"
type: web
url: "https://github.com/basicmachines-co/basic-memory"
fetched: 2026-03-23T00:00:00Z
hash: "c09307368686fdc7ed865f4415aea837bbf3c34e7a24c93d6ee3efcbeefff0ef"
---

# Basic Memory — Markdown Knowledge Graph MCP Server

Basic Memory is an MCP server that builds a persistent, bidirectional knowledge graph from natural language conversations, storing everything in local Markdown files. It bridges the gap between ephemeral LLM conversations and lasting knowledge.

## Core Concept

Most LLM interactions are ephemeral — conversations are forgotten between sessions. Basic Memory solves this by letting the LLM read from and write to a local markdown knowledge base via MCP, building a semantic graph over time.

### How It Works

1. User has a conversation with an LLM (Claude, Cursor, etc.)
2. The LLM creates structured Markdown files via MCP tools
3. Each file represents an entity with typed observations
4. Observations link to other entities, forming a knowledge graph
5. In future sessions, the LLM searches and reads this knowledge

## Markdown Format

Each knowledge file follows a structured format:

```markdown
title: <Entity title>
type: <The type of Entity> (e.g. note)
permalink: <a uri slug>
- <optional metadata> (such as tags)

Observations are facts about a topic, created as Markdown list items
with a special format that can reference categories, tags using "#",
and an optional context.
```

## MCP Tools

- **Create/update notes**: Write knowledge files with title, content, folder, and tags
- **Read notes**: Access by title or permalink
- **Edit notes**: Incremental modifications
- **Search**: Full-text and semantic search across the knowledge base
- **Move/delete**: Manage the knowledge graph structure
- **View as artifacts**: Formatted presentation of notes

## Architecture

- **Storage**: Plain Markdown files on local filesystem
- **Knowledge graph**: Bidirectional — entities link to each other through observations
- **Semantic search**: Built-in semantic search over the knowledge base
- **Sync**: Compatible with Obsidian and other markdown editors for human review

## Deployment

```json
{
  "mcpServers": {
    "basic_memory": {
      "command": "uvx",
      "args": ["basic-memory", "mcp"]
    }
  }
}
```

Works with Claude Desktop, VS Code, Cursor, Windsurf, and any MCP-compatible client. Also supports cloud synchronization as an optional feature.

## The MCP Memory Server Landscape

Basic Memory represents one approach in a growing ecosystem of MCP-based memory servers:

### Categories

1. **Markdown-first** (Basic Memory, mcp-memory-keeper): Store memories as human-readable files. Simple, editable, version-controllable. Limited retrieval sophistication.

2. **Vector-backed** (Mem0 OpenMemory, HPKV Memory): Use embedding databases for semantic retrieval. Better recall precision but require infrastructure.

3. **Graph-backed** (mcp-neo4j-agent-memory, Graphiti MCP): Store in knowledge graphs for relationship-aware retrieval. Best for interconnected knowledge but need graph databases.

4. **Hybrid** (mcp-memory-service): Combine knowledge graph + vector store + REST API. Most capable but most complex to deploy.

### Common Pain Points (from community)

- **Context rot**: Memory retrieval fills the context window, reducing rather than improving performance
- **Prompt integration**: Many memory MCP servers are available but agents don't consistently use them without explicit rules/prompts
- **Stale memories**: No memory server handles contradictions or outdated information well without manual intervention

## Key Design Characteristics

- **Local-first**: All data stays on local filesystem as plain Markdown
- **Human-readable**: Any text editor or Obsidian can view/edit the knowledge base
- **Bidirectional graph**: Not just storing facts but connecting them
- **MCP-native**: Designed specifically for the MCP protocol
- **Zero infrastructure**: No databases, servers, or cloud services required (by default)
- **Append-oriented**: Optimized for growing knowledge, less for updating/forgetting
