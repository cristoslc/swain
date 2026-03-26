---
source-id: "zep-graphiti-temporal-kg"
title: "Zep — Temporal Knowledge Graph Architecture for Agent Memory"
type: web
url: "https://arxiv.org/html/2501.13956v1"
fetched: 2026-03-23T00:00:00Z
hash: "206b270769aefb1a722becd7d38ceb71a8f428563d4946eea2acc7190dda6a68"
---

# Zep — Temporal Knowledge Graph Architecture for Agent Memory

Zep is a memory layer service for AI agents powered by Graphiti, a dynamic, temporally-aware knowledge graph engine. It outperforms MemGPT on the Deep Memory Retrieval (DMR) benchmark and excels in enterprise use cases requiring cross-session synthesis and long-term context.

## Core Problem

Existing RAG frameworks are limited to static document retrieval. Enterprise applications demand dynamic knowledge integration from diverse sources including ongoing conversations and business data. Simply enlarging context windows delays the problem — models get slower, costlier, and still overlook critical details.

## Architecture: Graphiti Knowledge Graph Engine

### Knowledge Graph Construction

#### Episodes

The fundamental unit of data ingestion. Each episode represents a single interaction (conversation message, business event, document update). Episodes are processed incrementally — no batch recomputation needed.

#### Semantic Entities

- **Entities**: Named concepts extracted from episodes (people, organizations, concepts). LLM-generated summaries evolve as new information arrives.
- **Facts**: Relationships between entities, stored as directed edges with temporal metadata. Each fact includes `valid_at` and `invalid_at` timestamps.
- **Temporal Extraction and Edge Invalidation**: When new information contradicts existing facts, the old fact's `invalid_at` is set and a new fact is created. This preserves the complete history of knowledge changes.

#### Communities

Groups of related entities detected via graph algorithms (Leiden community detection). Each community gets an LLM-generated summary for efficient high-level retrieval.

### Memory Retrieval

#### Hybrid Search

Three complementary search functions:

1. **Cosine semantic similarity** (φ_cos): Dense vector search via embeddings
2. **BM25 full-text search** (φ_bm25): Keyword-based retrieval
3. **Breadth-first graph traversal** (φ_bfs): Structural relationship following

All three use Neo4j's Lucene indexes for near-constant time access regardless of graph size.

#### Reranking

Results from all search functions are combined and reranked:
- Reciprocal Rank Fusion (RRF)
- Cross-encoder rerankers
- Maximal Marginal Relevance (MMR) for diversity

### Key Differentiator: No LLM Calls During Retrieval

Unlike Microsoft GraphRAG (which makes multiple LLM calls at query time), Zep's retrieval is deterministic and fast. LLM processing happens only during ingestion (entity/relationship extraction), not during retrieval.

## Benchmark Results

On a custom benchmark extending DMR with enterprise-relevant question types:

| Question Type | Zep Performance |
|---|---|
| Single-session-user | Strong |
| Single-session-assistant | Strong |
| Single-session-preference | Strong |
| Multi-session | Best-in-class |
| Knowledge-update | Best-in-class |
| Temporal-reasoning | Best-in-class |

Zep particularly excels at cross-session information synthesis and temporal reasoning — the two areas most important for enterprise deployment.

## Comparison with GraphRAG

| Characteristic | Zep/Graphiti | Microsoft GraphRAG |
|---|---|---|
| Graph updates | Incremental (real-time) | Batch recomputation |
| Retrieval | Deterministic (no LLM) | LLM-dependent |
| Temporal awareness | First-class (valid_at/invalid_at) | None |
| Latency | Low (index-based) | High (LLM calls at query time) |
| Data model | Episodes → Entities + Facts | Documents → Entities + Communities |

## Platform Offering

Zep is available as:

- **Open source** (Graphiti, Apache 2.0): The temporal knowledge graph engine
- **Zep Platform** (commercial): Managed service with context graph, ingestion from multiple sources (chat, CRM, documents), and assembled context delivery

### Data Sources

The platform ingests from: chat messages, JSON business data, documents, CRM systems, app events. All are unified into a single temporal context graph.

## Key Design Characteristics

- **Temporally-aware**: Every fact has a validity window; contradictions are resolved by invalidating old facts, not deleting them
- **Incremental processing**: New data is processed immediately without re-indexing the entire graph
- **Deterministic retrieval**: No LLM calls at query time — fast, predictable, auditable
- **Enterprise-focused**: Designed for multi-session, multi-source knowledge integration
- **Neo4j-backed**: Leverages Neo4j's index infrastructure for scalable search
