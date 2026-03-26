---
source-id: "cognee-knowledge-engine"
title: "Cognee — Open Source Knowledge Engine for AI Agent Memory"
type: web
url: "https://github.com/topoteretes/cognee"
fetched: 2026-03-23T00:00:00Z
hash: "42e3d4a643352d23aae1a64892241dc75186e0d0a9175f837f50581a61f51282"
---

# Cognee — Open Source Knowledge Engine for AI Agent Memory

Cognee is an open-source knowledge engine that ingests data in any format, builds a knowledge graph with vector embeddings, and provides contextual retrieval for AI agents. It combines vector search, graph databases, and cognitive science approaches.

## Core Concept

Cognee turns documents into AI memory through a three-step pipeline:

```python
import cognee

await cognee.add("Cognee turns documents into AI memory.")
await cognee.cognify()   # Build knowledge graph
results = await cognee.search("What does Cognee do?")
```

### Pipeline Architecture

1. **Ingestion**: Load data from 30+ supported sources (files, URLs, databases, APIs)
2. **Enrichment ("cognify")**: Extract entities and relationships (triplets: subject-relation-object), generate embeddings, build graph structure
3. **Retrieval**: Combine vector similarity, graph traversal, and time filters

## Memory-First Architecture

Cognee moved beyond traditional RAG by combining:

- **Embeddings**: Semantic similarity search via vector database
- **Graph extraction**: Triplet extraction (subject → relation → object) stored in a knowledge graph
- **Cognitive science approaches**: Memory organization inspired by human cognition

### Graph Skeletons

Cognee creates graph skeletons in memory that allow various operations on graphs and power custom retrievers. This enables developers to build custom knowledge graph logic — how to create, how to retrieve, which vectors to use.

## Data Sources

Supports 30+ input formats:
- Documents (PDF, DOCX, TXT, Markdown)
- Web pages and URLs
- Databases and APIs
- Code repositories (codegraph feature)

## Integration Model

- **Python SDK**: Primary interface
- **CLI**: `cognee-cli add`, `cognee-cli cognify`, `cognee-cli search`
- **MCP support**: Available as an MCP server for coding agents
- **Agent frameworks**: Works with LangChain, LlamaIndex, CrewAI

## Storage Backends

### Vector Stores
- Qdrant, Weaviate, PGVector, LanceDB

### Graph Stores
- Neo4j, Memgraph, NetworkX, FalkorDB

### Relational
- PostgreSQL, SQLite

## Key Design Characteristics

- **Pipeline-based**: Data flows through configurable enrichment pipelines rather than a single extraction step
- **Custom retrievers**: Developers build their own retrieval logic on top of graph skeletons
- **Multi-backend**: Supports multiple vector and graph database backends
- **Evolving knowledge**: Documents are connected by relationships that change as new data arrives
- **Self-improving**: Learns from feedback, updates concepts and synonyms
- **Open source**: Full framework available under open-source license

## Comparison to Similar Tools

- **vs. Mem0**: Cognee focuses on document-level knowledge graphs; Mem0 focuses on conversational memory extraction
- **vs. Zep/Graphiti**: Cognee uses configurable pipelines; Graphiti is specifically temporal-aware
- **vs. LangMem**: Cognee is a full knowledge engine; LangMem provides memory primitives for agent frameworks

## Research

Published research on optimizing knowledge graphs for LLM reasoning, demonstrating improvements in retrieval precision and reasoning accuracy.
