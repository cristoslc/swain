---
source-id: "architecture-conversation-summary"
title: "Swain Architecture Conversation Summary — Action Graph, ADR Context, Component Catalog, Intent/Evidence Primitives"
type: local
path: "Downloads/swain-architecture-conversation-summary.md"
fetched: 2026-03-23T00:00:00Z
hash: "--"
---

# Swain Architecture: Conversation Summary
**Date:** 2026-03-23  
**Scope:** Agentic runtime architecture, component cataloging, and foundational primitives for the swain project management system

---

## Purpose
Explore the architectural role of swain as an agentic runtime substrate — specifically: how it should model control flow vs. knowledge, maintain a non-drifting component catalog, and what its core philosophical primitives are.

---

## Process
Four sequential conceptual questions, each building on the prior:
1. Directed action graph vs. graph database (agentic runtime perspective)
2. How TideClaw should understand ADRs/designs at spec-planning time
3. How swain can maintain a component catalog that doesn't drift
4. Whether intent and evidence are swain's two core primitives

---

## Principal Findings

### 1. Action Graph ≠ Graph Database
| Dimension | Action Graph (swain DAG) | Graph Database |
|---|---|---|
| Purpose | What to do (control flow) | What is true (world model) |
| Agent relationship | Agent executes it | Agent queries it |
| Mutability | Human/planner-modified | Agent-modified |
| Query model | Traversal (follow edges) | Pattern matching (find subgraphs) |
| Analogue | A program | A database |

**Key insight:** Swain's frontmatter DAG is correct for human-authored, human-modified control flow. A graph DB earns its keep only when the agent needs to *discover* structure dynamically or answer cross-cutting queries (e.g., "all tasks blocked by X across all projects").

---

### 2. ADR/Design Context Assembly at Planning Time
**Problem:** Vector/RAG surfaces *related* ADRs by keyword similarity but cannot model supersession chains, component scope, or explicit conflicts.

**Solution:** A lightweight graph layer — derived from ADR/component frontmatter — built at agent startup or on-demand (not a server process).

**Relationship model:**
```
Spec ──[touches]──> Component ──[governed_by]──> ADR
                                                   │
                              [supersedes]─────────┘
                                                   │
                              [conflicts_with]──> ADR
                                                   │
                              [instantiated_by]──> DesignDoc
```

**Planning pipeline:**
1. Read task frontmatter → get `touches:` component scope
2. Query ADR graph → get applicable ADRs + supersession chain
3. Pull full ADR + design doc content → inject as planning context
4. Draft spec

**Technology:** Markdown files as source of truth; in-process graph (networkx or Kuzu) derived from frontmatter. No server required at current scale.

**ADR frontmatter schema (proposed):**
```yaml
id: ADR-019
status: accepted  # draft | accepted | superseded | deprecated
supersedes: ADR-007
governs:
  - auth-service
  - session-management
related_designs:
  - designs/session-token-architecture.md
```

---

### 3. Component Catalog: Declare Intent, Derive Evidence
**Core principle:** Source code tells you *what exists*; the catalog declares *what should be*. These are different things and must not be collapsed.

**Source code can provide:**
- What exists (services, modules, packages)
- Import/call graphs
- Directory/package ownership

**Source code cannot provide:**
- Conceptual component identity (human decision)
- Intended boundaries vs. accidental ones
- ADR governance associations
- Component status (stable, deprecated, experimental)

**Architecture:**
- **Authoritative layer:** Human-maintained markdown in `swain/catalog/components/` with `owns:` glob patterns and `governed_by:` ADR IDs
- **Derived layer:** Script crawls source, builds inferred component map, diffs against declared catalog
- **Drift surfaces as:** orphaned files, uncatalogued directories, boundary violations (imports crossing declared boundaries)

**Drift prevention mechanisms:**
- CI linter: every top-level service/package must map to a catalog entry
- Spec task validation: `touches:` references must resolve to valid catalog IDs
- ADR validation: `governs:` references must resolve to valid catalog IDs
- Periodic swain reconciliation task (agent flags, humans decide — no auto-update)

**Minimal starting structure:**
```
swain/
  catalog/components/
    asset-calc-web.md
    asset-calc-mobile.md
    ac-api.md
  adrs/
    ADR-001.md
```

---

### 4. Swain's Two Core Primitives: Intent and Evidence

**Intent** — what has been decided:
- Tasks, ADRs, specs, component catalog, goals

**Evidence** — what can be observed:
- Git history, test results, drift reports, incident records, source-derived dependency graphs

**The system's job:** Maintain the relationship between the two — not collapse them. Every intent artifact has a natural evidence question attached.

| Intent | Evidence question |
|---|---|
| Task | Was it done? What did it produce? |
| ADR | Is it being followed? Where instantiated? |
| Component boundary | Does code respect it? |
| Spec | Does implementation match? |
| Goal | What signal confirms progress? |

**Third primitive: Reconciliation**
The structured comparison of intent vs. evidence — where the system learns:
- Drift reports (catalog vs. source)
- Retrospectives (plan vs. actual)
- ADR revisions (original intent vs. learned reality)
- Spec gap analyses (specified vs. built)

TideClaw's highest-value role: running reconciliations. Structured comparison is exactly what agents do well.

**Proposed file structure:**
```
swain/
  intent/
    tasks/
    adrs/
    specs/
    catalog/
    goals/
  evidence/
    drift-reports/
    incident-records/
    test-snapshots/
    dependency-graphs/
  reconciliations/
    2026-03-catalog-drift.md
    ADR-019-compliance-check.md
```

**Philosophical resonance:** Maps to zhōngyōng (dynamic equilibrium between poles). Intent without evidence = ideology. Evidence without intent = noise. Swain is a structured container for the tension between them — at every scale (project, architecture, and potentially personal via wherry).

---

## Primary Outcomes

1. **Confirmed:** Swain's frontmatter DAG is correctly scoped as control flow, not world model. No graph DB needed for task execution.
2. **Identified:** ADR context assembly at planning time requires a lightweight graph layer (frontmatter-derived, in-process), not RAG.
3. **Established:** Component catalog architecture: human-declared intent + source-derived evidence + CI-enforced reconciliation.
4. **Named:** Swain's foundational duality — intent and evidence — with reconciliation as the operative third primitive.
5. **Confirmed:** The same duality appears at every scale, suggesting load-bearing architectural principle applicable to wherry as well.

---

## Produced Artifacts

| Artifact | Status | Notes |
|---|---|---|
| ADR frontmatter schema | Proposed | `id`, `status`, `supersedes`, `governs`, `related_designs` |
| Component catalog frontmatter schema | Proposed | `id`, `status`, `owns` (globs), `governed_by`, `team` |
| Spec task frontmatter extension | Proposed | `touches:` field referencing catalog IDs |
| ADR graph relationship model | Defined | 5 edge types: governs, supersedes, conflicts_with, instantiated_by, touches |
| Swain directory structure (intent/evidence/reconciliations) | Proposed | Tripartite layout |
| Catalog reconciliation swain task template | Proposed | Weekly, TideClaw agent, flag-don't-auto-update pattern |

---

## Open Questions / Next Steps
- Tooling for graph build from frontmatter: networkx (simpler) vs. Kuzu (queryable, embeddable)?
- Where does the catalog reconciliation script live — swain repo itself, or TideClaw agent skill?
- Does wherry adopt the same intent/evidence/reconciliation tripartite structure at the personal scale?
- Formal spec for the five ADR graph edge types (governs scope definition is the hardest)
