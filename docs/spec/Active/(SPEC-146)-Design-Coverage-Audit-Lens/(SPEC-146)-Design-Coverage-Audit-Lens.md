---
title: "Design Coverage Audit Lens"
artifact: SPEC-146
track: implementable
status: Active
author: cristos
created: 2026-03-21
last-updated: 2026-03-21
priority-weight: ""
type: enhancement
parent-epic: EPIC-035
parent-initiative: ""
linked-artifacts:
  - SPEC-145
  - SPEC-134
  - ADR-014
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Design Coverage Audit Lens

## Problem Statement

swain-design audits currently check alignment, ADR compliance, and unanchored artifacts — but they have no lens for design coverage gaps. When an operator runs an audit, they learn whether existing DESIGNs are stale or misaligned, but never whether DESIGNs are *missing*. An EPIC that modifies a complex data pipeline or introduces a new API surface passes audit cleanly even if no DESIGN artifact documents the design decisions being made.

[SPEC-145](../(SPEC-145)-Design-Creation-Prompts/(SPEC-145)-Design-Creation-Prompts.md) addresses creation-time nudges (proactive prompts during authoring). This spec addresses the retroactive case: discovering coverage gaps in existing artifacts that were created before the prompts existed, or where the operator declined the prompt and the gap grew significant.

## Desired Outcomes

Operators running swain audits get a clear picture of where design documentation is thin relative to the complexity of the work. This is especially valuable for consumer projects adopting swain — they inherit DESIGN infrastructure but may not have been prompted to use it. The audit lens surfaces "you have data pipelines with no design coverage" alongside "you have unanchored artifacts" — same advisory tier, same decision-support purpose.

## External Behavior

A new `design-coverage` audit pass runs as part of the standard swain-design audit workflow. It produces advisory findings (not blocking) at the same tier as `SCOPE_LEAK` or unanchored warnings.

### Detection heuristics

The audit scans for three classes of coverage gap:

**1. Contract files without companion DESIGNs**
Scan for `*-contract.yaml` files ([ADR-014](../../../adr/Active/(ADR-014)-Data-Contracts-For-Agent-Produced-Data/(ADR-014)-Data-Contracts-For-Agent-Produced-Data.md) pattern). For each, check whether any Active `domain: data` or `domain: system` DESIGN has a `sourcecode-refs` entry pointing to the contract file. If not, emit:

> `DESIGN_GAP`: `skills/swain-release/changelog-contract.yaml` has no companion DESIGN artifact tracking its evolution.

**2. EPICs with design-surface signals but no linked DESIGN**
For each Active EPIC, apply the signal detection table (from [SPEC-145](../(SPEC-145)-Design-Creation-Prompts/(SPEC-145)-Design-Creation-Prompts.md)) against scope/goal sections. If signals are detected and the EPIC has no `artifact-refs` with `rel: [aligned]` pointing to a DESIGN, emit:

> `DESIGN_GAP`: [EPIC-035](../../../epic/Active/(EPIC-035)-Design-Staleness-And-Drift-Detection/(EPIC-035)-Design-Staleness-And-Drift-Detection.md) has {domain} design-surface signals but no linked DESIGN.

**3. Completed SPECs that modified design-tracked files without a DESIGN**
For each Complete SPEC, check whether its implementation commits touched files that match common design-surface patterns (UI components, schema files, API route definitions) without any Active DESIGN's `sourcecode-refs` covering those paths. Emit:

> `DESIGN_GAP`: [SPEC-134](../../Complete/(SPEC-134)-Expand-DESIGN-Artifact-Scope-To-Data-And-System-Contracts/(SPEC-134)-Expand-DESIGN-Artifact-Scope-To-Data-And-System-Contracts.md) modified `design-template.md.template` — no DESIGN tracks this file.

### Output format

Findings are grouped under a `## Design Coverage` section in the audit report, with a summary count:

