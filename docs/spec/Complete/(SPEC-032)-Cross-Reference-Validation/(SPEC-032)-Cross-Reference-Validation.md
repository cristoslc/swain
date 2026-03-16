---
title: "Cross-Reference Validation and Bidirectional Edge Enforcement"
artifact: SPEC-032
track: implementable
status: Complete
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
type: feature
parent-epic: EPIC-013
linked-artifacts:
  - ADR-004
  - EPIC-005
  - JOURNEY-001
  - SPEC-010
  - SPEC-012
  - SPIKE-007
  - SPIKE-008
  - SPIKE-012
  - SPEC-033
depends-on-artifacts:
  - SPEC-030
addresses: []
source-issue:
swain-do: required
---

# Cross-Reference Validation and Bidirectional Edge Enforcement

## Problem Statement

Artifact body text frequently mentions other artifacts (e.g., "this depends on SPIKE-007 for container research") without declaring the relationship in frontmatter. This causes the dependency graph to miss edges, which means:
- `specgraph ready` reports artifacts as unblocked when they have implicit prerequisites
- `specgraph scope` and `impact` miss connections
- swain-status understates dependency chains

Additionally, when artifact A declares `depends-on-artifacts: [B]`, artifact B should have A in its `linked-artifacts` (the reciprocal edge). Currently no validation enforces this, leaving the graph asymmetric.

## External Behavior

### Cross-reference validation (xref)

**Body scanning:** For each artifact, scan the markdown body text (everything after the closing `---` of frontmatter) for patterns matching `TYPE-NNN` (e.g., `EPIC-005`, `SPIKE-007`, `SPEC-012`). Filter matches to only IDs present in the specgraph node set (excluding self-references).

**Frontmatter collection:** Collect all artifact IDs declared in any frontmatter relationship field: `depends-on-artifacts`, `linked-artifacts`, `validates`, `addresses`, `parent-epic`, `parent-vision`, `superseded-by`. Extract base IDs (e.g., `JOURNEY-001` from `JOURNEY-001.PP-03` in addresses).

**Discrepancy detection:**
- **body_not_in_frontmatter**: artifact IDs found in body but not in any frontmatter relationship → agent should classify as `depends-on-artifacts` or `linked-artifacts`
- **frontmatter_not_in_body**: artifact IDs in frontmatter but never referenced in body → possible stale reference

### Bidirectional edge enforcement

For every `depends-on-artifacts` edge A → B in the graph, check that B's frontmatter contains A in its `linked-artifacts`. If not, surface as a **missing reciprocal edge**.

### Cache integration

Store xref results in the specgraph cache under an `xref` key:

```json
{
  "xref": [
    {
      "artifact": "EPIC-005",
      "file": "docs/epic/Proposed/(EPIC-005)-Foo/...",
      "body_not_in_frontmatter": ["SPIKE-007", "SPIKE-008"],
      "frontmatter_not_in_body": [],
      "missing_reciprocal": []
    },
    {
      "artifact": "SPIKE-007",
      "file": "docs/research/Proposed/(SPIKE-007)-Foo/...",
      "body_not_in_frontmatter": [],
      "frontmatter_not_in_body": [],
      "missing_reciprocal": [
        {"from": "EPIC-005", "edge_type": "depends-on", "expected_field": "linked-artifacts"}
      ]
    }
  ]
}
```

### `xref` subcommand

**Human-readable mode (default):**
```
=== Cross-Reference Gaps ===

EPIC-005 (docs/epic/Proposed/.../...):
  -> SPIKE-007 (mentioned in body, not in frontmatter)
  -> SPIKE-008 (mentioned in body, not in frontmatter)

=== Missing Reciprocal Edges ===

SPIKE-007: should list EPIC-005 in linked-artifacts (EPIC-005 depends-on SPIKE-007)

=== Stale References ===

(none)
```

**JSON mode** (`xref --json`): outputs the raw `xref` array from cache.

## Acceptance Criteria

