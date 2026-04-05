---
title: "RTK As Optional Git Compression Dependency"
artifact: ADR-029
track: standing
status: Active
author: Cristos L-C
created: 2026-04-03
last-updated: 2026-04-03
linked-artifacts:
  - DESIGN-017
  - SPEC-253
depends-on-artifacts: []
evidence-pool: "trove: rtk-cli-token-compression@c94bfc1"
---

# RTK As Optional Git Compression Dependency

## Context

SPEC-253 introduced `.agents/bin/git-compact`, a wrapper that routes high-noise git commands (diff, log, status) through RTK for context-window compression. The script falls back transparently to raw git when RTK is absent. The question is how swain should treat RTK as a dependency.

Swain already has a pattern for optional external tools: `jq`, `gh`, `tmux`, `uv`, `fswatch`, and `ssh` are all detected by swain-doctor, reported with degradation notes, and never installed automatically. None require Homebrew — Homebrew is suggested as an install hint on macOS but is not itself a dependency.

RTK is an MIT-licensed Rust binary distributed via Homebrew, curl installer, and pre-built binaries.

## Decision

RTK is an **optional tool** — same category as `gh`, `tmux`, and `fswatch`. It is detected by swain-doctor via `command -v rtk` and listed in the tool-availability table with its degradation behavior. Swain never installs it automatically.

When RTK is absent, `git-compact` passes all commands through to raw git with no warning, no error, and no behavioral difference. The only signal is swain-doctor's tool availability report at session start.

## Alternatives Considered

1. **Vendor the RTK binary in `.agents/bin/`** — Rejected. A ~5MB Rust binary in git bloats the repo, requires manual updates per platform, and adds a maintenance burden for a tool that provides a performance optimization, not a functional requirement.

2. **Auto-install via curl in `swain-init`** — Rejected. Swain never installs tools automatically (established pattern). Running `curl | sh` without operator consent violates the principle of least surprise and the project's safety posture.

3. **Require RTK (hard dependency)** — Rejected. `git-compact` is an optimization, not a gate. Making RTK required would block sessions on machines where it can't be installed and adds friction to onboarding.

4. **Do nothing (no doctor detection)** — Rejected. Operators should know when an optimization is available but not active. The doctor table costs nothing and follows the existing pattern.

## Consequences

**Positive:**
- Zero-friction onboarding — swain works identically with or without RTK
- Consistent with how every other optional tool is handled
- Operators who want compression install once and forget; those who don't are unaffected
- No binary vendoring, no platform matrix, no update maintenance

**Accepted downsides:**
- Operators must install RTK themselves — no automatic provisioning
- Doctor detection adds one more line to the tool-availability check, but this is trivial
- RTK version drift is the operator's responsibility (Homebrew handles updates via `brew upgrade rtk`)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-03 | 1e95f94 | Initial creation |
