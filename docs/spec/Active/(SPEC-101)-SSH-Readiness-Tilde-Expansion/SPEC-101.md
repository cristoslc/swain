---
title: "ssh-readiness.sh: expand tilde in IdentityFile path before file test"
artifact: SPEC-101
track: implementable
status: Implementation
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: bug
parent-epic: ""
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: "gh#80"
swain-do: required
---

# ssh-readiness.sh: expand tilde in IdentityFile path before file test

## Problem Statement

`ssh-readiness.sh` reads the `IdentityFile` value from SSH config via awk, which returns the literal string (e.g., `~/.ssh/project_signing`). The subsequent `[[ -f "$alias_key" ]]` test fails because bash/zsh only expand `~` in unquoted contexts. This causes false-positive "missing key" reports on every preflight run, triggering unnecessary swain-doctor invocations.

## External Behavior

**Inputs:** SSH config file with `IdentityFile ~/.ssh/<key>` (standard SSH convention)
**Preconditions:** Key file exists at the expanded path
**Expected output:** `ssh-readiness.sh --check` exits 0, no false ISSUE reports
**Constraints:** Must not break configs using `$HOME` or absolute paths

## Acceptance Criteria

- **Given** an SSH config with `IdentityFile ~/.ssh/project_signing`, **When** `ssh-readiness.sh --check` runs and the key exists, **Then** no ISSUE is reported
- **Given** an SSH config with `IdentityFile /Users/foo/.ssh/key`, **When** the key exists, **Then** behavior is unchanged (no regression)
- **Given** an SSH config with `IdentityFile ~/.ssh/missing_key`, **When** the key does NOT exist, **Then** the ISSUE is correctly reported
- Tilde expansion applies in both `--check` and `--repair` code paths

## Implementation Notes

After `read_identity_file` returns, expand tilde before any `-f` test:

```bash
alias_key="${alias_key/#\~/$HOME}"
```

This is a one-line fix applied once, right after line 127 where `alias_key` is assigned.
