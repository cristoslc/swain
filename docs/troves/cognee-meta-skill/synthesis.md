# Synthesis: cognee-meta-skill Evidence Pool

## What is cognee-skills?

cognee-skills is an open-source system from topoteretes that gives AI agent skills a **self-improvement loop**. Built on top of Cognee's knowledge graph engine, it treats SKILL.md files not as static documents but as **living entities** in a graph that evolve based on execution feedback. The meta-skill itself is a SKILL.md that teaches agents how to use the self-improvement toolset — making the system self-documenting. [001, 002]

## Key Findings

### 1. The Self-Improvement Loop is the Core Innovation

The central contribution is a closed-loop system: execute → score → diagnose → fix → verify → rollback. Every skill execution is scored 0.0-1.0 by a second LLM call that evaluates **task usefulness** (not instruction-following — a subtle but important distinction). When scores drop below a threshold, the system automatically inspects failures, generates improved instructions, and applies them — with full rollback capability. [001, 003]

The loop consists of six graph node types:
- **Skill** → instructions and metadata
- **TaskPattern** → normalized intents with learned `prefers` edge weights
- **SkillRun** → execution records with quality scores
- **SkillInspection** → LLM-generated failure diagnoses
- **SkillAmendment** → proposed/applied instruction changes (original always preserved)
- **SkillChangeEvent** → temporal audit trail [002, 003]

### 2. Routing Uses Hybrid Vector + Graph Signals

Unlike Claude Code's native skill routing (pure LLM reasoning over descriptions), cognee-skills uses two-stage retrieval:
1. Vector search over `Skill_instruction_summary` for semantic candidates
2. Vector search over `TaskPattern_text` for query-relevant patterns
3. Graph-based `prefers` weights (learned from execution history) boost the final score

The blending formula: `final = (1 - boost) * vector_score + boost * prefers_score` where prefers_score is `max(pattern_sim * weight)` over matched patterns. This means skills that have historically succeeded on similar tasks get routing preference — the system literally learns which skills to prefer. [003]

### 3. The Parser is Intentionally Tolerant

The skill parser supports multiple community formats (Anthropic, OpenClaw, muratcankoylan) with extensive alias handling for frontmatter fields. It tries `SKILL.md → skill.md → Skill.md → README.md`. Missing frontmatter is acceptable — the LLM enrichment step fills gaps. This design prioritizes ecosystem compatibility over strict schemas. [003]

### 4. Four Integration Paths

cognee-skills can be used via: (a) Claude Code / MCP IDEs with zero code, (b) Python SDK for custom workflows, (c) CLI for terminal/CI, (d) MCP programmatically for custom agents. All four expose the same capabilities. [002]

### 5. Anthropic's Official Skill Testing Framework (skill-creator)

Anthropic released skill-creator enhancements (March 2026) that bring evals, benchmarking, and description tuning to SKILL.md authoring — no coding required. [017]

**Two skill categories with different testing needs:**
- **Capability uplift skills** encode techniques beyond the base model. Evals detect when model improvements make them obsolete.
- **Encoded preference skills** sequence existing capabilities per team process. Evals verify fidelity to the actual workflow.

**Key capabilities:**
- **Evals**: Test prompts + expected-output descriptions. Skill-creator reports pass/fail. Example: the PDF skill's non-fillable form bug was isolated and fixed via evals.
- **Benchmark mode**: Standardized assessment tracking pass rate, elapsed time, and token usage. Runnable after model updates or skill iterations. Results are local — storable, dashboardable, CI-integrable.
- **Multi-agent parallel eval**: Independent agents run evals concurrently in clean contexts. No cross-contamination from accumulated context.
- **Comparator agents**: Blind A/B comparison between two skill versions, or skill vs. no skill. Judges don't know which output came from which version.
- **Description tuning**: Analyzes skill descriptions against sample prompts, suggests edits to reduce false positives and false negatives. Improved triggering on 5/6 public document-creation skills.

**Forward-looking insight**: As models improve, SKILL.md may evolve from "implementation plan" (how to do it) to "specification" (what to do). Evals already describe the "what" — eventually, that description may *be* the skill itself. [017]

## Points of Agreement

