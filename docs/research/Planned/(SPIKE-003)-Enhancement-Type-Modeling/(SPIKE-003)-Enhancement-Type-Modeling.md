---
title: "Enhancement Type Modeling"
artifact: SPIKE-003
status: Planned
author: cristos
created: 2026-03-11
last-updated: 2026-03-11
question: "Should swain-design add a new ENHANCEMENT artifact type (parallel to BUG), or should SPECs gain a type discriminator field (type = epic | bug | enhancement)?"
gate: Pre-Implementation
risks-addressed:
  - Wrong abstraction leads to process overhead that defeats the purpose of lightweight enhancements
  - Type proliferation makes the artifact model harder to learn and maintain
depends-on: []
linked-research:
  - EPIC-002
evidence-pool: ""
---

# Enhancement Type Modeling

## Question

Should swain-design add a new ENHANCEMENT artifact type (parallel to BUG), or should SPECs gain a `type` discriminator field (type = epic | bug | enhancement)?

### Context

Today's artifact model has two extremes for implementation work:
- **BUG**: Small, one-off defect fix. Scoped to a single problem, usually touches a narrow area of code.
- **SPEC**: Full feature specification with acceptance criteria, implementation plan, verification gate. Designed for substantial work.

The gap: small improvements that aren't bugs. Examples: "add a `--compact` flag to swain-status", "support YAML frontmatter in evidence pool manifests", "make specwatch detect orphaned pain point references". These are bigger than a bug fix (may touch multiple stories, need some design thought) but smaller than a full spec (don't warrant acceptance criteria, verification gates, or formal implementation plans).

### The Two Approaches

**Option A: New ENHANCEMENT type**
- Parallel to BUG — lightweight lifecycle (Draft → Approved → Implemented → Verified?)
- Own template, own folder (`docs/enhancement/`)
- Can reference parent epic and linked stories
- `swain-do: required` in frontmatter (like BUG and SPEC)

**Option B: SPEC type discriminator**
- Add `type: epic | bug | enhancement` field to SPEC frontmatter
- Enhancement-typed SPECs get a simplified lifecycle (skip Testing phase? lighter acceptance criteria?)
- No new artifact type — reuse SPEC infrastructure
- Could also retroactively classify existing specs

## Go / No-Go Criteria

**Go for Option A (new type)** if:
- Enhancement lifecycle differs meaningfully from both BUG and SPEC (different phases, different gates, different decomposition rules)
- The overhead of a new type (template, definition, folder, index, specgraph support) is justified by the frequency of enhancement work items

**Go for Option B (discriminator)** if:
- Enhancement lifecycle is close enough to SPEC that a lighter variant works (same phases, just fewer required sections)
- Adding a type field to SPEC is simpler and avoids type proliferation

**No-go (defer)** if:
- The use cases are too varied to model with a single approach — revisit after more real-world examples accumulate

## Pivot Recommendation

If neither option is clean, consider a third path: keep BUG but broaden its semantics to cover "small changes" (not just defects). Rename it to PATCH or CHANGE, with a `kind: bug | enhancement` discriminator. This avoids a new type while keeping the lightweight lifecycle.

## Investigation Threads

1. **Audit existing artifacts** — Would any current SPECs or BUGs be better classified as enhancements? What would have changed?
2. **Lifecycle comparison** — Map the BUG, SPEC, and hypothetical ENHANCEMENT lifecycles side by side. Where do they diverge?
3. **Cross-story impact** — BUG is scoped to one problem; enhancements may address multiple stories. How does this affect `addresses:` and parent-epic linking?
4. **Tooling impact** — What changes in specgraph, specwatch, swain-status, and swain-do for each option?
5. **Issue tracker alignment** — GitHub Issues has labels (bug, enhancement). How does each option map to external issue types?

## Findings

_Populated during Active phase._

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-11 | — | Initial creation under EPIC-002 |
