---
source-id: "semanticwiki-research"
title: "SemanticWiki | Research | reasoning.software"
type: web
url: "https://reasoning.software/research/semanticwiki"
fetched: 2026-04-16T18:15:00Z
hash: ""
notes: "SPA site; content captured via browser snapshot"
---

# SemanticWiki | Research | reasoning.software

Active product and applied research. Updated 2026-02-05.

## Architectural documentation with source-code traceability

SemanticWiki pairs autonomous codebase understanding with precise, line-linked documentation generation for engineering teams.

## Product and Research Angles

### Product

- CLI-first workflow for architecture wiki generation
- Static site output with fast search and dark mode
- Traceability guarantees from concept to file:line implementation

### Research

- RAG retrieval quality under large codebase entropy
- Agentic planning reliability for long documentation runs
- Evaluation harness for traceability precision and broken-link drift

## Roadmap

1. **Phase 1** — Complete. Codebase digestion and architecture wiki generation.
2. **Phase 2** — Current. Robust link verification and traceability confidence scoring.
3. **Phase 3** — Planned. Comparative studies across retrieval and planning strategies.

## Key Signals

| Signal | Value |
|--------|-------|
| Primary Interface | CLI |
| Core Retrieval | FAISS + MiniLM |
| Output Surface | Static Wiki |

## Why This Exists

SemanticWiki addresses a practical engineering gap: architecture knowledge usually decays faster than code changes. The project treats documentation as a generated, verifiable artifact with direct traceability back to implementation.

> **Core Thesis**: Architectural understanding should be queryable, testable, and linked to exact source locations, not trapped in stale prose.

## Product Surface

SemanticWiki currently ships as an AI-powered CLI with two concrete operating modes:

- `semanticwiki generate` to produce architecture documentation and static wiki outputs.
- `semanticwiki continue` to resume long-running autonomous documentation sessions with cached context.

The output includes architecture overviews, module maps, data-flow docs, and getting-started guides with direct source references such as `src/auth/jwt.ts:23`.

## Product and Research Lenses

### Product Lens

Developer-facing value comes from speed to comprehension in unfamiliar codebases. The static site output focuses on searchability, keyboard navigation, and low-friction handoff across teams.

### Research Lens

The same generation loop acts as an experiment platform for studying retrieval quality and planning reliability. Each run can be evaluated for traceability precision, structural coverage, and documentation drift under code churn.

## System Architecture

SemanticWiki combines four layers:

1. Codebase exploration and structural extraction.
2. Semantic retrieval over embeddings (FAISS + all-MiniLM-L6-v2).
3. Agentic reasoning loop for documentation planning and synthesis.
4. Verification loop for source-link integrity and output consistency.

This architecture is intentionally dual-purpose: it powers a usable product and produces measurable research signals.

## Evaluation Strategy

| Metric | Definition | Failure Signal |
|--------|-----------|----------------|
| Traceability Precision | % of documentation claims that resolve to valid source spans | Broken links, wrong file-level mappings |
| Architectural Coverage | % of core modules and interfaces represented | Missing high-centrality modules |
| Regeneration Stability | Similarity across repeated runs with same inputs | High variance across unchanged code |
| Link Drift Resilience | Integrity after codebase edits | Growing unresolved references over time |

## Research Program

Current work is less about writing prettier docs and more about formalizing documentation generation as a reliability problem:

- How does retrieval strategy alter architectural coherence?
- Which planning loops best balance speed with verification quality?
- How much autonomous execution is safe before human checkpoints are required?

Negative outcomes, such as brittle trace mapping or overconfident summaries, are tracked as first-class artifacts.

## Near-Term Direction

- Add confidence scoring to all source-linked claims.
- Introduce benchmark suites that stress heterogeneous mono-repos.
- Compare planning strategies under identical retrieval corpora.

SemanticWiki is the intellectual property of reasoning.software (MadWatch LLC), created by Dakota Kim.

## External Links

- [npm package](https://www.npmjs.com/package/semanticwiki)
- [Build an Agent Workshop](https://buildanagentworkshop.com/)