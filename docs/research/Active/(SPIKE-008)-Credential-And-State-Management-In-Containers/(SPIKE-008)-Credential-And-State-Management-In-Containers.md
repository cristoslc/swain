---
title: "Credential and State Management in Isolated Environments"
artifact: SPIKE-008
status: Active
author: cristos
created: 2026-03-12
last-updated: 2026-03-14
question: "How should credentials, git configuration, and agent state be forwarded into ephemeral isolated environments while keeping storage filesystem-bound?"
gate: Pre-MVP
risks-addressed:
  - API keys baked into images would be a security risk
  - Git commit signing (SSH keys) may not transfer cleanly into isolated environments
  - Agent state directories (.claude/, .agents/, .tickets/) need to survive environment restarts
  - gh CLI auth tokens live in host-specific paths that differ inside the environment
evidence-pool:
linked-artifacts: []
---

# Credential and State Management in Isolated Environments

## Question

How should credentials, git configuration, and agent state be forwarded into ephemeral isolated environments while keeping storage filesystem-bound?

Sub-questions:
1. What is the minimal set of credentials Claude Code needs? (API key, git identity, gh auth token)
2. What filesystem binding strategy keeps agent state persistent? Map of host paths to environment paths for: project dir, `.claude/`, `.agents/`, `.tickets/`, global Claude config (`~/.claude/`).
3. How should the Anthropic API key be passed — environment variable, mounted secrets file, or runtime-specific secrets mechanism?
4. Can `gh auth` credentials be forwarded via binding `~/.config/gh/`? Any permission or path issues?
5. How do git signing keys (SSH-based, per swain-keys) work inside the environment? Does the agent need access to `~/.ssh/` or can signing be host-delegated?
6. What exclusions prevent leaking sensitive host files into the environment?

## Go / No-Go Criteria

- **Go**: A documented binding and env-var configuration that lets Claude Code inside the isolated environment: (a) authenticate to the Anthropic API, (b) make signed git commits, (c) push to GitHub via gh, and (d) persist .tickets/ and .claude/ state across restarts — all without baking secrets into the image.
- **No-Go**: Credential forwarding requires host-specific daemons (e.g., 1Password SSH agent socket) that can't be reliably forwarded across isolation boundaries.

## Pivot Recommendation

If credential forwarding proves too fragile:
1. Use a `.env` file (gitignored) read at environment start, accepting the tradeoff of secrets on disk
2. Use a compose/orchestration layer with structured secrets management
3. Fall back to running Claude Code on host but with restricted PATH/env to simulate isolation

## Findings

*(To be populated during Active phase)*

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-12 | — | Initial creation |
| Active | 2026-03-14 | 257ea9c | Transition to Active |
