---
title: "swain-box: Unified Sandbox Launcher"
artifact: SPEC-092
track: implementable
status: Active
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
type: feature
parent-epic: ""
parent-initiative: INITIATIVE-013
parent-vision: VISION-002
linked-artifacts:
  - ADR-008
  - DESIGN-002
  - DESIGN-005
  - EPIC-040
  - EPIC-037
  - INITIATIVE-017
  - SPEC-067
  - SPEC-068
  - SPEC-071
  - SPEC-081
  - SPEC-100
  - SPEC-101
  - SPIKE-032
  - SPIKE-034
depends-on-artifacts:
  - SPIKE-034
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
supersedes: ""
---

# swain-box: Unified Sandbox Launcher

## Problem Statement

swain-box has accumulated complexity from multiple specs (067, 068, 071, 081) built on flawed assumptions — `claude --sandbox` doesn't exist, Docker Sandboxes breaks Claude OAuth, and worktree management doesn't belong in the launcher. SPIKE-034 proved that Docker's sandbox template images work in regular `docker run` containers with full OAuth support. This spec rewrites swain-box as a clean two-step launcher: pick a runtime, pick an isolation mode, launch with session startup.

## External Behavior

### Two-step selection menu

**Step 1 — Runtime:**
```
swain-box: Multiple agent runtimes available. Select one:
  1) claude
  2) copilot
  3) codex
  4) gemini
  5) kiro
  6) opencode
Choice [1]: 1
```
Detection via `docker sandbox create --help`. Default 1.

**Step 2 — Isolation:**
```
swain-box: Select isolation for claude:
  1) Docker Sandboxes (microVM) ⚠ OAuth/Max broken — requires ANTHROPIC_API_KEY
  2) Docker Container — OAuth/Max works via /login
Choice [1]: 2
```
Always shown. Default 1 (microVM). Annotations:
- If known issues exist for the runtime + microVM combo: show warning
- If no known issues: show "recommended, strongest isolation"

### Launch paths

**microVM:** `docker sandbox run <runtime> <project-path> [-- <agent-args>]`

**Container:** `docker run -it --name <sandbox-name> -v <project-path>:/home/agent/workspace docker/sandbox-templates:<image-tag> [<agent-args>]`
- Container persists (no `--rm`) — credentials and state survive reconnects
- Reconnect: `docker start -ai <sandbox-name>` if container exists but is stopped
- Image tag mapping: `claude` → `claude-code`, others → runtime name

### Prompt injection

Per-runtime initial prompt that triggers session startup:

| Runtime | Mechanism | Default prompt |
|---------|-----------|---------------|
| claude | Positional arg after flags | `/swain-session` |
| others | Unknown — print reminder | `NOTE: run /swain-session to start` |

Override with `--prompt "custom message"`.

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--runtime=NAME` | auto-detect | Skip runtime menu |
| `--isolation=MODE` | menu | Skip isolation menu (`microvm` or `container`) |
| `--prompt=TEXT` | `/swain-session` | Initial prompt for the agent session |
| `[path]` | `$PWD` | Project directory |

### Cleanup

`./swain-box --cleanup NAME` removes the Docker container (and Docker Sandbox if applicable) for the named sandbox.

### Non-interactive mode

Both menus auto-select defaults with warnings to stderr. `--runtime` and `--isolation` flags bypass menus.

## Acceptance Criteria

**AC-1:** Runtime detection uses `docker sandbox create --help` (instant, no hanging probes)
**AC-2:** Isolation menu always shows with runtime-specific annotations
**AC-3:** microVM path launches via `docker sandbox run`
**AC-4:** Container path launches via `docker run` with persistent container
**AC-5:** Container reconnects to existing stopped container via `docker start -ai`
**AC-6:** Claude gets `/swain-session` as initial prompt via positional arg
**AC-7:** Unknown runtimes get a reminder to run session startup manually
**AC-8:** `--prompt` overrides the default initial prompt
**AC-9:** `--cleanup` removes container and/or sandbox
**AC-10:** Known issues (Claude+OAuth on microVM) shown in isolation menu

## Scope & Constraints

- POSIX sh only
- No worktree management — the agent handles that via session startup
- No `claude-sandbox` delegation — deleted, not needed
- No `--credentials` flag — credential handling is per-isolation-mode (proxy for microVM, env vars or /login for container)
- Known issues table is a simple case statement, not a config file

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-19 | — | Rewrite based on brainstorming + SPIKE-034 findings |
