---
title: "All Artifacts Must Be Foldered"
artifact: ADR-027
track: standing
status: Active
author: Cristos L-C
created: 2026-04-03
last-updated: 2026-04-03
linked-artifacts:
  - SPEC-225
  - SPEC-226
  - ADR-026
depends-on-artifacts: []
evidence-pool: ""
---

# All Artifacts Must Be Foldered

## Context

Swain artifacts started as flat Markdown files (e.g. `SPEC-183-title.md` sitting in `docs/spec/Active/`). Over time, features began needing storage beyond the main document. Verification logs ([SPEC-226](../../../spec/Active/(SPEC-226)-Verification-Evidence-Recording/(SPEC-226)-Verification-Evidence-Recording.md)) and relationship symlinks ([SPEC-249](../../../spec/Proposed/(SPEC-249)-Materialize-Related-Artifacts-Symlinks/(SPEC-249)-Materialize-Related-Artifacts-Symlinks.md)) both need a folder.

When the materializer hits a flat file and needs to create `_Related/` symlinks, it builds a directory at the file's path minus `.md`. This creates shadow directories next to the flat file -- untracked and rebuilt on every `chart.sh build`. The materializer should not create directories. It should work with what exists.

About 17 flat-file ADRs and one flat-file SPEC remain in this repo. Newer artifacts use folders, but there is no rule and no migration for the backlog.

## Decision

Every artifact must live in a folder named `(TYPE-NNN)-Title/` with the primary file `(TYPE-NNN)-Title.md` inside it. Flat files at the phase level are not allowed.

This applies to all artifact types in all consumer projects, not just the swain source repo.

**Enforcement points:**

1. **swain-design** -- always `mkdir -p` the folder before writing the file. Most types already do this. This ADR makes it a hard rule for all types, including ADRs.

2. **swain-doctor** -- detect flat files in any project, report them, and auto-migrate via `git mv`. This check covers all artifact types, not just specs and epics.

3. **The materializer** -- must not `mkdir -p` artifact paths. If a path does not exist as a directory, skip that artifact for both hierarchy and relationship symlinks. Doctor fixes structure; the materializer only reads it.

## Alternatives Considered

1. **Keep flat files, store data elsewhere.** Put symlinks and logs in a central directory keyed by ID. Avoids one folder per artifact, but splits state across locations.

2. **Let the materializer create directories.** This is the current (broken) behavior. The materializer should link, not build structure. Mixing roles creates shadow directories.

3. **Only enforce for new artifacts.** Creates a two-tier system forever. Doctor already has migration logic ([SPEC-225](../../../spec/Active/(SPEC-225)-Flat-Artifact-Migration/(SPEC-225)-Flat-Artifact-Migration.md)); full migration cost is low.

## Consequences

- Every artifact gets a folder that can hold logs, symlinks, and future metadata with no structural changes needed.

- The materializer gets simpler -- it only creates symlinks in existing folders, never creates folders.

- Doctor gives any consumer project a single migration path for legacy flat files.

- One-time migration cost for existing flat files (~17 ADRs, 1 SPEC in this repo). Doctor handles it.

- Single-file ADRs feel over-packaged in a folder. The benefit of uniform structure outweighs the clutter.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-03 | -- | Retroactive ADR; folder convention already in practice for most types |
