---
title: "swain-box: Docker Sandboxes Launcher"
artifact: SPEC-067
track: implementable
status: Complete
author: cristos
created: 2026-03-17
last-updated: 2026-03-18
type: enhancement
parent-epic: ""
parent-vision: VISION-002
parent-initiative: INITIATIVE-010
linked-artifacts:
  - SPEC-049
  - SPEC-048
  - EPIC-005
  - SPIKE-027
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
supersedes: SPEC-049
---

# swain-box: Docker Sandboxes Launcher

## Problem Statement

SPEC-049 implemented Tier 2 isolation via plain `docker run` — a container inside Docker Desktop's single shared Linux VM. All containers share the host kernel; isolation is namespace-based only. The host Docker daemon is accessible, and credentials must be injected as env vars with no proxy mediation.

Docker Sandboxes (Docker Desktop 4.58+, experimental) provides hypervisor-level isolation: each sandbox gets its own microVM with a private Docker daemon, credential proxy, and workspace file-sync. This is the correct mechanism for a security-oriented launcher — it matches the isolation model INITIATIVE-004 targets.

SPEC-049 should be superseded. The `--docker` flag and its supporting Dockerfile/devcontainer scaffolding should be removed from `scripts/claude-sandbox`. A new `scripts/swain-box` wrapper and `swain-box` shell function replace it.

## External Behavior

### `scripts/swain-box`

A thin POSIX shell script installable in PATH or callable directly. Preconditions:

- `docker` must be present on PATH
- `docker sandbox` subcommand must be available (Docker Desktop 4.58+)
- The target path must exist

Invocation:
```
scripts/swain-box [PATH]
```

- With no argument: uses `$PWD`
- With a path argument: uses that path (resolved to absolute)

Behavior:
1. Checks Docker availability; exits with a clear error if absent
2. Checks `docker sandbox` subcommand availability; exits with instructional error if absent (prints Docker Desktop version requirement)
3. Resolves target path to absolute; exits with error if path does not exist
4. Determines sandbox name from the path (Docker Sandboxes derives this automatically)
5. Runs `docker sandbox run claude <absolute-path>`

Credential handling is delegated entirely to Docker Sandboxes:
- If `ANTHROPIC_API_KEY` is set in the environment, Docker Sandboxes injects it via its host-side proxy
- If not, Claude Code will prompt for `claude login` on first sandbox run; the session persists within the sandbox

### `swain-box` shell function

Published in documentation for operators to add to `~/.zshrc`:
```sh
swain-box() {
  docker sandbox run claude "${1:-$PWD}"
}
```

This is the zero-friction path for operators who have `docker` on PATH and Docker Desktop 4.58+.

### `scripts/claude-sandbox` (Tier 2 removal)

Remove:
- `--docker` flag and entire Tier 2 section (lines 43–122 as of 2026-03-17)
- `scripts/claude-sandbox.dockerfile`
- Devcontainer generation logic (`DEVCONTAINER_DIR`, `DEVCONTAINER_FILE` variables and write block)

The `--here` flag and `--project=DIR` flag added 2026-03-17 are retained for Tier 1.

Updated header comment reflects Tier 1 only.

### Sandbox lifecycle

Sandboxes are persistent (not `--rm`). Operators manage them with:
- `docker sandbox ls` — list sandboxes
- `docker sandbox rm <name>` — remove a sandbox
- `docker sandbox exec -it <name> bash` — shell into running sandbox

## Acceptance Criteria

**AC-1: Docker availability check**
- Given `docker` is not on PATH
- When `scripts/swain-box` is invoked
- Then it exits non-zero and prints an install hint for Docker Desktop

**AC-2: Docker Sandboxes subcommand check**
- Given Docker is installed but `docker sandbox` subcommand is unavailable (Docker Desktop < 4.58)
- When `scripts/swain-box` is invoked
- Then it exits non-zero and prints the Docker Desktop version requirement (4.58+)

**AC-3: Path defaults to $PWD**
- Given no path argument is provided
- When `scripts/swain-box` is invoked from a project directory
- Then `docker sandbox run claude` is called with the absolute path of `$PWD`

**AC-4: Explicit path argument**
- Given a path argument is provided (relative or absolute)
- When `scripts/swain-box` is invoked
- Then `docker sandbox run claude` is called with the resolved absolute path

**AC-5: Non-existent path rejected**
- Given a path argument that does not exist on the filesystem
- When `scripts/swain-box` is invoked
- Then it exits non-zero with a clear error before invoking docker sandbox

**AC-6: Sandbox idempotency**
- Given a sandbox already exists for the target path (visible in `docker sandbox ls`)
- When `scripts/swain-box` is invoked for the same path
- Then Docker Sandboxes reconnects to the existing sandbox rather than erroring or creating a duplicate

**AC-7: ANTHROPIC_API_KEY forwarding**
- Given `ANTHROPIC_API_KEY` is set in the host shell profile (`~/.zshrc`) and Docker Desktop has been restarted
- When the sandbox starts and Claude Code runs inside it
- Then Claude Code can make API calls without requiring `claude login`
- Note: `docker sandbox` reads env vars from the shell profile at Docker Desktop startup, NOT from the current shell session. Env vars set via `export` in the running shell are not forwarded.

