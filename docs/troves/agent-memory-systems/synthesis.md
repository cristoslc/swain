# Synthesis: Agent Memory Systems

## Memory Type Taxonomy

All sources converge on a three-part taxonomy inspired by cognitive science, though naming and boundaries vary:

| Type | Academic Term | What It Stores | Coding Agent Equivalent |
|------|--------------|----------------|------------------------|
| **Semantic** | Declarative/factual | Facts, preferences, knowledge | User preferences, project conventions, architectural decisions |
| **Episodic** | Experiential | Past interactions with full context | Few-shot examples, debugging war stories, successful patterns |
| **Procedural** | Implicit/behavioral | How to act, rules, style | System prompts, instruction files, evolved behavioral rules |

**LangMem** (`langmem-conceptual-guide`) formalizes these as distinct APIs: `create_memory_manager` for semantic/episodic, `create_prompt_optimizer` for procedural. **EmergentMind** (`emergentmind-memory-taxonomy`) adds finer subdivisions: working memory vs. long-term, parametric vs. textual vs. structured storage, and agent-local vs. shared memory.

## Coding Agent Memory Comparison

| Feature | Claude Code | Codex | Gemini CLI | OpenCode |
|---------|------------|-------|------------|----------|
| **Instruction files** | CLAUDE.md (hierarchical, `.claude/rules/`) | User instructions in config | GEMINI.md (hierarchical) | AGENTS.md (project + global) |
| **Auto memory** | Yes — writes MEMORY.md + topic files | Yes — two-phase pipeline, SQLite-backed | No — explicit `save_memory` only | No native (plugins only) |
| **Memory extraction** | Autonomous, during session | Autonomous, background at startup (Phase 1) | User-triggered ("remember X") | N/A |
| **Consolidation** | Claude manages MEMORY.md as index + topic files | Phase 2 sub-agent consolidates into MEMORY.md + skills/ | None — append-only | N/A |
| **Forgetting** | Manual (user edits files) | Automatic — polluted threads removed, unused memories decay | Manual (user edits GEMINI.md) | N/A |
| **Storage** | Plain markdown in `~/.claude/projects/` | SQLite + markdown in `<codex_home>/memories/` | Appended to global GEMINI.md | N/A |
| **Scope** | Per-project (git repo scoped) | Per-project (codex_home scoped) | Global only (save_memory) | N/A |
| **200-line limit** | MEMORY.md index only | No documented limit | No documented limit | N/A |

## Key Design Patterns

### 1. Instruction Files Are Universal

Every tool uses markdown files for persistent instructions: CLAUDE.md, GEMINI.md, AGENTS.md. All support hierarchical loading (global → project → subdirectory). This is the **procedural memory** layer — human-authored, deterministic, loaded every session.

### 2. Automatic Memory Is the Differentiator

The major divide is between tools that **autonomously extract memories** (Claude Code, Codex) and those that require **explicit user action** (Gemini CLI) or **delegate to plugins** (OpenCode).

- **Claude Code**: Writes during the session, produces plain markdown files organized as an index + topic files. Simple, transparent, editable.
- **Codex**: Most sophisticated — two-phase background pipeline with SQLite state management, rollout extraction, consolidation sub-agent, memory pollution detection, watermark-based change tracking, and automatic forgetting. Also generates skills from memories.
- **Gemini CLI**: Minimal — `save_memory` tool appends a bullet to global GEMINI.md. No extraction, no consolidation, no forgetting.
- **OpenCode**: No native memory. Active community plugins (true-mem, opencode-mem) fill the gap.

### 3. Memory Formation Timing

Two modes emerge across all sources:

- **Hot path / conscious** (LangMem term): Memory formed during conversation. Claude Code does this. Adds latency but enables immediate context.
- **Background / subconscious** (LangMem term): Memory formed after conversation. Codex does this exclusively. No latency impact, deeper analysis, but delayed availability.

### 4. Storage Convergence on Markdown

All tools that implement memory use markdown as the storage format. Even Codex, which uses SQLite for state management, outputs markdown files (`MEMORY.md`, `memory_summary.md`, `rollout_summaries/*.md`). This reflects a design preference for human-inspectable, version-controllable, LLM-readable artifacts.

### 5. Memory Pollution and Quality Control

Codex introduces a unique concept: **memory pollution**. If a session uses web search or MCP tools, the thread is marked "polluted" and excluded from memory extraction. Previously extracted memories from that thread trigger a forgetting pass. No other coding CLI implements this.

## Points of Disagreement

- **Scope of saved memories**: Claude Code is project-scoped; Gemini CLI's `save_memory` is global-only. Neither is clearly better — it depends on whether knowledge is project-specific or personal.
- **Consolidation necessity**: Codex invests heavily in consolidation (Phase 2 agent); Claude Code relies on the agent self-organizing during sessions. The academic literature (EmergentMind) emphasizes consolidation as critical for long-term quality.
- **Forgetting**: Only Codex implements automatic forgetting. The academic literature strongly advocates for it (memory overload, error propagation). Claude Code and Gemini CLI rely on manual editing.

## Gaps

- **No tool implements episodic memory as described in LangMem/academic literature**: structured episodes with observation/thoughts/action/result. Codex's rollout summaries are closest but lack the structured schema.
- **No tool implements the academic "memory relevance = similarity + importance + strength" model**. Codex ranks by usage count and recency, which approximates strength but not importance.
- **Cross-agent memory sharing**: The academic literature describes multi-agent memory with access control (MIRIX, Collaborative Memory). No coding CLI implements shared memory across agents/sessions natively.
- **No tool addresses memory eviction budgets** or size limits beyond Claude Code's 200-line MEMORY.md index cap.
- **Procedural memory evolution** (LangMem's prompt optimizer) has no equivalent in any coding CLI — instructions are static unless manually edited.

## Sources

- `langmem-conceptual-guide` — LangMem conceptual guide: semantic/episodic/procedural taxonomy, collection vs. profile patterns, hot path vs. background formation
- `claude-code-memory` — Claude Code official docs: CLAUDE.md hierarchy, auto memory with MEMORY.md + topic files, 200-line limit, rules directory
- `codex-memory-system` — DeepWiki analysis of Codex internals: two-phase pipeline, SQLite state, rollout extraction, consolidation sub-agent, memory pollution, forgetting
- `gemini-cli-memory` — Gemini CLI docs: GEMINI.md hierarchy, save_memory tool, append-only fact storage
- `opencode-rules-context` — OpenCode docs + community: AGENTS.md instructions, no native memory, third-party plugin ecosystem
- `emergentmind-memory-taxonomy` — EmergentMind research survey: full taxonomy (scope, paradigm, composition, integration), A-MEM, HiAgent, MIRIX, consolidation/decay models
