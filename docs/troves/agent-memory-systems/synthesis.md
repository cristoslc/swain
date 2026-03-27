# Synthesis: Agent Memory Systems

## Memory Type Taxonomy

All sources converge on a three-part taxonomy inspired by cognitive science, though naming and granularity vary:

| Type | Academic Term | What It Stores | Examples in Practice |
|------|--------------|----------------|---------------------|
| **Semantic** | Declarative/factual | Facts, preferences, knowledge | User preferences, project conventions, entity relationships |
| **Episodic** | Experiential | Past interactions with context | Few-shot examples, debugging histories, rollout summaries |
| **Procedural** | Implicit/behavioral | How to act, rules, style | System prompts, instruction files, learned skills |

**LangMem** (`langmem-conceptual-guide`) formalizes these as distinct APIs. **EmergentMind** (`emergentmind-memory-taxonomy`) adds finer subdivisions: working vs. long-term memory, parametric vs. textual vs. structured storage, and agent-local vs. shared. **Letta** (`letta-memgpt`) maps them to a concrete architecture: core memory (semantic), archival memory (episodic), and system instructions (procedural).

## The Memory Landscape: Six Tiers

Across all 12 sources, memory systems fall into six tiers of increasing sophistication:

### Tier 1: Instruction Files (Procedural Only)

Every coding CLI provides markdown instruction files loaded at session start: CLAUDE.md, GEMINI.md, AGENTS.md. These are human-authored, deterministic, and universal. OpenCode (`opencode-rules-context`) lives entirely at this tier with no native memory beyond AGENTS.md.

### Tier 2: Explicit Fact Storage

Gemini CLI (`gemini-cli-memory`) adds a `save_memory` tool that appends facts to GEMINI.md. User-triggered, append-only, global scope. No extraction, consolidation, or forgetting. Basic Memory (`basic-memory-mcp`) sits here too — the LLM writes structured markdown files via MCP, building a knowledge graph, but only when explicitly prompted.

### Tier 3: Autonomous Memory Extraction

Claude Code (`claude-code-memory`) and Codex (`codex-memory-system`) autonomously extract memories without user prompting. Claude Code writes during sessions (hot path); Codex runs a two-phase background pipeline with SQLite state management, rollout extraction, and consolidation sub-agent. Both produce markdown artifacts.

### Tier 4: Convention-Driven Cognitive Architecture

**Cog** (`cog-repo`) represents a distinct tier: a full cognitive architecture built entirely from markdown conventions on top of a Tier 3 substrate (Claude Code). No application code — CLAUDE.md and skill files define all behavior. What makes this a separate tier rather than just "Tier 3 with more files":

- **Three-tier memory hierarchy** (hot/warm/glacier) with explicit size caps and progressive condensation (observations → patterns → hot-memory)
- **L0/L1/L2 tiered retrieval** — every file has a one-line `<!-- L0: ... -->` summary enabling scan-before-read, inspired by OpenViking
- **SSOT enforcement** — each fact lives in exactly one canonical file; all cross-references use `[[wiki-links]]`; housekeeping enforces this
- **Session transcript mining** — `/reflect` reads Claude Code's JSONL session files via a cursor to extract missed cues, broken promises, and memory gaps
- **Domain routing** — conversational `/setup` generates `domains.yml`, memory directories, and domain-specific slash commands; each skill loads only its own memory files
- **Entity registry** — strict 3-line compact format with temporal validity markers `(since YYYY-MM)` / `(until YYYY-MM)`, auto-struck by housekeeping
- **Threads (Zettelkasten layer)** — when a topic recurs 3+ times across 2+ weeks, it's raised into a synthesis file with Current State / Timeline / Insights spine; grows forever, never condensed

Cog implements all three memory types: semantic (entities, observations), episodic (session transcript ingestion, threads), and procedural (CLAUDE.md conventions, skill files that `/evolve` can modify).

### Tier 5: Memory Frameworks with Vector/Graph Storage

**Mem0** (`mem0-memory-layer`): LLM-powered extraction → vector storage → semantic retrieval. Optional graph layer (Mem0^g) with Neo4j for entity relationships. 26% improvement over OpenAI's memory on LOCOMO benchmark.

**LangMem** (`langmem-conceptual-guide`): Provides the primitives (memory managers, prompt optimizers) that other systems can compose. Framework-level, not a complete system.

**Cognee** (`cognee-knowledge-engine`): Pipeline-based knowledge engine. Ingests 30+ formats, extracts triplets into graph + embeddings into vector store. Most flexible ingestion.

