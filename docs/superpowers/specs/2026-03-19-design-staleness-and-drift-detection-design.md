# Design Staleness and Drift Detection

## Problem

DESIGN artifacts describe what the UI should look like and how users interact with it. But they go stale in two directions: code changes without the design being updated, and designs evolve without code catching up. Unlike TRAIN artifacts (which track one-way staleness against source artifacts), DESIGNs have a bidirectional relationship with implementation code.

Additionally, there's no mechanism to preserve the original design vision as the design's mutable sections evolve, and no way to protect alignment decisions (e.g., "this Epic fits this Design") from being silently violated by derived SPECs.

## Research

Trove `design-staleness-drift@c3fd9fb` — 7 sources covering DDR patterns, design rationale history, design-code drift tools, and design system governance.

Key findings:
- DDRs are structurally identical to ADRs — no need for a separate artifact type
- Design rationale capture fails when it adds overhead; successful systems make capture a byproduct of existing workflow
- Design drift is well-documented but all existing tooling operates at the code level (CSS tokens, DOM snapshots), not the document level
- The industry consensus is "encode intent as constraints" — make intent machine-checkable, not just human-readable

## Design Decisions

### 1. No DDR artifact type

ADRs cover design decisions. Design Intent captures vision within the DESIGN artifact itself. Creating a separate DDR type would duplicate ADR with a different name.

### 2. Separate `artifact-refs` and `sourcecode-refs`

Two new frontmatter fields replace the enriched `linked-artifacts` v2 format:

- `artifact-refs` — enriched references to swain artifacts (replaces v2 `linked-artifacts` with `rel`/`commit`/`verified`). Used by TRAIN and DESIGN.
- `sourcecode-refs` — blob-pinned references to implementation files. DESIGN-only (initially).
- `linked-artifacts` (v1 flat list) — unchanged, continues to work for simple cross-references on all artifact types.

`artifact-refs` structure (same shape as existing enriched `linked-artifacts`, renamed):

```yaml
artifact-refs:
  - artifact: SPEC-067
    rel: [documents]
    commit: abc1234
    verified: 2026-03-19
  - artifact: DESIGN-003
    rel: [aligned]
    commit: def5678
    verified: 2026-03-19
```

Existing standalone frontmatter fields (`superseded-by`, `depends-on-artifacts`) remain as-is — they are lifecycle/dependency markers, not content-tracked references.

The v2 → `artifact-refs` rename only affects TRAIN definitions and tooling. At implementation time, scan for any TRAIN artifacts with enriched `linked-artifacts` entries; if found, include a migration step to rename them.

### 3. Blob SHA pinning for sourcecode-refs

Each `sourcecode-refs` entry pins path + blob SHA + commit:

```yaml
sourcecode-refs:
  - path: src/components/Button/Button.tsx
    blob: a1b2c3d
    commit: def5678
    verified: 2026-03-19
```

Blob SHA provides content-based identity that survives renames. The check algorithm:

1. Path exists at HEAD? Compare current blob SHA vs pinned:
   - Same → **CURRENT**
   - Different → **STALE** (content changed in place; note: a complete file rewrite at the same path is indistinguishable from an incremental edit — both report STALE)
2. Path missing at HEAD? Search HEAD tree for pinned blob SHA (`git ls-tree -r HEAD | grep <blob>`):
   - Found at new path → **MOVED** (content identical, path changed)
   - Not found → run `git diff --find-renames --diff-filter=R <pinned-commit> HEAD -- <original-path>` to detect renames with content changes:
     - Rename found → **MOVED+STALE** (relocated and modified)
     - No rename found → **BROKEN** (file deleted with no rename target)

Getting the blob SHA at pin time: `git ls-tree HEAD -- <path> | awk '{print $3}'`

### 4. Design Intent section (write-once)

New section in the DESIGN template, immediately after the title:

```markdown
## Design Intent

**Context:** [One sentence anchoring the design to its user-facing purpose]

### Goals
- [What experience we're trying to create]

### Constraints
- [Machine-checkable or reviewable boundaries]

### Non-goals
- [What we explicitly decided NOT to do]
```

Write-once: established at creation/Active transition. If intent fundamentally changes, Supersede the DESIGN. The rest of the document (flows, states, screens) remains mutable.

Write-once is enforced by agent convention, not tooling. The structured format (Goals/Constraints/Non-goals) makes unintentional edits obvious in code review. A hash-based integrity check could be added later but is not in scope.

