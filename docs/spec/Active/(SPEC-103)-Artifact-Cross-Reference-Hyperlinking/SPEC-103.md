---
title: "Artifact cross-reference hyperlinking"
artifact: SPEC-103
track: implementable
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: enhancement
parent-epic: ""
parent-initiative: INITIATIVE-003
linked-artifacts:
  - SPEC-094
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Artifact cross-reference hyperlinking

## Problem Statement

Artifact references throughout the docs tree — in frontmatter fields (`linked-artifacts`, `depends-on-artifacts`, `parent-epic`, `parent-initiative`, `addresses`) and in body text — are plain-text IDs (e.g., `SPEC-045`, `EPIC-031`). They are not navigable: clicking does nothing in any markdown renderer. When artifacts move between phase directories (Active → Complete), references pointing at the old path silently break with no detection or repair mechanism.

## External Behavior

### 1. Hyperlinked references in body text

When swain-design creates or transitions an artifact, artifact ID references in **body text** (everything below the frontmatter fence) are emitted as relative markdown links:

- **Body text:** `[SPEC-045](../../spec/Active/(SPEC-045)-Whatever/SPEC-045.md)`

Paths are relative from the referencing artifact's directory to the referenced artifact's current location on disk.

**Frontmatter values remain plain IDs.** YAML frontmatter is machine-parsed — embedding markdown link syntax would break tooling that expects bare artifact IDs (specwatch, chart.sh, rebuild-index.sh). Staleness checking covers frontmatter by resolving the plain ID to a path and verifying the target exists, not by embedding links.

### 2. Broken-link detection in specwatch

`specwatch.sh scan` detects hyperlinked artifact paths that no longer resolve to a file. Output format:

```
BROKEN_LINK SPEC-098.md:12 -> docs/spec/Active/(SPEC-045)-Whatever/SPEC-045.md (file not found)
```

Exit code 1 when any broken links are found.

### 3. Relink command

A new `relink.sh` script (or `specwatch.sh relink`) resolves all broken artifact hyperlinks by scanning the docs tree for the referenced artifact ID and updating the path:

```bash
bash scripts/relink.sh                    # relink all broken refs
bash scripts/relink.sh SPEC-098.md        # relink refs in one file
```

### 4. Phase-transition auto-relink

When swain-design moves an artifact between phase directories, all documents that hyperlink to the moved artifact are updated in the same commit. This is integrated into the phase-transition workflow, not a separate manual step.

## Acceptance Criteria

- **Given** a new artifact is created with `linked-artifacts: [SPEC-045]`, **When** `specwatch.sh scan` runs, **Then** specwatch resolves the plain ID to a path and verifies the target exists
- **Given** an artifact body mentions `EPIC-031` as plain text, **When** swain-design writes the file, **Then** the body reference is a clickable markdown link with a relative path
- **Given** an artifact was moved from `Active/` to `Complete/`, **When** `specwatch.sh scan` runs, **Then** any hyperlinks pointing at the old `Active/` path are reported as `BROKEN_LINK`
- **Given** broken hyperlinks exist, **When** `relink.sh` runs, **Then** all broken links are resolved to the artifact's current path on disk
- **Given** an artifact transitions phases, **When** swain-design moves the directory, **Then** all inbound hyperlinks across the docs tree are updated in the same commit
- **Given** an artifact's directory slug is renamed (e.g., `(SPEC-045)-Old-Title` → `(SPEC-045)-New-Title`), **When** `relink.sh` runs, **Then** broken links are resolved by stable artifact ID, not by old path

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Frontmatter values stay as plain artifact IDs — no markdown link syntax in YAML. SPEC-094 adds a `rel-path` attribute to `artifact-refs` entries for structured navigation; the relink tool should update `rel-path` fields when present
- The relink tool must handle all artifact ID patterns: `SPEC-NNN`, `EPIC-NNN`, `INITIATIVE-NNN`, `VISION-NNN`, `SPIKE-NNN`, `ADR-NNN`, `PERSONA-NNN`, `RUNBOOK-NNN`, `DESIGN-NNN`, `JOURNEY-NNN`, `TRAIN-NNN`
- Relative paths must be computed from the referencing file's directory, not the repo root
- Performance: relink must handle 200+ artifacts without noticeable delay (< 5s)
- Non-goal: hyperlinking references inside code, scripts, or skill files — only `docs/` artifacts

## Implementation Approach

1. **Link resolution library** (`scripts/resolve-artifact-link.sh`): given an artifact ID and a source file path, locate the artifact on disk and return the relative path
2. **Authoring integration**: update swain-design's artifact creation workflow to call the resolver when writing body text references (frontmatter stays as plain IDs)
3. **specwatch extension**: add a `BROKEN_LINK` finding type that checks all `](...)` paths in artifact files against the filesystem
4. **relink command**: iterate all `BROKEN_LINK` findings and patch the paths using the resolver
5. **Phase-transition hook**: after `git mv`, run relink on all files that reference the moved artifact ID

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | — | Initial creation |