### Tier 6: Self-Editing Memory Agents

**Letta/MemGPT** (`letta-memgpt`): The LLM itself manages its own memory via tools (`core_memory_append`, `archival_memory_search`, etc.). Virtual memory paradigm — the agent decides what to page in and out. Sleep-time agents process memory between sessions.

**Zep/Graphiti** (`zep-graphiti-temporal-kg`): Temporal knowledge graph with first-class time semantics. Facts have `valid_at`/`invalid_at` windows. Contradictions are resolved by invalidation, not deletion. No LLM calls during retrieval — deterministic, fast, auditable.

**Cog's `/evolve`** (`cog-repo`) also operates at this tier for procedural memory: it audits the rules themselves and proposes/applies changes to skill files. This is self-editing behavior, but scoped to conventions rather than knowledge. The boundary between Tier 4 and Tier 6 in Cog's case is that data memory (observations, entities) flows through a structured pipeline, while rule memory (CLAUDE.md, skills) can be self-modified by the system.

## Storage Architecture Comparison

| System | Storage Backend | Graph Support | Retrieval Method |
|--------|----------------|---------------|------------------|
| Claude Code | Markdown files | None | Full file load + on-demand reads |
| Codex | SQLite + Markdown | None | Background consolidation into MEMORY.md |
| Gemini CLI | Markdown (GEMINI.md) | None | Full file load |
| OpenCode | N/A (instructions only) | N/A | Full file load |
| **Cog** | **Markdown files (3-tier)** | **Wiki-links + generated link-index** | **L0/L1/L2 progressive loading** |
| Mem0 | Vector DB + optional Neo4j | Optional (Mem0^g) | Semantic similarity + graph traversal |
| Letta | Vector DB + relational | Archival search | Agent-driven tool calls |
| Zep/Graphiti | Neo4j | Core architecture | Hybrid: cosine + BM25 + graph BFS |
| Cognee | Vector DB + Graph DB | Core architecture | Pipeline-defined custom retrievers |
| Basic Memory | Markdown files | Bidirectional links | MCP tool calls + semantic search |
| LangMem | Configurable (LangGraph Store) | Via LangGraph | Semantic search + metadata filtering |

## Graph Memory: The Emerging Frontier

Three systems place knowledge graphs at the center of their architecture:

### Zep/Graphiti
- **Temporal knowledge graph** with Neo4j backend
- Entities and facts extracted from episodes (conversations, events)
- Facts have temporal validity windows — contradictions create new edges rather than deleting old ones
- Hybrid retrieval (cosine + BM25 + BFS) with no LLM calls at query time
- Communities detected via Leiden algorithm with LLM-generated summaries

### Mem0^g (Graph Memory variant)
- Adds a graph layer on top of Mem0's vector memory
- Supports Neo4j, Memgraph, Neptune, Kuzu, Apache AGE
- Entity resolution across conversations
- ~2% improvement over base Mem0 on benchmarks

### Cognee
- Triplet extraction (subject → relation → object) into configurable graph backends
- Graph skeletons enable custom retrieval strategies
- Supports Neo4j, Memgraph, NetworkX, FalkorDB
- Pipeline-based: multiple enrichment steps between ingestion and retrieval

### Cog's Wiki-Link Graph (Lightweight Alternative)
- No external graph DB — `[[wiki-links]]` in markdown files create a navigable graph
- `link-index.md` auto-generated by housekeeping provides reverse lookups (what links to this file?)
- Write-time linking: when editing any file, actively add cross-references
- Write-time back-linking: when adding A→B, check if B benefits from pointing back to A
- Limitation: no semantic search, no multi-hop traversal, no temporal edges — but zero infrastructure and fully inspectable via `grep`

**Key insight**: Graph memory excels at **multi-hop reasoning** and **temporal relationships** but requires infrastructure (Neo4j or similar). For simple fact recall, vector-only approaches are sufficient and simpler. Cog demonstrates that wiki-links + a generated index can approximate basic graph navigation within git-first constraints.

## Memory Maintenance Pipelines

A distinguishing feature across the landscape is how systems maintain memory quality over time:

