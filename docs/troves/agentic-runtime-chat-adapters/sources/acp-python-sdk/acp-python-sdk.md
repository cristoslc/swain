---
source-id: acp-python-sdk
type: web
url: "https://github.com/agentclientprotocol/python-sdk"
title: "Agent Client Protocol Python SDK — Official Python SDK for ACP Clients and Agents"
fetched: 2026-04-06T00:00:00Z
author: agentclientprotocol (maintainer: Chojan Shang / PsiACE)
---

# Agent Client Protocol Python SDK

## Overview

The official Python SDK for the Agent Client Protocol (ACP). It enables building ACP-compliant agents and clients in Python without rebuilding JSON-RPC transports or schema models. The SDK is part of the official `agentclientprotocol` GitHub organization alongside TypeScript, Rust, Kotlin, and Java SDKs.

- **GitHub:** https://github.com/agentclientprotocol/python-sdk
- **Docs:** https://agentclientprotocol.github.io/python-sdk/
- **Package:** `agent-client-protocol` on PyPI
- **Version:** 0.9.0 (March 26, 2026)
- **License:** Apache-2.0
- **Python:** 3.8+ (async/await patterns)

## Installation

```bash
pip install agent-client-protocol
# or
uv add agent-client-protocol
```

## Core components

The SDK provides five main building blocks under `src/acp/`:

- **`acp.schema`** — Generated Pydantic models that track every ACP release, keeping payloads valid against the spec.
- **`acp.agent`** — Async base classes for building ACP-compliant agents with JSON-RPC supervision.
- **`acp.client`** — Async base classes for building ACP clients that connect to agents.
- **`acp.helpers`** — Builder utilities for content blocks, tool calls, session updates, and permissions. Mirrors the Go/TS SDK APIs.
- **`acp.contrib`** — Experimental utilities from production deployments: session accumulators, tool trackers, permission brokers.

## Protocol details

ACP is a stdio-based JSON-RPC protocol that lets clients (editors, shells, CLIs) orchestrate AI agents. Sessions exchange structured payloads including session updates, permissions, and tool calls. The Python SDK handles the transport plumbing so consumers work at the message level.

## Examples included

The repository ships runnable examples covering:

- Echo agent (minimal ACP agent).
- Streaming responses.
- Permission handling.
- Gemini bridge (connecting Gemini as an ACP agent).
- Client usage (programmatic launch and session management).
- Orchestration patterns (multi-agent coordination).

## Relevance to swain

This SDK provides a pure-Python path to both *consuming* ACP agents (as a client) and *exposing* agents via ACP (as a server). It eliminates the need for Node.js as a runtime dependency when integrating with ACP-compatible coding agents. The `acp.client` module can connect to any ACP agent over stdio, including Claude Code (via `claude-code-acp`), Codex, Gemini CLI, and others.
