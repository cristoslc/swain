# Synthesis: Agent Memory Systems

## Memory Type Taxonomy

All sources converge on a three-part taxonomy inspired by cognitive science, though naming and granularity vary:

| Type | Academic Term | What It Stores | Examples in Practice |
|------|--------------|----------------|---------------------|
| **Semantic** | Declarative/factual | Facts, preferences, knowledge | User preferences, project conventions, entity relationships |
| **Episodic** | Experiential | Past interactions with context | Few-shot examples, debugging histories, rollout summaries |
| **Procedural** | Implicit/behavioral | How to act, rules, style | System prompts, instruction files, learned skills |

**LangMem** (`langmem-conceptual-guide`) formalizes these as distinct APIs. **EmergentMind** (`emergentmind-memory-taxonomy`) adds finer subdivisions: working vs. long-term memory, parametric vs. textual vs. structured storage, and agent-local vs. shared. **Letta** (`letta-memgpt`) maps them to a concrete architecture: core memory (semantic), archival memory (episodic), and system instructions (procedural).

## The Memory Landscape: Five Tiers

Across all 11 sources, memory systems fall into five tiers of increasing sophistication:

### Tier 1: Instruction Files (Procedural Only)

Every coding CLI provides markdown instruction files loaded at session start: CLAUDE.md, GEMINI.md, AGENTS.md. These are human-authored, deterministic, and universal. OpenCode (`opencode-rules-context`) lives entirely at this tier with no native memory beyond AGENTS.md.

### Tier 2: Explicit Fact Storage

Gemini CLI (`gemini-cli-memory`) adds a `save_memory` tool that appends facts to GEMINI.md. User-triggered, append-only, global scope. No extraction, consolidation, or forgetting. Basic Memory (`basic-memory-mcp`) sits here too — the LLM writes structured markdown files via MCP, building a knowledge graph, but only when explicitly prompted.

### Tier 3: Autonomous Memory Extraction

Claude Code (`claude-code-memory`) and Codex (`codex-memory-system`) autonomously extract memories without user prompting. Claude Code writes during sessions (hot path); Codex runs a two-phase background pipeline with SQLite state management, rollout extraction, and consolidation sub-agent. Both produce markdown artifacts.

### Tier 4: Memory Frameworks with Vector/Graph Storage

**Mem0** (`mem0-memory-layer`): LLM-powered extraction → vector storage → semantic retrieval. Optional graph layer (Mem0^g) with Neo4j for entity relationships. 26% improvement over OpenAI's memory on LOCOMO benchmark.

**LangMem** (`langmem-conceptual-guide`): Provides the primitives (memory managers, prompt optimizers) that other systems can compose. Framework-level, not a complete system.

**Cognee** (`cognee-knowledge-engine`): Pipeline-based knowledge engine. Ingests 30+ formats, extracts triplets into graph + embeddings into vector store. Most flexible ingestion.

### Tier 5: Self-Editing Memory Agents

**Letta/MemGPT** (`letta-memgpt`): The LLM itself manages its own memory via tools (`core_memory_append`, `archival_memory_search`, etc.). Virtual memory paradigm — the agent decides what to page in and out. Sleep-time agents process memory between sessions.

**Zep/Graphiti** (`zep-graphiti-temporal-kg`): Temporal knowledge graph with first-class time semantics. Facts have `valid_at`/`invalid_at` windows. Contradictions are resolved by invalidation, not deletion. No LLM calls during retrieval — deterministic, fast, auditable.

## Storage Architecture Comparison

| System | Storage Backend | Graph Support | Retrieval Method |
|--------|----------------|---------------|------------------|
| Claude Code | Markdown files | None | Full file load + on-demand reads |
| Codex | SQLite + Markdown | None | Background consolidation into MEMORY.md |
| Gemini CLI | Markdown (GEMINI.md) | None | Full file load |
| OpenCode | N/A (instructions only) | N/A | Full file load |
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

**Key insight**: Graph memory excels at **multi-hop reasoning** and **temporal relationships** but requires infrastructure (Neo4j or similar). For simple fact recall, vector-only approaches are sufficient and simpler.

## Memory Formation Patterns

| Pattern | Who Does It | When | Examples |
|---------|------------|------|----------|
| **Human-authored** | User writes instructions | Before sessions | CLAUDE.md, GEMINI.md, AGENTS.md |
| **User-triggered** | User asks agent to remember | During conversation | Gemini CLI save_memory, Basic Memory |
| **Hot path / conscious** | Agent extracts during conversation | During conversation | Claude Code auto memory |
| **Background / subconscious** | System extracts after conversation | Between sessions | Codex Phase 1/2, Letta sleep-time agents |
| **Continuous ingestion** | System processes all data streams | Ongoing | Zep/Graphiti, Mem0 platform |

## Memory Quality Mechanisms

### Consolidation
- **Codex**: Phase 2 sub-agent merges raw memories into a consolidated MEMORY.md, with diff-based updates for incremental changes
- **Mem0**: LLM-powered consolidation that deduplicates, merges, and updates memories
- **Letta**: Agent self-consolidates by editing its own core memory blocks
- **Zep**: Graph community detection + LLM summarization

### Forgetting
- **Codex**: Automatic — "polluted" threads (web search used) are excluded; unused memories decay via `max_unused_days`
- **Zep**: Temporal invalidation — old facts get `invalid_at` timestamps but are preserved for history
- **Mem0**: Consolidation can merge/remove redundant memories
- **Claude Code**: Manual only (user edits files)
- **Gemini CLI**: Manual only

### Memory Pollution
Only Codex implements explicit memory pollution detection: if a session uses web search or MCP tools, the thread is marked "polluted" and excluded from memory extraction. This prevents unreliable external data from contaminating the persistent knowledge base.

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

## Points of Disagreement

- **Agent-driven vs. pipeline-driven memory**: Letta gives the LLM full control; Codex/Mem0/Zep use external pipelines. Both approaches work — the tradeoff is autonomy vs. predictability.
- **Graph vs. vector**: Zep/Graphiti argues temporal KGs are essential for enterprise; Mem0 treats graph as an optional enhancement over vector-first. Cognee offers both as configurable backends.
- **Forgetting strategy**: Codex's pollution-based exclusion, Zep's temporal invalidation, and Mem0's consolidation-based merging represent fundamentally different philosophies.

## Gaps in the Landscape

- **No system implements all three memory types well**: Semantic memory is well-served; episodic memory is nascent (only Codex rollout summaries and Letta recall); procedural memory evolution (LangMem's prompt optimizer) remains theoretical in production tools.
- **Cross-tool memory portability**: No standard for moving memories between systems. Markdown comes closest to portable, but schemas are incompatible.
- **Memory evaluation benchmarks**: LOCOMO and DMR exist but don't cover coding-agent-specific scenarios (project context, codebase understanding, debugging history).
- **Privacy and access control**: Only the academic literature (EmergentMind) seriously addresses multi-user memory privacy. Production tools assume single-user.
- **Cost and token efficiency**: Mem0 claims to reduce token costs via compression, but no comparative data exists across systems.

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
