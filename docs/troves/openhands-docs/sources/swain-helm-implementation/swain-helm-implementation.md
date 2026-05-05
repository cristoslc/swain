---
title: "swain-helm Implementation (GitHub Repository)"
url: https://github.com/cristoslc/swain/tree/epic/initiative-018-swain-helm-implementation/src/swain_helm
hostname: github.com
description: "swain-helm bridge implementation - project bridge kernel for remote operator interaction"
date: 2025-01-13
sitename: GitHub
type: repository
tags:
  - swain
  - helm
  - bridge
  - zulip
  - opencode
---

# swain_helm Implementation

## Repository Structure

From: https://github.com/cristoslc/swain/tree/epic/initiative-018-swain-helm-implementation/src/swain_helm

### Core Files

| File | Description |
|------|-------------|
| `__init__.py` | Package initialization |
| `config.py` | Configuration management |
| `protocol.py` | Protocol definitions for bridge communication |
| `provision.py` | Provisioning logic |
| `plugin_process.py` | Plugin process management |
| `session_registry.py` | Session registry for tracking active sessions |
| `watchdog.py` | Watchdog for monitoring and health checks |
| `worktree_scanner.py` | Scans worktrees for active projects |
| `opencode_discovery.py` | OpenCode server discovery |

### Subdirectories

| Directory | Contents |
|-----------|----------|
| `adapters/` | Bridge adapters for different platforms |
| `bridges/` | Bridge implementations |
| `plugins/` | Plugin implementations |

## Implementation Context

This is part of **INITIATIVE-018: Remote Operator Interaction** and **VISION-006: Untethered Operator**.

The swain-helm bridge enables:
- Project bridge kernel implementation
- Zulip integration for chat-based agent control
- OpenCode server management
- Session persistence and recovery
- Multi-project worktree scanning
- Plugin system for extensibility

## Key Design Patterns

1. **Bridge Pattern**: Abstracts communication between agent and operator
2. **Plugin Architecture**: Extensible via plugin system
3. **Session Registry**: Tracks and manages session lifecycle
4. **Watchdog**: Ensures system health and automatic recovery
5. **Worktree Scanning**: Automatic discovery of swain projects
