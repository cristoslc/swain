---
title: "swain-keys 1Password SSH Program Override"
artifact: SPEC-014
status: Draft
type: bug
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
parent-epic:
linked-research: []
linked-adrs: []
depends-on: []
addresses: []
evidence-pool: ""
source-issue: "github:cristoslc/swain#37"
swain-do: required
---

# swain-keys 1Password SSH Program Override

## Problem Statement

When 1Password's SSH signing program (`op-ssh-sign`) is configured globally — even in an included config file like `~/.config/git/linux.gitconfig` — `swain-keys --provision` generates a project-specific file-based signing key but commits fail because `op-ssh-sign` cannot use plain file keys:

```
error: 1Password: invalid ssh public key
fatal: failed to write commit object
```

`git config gpg.ssh.program` (without `--global`) resolves the effective value from all config sources including includes, so it reliably detects the problem.

## External Behavior

During `step_configure_git_signing`, swain-keys checks if `gpg.ssh.program` resolves to a 1Password binary (`op-ssh-sign`). If detected, it sets `git config --local gpg.ssh.program ssh-keygen` to override with the standard SSH signing implementation that works with file-based keys.

## Acceptance Criteria

- **Given** `gpg.ssh.program` resolves to a path containing `op-ssh-sign`, **when** swain-keys configures signing, **then** it sets `--local gpg.ssh.program ssh-keygen`
- **Given** `gpg.ssh.program` is not set or is not 1Password, **when** swain-keys configures signing, **then** no override is added
- **Given** the override is applied, **when** the user commits, **then** the file-based key signs successfully

## Scope & Constraints

- Fix is scoped to `skills/swain-keys/scripts/swain-keys.sh` `step_configure_git_signing()` function
- Uses substring match on `op-ssh-sign` to catch any install path
- Does not affect projects that don't use swain-keys provisioned keys

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-13 | — | Initial creation from GitHub #37 |