- **Skills need feedback loops**: Both cognee-skills and the broader skills ecosystem recognize that static instructions degrade over time. The Anthropic skill-creator adds eval-based quality testing and description optimization; cognee-skills extends this to runtime self-repair. [004, 007, 017]
- **SKILL.md as the interchange format**: All sources agree on SKILL.md with YAML frontmatter as the standard. cognee-skills consumes the same format but adds a graph persistence layer on top. [001, 004, 007]
- **Progressive disclosure matters**: Both Claude Code's native architecture and cognee-skills use lazy loading — metadata first, full instructions only when needed. [004, 003]
- **Testing separates "seems to work" from "known to work"**: Both Anthropic's eval framework and cognee-skills' execution scoring aim to provide objective quality signals rather than relying on subjective assessment. [017, 003]

## Points of Disagreement

- **Where intelligence lives**: Claude Code's native skills put all routing intelligence in the LLM (pure reasoning over descriptions). cognee-skills argues this is insufficient — you need learned preferences from execution history to route well. Anthropic's skill-creator approaches routing from the description-tuning side rather than learned weights. Neither approach has published head-to-head benchmarks. [004, 003, 017]
- **Evaluation scope**: cognee-skills evaluates output usefulness via a second LLM call on every run. Anthropic's skill-creator uses evals as an authoring-time tool (run manually or in CI), not a runtime feedback loop. The cognee approach is more automatic but adds latency; the Anthropic approach is lighter but requires author initiative. [003, 017]
- **Graph vs file as source of truth**: cognee-skills stores the "real" skill in the graph (amendments update the graph node, not necessarily the SKILL.md file). The rest of the ecosystem treats the file as the source of truth. This creates potential divergence — the graph can evolve away from the file on disk. [003]

## Gaps

1. **No benchmarks for the self-improvement loop itself**: How often does amendify actually improve skills vs. make them worse? What's the rollback rate in practice? The test_sdk.py demo uses a deliberately broken skill — real-world failure modes are more subtle.
2. **Multi-agent coordination**: The `prefers` edge updates are not concurrency-safe in the current implementation. Multiple agents executing the same skill could produce race conditions on weight updates.
3. **Evaluation model reliability**: The quality evaluator uses the same LLM config as execution. If the evaluator is unreliable, the entire improvement loop could amplify noise rather than signal.
4. **No cross-session learning for routing**: While `prefers` weights persist in the graph, there's no mechanism to transfer learned preferences between different cognee instances or share them across teams.
5. **SKILL.md ↔ graph drift**: When amendify changes instructions in the graph but doesn't write to disk (the default), the file and graph diverge. There's no reconciliation mechanism for this drift.
6. **Bridging cognee and skill-creator**: cognee-skills does runtime self-improvement; Anthropic's skill-creator does authoring-time eval + description tuning. A combined approach — using skill-creator evals as the scoring function for cognee's amendment loop — is an obvious but unexplored integration point. [003, 017]
7. **Eval portability**: Anthropic's skill-creator evals are described as local/storable but the exact format and schema for eval definitions isn't documented in the blog post. Whether cognee-skills could consume them as scoring criteria is unclear.

## Raw Source Coverage (added 2026-03-15)

Sources 008-016 contain the verbatim Python source code from `cognee/cognee_skills/` on branch `demo/graphskill_COG-4178`. This provides complete code-level reference for:

| Source | Module(s) | Key elements |
|--------|-----------|-------------|
| 008 | `client.py` | `Skills` class — `run()`, `execute()`, `auto_amendify()`, `_resolve_pattern()` |
| 009 | `execute.py` + `observe.py` | LLM execution via litellm, output evaluation prompt, `prefers` edge weight updates |
| 010 | `inspect.py` + `preview_amendify.py` + `amendify.py` | Failure diagnosis, amendment generation, apply/rollback/evaluate |
| 011 | `pipeline.py` + `retrieve.py` | Ingestion pipeline, content-hash upsert, hybrid vector+graph retrieval |
| 012 | `parser/skill_parser.py` | Multi-format parser with alias resolution, resource scanning, complexity detection |
| 013 | `models/` | All DataPoint subclasses (Skill, TaskPattern, SkillRun, SkillAmendment, etc.) |
| 014 | `tasks/` | Pipeline stages: parse, LLM enrich, TaskPattern materialization, node set tagging |
| 015 | `__init__.py` + `utils.py` + `example.py` | Public API surface, SkillChangeEvent factory, closed-loop demo |
| 016 | `tests/` | Unit tests for parser, execute, inspect, amendify — documents expected behavior |

These sources complement the analytical summary in source 003 by providing the actual implementation code for direct reference and code-level comparison.

## Anthropic skill-creator (added 2026-03-16)

Source 017 covers Anthropic's official skill-creator enhancements — the first-party tooling for testing, benchmarking, and improving SKILL.md files. This provides the "official" counterpart to cognee-skills' third-party self-improvement approach.