```
## Design Coverage

3 design coverage gaps found (advisory — not blocking):

- DESIGN_GAP: skills/swain-release/changelog-contract.yaml has no companion DESIGN
- DESIGN_GAP: EPIC-035 has system design-surface signals but no linked DESIGN
- DESIGN_GAP: SPEC-134 modified design-template.md.template — no DESIGN tracks this file
```

### Remediation

**Interactive mode:** The audit reports gaps and the operator decides which to address.

**Autonomous mode:** When running in a non-interactive context, the audit can create `Proposed` DESIGNs for high-confidence gaps (contract files without companions, EPICs with strong signal matches). Low-confidence gaps (SPEC file coverage heuristic) remain advisory-only even in autonomous mode.

### Integration point

The audit pass runs as part of the existing audit workflow (references/auditing.md), in parallel with alignment, ADR compliance, and unanchored checks. It reads the specgraph cache and Active DESIGNs' `sourcecode-refs` — no new scripts needed beyond the audit logic itself.

## Acceptance Criteria

**Given** a project with a `changelog-contract.yaml` and no `domain: data` DESIGN tracking it,
**When** the operator runs a swain-design audit,
**Then** the audit emits a `DESIGN_GAP` finding for the contract file.

**Given** a project with a `changelog-contract.yaml` and an Active DESIGN with `sourcecode-refs` pointing to it,
**When** the operator runs a swain-design audit,
**Then** no `DESIGN_GAP` is emitted for that contract file.

**Given** an Active EPIC whose goal mentions "new API gateway,"
**When** the audit evaluates design coverage,
**Then** it emits `DESIGN_GAP` for the EPIC if no linked DESIGN exists.

**Given** an Active EPIC with `artifact-refs: [{id: DESIGN-005, rel: [aligned]}]`,
**When** the audit evaluates design coverage,
**Then** no `DESIGN_GAP` is emitted — coverage exists.

**Given** a project with zero `*-contract.yaml` files and no design-surface EPICs,
**When** the audit runs the design-coverage pass,
**Then** the section is omitted or shows "0 design coverage gaps found."

## Verification

<!-- Populated when entering Testing phase -->

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

**In scope:**
- `DESIGN_GAP` finding type in audit reports
- Three detection heuristics (contract files, EPIC signals, SPEC file coverage)
- Integration into the existing audit workflow as a parallel pass
- Advisory tier — same as unanchored warnings, never blocking

**Out of scope:**
- Per-file design-surface pattern definitions (use [SPEC-145](../(SPEC-145)-Design-Creation-Prompts/(SPEC-145)-Design-Creation-Prompts.md)'s signal keyword table for now)
- CI enforcement of design coverage thresholds
- Design coverage metrics or dashboards

## Implementation Approach

### TDD Cycle 1: Contract file detection
- Add logic to scan for `*-contract.yaml` files
- Cross-reference against Active DESIGNs' `sourcecode-refs`
- Emit `DESIGN_GAP` for untracked contract files
- Test: project with/without companion DESIGNs for contract files

### TDD Cycle 2: EPIC signal detection
- Reuse [SPEC-145](../(SPEC-145)-Design-Creation-Prompts/(SPEC-145)-Design-Creation-Prompts.md)'s signal keyword table
- Scan Active EPICs' scope/goal text
- Check for `artifact-refs` with `rel: [aligned]` pointing to DESIGNs
- Emit `DESIGN_GAP` for uncovered EPICs
- Test: EPIC with/without linked DESIGNs

### TDD Cycle 3: SPEC file coverage detection
- Scan Complete SPECs' implementation commits for design-surface file patterns
- Cross-reference against Active DESIGNs' `sourcecode-refs` paths
- Emit `DESIGN_GAP` for uncovered modifications
- Test: SPEC modifying tracked vs. untracked design-surface files

### TDD Cycle 4: Audit integration
- Wire the three heuristics into `references/auditing.md` as a parallel audit pass
- Format output as `## Design Coverage` section
- Verify it runs alongside existing audit passes without blocking
- Test: full audit with and without design coverage gaps

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-21 | -- | Initial creation |