| System | Consolidation | Forgetting | Self-Audit |
|--------|--------------|------------|------------|
| Claude Code | Manual | Manual (user edits) | None |
| Codex | Phase 2 sub-agent | Pollution exclusion + `max_unused_days` decay | None |
| Mem0 | LLM-powered dedup/merge | Consolidation-based | None |
| Letta | Agent self-consolidates core memory | Agent-driven archival | None |
| Zep | Community detection + summarization | Temporal invalidation | None |
| **Cog** | **`/reflect` condenses obs→patterns→hot-memory** | **`/housekeeping` prunes by age/staleness, archives to glacier** | **`/evolve` audits rules; `/reflect` mines sessions for gaps** |

Cog is unique in having four distinct pipeline stages with strict file-ownership boundaries:
- `/housekeeping` — structural maintenance (archive, prune, link audit, glacier index, briefing bridge)
- `/reflect` — pattern extraction from session transcripts, condensation, thread detection, consistency sweeps
- `/evolve` — meta-level: audits and changes the rules themselves, never touches content
- `/foresight` — cross-domain strategic nudge (consumes briefing bridge from housekeeping)

The **briefing bridge** pattern is notable: housekeeping writes `briefing-bridge.md` as a producer-consumer handoff for foresight. Clean coupling between pipeline stages without direct dependency.

## Memory Formation Patterns

| Pattern | Who Does It | When | Examples |
|---------|------------|------|----------|
| **Human-authored** | User writes instructions | Before sessions | CLAUDE.md, GEMINI.md, AGENTS.md |
| **User-triggered** | User asks agent to remember | During conversation | Gemini CLI save_memory, Basic Memory |
| **Hot path / conscious** | Agent extracts during conversation | During conversation | Claude Code auto memory |
| **Background / subconscious** | System extracts after conversation | Between sessions | Codex Phase 1/2, Letta sleep-time agents |
| **Continuous ingestion** | System processes all data streams | Ongoing | Zep/Graphiti, Mem0 platform |
| **Convention-driven pipeline** | Scheduled skills follow rules | On invocation | Cog reflect/housekeeping/evolve/foresight |

## Memory Quality Mechanisms

### Consolidation
- **Codex**: Phase 2 sub-agent merges raw memories into a consolidated MEMORY.md, with diff-based updates for incremental changes
- **Mem0**: LLM-powered consolidation that deduplicates, merges, and updates memories
- **Letta**: Agent self-consolidates by editing its own core memory blocks
- **Zep**: Graph community detection + LLM summarization
- **Cog**: Progressive condensation — observations (append-only) → patterns (distilled rules, ≤70 lines) → hot-memory (rewrite freely, ≤50 lines). Each layer smaller and more actionable. Thread files synthesize recurring topics without condensing the raw observations.

### Forgetting
- **Codex**: Automatic — "polluted" threads (web search used) are excluded; unused memories decay via `max_unused_days`
- **Zep**: Temporal invalidation — old facts get `invalid_at` timestamps but are preserved for history
- **Mem0**: Consolidation can merge/remove redundant memories
- **Claude Code**: Manual only (user edits files)
- **Gemini CLI**: Manual only
- **Cog**: Structured archival — observations >50 entries archived to glacier by primary tag; entities inactive >6 months moved to glacier with stubs; completed action items >10 archived. Glacier files get YAML frontmatter and are indexed in `glacier/index.md`. Nothing deleted — everything moves to the right tier.

### Memory Pollution
Only Codex implements explicit memory pollution detection: if a session uses web search or MCP tools, the thread is marked "polluted" and excluded from memory extraction. This prevents unreliable external data from contaminating the persistent knowledge base.

### Consistency & Contradiction Detection
- **Cog**: `/reflect` runs a systematic consistency sweep — hot-memory vs. canonical sources (canonical wins), cross-file fact checks (more recent wins), temporal validity checks on entity facts. Cross-domain entity deduplication ensures one canonical entry with pointers from secondary domains.
- **Zep**: Temporal invalidation creates new edges rather than deleting contradictions
- **Mem0**: LLM-powered consolidation handles dedup but without explicit temporal reasoning

## MCP Memory Server Ecosystem

Basic Memory (`basic-memory-mcp`) represents a growing category. The landscape includes:

| Category | Examples | Storage | Complexity |
|----------|---------|---------|------------|
| Markdown-first | Basic Memory, mcp-memory-keeper | Local files | Low |
| Vector-backed | Mem0 OpenMemory, HPKV Memory | Embedding DB | Medium |
| Graph-backed | mcp-neo4j-agent-memory | Neo4j | High |
| Hybrid | mcp-memory-service | KG + vector + REST | Highest |

