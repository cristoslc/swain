# Synthesis — Cog Cognitive Architecture

## Key Findings

Cog is a convention-only cognitive architecture for Claude Code that achieves persistent memory, self-reflection, and strategic foresight using nothing but markdown files and CLAUDE.md instructions. It represents a fully realized implementation of the "instructions-as-architecture" pattern — no runtime, no server, no application code.

### Memory Architecture

- **Three-tier hot/warm/glacier model** with progressive condensation (observations → patterns → hot-memory). Similar conceptually to swain's artifact lifecycle but applied to personal/work memory rather than development artifacts.
- **L0/L1/L2 tiered retrieval** inspired by OpenViking — every file has a one-line `<!-- L0: ... -->` summary enabling scan-before-read. This is a concrete implementation of progressive context loading.
- **SSOT enforcement** — each fact lives in exactly one canonical file; other files use `[[wiki-links]]`. Housekeeping and reflect both enforce this.
- **Threads (Zettelkasten layer)** — when a topic recurs 3+ times across 2+ weeks, it gets "raised" into a dedicated synthesis file with Current State / Timeline / Insights spine. Threads grow indefinitely and are never condensed.

### Pipeline / Self-Improvement

- **Four pipeline skills** with strict boundaries: `/housekeeping` (structural maintenance), `/reflect` (pattern extraction from session transcripts), `/evolve` (architecture-level rule changes), `/foresight` (cross-domain strategic nudges).
- **Evolve is meta-level** — it changes the rules that govern how other skills work, but never touches memory content directly. This separation of concerns (content vs. rules vs. architecture) is a notable design pattern.
- **Scenario simulation** — `/scenario` models decision branches with timeline overlays against the real calendar, canary signals, and contingency mappings. Calibrated against past prediction accuracy.
- **Session transcript ingestion** — `/reflect` reads Claude Code's JSONL session files via a cursor, enabling it to mine past conversations for missed cues, broken promises, and memory gaps.

### Domain Routing

- Conversational `/setup` generates `domains.yml`, memory directories, and domain-specific slash commands from a natural conversation about the user's life and work.
- Domain types: personal (always one), work, side-project, system (cog-meta, auto-created).
- Each domain skill loads only its own memory files, with a shared template.

### Notable Design Patterns

1. **Briefing bridge** — housekeeping writes `briefing-bridge.md` as a handoff artifact for foresight to consume. Clean producer-consumer coupling between pipeline stages.
2. **Entity registry format** — strict 3-line compact format per entity (name/facts/status), with heavy entries promoted to dedicated thread files.
3. **Temporal validity markers** — `(since YYYY-MM)` / `(until YYYY-MM)` on facts, with housekeeping auto-striking expired facts.
4. **Pattern routing** — core patterns (universal, ≤70 lines) vs. satellite patterns (domain-specific, ≤30 lines each), loaded contextually.
5. **Glacier archival with YAML frontmatter** — archived data is searchable via a generated index without reading full files.

## Points of Agreement with Swain

- Convention-driven architecture (CLAUDE.md / AGENTS.md as the source of truth)
- Artifact lifecycle management (though Cog's is memory-focused, swain's is development-focused)
- Self-improvement loops (Cog's evolve ≈ swain's retro + doctor)
- Strict file ownership between skills/pipeline stages

## Points of Disagreement / Different Approaches

- **No task tracking system** — Cog uses simple `action-items.md` with checkboxes rather than an external task manager (swain uses `tk`)
- **No artifact graph** — Cog's memory is flat (domain directories) rather than hierarchical (Vision → Initiative → Epic → Spec)
- **Personal life scope** — Cog is designed for personal + work memory; swain is development-focused
- **Self-modification** — Cog's `/evolve` can change its own rules directly; swain treats skill changes as code changes requiring worktree isolation
- **No version control integration** — Cog doesn't use commit hashing for artifact pinning (swain's dual-commit pattern)

## Gaps

- No test or validation framework for the conventions themselves
- No migration path for schema changes (what happens when CLAUDE.md conventions evolve?)
- No multi-user or team collaboration model
- No security model beyond `.gitignore` for sensitive data
- Pipeline scheduling depends on external cron or manual invocation
- No mechanism to detect when conventions are being violated (beyond evolve's manual audit)

## Relevance to Swain

Cog is the closest comparable system to swain's approach of using plain-text conventions for AI agent architecture. Key differences: Cog targets personal cognitive augmentation, swain targets development workflow governance. The L0/L1/L2 retrieval protocol, briefing bridge pattern, and entity registry format are design patterns worth studying. The `/evolve` self-modification loop raises interesting questions about skill change discipline that swain addresses differently (worktree isolation).