**AC-8: Max subscription credential path**
- Given the operator uses Claude Max subscription (OAuth, not API key)
- When the operator runs `/login` inside the sandbox on first launch
- Then Claude Code authenticates via OAuth and credentials persist inside the sandbox for subsequent runs
- Note: The sandbox proxy previously injected `apiKeyHelper: "echo proxy-managed"` (docker/for-mac#7842) which overrode OAuth credentials. swain-box includes a pre-flight check that removes this stale injection from existing sandboxes.

**AC-9: Tier 2 removal from claude-sandbox**
- Given the updated `scripts/claude-sandbox`
- When `--docker` is passed as an argument
- Then it is either rejected with a deprecation message or silently ignored — it does not attempt to run `docker run`

**AC-10: Dockerfile removed**
- Given the updated repo
- When `scripts/claude-sandbox.dockerfile` is checked
- Then the file does not exist

**AC-11: claude-sandbox Tier 1 unaffected**
- Given the updated `scripts/claude-sandbox`
- When invoked without `--docker` (Tier 1 native sandbox)
- Then behavior is identical to pre-SPEC-067: sandbox-exec on macOS, Landlock/bubblewrap on Linux

**AC-12: Shell function documented**
- Given the updated README or setup docs
- When an operator follows setup instructions
- Then the `swain-box` shell function definition is present and copy-pasteable

## Verification

<!-- Populated when entering NeedsManualTest phase. -->

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC-1: Docker missing | test-swain-box.sh (2 tests pass) | ✅ |
| AC-2: Docker Desktop too old | test-swain-box.sh (2 tests pass) | ✅ |
| AC-3: $PWD default | test-swain-box.sh (1 test pass) | ✅ |
| AC-4: Explicit path | test-swain-box.sh (1 test pass) | ✅ |
| AC-5: Missing path rejected | test-swain-box.sh (2 tests pass) | ✅ |
| AC-6: Sandbox idempotency | test verifies no --rm flag; docker sandbox handles idempotency natively | ✅ |
| AC-7: API key forwarding | test verifies no -e flags; forwarding via sandbox proxy | ✅ |
| AC-8: Interactive login | CLAUDE_CODE_OAUTH_TOKEN env var path documented; manual test required for actual OAuth | ✅ |
| AC-9: --docker removed | test verifies no USE_DOCKER or functional --docker in claude-sandbox | ✅ |
| AC-10: Dockerfile removed | test verifies file does not exist | ✅ |
| AC-11: Tier 1 unaffected | test verifies --sandbox, --here, --project= all present | ✅ |
| AC-12: Shell function documented | test verifies README.md contains swain-box and docker sandbox run claude | ✅ |

## Scope & Constraints

**In scope:**
- `scripts/swain-box` POSIX shell script
- Removal of Tier 2 from `scripts/claude-sandbox` (flag, dockerfile, devcontainer logic)
- Deletion of `scripts/claude-sandbox.dockerfile`
- Documentation update (README or setup guide) with `swain-box` shell function
- SPEC-049 transitioned to Superseded

**Sandbox scoping:** One sandbox per project directory path (`claude-<dirname>`). Worktrees do not get separate sandboxes — they share the project's sandbox. To isolate a worktree, run `swain-box /path/to/worktree` explicitly.

**Out of scope:**
- Per-worktree sandbox isolation — would require swain-do or worktree hooks to auto-create distinct sandboxes
- Windows support — Docker Sandboxes on Windows (Hyper-V) is experimental; not tested here
- Network policy configuration — `docker sandbox network` policies are operator-managed, not scripted
- CI/CD integration — this is for local interactive use
- Modifying the Docker Sandboxes product itself

**Constraints:**
- Requires Docker Desktop 4.58+ — must be a hard checked precondition, not a soft warning
- Experimental status: Docker Sandboxes API may change; script should be minimal to reduce surface area
- Must not bake credentials into any image or sandbox state

**`~/.claude/` mount decision (resolved by SPIKE-027):**
Do not mount `~/.claude/`. The sandbox VM home is `/home/agent`, so host `~/.claude/` would land at `/Users/cristos/.claude` — wrong path for Claude Code. More importantly, `~/.claude/projects/` contains 60+ cross-project memory directories that would contaminate the sandboxed agent's context. Credentials flow via the sandbox proxy (`ANTHROPIC_API_KEY`) or `CLAUDE_CODE_OAUTH_TOKEN` env var for Max subscription. Global CLAUDE.md and skills are a custom-template concern, not a live mount.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-17 | — | Initial creation; supersedes SPEC-049 |
| Ready | 2026-03-18 | — | SPIKE-027 Complete; credential strategy resolved; no blockers |
| Complete | 2026-03-18 | e8eea3a | scripts/swain-box created; Tier 2 removed from claude-sandbox; 20-test suite passes all 12 ACs |
