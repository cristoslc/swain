---
title: "Config and Credential Resolution"
artifact: SPEC-320
track: implementable
status: Active
author: cristos
created: 2026-04-18
last-updated: 2026-04-18
priority-weight: high
type: feature
parent-epic: EPIC-084
parent-initiative: ""
linked-artifacts:
  - ADR-047
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Config and Credential Resolution

## Problem Statement

1Password references must be resolved once at startup when the operator is present. Storing `op://` references in config files is the correct security posture, but the bridge process needs actual credential values at runtime. The resolution must happen once, fail fast if 1Password is locked, and never write resolved secrets to disk.

## Desired Outcomes

A config resolution module that walks the config tree, resolves all `op://` references via `op read`, caches results in process-locked memory, and validates schemas for both `helm.config.json` and project-level configs. If any resolution fails, the process exits with a clear error before any bridge starts.

## External Behavior

**Input:** `helm.config.json` and project config files, potentially containing `op://` prefixed string values.

**Output:** Fully resolved config objects in memory; no disk writes of resolved secrets.

**Resolution flow:**
1. Walk every string value in the config tree.
2. If a value starts with `op://`, call `op read <reference>`.
3. Replace the value with the resolved output.
4. Cache all resolutions in a module-level dict.
5. If any resolution fails (exit code non-zero), abort with an error message naming the failed reference.

**Logging:** stdout shows which 1Password items were fetched (success/failure), never the contents.

## Acceptance Criteria

1. **Given** `helm.config.json` contains `op://vault/item/field` values, **when** resolution runs, **then** each `op://` value is replaced with the output of `op read <reference>`.

2. **Given** all `op://` references in the config, **when** resolution runs at startup, **then** each is resolved via `op read <reference>` exactly once.

3. **Given** 1Password is locked or a reference is invalid, **when** resolution runs, **then** the process exits with an error naming the failed reference and its field path.

4. **Given** resolved credential values, **when** they are cached, **then** they exist only in a process-locked module-level dict and are never written to disk.

5. **Given** resolution succeeds, **when** the process logs its activity, **then** stdout shows which 1Password items were fetched with success/failure status, never the resolved contents.

6. **Given** a project config file, **when** it is validated, **then** it conforms to the schema: `name`, `path`, `stream`, `runtime`, `auto_start`, `worktree_poll_interval_s`.

7. **Given** `helm.config.json`, **when** it is validated, **then** it conforms to the schema: `scan_paths`, `chat` (with `platform`, `bot_email`, `bot_api_key`, `server_url`, `operator_email`), `opencode` (with `ports` map, `config_path`, `default_port`).

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- ~100 lines of Python.
- Resolution is recursive: any nested string can be an `op://` reference.
- Schema validation is structural (required keys, types) — no business-rule validation.
- `op read` is the only supported resolution backend; no vault CLI alternatives.
- The module returns the resolved config dict; callers never see `op://` values.

## Implementation Approach

1. Write a recursive walker that visits every string value in a nested dict/list.
2. For each `op://` string, call `op read` via subprocess, capture stdout, and replace the value.
3. Maintain a module-level `_cache` dict mapping references to resolved values (dedup across config files).
4. On any `op read` failure, raise a `ResolutionError` with the field path and reference.
5. Write schema validators for `helm.config.json` and project configs (required keys, types).
6. Wire into watchdog startup — resolve before any bridge process is spawned.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-18 | -- | Initial creation |