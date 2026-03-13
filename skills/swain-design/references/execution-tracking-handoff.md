# Execution Tracking Handoff

Artifact types fall into four tracking tiers based on their relationship to implementation work:

| Tier | Artifacts | Rule |
|------|-----------|------|
| **Implementation** | SPEC | Execution-tracking **must** be invoked when the artifact comes up for implementation — create a tracked plan before writing code |
| **Coordination** | EPIC, VISION, JOURNEY | Swain-design decomposes into implementable children first; swain-do runs on the children, not the container |
| **Research** | SPIKE | Execution-tracking is optional but recommended for complex spikes with multiple investigation threads |
| **Reference** | ADR, PERSONA, RUNBOOK, DESIGN | No execution tracking expected |

## The `swain-do` frontmatter field

Artifacts that need swain-do carry `swain-do: required` in their frontmatter. This field is:
- **Always present** on SPEC artifacts (injected by their templates)
- **Added per-instance** on SPIKE artifacts when swain-design assesses the spike is complex enough to warrant tracked research
- **Never present** on EPIC, VISION, JOURNEY, ADR, PERSONA, RUNBOOK, or DESIGN artifacts — orchestration for those types lives in the skill, not the artifact

When an agent reads an artifact with `swain-do: required`, it should invoke the swain-do skill before beginning implementation work.

When implementation begins on a SPEC, swain-design should keep the lifecycle state aligned with the real work:
- If the SPEC is not already in `In Progress`, transition it to `In Progress` before handing off implementation tracking.
- If that SPEC has a parent EPIC and the EPIC is not already Active, transition the parent EPIC to Active as well.
- Treat both transitions as idempotent: if either artifact is already in the target state, leave it unchanged.

## What "comes up for implementation" means

The trigger is intent, not phase transition alone. An artifact comes up for implementation when the user or workflow indicates they want to start building — not merely when its status changes.

- "Let's implement SPEC-003" → invoke swain-do
- "Move SPEC-003 to Ready" → phase transition only, no tracking yet
- "Fix SPEC-007 (type: bug)" → invoke swain-do
- "Let's work on EPIC-008" → decompose into SPECs first, then track the children

## Coordination artifact decomposition

When swain-do is requested on an EPIC, VISION, or JOURNEY:

1. **Swain-design leads.** Decompose the artifact into implementable children (SPECs) if they don't already exist.
2. **Swain-do follows.** Create tracked plans for the child artifacts, not the container.
3. **Swain-design monitors.** The container transitions (e.g., EPIC → Complete) based on child completion per the existing completion rules.