1. **Given** EPIC-005 mentions SPIKE-007 in body text but not in frontmatter, **when** xref runs, **then** SPIKE-007 appears in EPIC-005's `body_not_in_frontmatter` list.

2. **Given** an artifact with `depends-on-artifacts: [SPEC-010]` in frontmatter and "SPEC-010" in body text, **when** xref runs, **then** SPEC-010 does NOT appear in `body_not_in_frontmatter` (already declared).

3. **Given** an artifact body mentioning "UTF-8" or "SHA-256" (uppercase-dash-number patterns that aren't artifacts), **when** xref runs, **then** those are filtered out by the known-ID check.

4. **Given** an artifact mentioning its own ID in the body, **when** xref runs, **then** the self-reference is excluded.

5. **Given** SPEC-010 declares `depends-on-artifacts: [SPIKE-012]`, **when** bidirectional check runs, **then** SPIKE-012 is flagged if it does not have SPEC-010 in its `linked-artifacts`.

6. **Given** SPEC-010 depends-on SPIKE-012 and SPIKE-012 has SPEC-010 in `linked-artifacts`, **when** bidirectional check runs, **then** no reciprocal edge gap is flagged.

7. **Given** `specgraph.py build` is run, **when** complete, **then** the cache includes the `xref` key with current validation results.

8. **Given** `specgraph.py xref`, **when** run, **then** human-readable output shows all three categories (body gaps, reciprocal gaps, stale refs) with artifact IDs and file paths.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| 1. body_not_in_frontmatter detection | test_xref.py::TestComputeXrefPipeline — 47/47 passing | ✅ |
| 2. Already-declared IDs not flagged | TestComputeXrefPipeline::test_both_artifacts_clean_returns_empty | ✅ |
| 3. UTF-8/SHA-256 filtered out | TestScanBodyNonArtifactFiltering — broad sweep documented | ✅ |
| 4. Self-reference excluded | TestScanBodySelfExclusion | ✅ |
| 5. Missing reciprocal flagged | TestCheckReciprocalEdgesBasic | ✅ |
| 6. Present reciprocal not flagged | test_reciprocal_present_no_gap | ✅ |
| 7. xref key in cache after build | Integration test: specgraph.py build → 66 xref entries | ✅ |
| 8. xref subcommand human output | specgraph.py xref shows all 3 sections on live repo | ✅ |

## Scope & Constraints

- Body scanning uses `re.findall(r'[A-Z]+-\d+', body)` — no word-boundary assertion needed since results are filtered against known IDs
- `source-issue` and `evidence-pool` frontmatter values are not artifact IDs and should be excluded from xref comparison
- xref computation runs during `build` and results are cached — `xref` subcommand reads from cache
- Performance: ~66 artifacts × body scan is acceptable; no optimization needed

## Implementation Approach

1. **Body scanner (TDD):** Write tests for ID extraction from sample body text (including edge cases: code blocks, URLs, self-references, non-artifact patterns). Implement as a function in a new `xref.py` module.

2. **Frontmatter ID collector (TDD):** Write tests for collecting all relationship IDs from parsed frontmatter. Implement as a function that takes parsed frontmatter and returns a set of IDs.

3. **Discrepancy computation (TDD):** Write tests for set-difference logic and known-ID filtering. Implement the comparison function.

4. **Bidirectional check (TDD):** Write tests for reciprocal edge detection. Implement as a graph-level check that iterates `depends-on` edges and verifies the inverse `linked-artifacts` declaration.

5. **Cache integration:** Add xref computation to the `build` pipeline, store results under the `xref` cache key.

6. **CLI:** Add `xref` subcommand with `--json` flag for raw output.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-13 | — | Initial creation |
| Ready | 2026-03-14 | b4037a0 | Batch approval — ADR compliance and alignment checks pass |
| Complete | 2026-03-14 | 5a4386c | xref.py + cli xref subcommand, 47/47 tests, 66 real discrepancies found |
