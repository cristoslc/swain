# Synthesis: Scenario Modeling Prior Art

**Trove:** scenario-modeling-prior-art · 10 sources · created 2026-04-28
**For:** [SPIKE-070](../../research/Complete/(SPIKE-070)-ADR-Alignment-Check-Invocation-Points/(SPIKE-070)-ADR-Alignment-Check-Invocation-Points.md) — First-Class Scenario Modeling in swain-design
**Related trove:** likec4

---

## Key Finding: Two Distinct Primitives

Every tool surveyed conflates or separates two different primitives. Swain must pick one or both:

1. **Projection** — same model, different display filter. `swain chart ready` already does this.
2. **Scenario** — different input assumptions, same schema, different computed graph. Nothing in swain does this today.

PKM tools (Obsidian, Roam, Logseq) and architecture tools (Structurizr perspectives, LikeC4 static views) have exhausted the "projection" solution space. They offer no help for structural alternatives. The confirmed gap is **scenario as alternative input context** — and it is unmet across all tool categories surveyed.

---

## Where Sources Agree

### No tool does ADR-level scenario branching

The ADR tooling ecosystem survey (`adr-tooling-ecosystem`) found zero tools that model "the artifact tree under an alternative ADR state." Supersession is a linear chain. The counterfactual tree is not computable from any existing tool. This is a genuine unmet need.

### Scenarios are delta-encoded, not full copies

Every mature tool (Kustomize, financial scenario planners, Helm) represents a scenario as a **delta from a base**, not a full copy of the system. Kustomize overlays patch specific fields. Financial scenario tools store overrides against a base model. Scenarios that are full copies create maintenance debt — every base change must be propagated to all scenario copies. swain should adopt the delta pattern.

### Named scenarios need a lifecycle

Feature flags (`feature-flags-scenario-modeling`) and financial scenario tools (`scenario-planning-software-2025`) both warn against accumulating stale scenarios. Feature flag debt is a recognized anti-pattern. Both communities have converged on explicit lifecycle management for scenarios. swain would need to add scenario lifecycle (Proposed → Active → Archived) to prevent scenario proliferation.

### Sensitivity analysis beats full enumeration

MCDA tools (`1000minds-mcda`) discovered that "sweep one variable at a time" is more useful than enumerating all combinations. The "tipping point" — the threshold at which the ranking flips — is the most actionable output. swain's scenario feature should prioritize single-variable sweep ("flip one ADR's status") before multi-variable scenarios.

### Comparison view is the key UX

Every tool that does scenarios also provides a comparison view. Financial planners compare scenarios side by side in a table. Wardley Maps compare alternative futures as visual overlays. LikeC4's MCP server provides a `diff` tool. The canonical invocation for swain would be `swain chart --compare=scenario-A,scenario-B`.

---

## Points of Disagreement

### Runtime vs. static comparison

Feature flags (`feature-flags-scenario-modeling`) run both variants simultaneously and measure outcomes with data. Scenario planning software (`scenario-planning-software-2025`) computes scenarios statically and compares projections. swain's artifact graph is static (no runtime behavior), so the static comparison model applies — but the feature flag lesson about **dependency-aware re-evaluation** still applies: when ADR-X changes state, downstream artifacts that reference it need re-evaluation.

### Copy vs. overlay vs. branch

- Kustomize: overlay (delta against base, no copy)
- Helm: values file (parameter substitution, no structural copy)
- Wardley Maps: new map (full copy, visual comparison)
- Financial planners: scenario container (override specific parameters)
- Git branches: full copy of all files, structural divergence possible

For swain, the overlay (Kustomize) and parameter-substitution (Helm/financial) patterns are preferable to full branching. Full branching (git-style) is available but heavyweight — it should be a last resort, not the default scenario primitive.

---

## Gaps in Prior Art

### No tool surfaces *where* scenarios diverge

Wardley Maps come closest — the visual comparison shows where alternative futures branch. But this is manual. No tool computes and highlights "these are the artifacts that change between scenario A and scenario B." This would be a novel capability for swain.

### No tool attaches probability to scenario activation

Financial tools (Indicio) attach probabilities to scenarios for weighted expected-value calculations. No architecture or ADR tool does this. swain could eventually surface "which scenarios are most likely?" by tracking how often specific ADRs get superseded.

### No tool models partial assumption sets

All scenario tools require complete assumption specifications. No tool handles "I only know that ADR-X is active; everything else is uncertain." A probabilistic or partial-specification mode is an open research area.

---

## Primitive Recommendation for swain

Based on the convergence across sources, the recommended primitive is:

**A scenario file is a named YAML overlay that pins specific artifact-graph inputs (ADR states, priority weights) to non-canonical values, evaluated against the canonical graph to produce a computed alternative tree.**

Invocation: `swain chart --scenario=post-helm-refactor`
Comparison: `swain chart --compare=canonical,post-helm-refactor`
Format:
```yaml
# scenarios/post-helm-refactor.yaml
scenario: post-helm-refactor
description: "What the artifact tree looks like if ADR-046 had not been superseded"
overrides:
  ADR-046: { status: Active }
  ADR-048: { status: Superseded }
```

This is the Kustomize overlay pattern applied to swain's artifact graph. It is:
- Delta-encoded (only overrides, no full copies).
- Named (invokable by slug).
- Composable (multiple overrides in one scenario file).
- Lifecycle-managed (scenario files are artifacts with their own status).
- Diffable (git tracks changes to scenario files).

---

## Implications for SPIKE-070 Threads

- **Thread 2 (Data model):** The overlay YAML pattern is the strongest candidate. Start there.
- **Thread 3 (UX):** `swain chart --scenario` and `--compare` are the target invocation surface. The "tipping point" concept from MCDA should inform the diff output format.
- **Thread 4 (Integration):** Dependency-aware re-evaluation (feature flags lesson) and scenario lifecycle (flag debt lesson) are the two integration concerns that need design before implementation.
