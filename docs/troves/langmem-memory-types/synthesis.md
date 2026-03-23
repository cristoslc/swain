# Synthesis: LangMem Memory Types

## Key Findings

LangMem's conceptual guide presents a three-type taxonomy for long-term memory in LLM applications, mapped from cognitive science:

### 1. Semantic Memory — Facts and Knowledge

Two storage patterns:

- **Collections**: Unbounded set of individually stored memories, searched at runtime via semantic similarity + importance + recency/frequency ("strength"). Requires reconciliation logic to avoid over-extraction (low precision) or under-extraction (low recall). LangMem provides a "memory enrichment" process that balances creation vs. consolidation.
- **Profiles**: A single, schema-constrained document per entity (user, agent). New information overwrites rather than appends. Best when only the latest state matters and when you want the user to be able to manually edit.

**Design tradeoff**: Collections maximize recall across many interactions; profiles maximize lookup speed and editability at the cost of information loss.

### 2. Episodic Memory — Past Experiences

Stores full interaction context — situation, reasoning, action, outcome — as structured episodes (observation/thoughts/action/result). Used to generate few-shot examples and learn from successful patterns. Distinct from semantic memory in that it preserves *process*, not just *facts*.

### 3. Procedural Memory — System Instructions

Starts as the system prompt, then evolves via a "prompt optimizer" that rewrites instructions based on conversation trajectories and user feedback. This is the only memory type that directly modifies agent behavior rather than providing retrieval context.

## Memory Formation Timing

Two modes:

- **Conscious (hot path)**: Memories formed during the conversation. Immediate but adds latency and cognitive load to the agent.
- **Subconscious (background)**: Memories formed after the conversation via asynchronous reflection. No latency impact, higher recall, but delayed availability.

## Integration Architecture

Two layers:

- **Core API** (stateless): `create_memory_manager` and `create_prompt_optimizer` — pure functions that transform memory state. No storage dependency.
- **Stateful layer** (LangGraph-dependent): `create_memory_store_manager` and memory tools that persist to LangGraph's `BaseStore`. Adds namespace-based organization and flexible retrieval (direct access, semantic search, metadata filtering).

## Gaps

- No discussion of memory **eviction** or **decay** strategies — only creation and consolidation.
- No explicit guidance on **memory size budgets** or how to handle memory stores that grow beyond useful retrieval thresholds.
- Procedural memory optimization (prompt rewriting) is presented as automatic, but no discussion of **guardrails** to prevent prompt drift or regression.
- The relationship between the three memory types at runtime (how they compose in a single agent) is implied but not explicitly architected.

## Sources

- `langmem-conceptual-guide` — LangMem conceptual guide documentation page
