---
title: "Swain Skill Cognitive Load Classification"
artifact: SPIKE-014
status: Complete
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
question: "Which swain skill operations belong to which cognitive load tier (heavy / analysis / lightweight), and what reasoning effort level is appropriate for each?"
gate: Pre-EPIC-007-specs
risks-addressed:
  - Over-classifying lightweight work as heavy increases cost and latency unnecessarily
  - Under-classifying heavy work as analysis degrades output quality on the most important decisions
  - Some skills contain mixed-tier operations — classification must be at the operation level, not just skill level
linked-artifacts:
  - EPIC-007
  - SPIKE-013
evidence-pool: ""
---

# Swain Skill Cognitive Load Classification

## Question

Which swain skill operations belong to which cognitive load tier (heavy / analysis / lightweight), and what reasoning effort level is appropriate for each?

## Go / No-Go Criteria

**Go:** A complete classification table mapping each swain skill (and significant sub-operations within skills) to: (a) tier (heavy / analysis / lightweight), (b) recommended model for Claude Code (Opus / Sonnet / Haiku), (c) reasoning effort (extended-thinking on/off, budget hint), and (d) rationale.

**No-Go:** Operations within a single skill span multiple tiers in a way that cannot be statically annotated at the skill level. In that case, produce a per-operation annotation plan and flag which skills need internal routing logic.

## Pivot Recommendation

If no-go on static skill-level annotation: design sub-operation annotation blocks within SKILL.md (e.g., section-level `<!-- model: opus -->` hints) and have skill-creator insert them at the section level rather than the file level.

## Classification seed (to validate during investigation)

| Tier | Examples |
|------|---------|
| Heavy (Opus + extended thinking) | swain-design artifact creation, SPIKE investigation, ADR drafting, EPIC decomposition, swain-search evidence gathering, skill-creator |
| Analysis (Sonnet) | swain-status, swain-doctor, specgraph queries, swain-do task management, adr-check, spec-verify, swain-push |
| Lightweight (Haiku) | swain-stage layout/pane ops, swain-session tab naming and bookmarks, swain-keys key provisioning |

## Findings

### Verdict: NO-GO on static skill-level annotation

Three skills (swain-design, swain-do, swain-help) contain operations spanning multiple tiers. Static skill-level classification would either over-provision lightweight operations or under-provision heavy ones. The pivot recommendation applies: per-operation annotation within SKILL.md.

### Complete Classification Table

| Skill | Operation | Tier | Model | Effort | Rationale |
|-------|-----------|------|-------|--------|-----------|
| **swain** | Route to sub-skill | Lightweight | Haiku | low | Pattern match on keywords, no reasoning needed |
| **swain-design** | Artifact creation (Vision, Epic, Persona) | Heavy | Opus | high | Requires synthesis, brainstorming, multi-step document generation |
| **swain-design** | Artifact creation (Spec, Story, ADR) | Heavy | Opus | medium | Structured but requires understanding constraints and dependencies |
| **swain-design** | Artifact creation (Spike, Runbook, Design) | Analysis | Sonnet | medium | Template-driven with some judgment calls |
| **swain-design** | Phase transition | Analysis | Sonnet | low | Procedural — move directory, update fields, run scripts |
| **swain-design** | Index refresh | Lightweight | Haiku | low | Purely mechanical table update |
| **swain-design** | Specwatch/specgraph queries | Analysis | Sonnet | low | Read script output and present results |
| **swain-design** | ADR compliance check | Analysis | Sonnet | medium | Interpret findings, assess relevance |
| **swain-design** | Alignment check | Analysis | Sonnet | medium | Assess scope drift, goal alignment |
| **swain-design** | Audit (full) | Heavy | Opus | high | Deep cross-artifact analysis, pattern detection |
| **swain-search** | Evidence pool creation | Heavy | Opus | high | Web research, source evaluation, synthesis |
| **swain-search** | Pool extension/refresh | Analysis | Sonnet | medium | Incremental research, dedup |
| **swain-do** | Task creation/update | Analysis | Sonnet | low | CLI commands with context from spec |
| **swain-do** | Implementation plan creation | Heavy | Opus | high | TDD plan decomposition, dependency analysis |
| **swain-do** | Code implementation (per task) | Heavy | Opus | high | Actual code writing and testing |
| **swain-do** | Escalation/abandonment | Analysis | Sonnet | medium | Judgment about scope and direction |
| **swain-do** | Ready/status queries | Lightweight | Haiku | low | Run CLI, present output |
| **swain-push** | Stage + commit + push | Analysis | Sonnet | low | Diff analysis for commit message, scripted flow |
| **swain-release** | Changelog + version bump | Analysis | Sonnet | medium | Commit analysis, semantic versioning judgment |
| **swain-status** | Dashboard refresh | Analysis | Sonnet | low | Aggregate data sources, format output |
| **swain-doctor** | Health checks | Analysis | Sonnet | low | Run scripts, report findings, remediate |
| **swain-help** | Simple reference query | Lightweight | Haiku | low | Look up documented answer |
| **swain-help** | Conceptual explanation | Analysis | Sonnet | medium | Explain workflows, connect concepts |
| **swain-help** | Troubleshooting guidance | Heavy | Opus | medium | Diagnose novel problems, suggest approaches |
| **swain-session** | Tab naming, bookmarks | Lightweight | Haiku | low | String operations, file writes |
| **swain-session** | Preferences management | Lightweight | Haiku | low | Read/write settings file |
| **swain-stage** | Layout/pane management | Lightweight | Haiku | low | tmux commands, no reasoning |
| **swain-stage** | MOTD start/update | Lightweight | Haiku | low | Run script, write JSON |
| **swain-keys** | Key provisioning | Lightweight | Haiku | low | Run provisioning script, follow prompts |
| **swain-update** | Pull and reconcile | Analysis | Sonnet | low | Git operations, doctor invocation |
| **swain-init** | Project onboarding | Analysis | Sonnet | medium | Assess project state, configure governance |

### Mixed-Tier Skills (require internal routing)

| Skill | Tier Span | # Operations | Internal Routing Needed |
|-------|-----------|-------------|------------------------|
| **swain-design** | Heavy → Lightweight | 10 | Yes — creation vs transition vs index |
| **swain-do** | Heavy → Lightweight | 5 | Yes — plan creation vs status queries |
| **swain-help** | Heavy → Lightweight | 3 | Yes — troubleshooting vs lookup |

### Annotation Approach

Since static skill-level annotation fails for 3 skills, the recommended approach is **section-level hints** within SKILL.md:

```markdown
<!-- swain-model-hint: opus, effort: high -->
## Creating artifacts
...

<!-- swain-model-hint: sonnet, effort: low -->
## Phase transitions
...
```

The skill-creator tool would insert these hints during skill creation. The model routing layer (EPIC-007) would parse them and adjust the model/effort per the annotated section being invoked.

### Token Cost Estimates

Using approximate pricing ratios (Opus:Sonnet:Haiku = 15:3:1):

| Scenario | Heavy Ops | Analysis Ops | Light Ops | Relative Cost |
|----------|-----------|-------------|-----------|---------------|
| All Opus (current) | 15x | 15x | 15x | 100% |
| Tier-routed | 15x | 3x | 1x | ~45% |
| All Sonnet | 3x | 3x | 3x | 20% |

Tier-routing saves ~55% vs all-Opus while preserving quality where it matters. The heaviest operations (artifact creation, implementation planning, code writing) stay on Opus.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-13 | — | Initial creation |
