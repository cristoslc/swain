---
title: "Credential-Scoped Sandbox Launcher"
artifact: SPEC-071
track: implementable
status: Complete
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
type: feature
parent-epic: ""
parent-initiative: INITIATIVE-011
parent-vision: VISION-002
linked-artifacts:
  - EPIC-030
  - SPEC-067
  - SPEC-068
  - SPIKE-031
  - SPIKE-032
depends-on-artifacts:
  - SPIKE-031
  - SPIKE-032
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Credential-Scoped Sandbox Launcher

## Problem Statement

swain-box (SPEC-067) launches agents in Docker Sandboxes but passes credentials without scoping — the agent receives whatever the operator's environment provides. For unattended operation, agents should receive only the credentials they need, injected at the sandbox boundary, never persisted inside the sandbox.

## External Behavior

**Input:** `swain-box [--credentials <scope>] <workspace-path>`

- `--credentials minimal` (default for unattended): passes only ANTHROPIC_API_KEY / CLAUDE_CODE_OAUTH_TOKEN and a scoped git credential
- `--credentials full`: passes the operator's full credential set (current behavior, for attended use)
- Credential scope definitions live in a config file (`.swain-box/credentials.yaml` or equivalent)

**Output:** Docker Sandboxes session launched with scoped credentials. Credential scope echoed to stderr on launch.

**Preconditions:** Docker Desktop >= 4.58, `docker sandbox` available, workspace path exists.

**Postconditions:** Agent inside sandbox can access only the credentials in the declared scope. No credentials persisted in sandbox filesystem or image layers.

## Acceptance Criteria

- Given `--credentials minimal`, when swain-box launches, then only the declared minimal credential set is available inside the sandbox
- Given `--credentials full`, when swain-box launches, then the full operator credential set is available (backward-compatible)
- Given no `--credentials` flag in unattended mode, when swain-box launches, then minimal credentials are used by default
- Given a credential scope that references a missing credential, when swain-box launches, then it warns on stderr but does not block launch
- Given any credential scope, when the sandbox exits, then no credentials are persisted in the sandbox filesystem

## Scope & Constraints

- SPIKE-031 confirmed: native sandbox cannot scope env vars at kernel level, but `env -i` provides effective application-level scoping
- SPIKE-032 confirmed: Docker Sandboxes already scopes credentials via MITM proxy; OAuth broken, API key path works
- Does not change sandbox type selection logic (that's EPIC-030/SPEC-068)
- Does not implement network allowlists (future scope)
- Does not cover file-based credentials (~/.aws, keychain) — env var scoping only

## Implementation Approach

### Native launcher (`scripts/claude-sandbox`)
1. Add `--credentials` flag: `minimal` (default) or `full`
2. When `minimal`: wrap the `claude --sandbox` invocation with `env -i`, passing only:
   - `HOME`, `PATH`, `TERM`, `LANG`, `USER`, `SHELL`, `TMPDIR` (required for shell operation)
   - `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` (whichever is set)
   - `GH_TOKEN` or `GITHUB_TOKEN` (for git operations)
3. When `full`: current behavior (no `env -i`)
4. Echo credential scope to stderr on launch

### Docker Sandboxes launcher (`skills/swain/scripts/swain-box`)
1. Add `--credentials` flag for API symmetry (Docker Sandboxes always scopes via proxy)
2. Echo credential scope info on launch
3. No functional change — proxy-managed isolation is already the strongest posture

### Architecture overview update
Update the Credential Scoping Model table in `docs/vision/Active/(VISION-002)-Safe-Autonomy/architecture-overview.md` with findings from both spikes.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-19 | — | Created for INITIATIVE-011; blocked on SPIKE-031 and SPIKE-032 |
| Active | 2026-03-19 | — | Spikes complete (both Conditional Go); implementing credential scoping |
| Complete | 2026-03-19 | — | env -i wrapper in claude-sandbox, --credentials flag in both launchers, arch overview updated |