### 5. Decision protection over repeated asking

When an operator confirms alignment between an Epic and a DESIGN (via `rel: [aligned]` edge on the Epic's `artifact-refs`), swain protects that decision rather than re-asking for each derived SPEC. Integrity checking compares SPEC scope/acceptance criteria against the DESIGN's Goals, Constraints, and Non-goals — only surfacing potential violations.

Traversal path for integrity checks: SPEC → parent EPIC → `artifact-refs` with `rel: [aligned]` → DESIGN → Design Intent section. The relationship model needs updating to reflect this directed edge (EPIC → DESIGN with `aligned` semantics).

### 6. Typed relationship edges (`rel` vocabulary)

`artifact-refs` entries support multiple `rel` types. `sourcecode-refs` entries implicitly carry a `describes` relationship — no explicit `rel` tag needed.

**`artifact-refs` rel types:**

| rel type | Meaning | Used by |
|----------|---------|---------|
| `linked` | Informational cross-reference (default) | All types |
| `documents` | Content dependency, commit-pinned | TRAIN → artifact |
| `aligned` | Alignment decision recorded | EPIC → DESIGN |

**`sourcecode-refs`:** The relationship is always "this DESIGN describes these files." No `rel` field — having an entry implies the `describes` relationship.

### 7. design-check.sh (staleness detection)

New script, sister to `train-check.sh`. Reads `sourcecode-refs`, performs blob SHA comparison, reports: CURRENT / STALE / MOVED / MOVED+STALE / BROKEN.

Exit codes:
- 0 = all refs CURRENT or MOVED (content intact — MOVED paths can be auto-updated)
- 1 = at least one ref is STALE, MOVED+STALE, or BROKEN (content has diverged or is lost)
- 2 = git unavailable (graceful degradation)

### 8. Integration hooks

**Automated (script-level):**
- **specwatch scan**: add `design-check.sh` call parallel to existing `train-check.sh` integration (specwatch.sh needs a new integration block, ~10 lines mirroring the train-check pattern)
- **swain-sync pipeline**: add `design-check.sh` alongside Step 3.7 (ADR compliance check). Advisory, not blocking — report drift but don't fail the sync.
- **DESIGN lifecycle hooks**:
  - Creation: validate all `sourcecode-refs` paths exist at HEAD
  - Proposed → Active: validate all refs are CURRENT (existence + blob match)
  - Active → Superseded: new DESIGN inherits `sourcecode-refs` from old (with fresh pins)

**Agent-level (judgment):**
- SPEC Implementation transition: surface linked DESIGN's Intent for alignment awareness
- SPEC completion: cross-reference changed files against `sourcecode-refs`, nudge to update DESIGN and re-pin
- SPEC derivation under aligned Epic: check SPEC scope against DESIGN constraints, flag violations
- DESIGN modified but `sourcecode-refs` blobs unchanged: surface as "design evolved, code hasn't caught up" (design→code drift direction)

## Out of Scope

- Frontmatter schema versioning (`schema: v2`) and template compression — separate SPEC
- Code-level visual drift detection (CSS token snapshots, DOM fingerprinting) — future enhancement
- `artifact-refs` migration for existing TRAIN definitions — separate small SPEC
- `rel` type vocabulary as a formal schema — include in frontmatter schema SPEC

## Implementation Notes

- The relationship model (`references/relationship-model.md`) needs updating to reflect EPIC → DESIGN `aligned` edges and DESIGN → sourcecode `describes` relationships.
- `design-check.sh` also needs a `--repin` mode (or companion script) to update `sourcecode-refs` blob SHAs and commits after the operator confirms a DESIGN update. Detection without remediation creates maintenance burden.

## Open Questions

1. Should `sourcecode-refs` support glob patterns (e.g., `src/components/Button/**`) for tracking entire component directories, or only individual files?
2. Should the alignment integrity check (SPEC vs DESIGN constraints) be a formal script or remain an agent-level workflow step?
3. What happens when multiple DESIGNs reference the same source file? Should `design-check.sh` warn about this, or is it expected (e.g., a shared component described by both a page-level and component-level design)?
4. How should design→code drift be detected? (DESIGN's mutable sections changed since last `sourcecode-refs` pin, but the pinned blobs haven't changed — the design evolved but code hasn't caught up.) One option: compare DESIGN's `last-updated` date against `sourcecode-refs` `verified` dates.
