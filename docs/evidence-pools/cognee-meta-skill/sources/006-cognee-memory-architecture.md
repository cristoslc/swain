---
source-id: "006"
title: "Cognee AI Memory Architecture — Knowledge Engine Overview"
type: web
url: "https://www.cognee.ai/blog/fundamentals/how-cognee-builds-ai-memory"
fetched: 2026-03-15T21:06:00Z
hash: "sha256:placeholder"
---

# Cognee AI Memory Architecture

Cognee is an open-source knowledge engine for AI agent memory. It combines vector search, graph databases, and self-improvement to make documents searchable by meaning and connected by relationships.

## Core Architecture

- **Session memory** (short-term): Loads relevant embeddings and graph fragments into runtime context for fast reasoning
- **Permanent memory** (long-term): Stores knowledge artifacts — user data, interaction traces, external documents, derived relationships
- **Graph structure**: Nodes represent entities, edges represent relationships; the graph evolves over time

## Self-Improvement

The system prunes stale nodes, strengthens frequent connections, reweights edges based on usage signals, and adds derived facts. Memory is not static storage — it's an evolving structure that adapts based on feedback and interaction traces.

## Cognee as Skills Infrastructure

cognee-skills adds a skill layer on top of the knowledge engine:
- Skills are parsed from SKILL.md files and stored as nodes in the knowledge graph
- Every execution creates SkillRun nodes with success scores
- TaskPattern nodes enable learned routing preferences via `prefers` edges
- The self-improvement loop (inspect → preview → amendify → evaluate → rollback) operates entirely within the graph

## Key Differentiators (from benchmarks)

- Cognee outperformed Mem0, Graphiti, and LightRAG on HotPotQA multi-hop reasoning benchmarks (Exact Match, F1, human-like correctness metrics)
- Multi-layer semantic graphs with detailed relationship edges vs. simpler approaches
- Production scale: 1M+ pipelines/month, 70+ companies

## Graph-Based Skill Routing

Cognee's skill routing uses a two-stage retrieval:
1. Vector search finds semantically similar skills by instruction_summary
2. Graph-based `prefers` edges boost skills that have historically performed well on similar TaskPatterns
3. Blended score combines semantic similarity with learned preference weights
