---
title: "Embedding Nearest-Neighbor Artifact Navigation"
artifact: SPIKE-058
track: container
status: Active
author: Cristos L-C
created: 2026-04-04
last-updated: 2026-04-04
question: "Can vector embeddings of artifact content enable fast nearest-neighbor lookup for navigating, discovering, and linking related artifacts — and does this outperform keyword grep for cross-artifact discovery?"
gate: Pre-MVP
risks-addressed:
  - Artifact discovery degrades as the corpus grows beyond grep's ergonomic limit
  - Cross-artifact links are missed because keyword overlap is low but semantic overlap is high
evidence-pool: ""
---

# Embedding Nearest-Neighbor Artifact Navigation

## Summary

<!-- Final-pass section: populated when transitioning to Complete. -->

## Question

Can vector embeddings of artifact content enable fast nearest-neighbor lookup for navigating, discovering, and linking related artifacts — and does this outperform keyword grep for cross-artifact discovery?

Sub-questions:
1. **Embedding model**: Which embedding model balances quality vs. local-first operation? (e.g., `nomic-embed-text` via Ollama, OpenAI `text-embedding-3-small`, sentence-transformers)
2. **Chunking strategy**: Should each artifact embed as one vector, or should sections (Summary, Question, Findings, ACs) embed separately for finer-grained matching?
3. **Index format**: What vector store fits swain's constraints — flat file (numpy/faiss), SQLite with vec extension, or a lightweight embedded DB like LanceDB?
4. **Query interface**: How should an agent or operator query nearest neighbors? CLI tool? Chart.sh lens? Inline during artifact creation?
5. **Staleness**: How do we keep the index fresh as artifacts change — rebuild on commit hook, lazy rebuild on query, or incremental via git diff?
6. **Semantic gain**: On the current swain corpus, does embedding similarity surface relationships that keyword grep misses?

## Go / No-Go Criteria

1. **Precision@5 >= 0.6** — given a query artifact, at least 3 of the top 5 nearest neighbors should be artifacts a human would consider related (manual judgment on 10 sample queries across the swain corpus).
2. **Latency < 500ms** — full-corpus nearest-neighbor query (embed query + search) must complete in under 500ms on a local machine with no GPU.
3. **Index size < 10MB** — the vector index for a corpus of up to 500 artifacts must stay under 10MB on disk.
4. **Local-first viable** — at least one embedding path must work fully offline (no API calls required for embedding or search).
5. **Incremental update < 2s** — re-embedding a single changed artifact and updating the index must take under 2 seconds.

## Pivot Recommendation

If embedding quality is poor (Precision@5 < 0.4) or latency is unacceptable: fall back to **TF-IDF with cosine similarity** over artifact content. TF-IDF is trivially local, fast, and may suffice for a corpus this size. This could be implemented as a `chart.sh similar <ARTIFACT-ID>` lens with no external dependencies beyond Python.

If the local-first constraint fails (no offline model produces acceptable quality): consider a **hybrid approach** where embeddings are generated on-demand via API when online, cached locally, and TF-IDF is the offline fallback.

## Findings

<!-- Populated during Active phase. -->

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | 0032246a | Initial creation — user requested |
