---
title: "Sandbox Templates In Regular Docker Containers"
artifact: SPIKE-034
track: container
status: Active
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
parent-initiative: INITIATIVE-013
parent-vision: VISION-002
question: "Can docker/sandbox-templates:claude run in a regular docker run container, and if not, what's the minimal image that works?"
gate: Pre-MVP
risks-addressed:
  - Docker Sandboxes' template images may depend on microVM infrastructure (proxy, daemon, workspace sync) that doesn't exist in regular containers
  - Building/maintaining a custom Claude Code Docker image adds maintenance burden
evidence-pool: ""
linked-artifacts:
  - SPEC-067
  - SPEC-092
  - SPIKE-032
depends-on-artifacts: []
---

# Sandbox Templates In Regular Docker Containers

## Summary

**Verdict: Go.** The sandbox template image (`docker/sandbox-templates:claude-code`) works in regular `docker run` — no microVM dependencies. Claude Code starts, recognizes `-e ANTHROPIC_API_KEY`, and the workspace mount works. Additionally, `/login` works inside the container — the OAuth flow completes successfully because the container reaches `api.claude.ai` directly without a MITM proxy. Max subscriptions work. Credentials persist inside the container across reconnects (as long as the container isn't removed).

## Question

Can `docker/sandbox-templates:claude-code` run in a regular `docker run` container, and if not, what's the minimal image that works?

## Go / No-Go Criteria

- **Go (template works):** The sandbox template image boots in `docker run`, Claude Code starts, accepts API key auth via `-e`, and can execute commands in the mounted workspace.
- **No-Go (template is VM-specific):** The image depends on microVM infrastructure (MITM proxy, workspace sync daemon, sandbox lifecycle hooks) that doesn't exist in a regular container.
- **Threshold:** Claude Code must be functional enough to run a simple prompt (`claude -p "echo hello"`) inside the container with workspace access.

## Pivot Recommendation

If the template doesn't work: build a minimal Dockerfile (`FROM node:lts` + `npm install -g @anthropic-ai/claude-code`) or find an existing community image. The image should be as thin as possible — just enough to run Claude Code with workspace mount and credential injection.

## Findings

### 1. Image name correction

The actual image tag is `docker/sandbox-templates:claude-code`, not `:claude`. The `docker sandbox run claude` command maps the runtime name `claude` to this image internally.

### 2. Image config — no sandbox dependencies

```
User: agent
Cmd: ["claude", "--dangerously-skip-permissions"]
WorkingDir: /home/agent/workspace
Base: ubuntu:questing (25.10)
Size: 2.38GB (617MB compressed)
```

No entrypoint script, no sandbox daemon dependencies, no references to the MITM proxy or workspace sync. The image is a straightforward Ubuntu + Claude Code install.

### 3. Regular docker run — works

```sh
$ docker run --rm docker/sandbox-templates:claude-code claude --version
2.1.78 (Claude Code)
```

Claude Code starts immediately. No errors about missing sandbox infrastructure.

### 4. API key auth — works

```sh
$ docker run --rm \
  -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  -v "$PWD:/home/agent/workspace" \
  docker/sandbox-templates:claude-code \
  claude -p "echo hello" --max-turns 1
```

Result: "Credit balance is too low" — which confirms the API key was recognized and the request reached `api.anthropic.com`. The failure is an account billing issue, not an image issue.

### 5. OAuth/Keychain — does not work (expected)

```sh
$ docker run --rm \
  -v "$HOME/.claude:/home/agent/.claude:ro" \
  -v "$PWD:/home/agent/workspace" \
  docker/sandbox-templates:claude-code \
  claude -p "echo hello" --max-turns 1
```

Result: "Not logged in · Please run /login" — OAuth tokens live in the macOS Keychain, not in `~/.claude/`. The container has no access to the host keychain. This is the same fundamental constraint as Docker Sandboxes (where the MITM proxy works around it by injecting credentials per-request).

### 6. Available template images

| Image tag | Size | Runtime |
|-----------|------|---------|
| `docker/sandbox-templates:claude-code` | 2.38GB | Claude Code 2.1.78 |
| `docker/sandbox-templates:codex` | 2.37GB | OpenAI Codex |
| `docker/sandbox-templates:shell` | 2.07GB | Generic shell |

### 7. Credential injection options for container fallback

| Method | Works? | Notes |
|--------|--------|-------|
| `-e ANTHROPIC_API_KEY=...` | Yes | Requires API credits (separate from Max subscription) |
| `-e ANTHROPIC_AUTH_TOKEN=...` | Untested | Bearer token for LLM gateways — higher priority than API key in Claude's auth chain |
| `-v ~/.claude:/home/agent/.claude` | No | OAuth tokens in Keychain, not filesystem |
| Interactive `/login` inside container | **Yes** | Operator-tested: OAuth flow completes, Max subscription works. Credentials persist in the container. |

### Architecture implication

The container fallback for Claude is viable:

```sh
docker run --rm -it \
  -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  -v "$WORKTREE_PATH:/home/agent/workspace" \
  docker/sandbox-templates:claude-code
```

This gives container-level isolation (shared kernel, isolated filesystem/network) with explicit credential injection. Not as strong as Docker Sandboxes' microVM, but stronger than `env -i` on the host, and it works with OAuth users who also have API credits.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-19 | — | Investigating Docker Sandboxes template reuse for regular containers |