**Community pain points**: context rot (memory retrieval fills context), poor prompt integration (agents don't use memory tools without explicit rules), and stale memories (no automatic contradiction handling).

## Points of Agreement

1. **Markdown instruction files are table stakes** — every tool has them
2. **Memory should be inspectable and editable** by humans
3. **LLM-powered extraction** outperforms rule-based approaches for memory quality
4. **Semantic search** is the baseline retrieval method; graph traversal adds value for connected knowledge
5. **Background processing** (post-session) is preferred over hot-path for quality; hot-path is preferred for immediacy
6. **Progressive condensation** appears independently in multiple systems: Codex (Phase 1→2→MEMORY.md), Cog (observations→patterns→hot-memory), Zep (episodes→facts→communities)

## Points of Disagreement

- **Agent-driven vs. pipeline-driven memory**: Letta gives the LLM full control; Codex/Mem0/Zep use external pipelines. Both approaches work — the tradeoff is autonomy vs. predictability. Cog is a hybrid: convention-driven pipelines, but `/evolve` can self-modify the rules.
- **Graph vs. vector**: Zep/Graphiti argues temporal KGs are essential for enterprise; Mem0 treats graph as an optional enhancement over vector-first. Cognee offers both as configurable backends. Cog proves that wiki-links + a generated index can serve basic graph needs within git-first constraints.
- **Forgetting strategy**: Codex's pollution-based exclusion, Zep's temporal invalidation, Mem0's consolidation-based merging, and Cog's structured archival represent fundamentally different philosophies.
- **Infrastructure requirements**: Tier 5-6 systems (Mem0, Zep, Cognee, Letta) require external services. Cog demonstrates that a sophisticated memory architecture can operate with zero infrastructure beyond the filesystem, though it trades semantic search and multi-hop traversal for inspectability and simplicity.

## Gaps in the Landscape

- **No system implements all three memory types well**: Semantic memory is well-served; episodic memory is nascent (only Codex rollout summaries, Letta recall, and Cog's session transcript mining); procedural memory evolution (LangMem's prompt optimizer, Cog's `/evolve`) remains experimental.
- **Cross-tool memory portability**: No standard for moving memories between systems. Markdown comes closest to portable, but schemas are incompatible.
- **Memory evaluation benchmarks**: LOCOMO and DMR exist but don't cover coding-agent-specific scenarios (project context, codebase understanding, debugging history).
- **Privacy and access control**: Only the academic literature (EmergentMind) seriously addresses multi-user memory privacy. Production tools assume single-user.
- **Cost and token efficiency**: Mem0 claims to reduce token costs via compression, but no comparative data exists across systems.
- **Convention testing and validation**: Cog's convention-only approach raises an open question — how do you test that conventions are being followed? Cog's `/evolve` audits manually, but there's no automated validation framework for instruction-based architectures.
- **Migration paths**: No system (including Cog) addresses schema evolution well — what happens when memory conventions change? Cog lacks migration scripts for its own convention changes.

## Sources

- `langmem-conceptual-guide` — LangMem: semantic/episodic/procedural taxonomy, collection vs. profile, hot path vs. background
- `claude-code-memory` — Claude Code: CLAUDE.md hierarchy, auto memory, 200-line MEMORY.md index
- `codex-memory-system` — Codex: two-phase pipeline, SQLite, rollout extraction, consolidation sub-agent, pollution, forgetting
- `gemini-cli-memory` — Gemini CLI: GEMINI.md hierarchy, save_memory tool, append-only
- `opencode-rules-context` — OpenCode: AGENTS.md only, no native memory, plugin ecosystem
- `emergentmind-memory-taxonomy` — Academic survey: full taxonomy, A-MEM, HiAgent, MIRIX, consolidation/decay
- `mem0-memory-layer` — Mem0: universal memory layer, vector + graph, LLM extraction, OpenMemory MCP
- `letta-memgpt` — Letta/MemGPT: self-editing memory, virtual memory paradigm, sleep-time agents
- `zep-graphiti-temporal-kg` — Zep/Graphiti: temporal knowledge graph, no-LLM retrieval, Neo4j-backed
- `cognee-knowledge-engine` — Cognee: pipeline-based knowledge engine, 30+ sources, graph + vector
- `basic-memory-mcp` — Basic Memory: markdown knowledge graph MCP server, local-first, bidirectional links
- `cog-repo` — Cog: convention-only cognitive architecture on Claude Code, 3-tier memory, L0/L1/L2 retrieval, 4-stage maintenance pipeline, wiki-link graph, self-modifying rules via /evolve
