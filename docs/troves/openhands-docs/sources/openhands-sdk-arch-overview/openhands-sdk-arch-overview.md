---
title: "OpenHands SDK Architecture Overview"
url: https://docs.openhands.dev/sdk/arch/overview
hostname: docs.openhands.dev
description: "Understanding the OpenHands Software Agent SDK's package structure, component interactions, and execution models."
date: 2025-01-13
sitename: OpenHands Documentation
type: web-page
---

# Overview

> Understanding the OpenHands Software Agent SDK's package structure, component interactions, and execution models.

The **OpenHands Software Agent SDK** provides a unified, type-safe framework for building and deploying AI agents.

## Four-Package Architecture

The agent-sdk is organized into four distinct Python packages:

| Package                     | What It Does                                        | When You Need It                             |
| --------------------------- | --------------------------------------------------- | -------------------------------------------- |
| **openhands.sdk**           | Core agent framework + base workspace classes       | Always (required)                            |
| **openhands.tools**         | Pre-built tools (bash, file editing, etc.)          | Optional - provides common tools             |
| **openhands.workspace**     | Extended workspace implementations (Docker, remote) | Optional - extends SDK's base classes        |
| **openhands.agent_server**  | Multi-user API server                               | Optional - used by workspace implementations |

### Two Deployment Modes

**Mode 1: Local Development**
- Install: `openhands-sdk` + `openhands-tools`
- LocalWorkspace included in SDK
- Everything runs in one process
- Quick setup, no Docker required

**Mode 2: Production / Sandboxed**
- Install all 4 packages
- RemoteWorkspace auto-spawns agent-server in containers
- Sandboxed execution for security
- Multi-user deployments

### Key Components

- **Agent**: Implements the reasoning-action loop
- **Conversation**: Manages conversation state and lifecycle
- **LLM**: Provider-agnostic language model interface
- **Tool System**: Action/Observation/Executor pattern with MCP integration
- **Events**: Typed event framework
- **Workspace**: Base classes (LocalWorkspace, RemoteWorkspace)
- **Skill**: Reusable prompts with trigger-based activation
- **Condenser**: Conversation history compression
- **Security**: Action risk assessment and validation
