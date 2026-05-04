---
source-id: acp-vercel-ai-sdk-provider
type: web
url: "https://ai-sdk.dev/providers/community-providers/acp"
title: "ACP Provider for Vercel AI SDK — Bridge ACP Agents to Web Applications"
fetched: 2026-04-06T00:00:00Z
author: Vercel / ACP community
---

# ACP Provider for Vercel AI SDK

## Overview

A community provider that bridges ACP agents (Claude Code, Gemini CLI, Codex CLI, and others) to the Vercel AI SDK. This enables building web applications and Node.js services that communicate with coding agents through the LanguageModel interface.

- **URL:** https://ai-sdk.dev/providers/community-providers/acp
- **Type:** Library / SDK integration

## How it works

- Wraps ACP agents as LanguageModel instances.
- Accepts a command parameter to execute the ACP agent (e.g., `gemini`, `claude-code-acp`, `codex-acp`).
- Enables building web UIs on top of agent sessions using standard AI SDK patterns.

## Runtimes supported

- Claude Code.
- Gemini CLI.
- Codex CLI.
- Any ACP-compatible agent.

## Relevance to build-vs-buy

This is the most composable piece in the landscape. Rather than a complete product, it is a library that exposes ACP agents through a standard interface (Vercel AI SDK LanguageModel). A web chat UI built on AI SDK could use this to talk to any ACP agent. Combined with ACPX for session management, this could form the adapter layer for Untethered Operator without building a full custom bridge.
