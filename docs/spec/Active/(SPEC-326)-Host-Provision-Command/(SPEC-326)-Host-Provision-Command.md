---
title: "Host Provision Command"
artifact: SPEC-326
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
  - ADR-047
depends-on-artifacts:
  - SPEC-319
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Host Provision Command

## Problem Statement

The `swain-helm host provision` command is listed in EPIC-074 success criteria but has no implementation spec. The operator needs a single command to register the Zulip bot, create streams, and write the helm config file.

## Desired Outcomes

Running `swain-helm host provision` with the required flags writes `~/.config/swain-helm/helm.config.json` with `op://` credential references, creates the Zulip stream, and prints next steps. First run completes in under 5 minutes.

## External Behavior

**Command:** `swain-helm host provision --zulip-site URL --zulip-email EMAIL --zulip-api-key KEY --operator-email EMAIL --project NAME --project-path PATH`

**Steps:**
1. Validate that `op` CLI is available (if `op://` references are used).
2. Register the Zulip bot by verifying credentials.
3. Create the project stream with a control topic.
4. Write `helm.config.json` with `op://` references (never plaintext secrets).
5. Set file permissions to 600.
6. Print instructions for starting the daemon.

## Acceptance Criteria

1. **Given** the operator runs `swain-helm host provision`, **when** all flags are provided, **then** a `helm.config.json` is written to `~/.config/swain-helm/`.

2. **Given** the config file is written, **when** it is read, **then** it contains `op://` references for credentials, not plaintext secrets.

3. **Given** the Zulip credentials are valid, **when** provision runs, **then** a stream is created with a control topic welcome message.

4. **Given** the config file, **when** `stat` is checked, **then** permissions are 600.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- ~60 lines of Python in `provision.py`.
- Reuse existing `provision()` function — update it to use `op://` references by default.
- The welcome message mentions swain-helm commands (not the old untethered commands).

## Implementation Approach

1. Update `provision.py` to accept `op://` credential references and write them as-is.
2. Add a `cmd_host_provision` entry in the CLI that calls `provision()`.
3. Ensure file permissions are set on the config output.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-18 | -- | Initial creation |