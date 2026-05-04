---
title: "Reporting Format Library Design"
artifact: SPIKE-063
track: container
status: Proposed
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
question: "What output formats does swain need in a reporting format library, and how should the operator select them?"
gate: Pre-development
risks-addressed:
  - Operator overwhelm when too much artifact content needs review at once
  - Each reporting need gets its own one-off implementation instead of reusing shared formats
  - Format selection forces the operator to learn a taxonomy instead of using plain language
parent-initiative: INITIATIVE-005
linked-artifacts:
  - EPIC-022
  - SPIKE-024
  - EPIC-049
  - VISION-004
  - SPEC-163
evidence-pool:
---

# Reporting Format Library Design

## Summary

<!-- Populated when transitioning to Complete. -->

## Question

What output formats does swain need in a reporting format library, and how should the operator select them?

The operator needs different reports at different moments. Approving a batch of specs looks nothing like catching up on an overnight session. Checking an old ADR looks nothing like either. Each need calls for a different output shape. Today these are handled ad-hoc or not at all. A format library gives swain a small set of reusable templates for shaped output.

## Go / No-Go Criteria

**GO (build format library):**
- Evidence from existing artifacts maps to ≤8 distinct format clusters with clear borders
- Each format covers ≥2 real use cases found in the evidence — not guesses
- Plain phrases can pick the right format without the operator learning a taxonomy
- The library works as skill reference files (templates + selection logic) with no new infrastructure

**NO-GO (defer or simplify):**
- Use cases collapse to ≤2 formats, making a "library" pointless — just build those directly
- Format borders are so blurry that picking one is harder than writing one-off output
- The real bottleneck is gathering the right input, not shaping the output

## Pivot Recommendation

If NO-GO: fold the two main formats (likely postflight and digest) into their own epics (EPIC-022 and EPIC-049) as local details rather than a shared library.

## Investigation Areas

### 1. Evidence-driven format matrix

Mine existing artifacts for every case where the operator needed shaped output. Map each case onto the matrix:

| Axis | Values |
|------|--------|
| Temporal orientation | Retrospective / Current state / Prospective |
| Audience | Operator-as-decider / Operator-as-reviewer / Future-self |
| Purpose | Inform / Persuade / Decide |

**Known instances from artifact mining:**

| Evidence source | Use case | Time | Audience | Purpose |
|----------------|----------|------|----------|---------|
| EPIC-022 / SPIKE-024 | Post-completion context recovery: "what happened, what's next" | Present | Operator-as-decider | Inform + Decide |
| VISION-004 | Decision fatigue: surfaces everything, operator can't filter | Present | Operator-as-decider | Decide |
| SPEC-163 | Cross-session continuity: decision history across sessions | Past | Future-self | Inform + Persuade |
| Retro (2026-03-21) | Velocity so high operator can't track what changed | Past | Operator-as-reviewer | Inform |
| Superpowers retro design | Trust gap: approving output faster than grasping it | Past | Future-self | Persuade |
| SPEC-011 | Learnings evaporate between sessions | Past | Future-self | Inform |
| INITIATIVE-005 SC | "What needs my decision?" in <30 seconds | Present | Operator-as-decider | Decide |
| Operator request (2026-04-06) | 6 specs to approve — need a compressed decision surface | Future | Operator-as-decider | Decide |
| Operator request (2026-04-06) | Overnight session ran — need action digest | Past | Operator-as-reviewer | Inform |
| Operator request (2026-04-06) | Scoped README for a feature slice | Current | Future-self | Inform |
| Operator request (2026-04-06) | Should I undo this ADR? What was the impact? | Past | Future-self | Persuade |

**Task:** Group these into format clusters. Look for cells with ≥2 cases that share enough structure for one template. Name each cluster.

### 2. Format template definition

For each cluster identified in §1, define:

- **Name** — clear enough that the operator can ask for it by name ("give me a ___")
- **Required inputs** — what scope, artifacts, or time range the format needs
- **Sections** — what the output contains (structure, not exact wording)
- **Length constraint** — rough size target (3-5 lines? 1 page? open-ended?)
- **Existing analog** — closest thing today (postflight, retro, README, ADR, PRFAQ, changelog)

### 3. Format selection routing

How does operator intent map to a format?

- Can plain phrases pick the right format? ("catch me up" → digest, "approve these?" → decision brief, "how does auth work?" → overview)
- Must scope be stated, or can it come from session context?
- Is a default format needed for bare "report on X" requests? Which one?

### 4. Relationship to existing work

- **SPIKE-024 / EPIC-022:** Does the postflight join the library or stay on its own? If it joins, does SPIKE-024's scope change?
- **EPIC-049:** Session digests are one format. Does the library absorb SPEC-199 or sit beside it?
- **swain-retro:** Retro output is already shaped. Library format, or a separate system?
- **PRFAQ:** It targets an outside audience and aims to persuade. Is "outside audience" a real axis for swain, or is output always for the operator?

### 5. Implementation shape

- **Where do templates live?** Skill reference files (like existing templates)? A new `formats/` directory?
- **Who invokes them?** Any skill that writes output for the operator? A single "report" skill?
- **How are they rendered?** Jinja2 (like roadmap templates)? Markdown with section markers? LLM output shaped by a structural prompt?

## Findings

<!-- Populated during Active phase. -->

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-06 | c213c99 | Created from operator discussion; evidence pre-seeded from artifact mining |
