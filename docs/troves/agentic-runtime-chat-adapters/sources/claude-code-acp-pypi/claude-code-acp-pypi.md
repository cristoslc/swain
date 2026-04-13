---
source-id: claude-code-acp-pypi
type: web
url: "https://pypi.org/project/claude-code-acp/"
title: "claude-code-acp — Python ACP Server and Client for Claude Code"
fetched: 2026-04-06T00:00:00Z
author: claude-code-acp maintainers
---

# claude-code-acp

## Overview

A Python package that implements the Agent Client Protocol (ACP) for Claude Code. It combines Anthropic's Claude Agent SDK with ACP to enable Claude Code integration across editors, applications, and orchestration systems. Wraps the Claude CLI as a subprocess and communicates via stdio using ACP.

- **PyPI:** https://pypi.org/project/claude-code-acp/
- **Package:** `claude-code-acp`
- **Version:** 0.5.1 (March 19, 2026)
- **License:** MIT
- **Python:** 3.10+

## Installation

```bash
pip install claude-code-acp
# or
uv tool install claude-code-acp
```

## Core components

The package provides four main components:

1. **ClaudeAcpAgent** — ACP server that allows editors (Zed, Neovim, JetBrains) to use Claude Code as an ACP-compliant agent.
2. **ClaudeClient** — Event-driven Python API with decorator-based handlers for querying Claude Code programmatically.
3. **AcpClient** — General ACP client that connects to any ACP-compatible agent (not just Claude).
4. **AcpProxyServer** — Bridge between Copilot SDK and ACP backends.

## How it works

The package wraps the Claude CLI as a subprocess. No API key is needed; it uses the existing Claude CLI subscription. Communication flows over stdio using the Agent Client Protocol, enabling bidirectional messaging for tool calls, permissions, and streaming responses.

## Python API example

```python
import asyncio
from claude_code_acp import ClaudeClient

async def main():
    client = ClaudeClient(cwd=".", system_prompt="You are helpful.")

    @client.on_text
    async def handle_text(text: str):
        print(text, end="", flush=True)

    async with client:
        response = await client.query("Your prompt here")

asyncio.run(main())
```

## Key features

- Full ACP protocol compatibility.
- Uses Claude CLI subscription (no separate API key needed).
- Session management: create, fork, resume, list.
- MCP server support with dynamic loading.
- File operation interception.
- Terminal execution control.
- Multi-agent support through the ACP client component.

## CLI commands

- `claude-code-acp` — Runs ACP server for editor integration.
- `copilot-acp-proxy` — Bridges Copilot SDK to ACP backends.

## Relevance to swain

This is the most direct Python-native path to controlling Claude Code via ACP. It wraps the Claude CLI subprocess and exposes a clean async Python API. Swain could use `ClaudeClient` for direct Claude Code integration or `AcpClient` for connecting to any ACP agent, all without Node.js. The decorator-based event API aligns well with Python async patterns.
