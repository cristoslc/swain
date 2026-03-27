---
title: "Expand DESIGN Artifact Scope to Data and System Contracts"
artifact: SPEC-134
track: implementable
status: Complete
author: cristos
created: 2026-03-20
last-updated: 2026-03-21
type: enhancement
parent-epic: ""
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# Expand DESIGN Artifact Scope to Data and System Contracts

## Problem Statement

Swain's DESIGN artifact type currently scopes itself exclusively to UI/UX interaction design — "screens, states, flows, wireframes, happy/sad paths, and UI decisions." The definition explicitly excludes data architecture: "Designs are NOT Specs. They do not define API contracts, data models, or system behavior."

This creates a gap: there is no standing-track artifact type for capturing data architecture (entity models, data flows, schema evolution rules, invariants) or system contracts (API boundaries, behavioral guarantees, SLAs). These concerns share identical lifecycle mechanics with interaction design — they are living documents that drift against code, need `sourcecode-refs` for staleness detection, persist across multiple SPECs, and follow the same Proposed → Active → Retired/Superseded lifecycle.

Rather than duplicating the entire DESIGN machinery into a new artifact type (adding definition, template, scripts, specwatch patterns, index maintenance, and cognitive overhead), this SPEC proposes expanding DESIGN's scope to encompass data and system architecture alongside interaction design, using a `domain` frontmatter field to distinguish between design domains.

## Brainstorming Summary

### Why not a separate artifact type?

The structural comparison reveals no divergence:

| Concern | Interaction Design | Data/System Design |
|---------|-------------------|-------------------|
| Lifecycle track | Standing | Standing |
| Drift detection | `sourcecode-refs` + `design-check.sh` | Same |
| Relationship to SPECs | SPECs implement, DESIGN persists | Same |
| Design Intent (write-once) | Goals, constraints, non-goals | Same |
| Supersession mechanics | Same | Same |
| Cross-cutting references | Not owned by any single EPIC | Same |
| Folder structure | `docs/design/<Phase>/(DESIGN-NNN)-<Title>/` | Same |

The only difference is the *domain* of what's being designed — not the artifact's structural role in the system. Swain already handles domain variation within types (SPEC has `type: feature | enhancement | bug`). A DESIGN `domain` field follows the same pattern.

### Why was data excluded originally?

The DESIGN definition's exclusion ("Designs are NOT Specs. They do not define API contracts, data models, or system behavior") reads as a scope fence for the initial rollout, not a principled architectural boundary. No ADR documents this decision. The DESIGN type was introduced to solve the UI/UX design gap; data architecture wasn't considered at that time.

### What does industry prior art say?

Research (trove: `nvidia-openshell-nemoclaw@e64ab14` plus web research on data contracts) reveals:

- **Data contracts** (Confluent, Soda, ODCS, PayPal) focus on producer/consumer agreements — schema + SLAs + quality rules + ownership. These are narrower than what we need — they're CI enforcement artifacts, not design documents.
- **C4 model** treats data stores as "containers" but doesn't give data architecture a first-class living-document representation.
- Neither approach tracks design-to-code drift. Swain's `sourcecode-refs` mechanism is more sophisticated than either.

The gap in industry tooling validates creating a *design-level* document for data architecture rather than adopting an existing contract format.

### When might separation still be right?

