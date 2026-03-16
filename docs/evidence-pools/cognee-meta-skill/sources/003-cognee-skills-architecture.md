---
source-id: "003"
title: "cognee-skills Python Architecture — Models, Pipeline, Router, and Client"
type: local
path: "cognee/cognee_skills/"
url: "https://github.com/topoteretes/cognee/tree/demo/graphskill_COG-4178/cognee/cognee_skills"
fetched: 2026-03-15T21:05:00Z
hash: "sha256:placeholder"
---

# cognee-skills Python Architecture

Comprehensive analysis of the implementation code across models, pipeline, client, parser, retrieve, execute, observe, inspect, amendify, and preview_amendify modules.

## Module Overview

### `__init__.py` — Public API surface

Exports two tiers:
- **High-level**: `Skills` class (singleton `skills`), with methods: `ingest()`, `ingest_meta_skill()`, `upsert()`, `remove()`, `get_context()`, `load()`, `run()`, `execute()`, `list()`, `observe()`, `inspect()`, `preview_amendify()`, `amendify()`, `rollback_amendify()`, `evaluate_amendify()`, `auto_amendify()`
- **Low-level**: Direct function imports for custom pipelines

### Models (DataPoint subclasses — stored in graph)

**Skill**: Core entity. Fields: `skill_id`, `name`, `description`, `instructions` (full markdown body, stored not indexed), `instruction_summary` (LLM-generated, indexed), `triggers`, `tags`, `complexity` (simple/workflow/agent), `task_pattern_candidates`, `tools`, `source_path`, `content_hash`, `resources`, `related_skills`, `solves` (edge to TaskPattern).

Key design: parser-derived fields (`description_raw`, `triggers_raw`, `tags_raw`) are preserved separately from LLM-enriched fields to maintain provenance.

**TaskPattern**: Normalized intent categories. Fields: `pattern_id`, `text` (LLM-generated), `category`, `source_skill_ids`, `examples`, `prefers` (edge to Skill with learned weight).

**SkillRun**: Execution record. Fields: `run_id`, `session_id`, `task_text`, `result_summary`, `success_score` (0.0-1.0), `candidate_skills` (routing decision trace), `selected_skill_id`, `task_pattern_id`, `tool_trace` (ToolCall list), `error_type`, `latency_ms`, `feedback`.

**SkillInspection**: Failure diagnosis. Fields: `failure_category` (instruction_gap/ambiguity/wrong_scope/tooling/context_missing/other), `root_cause`, `severity` (low/medium/high/critical), `improvement_hypothesis`, `analyzed_run_count`, `avg_success_score`, `inspection_confidence`.

**SkillAmendment**: Proposed/applied fix. Fields: `amendment_id`, `original_instructions`, `amended_instructions`, `change_explanation`, `expected_improvement`, `status` (proposed/applied/rolled_back/rejected), `amendment_confidence`, `pre_amendment_avg_score`, `post_amendment_avg_score`.

**SkillChangeEvent**: Audit trail. Fields: `skill_id`, `change_type` (added/updated/removed/amended/rolled_back), `old_content_hash`, `new_content_hash`, `at` (Timestamp).

### Parser (`parser/skill_parser.py`)

Multi-format support: Anthropic agent-skills spec, OpenClaw skills, muratcankoylan convention.

Entry file discovery: `SKILL.md → skill.md → Skill.md → README.md`

Frontmatter extraction with aliases:
- Name: `name`, `title`, `skill_name`, `skill-name`
- Description: `description`, `summary`, `short_description`, `about`
- Tags: `tags`, `categories`, `keywords`, `labels` (also OpenClaw `metadata.openclaw.tags`)
- Triggers: `triggers`, `activation` (also `## When to Activate` body section, quoted phrases in description)
- Tools: `allowed-tools`, `allowed_tools`

Complexity detection from body keywords: "subagent/multi-step/agent loop" → agent, "workflow/pipeline/step 1" → workflow, else simple.

Resource scanning: classifies bundled files as script/reference/asset/other.

### Pipeline (`pipeline.py`)

Ingestion: `parse → enrich (LLM) → materialize_task_patterns → apply_node_set → add_data_points → index_graph_edges`

Upsert: Content-hash comparison. Unchanged → skip, changed → delete old + re-ingest, removed → delete from graph AND vector. Emits SkillChangeEvents.

### Retrieval (`retrieve.py`)

Two-stage semantic search:
1. Vector search over `Skill_instruction_summary` (semantic candidates)
2. Vector search over `TaskPattern_text` (query-relevant patterns)

Blending: `final_score = (1 - prefers_boost) * vector_score + prefers_boost * prefers_score`

Prefers score: `max over matched patterns of (pattern_sim * weight)` — learned from execution history.

### Execution (`execute.py`)

System prompt template injects skill name + instructions. Uses litellm for model-agnostic LLM calls.

Output evaluation: Second LLM call scores output 0.0-1.0 on task usefulness (not instruction-following). This is key — the evaluator explicitly ignores whether the output follows instructions, scoring only human-perceived helpfulness.

### Observe (`observe.py`)

Records SkillRun to graph. Updates TaskPattern → Skill `prefers` edge weight incrementally: running average of success scores.

### Inspect (`inspect.py`)

Loads failed runs (success_score < threshold). Sends skill instructions + formatted failure records to LLM. Returns structured InspectionResult with failure_category, root_cause, severity, improvement_hypothesis. Persists as SkillInspection node.

### Preview Amendify (`preview_amendify.py`)

Takes inspection + current instructions. LLM generates complete amended instructions (not a diff). Persists as SkillAmendment with status="proposed". Original instructions preserved in amendment node.

### Amendify (`amendify.py`)

Applies proposed amendment: updates Skill node, re-runs enrichment pipeline, emits SkillChangeEvent. Optional: write to disk, validate by executing.

Rollback: restores original instructions from amendment node, re-enriches, emits change event.

Evaluate: compares pre/post amendment success scores using SkillRun timestamps vs applied_at_ms.

### Client (`client.py`)

`Skills` class orchestrates the full loop:
- `run()`: get_context → execute (auto_observe + auto_evaluate) → auto_amendify on failure
- `execute()`: load → execute_skill → evaluate_output → record_skill_run → auto_amendify
- `auto_amendify()`: inspect → preview_amendify → amendify in one call
- `_resolve_pattern()`: vector search to find best TaskPattern for a query
