---
title: "Multi-Project Registration"
artifact: SPEC-327
track: implementable
status: Active
author: cristos
created: 2026-04-18
last-updated: 2026-04-18
priority-weight: medium
type: feature
parent-epic: EPIC-074
parent-initiative: ""
linked-artifacts:
  - ADR-046
depends-on-artifacts:
  - SPEC-319
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Multi-Project Registration

## Problem Statement

EPIC-074 requires that adding a second project to an existing chat service creates a room and project bridge without re-provisioning. The current `project add` command creates a project config but does not register the stream with the Zulip server.

## Desired Outcomes

When the operator runs `swain-helm project add <path>` on a second project, a Zulip stream is created for that project, a project config is written, and the bridge can start for the new project without re-running `host provision`. This takes under 1 minute.

## External Behavior

**Command:** `swain-helm project add <path> --stream STREAM_NAME`

**Steps:**
1. Verify the path contains `.git/`.
2. Read `helm.config.json` for the Zulip bot credentials.
3. Create (or verify) the Zulip stream for the project.
4. Write a project config at `~/.config/swain-helm/projects/<name>.json`.
5. Print confirmation.

## Acceptance Criteria

1. **Given** an existing `helm.config.json`, **when** the operator adds a second project, **then** a Zulip stream is created and a project config is written.

2. **Given** the existing chat service, **when** a second project is added, **then** the first project bridge is unaffected.

3. **Given** the project config, **when** the bridge starts for the new project, **then** it connects to the same Zulip server with its own stream.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- ~40 lines of Python changes to the `project add` CLI handler.
- Reuse Zulip client from provision module.
- No new config file format — project configs stay at `projects/<name>.json`.

## Implementation Approach

1. Add `--stream` flag to `project add` in `bin/swain-helm`.
2. If `helm.config.json` exists, read Zulip credentials and create the stream.
3. Write project config with stream name.
4. Skip Zulip stream creation if `--stream` is not provided (offline mode).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-18 | -- | Initial creation |