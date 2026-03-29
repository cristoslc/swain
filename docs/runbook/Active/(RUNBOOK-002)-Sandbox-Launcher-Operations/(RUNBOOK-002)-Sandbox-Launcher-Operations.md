---
title: "Sandbox Launcher Operations"
artifact: RUNBOOK-002
track: standing
status: Active
mode: manual
trigger: on-demand
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
validates:
  - SPEC-067
  - SPEC-068
  - SPEC-071
  - SPEC-081
parent-epic: ""
depends-on-artifacts: []
linked-artifacts:
  - VISION-002
---

# Sandbox Launcher Operations

## Purpose

Step-by-step guide for launching agents in sandboxed environments using `swain-box` (Docker Sandboxes, Tier 2) and `claude-sandbox` (native sandbox, Tier 1). Covers launch, flags, worktree lifecycle, auth setup, and troubleshooting.

## Prerequisites

- Docker Desktop 4.58+ installed (for `swain-box`)
- `claude` CLI installed (for `claude-sandbox`)
- Git repository with a working tree
- At least one auth credential configured (see Auth Setup below)

---

## Quick Start

### Docker Sandboxes (strongest isolation)

**Prerequisite for Claude runtime:** `ANTHROPIC_API_KEY` must be set in your shell profile (`~/.zshrc`) and Docker Desktop restarted. OAuth/Max subscriptions do NOT work in Docker Sandboxes (docker/desktop-feedback#198). swain-box will block launch without an API key.

```sh
# Launch in current directory — creates worktree automatically
bin/swain-box .

# Launch with explicit runtime
bin/swain-box --runtime=claude .

# Attended mode (no worktree, work directly on main)
bin/swain-box --no-worktree .
```

### Native Sandbox (near-zero overhead)

```sh
# Launch in current directory — creates worktree, scopes credentials
scripts/claude-sandbox --here

# Launch for a specific project
scripts/claude-sandbox --project=/path/to/project

# Full credential access (attended use)
scripts/claude-sandbox --here --credentials=full --no-worktree
```

---

## Flag Reference

### swain-box

| Flag | Default | Description |
|------|---------|-------------|
| `--runtime=NAME` | auto-detect | Skip detection, use this runtime (`claude`, `copilot`, `codex`) |
| `--credentials=MODE` | `minimal` | Credential scoping (`minimal` or `full`). No functional effect in Docker Sandboxes — proxy always manages credentials |
| `--no-worktree` | off | Skip worktree creation; mount project root directly |
| `--cleanup NAME` | — | Remove worktree and branch for the named sandbox, then exit |
| `[path]` | `$PWD` | Project directory to mount |

### claude-sandbox

| Flag | Default | Description |
|------|---------|-------------|
| `--here` | — | Use `$PWD` as project root (instead of swain repo root) |
| `--project=DIR` | repo root | Use DIR as project root |
| `--credentials=MODE` | `minimal` | `minimal`: `env -i` wrapper, only essential vars forwarded. `full`: inherit full environment |
| `--no-worktree` | off | Skip worktree creation; use project root directly |

---

## Auth Setup

### For Docker Sandboxes (swain-box)

Docker Sandboxes uses a MITM proxy that reads credentials from your shell profile — **not** from the current shell session.

1. **Add API key to shell profile:**
   ```sh
   echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.zshrc
   ```

2. **Restart Docker Desktop** (required — the daemon reads env vars at startup)

3. **Verify:** Launch `swain-box` — you should NOT see the "No ANTHROPIC_API_KEY detected" warning.

**OAuth/Max subscriptions do NOT work** in Docker Sandboxes (docker/desktop-feedback#198). The MITM proxy breaks `api.claude.ai` traffic. Use `claude-sandbox` for Max/Pro subscriptions.

### For Native Sandbox (claude-sandbox)

With `--credentials=minimal` (default), only these env vars are forwarded:

| Category | Variables |
|----------|-----------|
| Shell essentials | `HOME`, `PATH`, `TERM`, `LANG`, `USER`, `SHELL`, `TMPDIR` |
| Claude auth | `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` (whichever is set) |
| Git auth | `GH_TOKEN` or `GITHUB_TOKEN` (whichever is set) |

Set your credentials in the current shell before launching:
```sh
export ANTHROPIC_API_KEY="sk-ant-..."
scripts/claude-sandbox --here
```

Or use `--credentials=full` to inherit everything (attended use only).

### Per-Runtime Credentials (multi-runtime)

| Runtime | Required credential | Detection |
|---------|-------------------|-----------|
| `claude` | `ANTHROPIC_API_KEY` | Shell profile or env var |
| `copilot` | `GITHUB_TOKEN` | Env var or `gh auth token` |
| `codex` | `OPENAI_API_KEY` | Env var |

---

## Worktree Lifecycle

### How it works

By default, both launchers create a git worktree before launching the agent:

```
<project>/.sandboxes/<sandbox-name>/    ← worktree directory
  on branch: agent/<sandbox-name>       ← isolated branch
```

The agent sees only its worktree. It cannot write to main or another agent's directory.

### Step 1: Launch (automatic)

```sh
skills/swain/scripts/swain-box /path/to/project
# Output:
#   swain-box: created worktree at /path/to/project/.sandboxes/claude-project (branch agent/claude-project)
#   swain-box: using claude.
#   swain-box: credential scope — proxy-managed
```

### Step 2: Agent works on its branch

The agent makes commits on `agent/claude-project`. It cannot push to main — it only sees its worktree.

### Step 3: Review the agent's work

```sh
# From the project root, see what the agent did:
git log agent/claude-project --oneline

# Diff against main:
git diff main..agent/claude-project

# Or browse the worktree directly:
ls .sandboxes/claude-project/
```

### Step 4: Merge or discard

```sh
# Merge the agent's work:
git merge agent/claude-project

# Or cherry-pick specific commits:
git cherry-pick <commit-hash>

# Or discard:
skills/swain/scripts/swain-box --cleanup claude-project
```

### Step 5: Cleanup

```sh
# Remove worktree + branch for a specific sandbox:
skills/swain/scripts/swain-box --cleanup claude-project
# Output:
#   swain-box: removed worktree at .sandboxes/claude-project
#   swain-box: deleted branch agent/claude-project

# Clean up all stale worktrees:
git worktree prune
```

### Reuse

If you launch `swain-box` again with the same project path and runtime, it reuses the existing worktree rather than creating a new one.

---

## Troubleshooting

### "docker sandbox subcommand is not available"

Docker Desktop is too old. Requires 4.58+.
```sh
docker --version   # Check version
# Update: https://www.docker.com/products/docker-desktop/
```

### "No supported agent runtimes found in Docker Sandboxes"

No runtime images are installed. Verify:
```sh
docker sandbox run claude --version
docker sandbox run copilot --version
docker sandbox run codex --version
```

### "No ANTHROPIC_API_KEY detected" warning

The key must be in your **shell profile** (`~/.zshrc`), not just the current session. Docker Desktop reads from the profile at startup.
```sh
# Add to profile:
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.zshrc
# Then restart Docker Desktop
```

### "Credit balance too low" inside sandbox

OAuth auth is being used but doesn't work through the MITM proxy. Switch to API key auth (see Auth Setup above) or use `claude-sandbox` instead.

### Worktree creation fails

```sh
# Check for stale worktrees:
git worktree list
git worktree prune

# Check for branch name conflict:
git branch | grep agent/

# Manual cleanup:
rm -rf .sandboxes/<name>
git worktree prune
git branch -D agent/<name>
```

### Agent can't find project files

If using `--no-worktree`, the agent sees the project root directly. If using worktree mode (default), ensure the worktree was created from the correct branch:
```sh
cd .sandboxes/<name>
git log --oneline -3   # Should show main's history
```

### stale apiKeyHelper in sandbox settings

Docker Desktop < 4.60.1 injected a bad `apiKeyHelper` value. swain-box auto-cleans this, but if you see it manually:
```sh
docker sandbox exec <name> sh -c 'sed -i "/apiKeyHelper/d" "$HOME/.claude/settings.json"'
```

---

## Credential Security Properties

| Property | Native (`--credentials=minimal`) | Docker Sandboxes |
|----------|----------------------------------|------------------|
| Env var isolation | Allowlist via `env -i` | Complete (proxy-managed) |
| Credentials in agent memory | Only allowlisted vars | Never |
| File-based credentials | Accessible (~/.aws, keychain) | Not accessible |
| Network exfiltration | Possible (allowed domains) | Proxy-filtered |
| OAuth support | Yes | No (MITM breaks TLS) |

See `docs/vision/Active/(VISION-002)-Safe-Autonomy/architecture-overview.md` for the full comparison matrix.

---

## Run Log

| Date | Executor | Result | Duration | Notes |
|------|----------|--------|----------|-------|
| 2026-03-19 | cristos | — | — | Created |

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-19 | — | Initial creation covering swain-box + claude-sandbox operations |
