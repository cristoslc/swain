---
title: "Enhancement Type Modeling"
artifact: SPIKE-003
track: container
status: Complete
author: cristos
created: 2026-03-11
last-updated: 2026-03-11
question: "Should swain-design add a new ENHANCEMENT artifact type (parallel to BUG), or should SPECs gain a type discriminator field (type = epic | bug | enhancement)?"
gate: Pre-Implementation
risks-addressed:
  - Wrong abstraction leads to process overhead that defeats the purpose of lightweight enhancements
  - Type proliferation makes the artifact model harder to learn and maintain
trove: ""
linked-artifacts:
  - EPIC-002
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

### Thread 1: Audit of existing artifacts

- **SPEC-002 (evidencewatch)** is enhancement-shaped — a modest monitoring script that could be delivered as a lightweight task within SPEC-001 rather than requiring full spec ceremony.
- **9 of 10 open GitHub issues** are enhancement-shaped (small improvements, not defects). Only #8 (malformed hyperlinks) is a true bug.
- **Zero BUG artifacts exist** — `docs/bug/` directory doesn't exist yet.
- Conclusion: enhancement-type work is the most common category of incoming work. The need is real and frequent.

### Thread 2: Lifecycle comparison

| | BUG | SPEC | Enhancement (hypothetical) |
|---|---|---|---|
| Phases | Reported → Active → Fixed → Verified | Draft → Review → Approved → Testing → Implemented | Same as SPEC — agent fills out all detail regardless |
| Gates | Triage at creation | Verification table, spec-verify.sh | Same as SPEC |
| Tracking | `swain-do: required` | `swain-do: required` | `swain-do: required` |
| Hierarchy | Independent (`affected-artifacts:`) | Under epic (`parent-epic:`) | **This is the friction point** |

Key finding: the lifecycle for enhancements is identical to SPEC. The agent fills out acceptance criteria and verification gates regardless of scope — "light" vs "heavy" ceremony is a non-issue. The real friction is that SPECs require `parent-epic`, making standalone improvements feel like antipatterns.

### Thread 3: Cross-story impact

Enhancements may address pain points from multiple journeys and touch multiple stories, just like SPECs. The `addresses:` and `parent-epic:` fields already support this. Making `parent-epic` optional enables standalone SPECs without changing the relationship model.

### Thread 4: Tooling impact

| Script | Option A (new type) | Option B (type field on SPEC) | Option C (BUG + kind) |
|--------|----|----|---|
| specgraph.sh | +1 to type regex | 0 changes | 0 changes |
| specwatch.sh | +1 to TYPE_DIRS + new directory structure | 0 changes | 0 changes |
| swain-status.sh | 6 code changes | 0 changes (SPECs already handled) | 3-4 changes |
| adr-check.sh | 0 changes | 0 changes | 0 changes |
| spec-verify.sh | 0 changes | 0 changes | 0 changes |

Option B requires zero tooling changes because SPECs are already fully supported everywhere.

### Thread 5: Issue tracker alignment

GitHub Issues added first-class issue types in Jan 2025 (bug, task, initiative). Linear has zero types — everything is an issue with labels. The industry trend is toward fewer types with metadata, not more types.

For swain's planned issue integration (EPIC-002 pillar 2), a SPEC `type` field maps cleanly to GitHub issue labels. When importing a GitHub issue labeled "enhancement," create a SPEC with `type: enhancement`. When importing one labeled "bug," create a BUG artifact. The mapping is straightforward regardless of whether SPECs have a type field.

### Philosophical reframe

Web research surfaced a deeper insight that reframed the question entirely:

**Type matters less than structure.** Linear operates with zero types. Shape Up has one (the Pitch). The Cape of Good Code argues for types only when they enable quality metrics — irrelevant for a solo developer with AI agents.

**The two consumers of swain artifacts have different needs:**
1. The **operator** (developer) needs decision support — what needs my attention, what's the impact, should I approve this?
2. The **agent** needs implementation alignment — what are the acceptance criteria, constraints, dependencies, and boundaries?

Neither consumer cares about the bug/enhancement distinction at consumption time. The operator cares about impact and urgency. The agent cares about structure and constraints. Everything swain does for the operator supports decision-making; everything it does for the agent provides alignment and verification.

From this lens: SPEC ceremony isn't the problem (agents fill it out). SPEC's mandatory `parent-epic` is the problem — it forces organizational overhead that doesn't serve either consumer.

### Recommendation

**Go for Option B (extended): Unify all implementation work under SPEC.**

1. Make `parent-epic` optional in the SPEC template and definition. A SPEC without a parent-epic is standalone work.
2. Add `type: feature | enhancement | bug` frontmatter field to SPEC. Determines which optional sections are relevant (bug-typed SPECs include reproduction steps, severity, expected/actual behavior) and maps to external issue tracker labels.
3. **Fold BUG into SPEC entirely.** Eliminate BUG as a standalone artifact type. Bugs become SPECs with `type: bug` — same lifecycle, same template (with conditional sections), same tooling. This reduces the artifact model from 11 types to 10.
4. Use GitHub Issues as the lightweight intake funnel. Most enhancements live as issues until promoted to a SPEC when worth structuring.
5. **Migration path** for existing swain consumers: swain-doctor detects `docs/bug/` artifacts and converts them to SPECs with `type: bug`, rewriting frontmatter and cross-references.

**Why not the other options:**
- **Option A (new ENHANCEMENT type)**: Type proliferation with no lifecycle difference from SPEC. The agent fills out the same template regardless.
- **Option B (original, keep BUG)**: BUG's lifecycle doesn't differ meaningfully enough from SPEC to justify a separate type. The agent fills out bug detail regardless — reproduction steps and severity can be SPEC sections.
- **Option C (BUG + kind)**: Semantic mismatch (BUG-NNN for enhancements). Migration cost without the payoff of unification.
- **Option D (rename BUG → ISSUE)**: Bigger rename for no additional benefit over folding into SPEC.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-11 | a950529 | Initial creation under EPIC-002 |
| Active | 2026-03-11 | 7aadee8 | Investigation began |
| Complete | 2026-03-11 | 7aadee8 | Decision: standalone SPECs with optional type field (Option B modified) |
