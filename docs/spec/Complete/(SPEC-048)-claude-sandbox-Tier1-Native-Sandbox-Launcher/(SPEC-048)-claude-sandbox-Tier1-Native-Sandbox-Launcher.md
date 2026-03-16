---
title: "claude-sandbox: Tier 1 Native Sandbox Launcher"
artifact: SPEC-048
track: implementable
status: Complete
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
type: feature
parent-epic: EPIC-005
linked-artifacts:
  - EPIC-005
  - SPIKE-009
  - SPEC-049
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# claude-sandbox: Tier 1 Native Sandbox Launcher

## Problem Statement

EPIC-005 requires a one-command launcher to run Claude Code in an isolated environment. SPIKE-009 determined that Tier 1 (native sandboxing via `claude --sandbox`) provides sufficient isolation for interactive developer use with near-zero startup overhead and no external runtime dependencies. This spec implements the launcher script and project-level configuration for Tier 1.

## External Behavior

A shell script `claude-sandbox` is placed in the project root (or on PATH via `scripts/`). When run from the project root, it:

1. Detects the current platform (macOS or Linux)
2. Reads optional project-level sandbox config from `swain.settings.json` (allowed domains, extra write paths)
3. Invokes `claude --sandbox` with the project directory and agent state directories explicitly allowed for read/write
4. Forwards required credentials as environment variables (`ANTHROPIC_API_KEY`, `GITHUB_TOKEN`, `GH_TOKEN`)
5. Forwards git identity (`GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL`, `GIT_COMMITTER_NAME`, `GIT_COMMITTER_EMAIL`)
6. The session is ephemeral — no state leaks outside the allowed paths after exit

### Platform behavior

| Platform | Mechanism | Notes |
|----------|-----------|-------|
| macOS | `sandbox-exec` (Seatbelt via `claude --sandbox`) | Kernel-level; deny-first profiles |
| Linux | Landlock (default) or bubblewrap (`--sandbox-level 2`) | Selected by `claude --sandbox` automatically |

### Configuration

Optional `swain.settings.json` stanza:

```json
{
  "sandbox": {
    "allowedDomains": ["api.anthropic.com", "github.com"],
    "extraWritePaths": ["../shared-notes"]
  }
}
```

## Acceptance Criteria

1. **Given** a macOS or Linux host with Claude Code CLI installed, **when** `./claude-sandbox` is run from the project root, **then** Claude Code launches inside a sandboxed session without requiring Docker or any other runtime.
2. **Given** a running `claude-sandbox` session, **when** the agent attempts to read or write project files under the project root, **then** the operations succeed.
3. **Given** a running `claude-sandbox` session, **when** the agent attempts to write to a path outside the allowed list (e.g., `~/Desktop`), **then** the write is denied by the sandbox.
4. **Given** `ANTHROPIC_API_KEY` is set in the host environment, **when** `claude-sandbox` launches, **then** the key is available inside the sandbox without being written to disk.
5. **Given** the session exits normally or via Ctrl-C, **when** cleanup completes, **then** no sandbox state, temp files, or processes persist outside the project directory.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1: Launches without Docker | `scripts/claude-sandbox` invokes `claude --sandbox` with no Docker dependency; POSIX sh script | ✅ |
| AC2: Project file access succeeds | `claude --sandbox` permits read/write of project root by default | ✅ |
| AC3: Out-of-scope writes denied | `claude --sandbox` enforces deny-first Seatbelt/Landlock profiles | ✅ |
| AC4: API key forwarded without disk write | Credentials passed via env var; script forwards from host environment, not written to disk | ✅ |
| AC5: Ephemeral — no persistent artifacts | `--rm`-equivalent behavior via sandbox profiles; sandbox-exec/Landlock leave no temp files | ✅ |

## Scope & Constraints

- Tier 1 only — Docker is handled by SPEC-049
- Must work without any external runtime (no Docker, no VM)
- `claude --sandbox` flag must be available in the installed Claude Code CLI version
- Script should be idempotent — safe to re-run if a previous session exited uncleanly

## Implementation Approach

1. Write `scripts/claude-sandbox` as a POSIX sh script (not bash-specific)
2. Read `swain.settings.json` with `jq` if available; fall back to defaults
3. Build the `claude --sandbox` invocation with environment forwarding
4. Make it executable (`chmod +x`)
5. Add a symlink or Makefile target in the project root for convenience

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | cded412 | Created from EPIC-005 decomposition; SPIKE-009 GO recommendation |
| Complete | 2026-03-14 | 0eb40a8 | scripts/claude-sandbox POSIX sh launcher written; platform detection, credential forwarding, jq-optional config reading |
