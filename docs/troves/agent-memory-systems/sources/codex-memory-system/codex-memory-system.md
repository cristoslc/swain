---
source-id: "codex-memory-system"
title: "OpenAI Codex Memory System — DeepWiki Analysis"
type: web
url: "https://deepwiki.com/openai/codex/3.7-memory-system"
fetched: 2026-03-23T00:00:00Z
hash: "8e86b6d010108c3bc6d4c9b84b2dc576aa74b8faa3813bb0b1d5f06b7db3ea1e"
---

# OpenAI Codex Memory System

The memory system builds a persistent, cross-session knowledge base by post-processing completed rollouts. It runs asynchronously in the background at startup.

## Two-Phase Pipeline Architecture

### Phase 1: Rollout Extraction

For each eligible rollout (completed conversation session), an LLM extracts a structured `raw_memory` and `rollout_summary`, stored in SQLite.

- **Claim startup jobs**: `claim_startup_jobs` with parameters from `MemoriesConfig`
- **Build request context**: resolves the extraction model
- **Run jobs in parallel**: bounded by `CONCURRENCY_LIMIT`
- **Per-job extraction**: Load rollout items from `.jsonl` file, filter to memory-relevant items, call model with structured output schema (`raw_memory`, `rollout_summary`, `rollout_slug`), redact secrets

Eligibility filters:
- Session must not be ephemeral
- Memory feature must be enabled
- Session must not be a sub-agent session
- State DB must be available
- `memory_mode = 'enabled'` (not disabled or polluted)
- Rollout within `max_rollout_age_days` and idle for `min_rollout_idle_hours`

### Phase 2: Global Consolidation

Serialized through a singleton global job. Only one consolidation runs at a time.

1. Syncs local filesystem artifacts (`raw_memories.md`, `rollout_summaries/`)
2. Spawns a dedicated consolidation sub-agent to update `MEMORY.md`, `memory_summary.md`, and `skills/`
3. Applies forgetting: for removed thread IDs, deletes only evidence supported by that thread

**Consolidation sub-agent** runs sandboxed:
- `approval_policy`: Never (auto-approved)
- `sandbox_policy`: WorkspaceWrite with codex_home as writable root, no network
- Collab feature disabled (prevents recursive delegation)

### Watermark Logic

Prevents re-running Phase 2 when there's no new data:
- `input_watermark` set when Phase 1 succeeds
- `last_success_watermark` set when Phase 2 succeeds
- Phase 2 only runs when `input_watermark > last_success_watermark`

## SQLite-Backed State

| Table | Purpose |
| --- | --- |
| `jobs` | Tracks Phase 1 and Phase 2 job state |
| `stage1_outputs` | Per-thread Phase 1 extraction results |
| `threads` | Thread registry; `memory_mode` controls eligibility |

### Thread Memory Modes

| Value | Meaning |
| --- | --- |
| `enabled` | Eligible for Phase 1 extraction |
| `disabled` | Excluded (set during `reset_memory_data_for_fresh_start`) |
| `polluted` | Contaminated (e.g., web search used); excluded and may trigger Phase 2 forgetting |

## Filesystem Layout

```
<codex_home>/memories/
├── MEMORY.md                        ← Consolidated handbook, structured by task group
├── memory_summary.md                ← Short user profile + tips; injected into system prompt
├── raw_memories.md                  ← Merged Phase 1 raw_memory fields, latest-first
├── rollout_summaries/
│   ├── <timestamp>-<hash>.md        ← Per-rollout summary (no slug)
│   └── <timestamp>-<hash>-<slug>.md ← Per-rollout summary (with slug)
└── skills/
    └── <skill-name>/
        └── SKILL.md                 ← Reusable procedure
```

## Configuration (`MemoriesConfig`)

| Field | Phase | Meaning |
| --- | --- | --- |
| `max_rollouts_per_startup` | 1 | Max Stage 1 jobs claimed per startup |
| `max_rollout_age_days` | 1 | Exclude rollouts older than this |
| `min_rollout_idle_hours` | 1 | Exclude rollouts updated more recently than this |
| `extract_model` | 1 | Model for extraction (optional override) |
| `max_raw_memories_for_consolidation` | 2 | Top-N stage-1 outputs to feed into Phase 2 |
| `max_unused_days` | 2 | Exclude memories not used within this window |
| `consolidation_model` | 2 | Model for the consolidation sub-agent |
| `no_memories_if_mcp_or_web_search` | Session | Disable memory generation if web/MCP used |

## Key Design Decisions

- **Asynchronous**: Memory extraction runs in the background at startup, not during conversation
- **SQLite-backed**: All state managed through SQLite with job claiming, leasing, and retry
- **Memory pollution**: Web search or MCP tool use marks a thread as "polluted," excluding it from memory extraction and triggering forgetting of any previously extracted memories from that thread
- **Consolidation agent**: Phase 2 uses a dedicated sub-agent with its own model and sandboxed environment
- **Forgetting**: Explicit removal of evidence from threads that are no longer in the top-N selection or have been polluted
- **Input selection ranking**: `usage_count DESC`, `last_usage / generated_at DESC`, `source_updated_at DESC`