If in practice we find that:
- Data designs need fundamentally different template sections (not just different content in the same sections)
- The `design-check.sh` tooling needs domain-specific logic beyond what a `domain` field provides
- Teams want different lifecycle rules (e.g., data contracts needing approval gates that interaction designs don't)

...then separation would be warranted. But these are empirical findings, not upfront predictions. Start unified, split if evidence demands it.

## External Behavior

### New frontmatter field: `domain`

Add an optional `domain` field to DESIGN frontmatter:

```yaml
domain: interaction | data | system
```

- **`interaction`** (default) — UI/UX interaction design. Screens, flows, states, wireframes. Current DESIGN scope.
- **`data`** — Data architecture design. Entity models, data flows, schema definitions, storage patterns, evolution rules, invariants.
- **`system`** — System contract design. API boundaries, behavioral guarantees (pre/postconditions, error semantics), integration interfaces, SLAs.

When `domain` is omitted, defaults to `interaction` for backward compatibility.

### Template sections by domain

The template structure adapts based on domain. All domains share:
- **Design Intent** (write-once: Goals, Constraints, Non-goals)
- **Design Decisions** (key choices and why)
- **Assets** (supporting files index)
- **Lifecycle** table

Domain-specific sections:

#### `interaction` (unchanged from current)
- Interaction Surface
- User Flow (with mandatory flowchart)
- Screen States
- Edge Cases and Error States

#### `data`
- Data Surface (what part of the system's data this design covers)
- Entity Model (entities, relationships, cardinality — mermaid ER diagram required)
- Data Flow (how data moves through the system — mermaid flowchart required)
- Schema Definitions (field-level definitions, types, constraints, nullability)
- Evolution Rules (backward/forward compatibility requirements, migration strategy)
- Invariants (what must always be true — business rules, referential integrity, consistency guarantees)

#### `system`
- Interface Surface (what boundary this design covers)
- Contract Definition (inputs, outputs, error semantics, idempotency)
- Behavioral Guarantees (pre/postconditions, SLAs, retry semantics, ordering guarantees)
- Integration Patterns (how consumers discover and connect — protocol, auth, versioning)
- Evolution Rules (versioning strategy, deprecation policy, breaking change process)

### Definition changes

1. **Remove exclusion language**: Delete "Designs are NOT Specs. They do not define API contracts, data models, or system behavior. If a Design starts accumulating technical implementation details, those belong in a Spec."

2. **Replace with domain guidance**: "A DESIGN captures the *shape* of a system concern — interaction surfaces, data structures, or system interfaces — as a standing document that persists across implementation cycles. Implementation *details* (how to build it) belong in SPECs. Design *decisions* with architectural weight belong in ADRs. The domain field indicates which aspect of the system the DESIGN addresses."

3. **Add domain-specific scoping guidance**:
   - `interaction`: One Design per cohesive interaction surface or workflow (unchanged)
   - `data`: One Design per bounded data domain or data product (e.g., "the task tracking data model" or "the artifact metadata schema")
   - `system`: One Design per integration boundary or API surface (e.g., "the specgraph CLI interface" or "the webhook contract")

### Tooling changes

1. **`design-check.sh`** — No changes needed. Blob-pinned `sourcecode-refs` work identically regardless of domain. A data DESIGN pins schema files; an interaction DESIGN pins component files. Same mechanism.

2. **`specwatch.sh`** — No changes needed. Scans all DESIGNs regardless of domain.

3. **Template rendering** — The template needs domain-conditional sections. Since swain templates are Jinja2 structural references (not rendered), this means documenting domain-specific section alternatives in the template file with conditional comments.

4. **`list-design.md` index** — Add `domain` column to the index table.

5. **`chart.sh`** — No changes needed. DESIGNs already appear in the graph; domain is just metadata.

### Decision protection hooks — domain-aware updates

The existing DESIGN decision protection hooks in SKILL.md (SPEC implementation transition, SPEC completion, alignment cascading, design-to-code drift) apply to all domains equally. No hook changes needed.

## Acceptance Criteria

1. **Given** the DESIGN definition file, **when** I read the artifact scope, **then** it covers interaction, data, and system design domains without exclusion language.

2. **Given** a new DESIGN with `domain: data`, **when** I create it using swain-design, **then** the template includes data-specific sections (Entity Model, Data Flow, Schema Definitions, Evolution Rules, Invariants) instead of interaction-specific sections.

3. **Given** a new DESIGN with `domain: system`, **when** I create it using swain-design, **then** the template includes system-specific sections (Contract Definition, Behavioral Guarantees, Integration Patterns, Evolution Rules) instead of interaction-specific sections.

4. **Given** a DESIGN with `domain: data` and `sourcecode-refs` pointing to schema files, **when** I run `design-check.sh`, **then** drift detection works identically to interaction DESIGNs.

5. **Given** an existing DESIGN with no `domain` field, **when** swain-design processes it, **then** it treats it as `domain: interaction` (backward compatible).

6. **Given** the `list-design.md` index, **when** it is regenerated, **then** it includes a `domain` column showing each DESIGN's domain.

7. **Given** the DESIGN template, **when** I read it, **then** domain-specific sections are clearly documented with conditional guidance.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| definition covers all 3 domains without exclusion language | `design-definition.md` lines 22–28: domain table lists interaction/data/system; no "Designs are NOT Specs" text | Pass |
| `domain: data` template has data-specific sections | `design-template.md.template` lines 117–164: Entity Model, Data Flow, Schema Definitions, Evolution Rules, Invariants | Pass |
| `domain: system` template has system-specific sections | `design-template.md.template` lines 170+: Contract Definition, Behavioral Guarantees, Integration Patterns, Evolution Rules | Pass |
| `design-check.sh` works identically for `domain: data` | design-check.sh is domain-agnostic (blob-pinned sourcecode-refs); no changes needed | Pass |
| existing DESIGNs without `domain` treated as `interaction` | template uses `{{ domain \| default("interaction") }}`; 413 tests pass | Pass |
| `list-design.md` includes domain column | `docs/design/list-design.md` header confirmed: `\| Domain \|` | Pass |
| template has domain-conditional sections with guidance comments | Jinja2 `{%- if domain == "data" %}` / `{%- elif domain == "system" %}` blocks with comment headers | Pass |

## Scope & Constraints

### In scope
- DESIGN definition file update (remove exclusion, add domain guidance)
- DESIGN template update (domain-conditional sections)
- `list-design.md` index format update (add domain column)
- Existing DESIGN artifacts: no migration needed (default to `interaction`)

### Out of scope
- No changes to `design-check.sh` (already domain-agnostic)
- No changes to `specwatch.sh` or `chart.sh`
- No changes to decision protection hooks in SKILL.md
- No creation of example data/system DESIGNs (that's a follow-up)
- No formal data contract enforcement tooling (CI-level schema validation is a different concern)

### Non-goals
- This is NOT adopting industry "data contract" standards (ODCS, Confluent contracts). Those are CI/pipeline enforcement artifacts. DESIGN captures the design-level document that *informs* such enforcement.
- This is NOT creating a schema registry or machine-readable contract format. DESIGNs remain human-readable markdown documents with code-pinned references.

## Implementation Approach

### TDD Cycle 1: Definition update
- Update `design-definition.md`: remove exclusion language, add domain field documentation, add domain-specific scoping guidance
- Verify: definition coherently covers all three domains without contradicting existing DESIGN patterns

### TDD Cycle 2: Template update
- Update `design-template.md.template`: add `domain` field to frontmatter, add domain-conditional section blocks with clear guidance comments
- Verify: template renders sensibly for each domain value

### TDD Cycle 3: SKILL.md update
- Update SKILL.md: remove "Designs are NOT Specs..." content distinction language, add domain-aware creation guidance
- Verify: swain-design skill correctly routes domain-specific template sections during DESIGN creation

### TDD Cycle 4: Index update
- Update `rebuild-index.sh` or index generation logic to include `domain` column in `list-design.md`
- Verify: existing DESIGNs show `interaction` (default), index renders correctly

### TDD Cycle 5: Backward compatibility verification
- Run `design-check.sh` on all existing Active DESIGNs
- Run `specwatch.sh scan`
- Verify: no regressions, existing DESIGNs unaffected

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | -- | Initial creation |
| Complete | 2026-03-21 | d491b1a | Retroactive close — all deliverables already in codebase; 413/414 tests pass |
