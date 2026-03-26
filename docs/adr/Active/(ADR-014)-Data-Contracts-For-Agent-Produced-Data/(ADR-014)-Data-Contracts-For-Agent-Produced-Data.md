---
title: "Data Contracts For Agent-Produced Data"
artifact: ADR-014
track: standing
status: Active
author: cristos
created: 2026-03-21
last-updated: 2026-03-21
linked-artifacts:
  - ADR-013
  - EPIC-029
depends-on-artifacts: []
evidence-pool: "data-contract-standards"
---

# Data Contracts For Agent-Produced Data

## Context

Swain skills produce structured data that downstream templates consume. The changelog pipeline is the first example: the agent classifies git commits into a JSON structure, and a Jinja2 template renders it to markdown. The problem is that the agent's interpretation rules — what each field *means*, what constitutes good vs bad data, where the data comes from — are scattered across SKILL.md prose. When the agent misclassifies (e.g., putting artifact state transitions into the "roadmap" bucket instead of forward-looking previews), the only feedback is a human noticing the rendered output looks wrong.

Research into established data contract standards (ODCS v3.1.0, datacontract.com spec v0.9.0, OpenMetadata Data Contract entity) surfaced a common three-layer pattern:

1. **Schema** — structural contract (field names, types, shapes)
2. **Semantics** — meaning contract (what each field represents, per-field interpretation rules)
3. **Quality** — correctness contract (rules, anti-patterns, examples that distinguish good from bad data)

All three standards also track **source lineage** (where the data comes from) and **ownership** (who produces/consumes it). The standards diverge on scope: ODCS and datacontract.com are enterprise-grade with SLAs, pricing, infrastructure. OpenMetadata is the only one with an explicit `semantics` field per column — closest to what we need.

None of the standards address our specific use case: an **LLM agent** as the data producer, where the "quality rules" are really **interpretation guidance** that shapes how the agent reasons about classification. The agent isn't running SQL queries against a warehouse — it's reading commit messages and deciding what bucket they belong in. The contract needs to tell it *how to think about each field*, not just what type it is.

## Decision

**Define a lightweight data contract format for agent-produced data products.** Each contract is a YAML file that lives alongside the template it governs. The contract is the single source of truth for both the agent (producer) and the template (consumer).

### Contract structure

```yaml
# <product>-contract.yaml
kind: DataContract
version: "1.0"

product:
  name: release-changelog
  owner: swain-release
  description: >
    Structured changelog data for human-readable release notes.

source:
  description: How to obtain the raw input data
  # Free-form — each product defines its own source shape

schema:
  <field-name>:
    type: <json-type>          # string, array, object, etc.
    items: <item-schema>       # for arrays: what each element looks like
    required: <bool>           # whether the field must be present

    semantic: >                # WHAT this field means — one sentence
      <interpretation rule>

    source: >                  # WHERE the data comes from
      <lineage description>

    quality:                   # HOW to produce good data
      rules:
        - <affirmative rule>
      anti-patterns:
        - pattern: <what bad data looks like>
          why: <why it's bad>
      examples:
        good:
          - value: <example>
            why: <why it's good>
        bad:
          - value: <example>
            why: <why it's bad>
```

### Three-layer design

**Schema layer** — structural types and shapes. Validates that the JSON is well-formed. This is the layer that JSON Schema covers.

**Semantic layer** — per-field `semantic` and `source` fields. Tells the agent what each field *means* and where its data comes from. This is the layer that SKILL.md prose currently handles poorly because it's not scoped to individual fields. The semantic field is the single most important line in the contract — it's the interpretation rule the agent applies when classifying data.

**Quality layer** — per-field `quality` block with rules, anti-patterns (with `why`), and examples (good and bad, with `why`). This is the layer that was completely missing. Anti-patterns with explanations are critical because they prevent the agent from repeating known mistakes. The `why` field on each anti-pattern and example is load-bearing — without it, the agent can't generalize to novel cases.

### Why `why` is mandatory on anti-patterns and examples

An anti-pattern without a reason is a brittle rule. "Don't put EPIC-029 activated in roadmap" teaches the agent to avoid that exact string. "Don't put artifact state transitions in roadmap — *because the reader doesn't know what EPIC-029 is and doesn't care about internal tracking bookkeeping*" teaches the agent to recognize the *category* of mistake. The `why` field is what makes the contract generalize.

### Contract consumption workflow

1. Agent reads the contract file before producing data
2. For each field, agent applies: semantic (what am I filling?), source (where do I look?), quality (what does good data look like?)
3. Agent produces JSON conforming to the schema
4. (Optional) A validation script checks structural conformance and simple quality rules (regex-matchable anti-patterns)
5. Jinja2 template renders the validated JSON to the output format

### File naming and placement

Contracts live next to their consumers:
- `skills/swain-release/changelog-contract.yaml` governs `skills/swain-release/templates/changelog.md.j2`
- Future data products follow the same pattern: `<skill>/contracts/<product>-contract.yaml`

## Alternatives Considered

### A. JSON Schema with `description` fields

Use standard JSON Schema with per-field `description` containing the interpretation rules.

**Pros:**
- Standard format, IDE autocompletion, existing validation tools
- Per-field scoping via `description`

**Cons:**
- `description` is a single string — can't structure rules vs anti-patterns vs examples
- No standard way to express quality rules or source lineage
- Validation tooling checks types, not semantic quality
- Would need to be extended so far beyond standard JSON Schema that it's effectively a custom format anyway

### B. Adopt ODCS or datacontract.com verbatim

Use an established standard as-is.

**Pros:**
- Community-maintained, tooling ecosystem (datacontract-cli)
- Established credibility

**Cons:**
- Designed for data warehouse/streaming contracts, not LLM-agent-produced data
- ODCS requires sections we'll never use (SLA, pricing, infrastructure, servers)
- Neither has the semantic-per-field granularity we need
- Neither has anti-patterns with `why` — the critical feature for agent guidance
- Adopting a heavyweight standard for a lightweight use case adds complexity without value

### C. Keep rules in SKILL.md prose

Status quo — scatter interpretation rules across the skill's markdown instructions.

**Pros:**
- No new files or formats to maintain
- Agent reads SKILL.md anyway

**Cons:**
- Rules aren't scoped to fields — the agent reads a wall of prose and must mentally map "this rule applies to the roadmap array"
- No structure for anti-patterns vs examples vs rules
- Feedback loop is slow — human notices bad output, edits SKILL.md, hopes the agent reads it differently next time
- Can't be validated programmatically

## Consequences

**Positive:**
- Per-field interpretation rules give the agent scoped guidance instead of unstructured prose
- Anti-patterns with `why` prevent known mistakes and generalize to novel cases
- Contract file is the single source of truth — SKILL.md references it instead of duplicating rules
- Contracts are version-controlled, diffable, and reviewable
- Same format can govern any agent-produced data product (not just changelogs)
- Optional validation script can catch structural and pattern-matchable quality issues before rendering

**Accepted downsides:**
- New file format to maintain (though simpler than any established standard)
- Agent must read one more file before producing data (minimal token cost)
- No ecosystem tooling — we build our own validation if needed
- Format may evolve as we apply it to more data products beyond changelogs

**Constraints imposed:**
- Every agent-produced structured data pipeline must have a contract file
- SKILL.md instructions must reference the contract rather than duplicating interpretation rules
- Anti-patterns and examples must include `why` — entries without explanations are incomplete

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-21 | -- | Adopted; informed by ODCS, datacontract.com, OpenMetadata research |
