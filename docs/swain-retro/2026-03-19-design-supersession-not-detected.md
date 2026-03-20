# Retro: DESIGN Supersession Not Detected at Creation Time

**Date:** 2026-03-19
**Scope:** swain-design artifact creation workflow
**Period:** 2026-03-18 — 2026-03-19

## Summary

DESIGN-005 (swain-box Launcher UX) was created on 2026-03-19 while DESIGN-002 (swain-box Agent Selection Experience) was Active, covering the same interaction surface — the `swain-box` CLI from invocation to launch. DESIGN-005 fully subsumes DESIGN-002's scope (runtime selection, menu, auto-select, explicit flag, credential check) and extends it (isolation mode, auth model, container lifecycle, sandbox management). The supersession was only caught when the operator noticed it manually during a flowchart rework session.

DESIGN-005's `linked-artifacts` field explicitly listed `DESIGN-002` — a direct signal that was never evaluated as a potential supersession.

## Root cause analysis

### 1. No same-type overlap detection at creation time

The swain-design creation workflow (SKILL.md steps 7-8b) validates:
- **Parent references exist** (step 7)
- **ADR compliance** (step 8)
- **Alignment with parent chain** (step 8a) — via `chart.sh scope`
- **Vision ancestry** (step 8b) — unanchored check

None of these check: "Is there already an Active DESIGN covering the same interaction surface?" The alignment checking system (alignment-checking.md) defines relationship checks for Vision-Epic, Epic-SPEC, and sibling SPECs — but DESIGNs are cross-cutting reference artifacts with no parent hierarchy. They have no siblings to conflict with.

### 2. Linked-artifact references don't trigger supersession analysis

DESIGN-005 declared `DESIGN-002` in its `linked-artifacts`. The specwatch cross-reference validator checks for missing reciprocal links and undeclared body references — structural graph integrity. It does not interpret the *semantic meaning* of a same-type link. A DESIGN linking to another DESIGN of the same surface is a strong supersession signal, but no check looks for it.

### 3. The scoping rule exists but isn't enforced

The DESIGN definition states: "One Design per cohesive interaction surface or workflow." This is a prose convention — it isn't checked during artifact creation. When DESIGN-005 was created with `Interaction Surface: The terminal UX for ./swain-box from invocation to agent session`, no scan compared this against DESIGN-002's `Interaction Surface: The terminal UX for scripts/swain-box from invocation to sandbox launch`.

### 4. Pattern match with prior retro

This is structurally identical to the spike-findings-not-back-propagated retro (2026-03-19): the system validates at creation time but doesn't re-evaluate when new evidence (or new artifacts) changes the picture. In that case, a spike invalidated a spec's assumption. Here, a broader design made a narrower design redundant.

## Proposed process change

### Same-type overlap check at DESIGN creation (step 7.5)

When creating a new DESIGN artifact:

1. Scan `docs/design/Active/` for all Active DESIGNs
2. For each, compare `Interaction Surface` sections — if the new DESIGN's surface overlaps with or subsumes an existing DESIGN's surface, flag it
3. If flagged: ask the operator whether the new DESIGN supersedes the existing one. If yes, transition the old DESIGN to Superseded as part of the same operation

This check should also apply when a DESIGN's `linked-artifacts` includes another DESIGN of the same type — same-type links are a direct signal.

### Generalize to all standing-track artifacts

DESIGNs, Personas, and Runbooks all use the standing lifecycle track and can overlap without parent-sibling relationships. The same overlap check should apply to all standing-track types, not just DESIGNs.

## Learnings captured

| Memory file | Type | Summary |
|------------|------|---------|
| (proposed — pending operator validation) | feedback | Same-type overlap check needed at creation for standing-track artifacts (DESIGN, Persona, Runbook) |
