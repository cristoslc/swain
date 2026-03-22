---
title: "Auto-Populate specwatch-ignore on Supersession"
artifact: SPEC-129
track: implementable
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: enhancement
parent-epic: ""
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Auto-Populate specwatch-ignore on Supersession

## Problem Statement

When swain-design supersedes an artifact, the superseding artifact (or an ADR documenting the decision) intentionally links back to the superseded artifact for provenance. Specwatch flags these as warnings (`target is Superseded`), polluting the scan output with noise the operator must mentally filter every run.

The ignore mechanism exists — `specwatch.sh` reads `.agents/specwatch-ignore` for gitignore-style glob patterns — but nothing in the supersession workflow populates it. The agent must remember to do it manually, and currently doesn't.

## External Behavior

When swain-design transitions an artifact to Superseded:

1. Identify all artifacts that will intentionally link to the superseded artifact after the transition:
   - The superseding artifact (the one whose `superseded-by` or `linked-artifacts` points to the old one)
   - Any ADR created as part of the same operation that references the superseded artifact
   - The superseded artifact itself (its outbound `linked-artifacts` to active children are now frozen history)

2. For each identified file, append a glob pattern to `.agents/specwatch-ignore`:
   ```
   # <ARTIFACT-ID> superseded by <NEW-ID> (<date>)
   docs/<type>/Superseded/(<OLD-ID>)*
   docs/<type>/Active/(<NEW-ID>)*
   ```

3. If `.agents/specwatch-ignore` doesn't exist, create it with a header comment.

4. Deduplicate: don't append a pattern that already exists in the file.

### Constraints

- Patterns use the same gitignore-style globs that `specwatch.sh` already supports.
- Comments explain *why* the pattern exists (which supersession created it).
- Only suppress the specific source file paths — never suppress by artifact ID alone (that would hide legitimate warnings about other files referencing the superseded artifact).

## Acceptance Criteria

- **Given** swain-design transitions INITIATIVE-X to Superseded with superseding INITIATIVE-Y, **when** the transition completes, **then** `.agents/specwatch-ignore` contains patterns for both the superseded and superseding artifacts' paths.
- **Given** an ADR is created that intentionally references a superseded artifact, **when** the ADR is written, **then** its path is added to specwatch-ignore.
- **Given** `.agents/specwatch-ignore` doesn't exist, **when** a supersession occurs, **then** the file is created with a header comment and the relevant patterns.
- **Given** a pattern for the same file already exists in specwatch-ignore, **when** a second supersession references it, **then** no duplicate is added.
- **Given** specwatch runs after a supersession, **when** the intentional references are in the ignore file, **then** they do not appear in the specwatch log.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Implementation target is swain-design's SKILL.md — add ignore-file maintenance to the supersession workflow steps, not a new script.
- The same-type overlap check (step 7.5 in SKILL.md) already handles the supersession transition — the ignore-file step hooks into that flow.
- Phase transition instructions in `references/phase-transitions.md` may also need a line for `→ Superseded` transitions.

## Implementation Approach

1. Add a "specwatch-ignore maintenance" step to SKILL.md's phase transition workflow, specifically for `→ Superseded` transitions.
2. The step runs after the `git mv` and status update but before the post-operation specwatch scan.
3. Logic: read the superseded artifact's path and the superseding artifact's path, append both as glob patterns with a comment to `.agents/specwatch-ignore`.
4. Also add the step to ADR creation when the ADR's `linked-artifacts` includes a Superseded artifact.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | -- | Initial creation |
