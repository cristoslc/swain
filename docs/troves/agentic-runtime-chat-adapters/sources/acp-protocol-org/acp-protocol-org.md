---
source-id: acp-protocol-org
type: web
url: "https://github.com/agentclientprotocol/agent-client-protocol"
title: "Agent Client Protocol Specification — Official Protocol Repo and SDK Ecosystem"
fetched: 2026-04-06T00:00:00Z
author: agentclientprotocol (stewarded by Zed)
---

# Agent Client Protocol — Specification and SDK Ecosystem

## Overview

The Agent Client Protocol (ACP) is an open specification that standardizes communication between code editors (interactive programs for viewing and editing source code) and coding agents (AI systems that autonomously modify code). The protocol is stewarded by Zed and has become the dominant wire protocol for agentic coding tools.

- **GitHub org:** https://github.com/agentclientprotocol
- **Spec repo:** https://github.com/agentclientprotocol/agent-client-protocol
- **Schema:** `schema/schema.json` in the spec repo
- **Docs:** https://agentclientprotocol.com

## Official SDKs — five languages

The ACP organization maintains official SDKs in five languages:

| Language | Repository | Package |
|----------|-----------|---------|
| TypeScript | `agentclientprotocol/typescript-sdk` | `@agentclientprotocol/sdk` (npm) |
| Python | `agentclientprotocol/python-sdk` | `agent-client-protocol` (PyPI) |
| Rust | `agentclientprotocol/rust-sdk` | `agent-client-protocol` (crates.io) |
| Kotlin | `agentclientprotocol/kotlin-sdk` | JVM target (other targets in progress) |
| Java | `agentclientprotocol/java-sdk` | JVM target |

Community SDKs also exist but are not catalogued on the main spec page.

## Protocol transport

ACP uses stdio-based JSON-RPC as its transport. Clients spawn agents as subprocesses and communicate over stdin/stdout with structured JSON-RPC messages. This design means any language that can spawn a subprocess and read/write stdio can participate in the protocol, regardless of the SDK language.

## Implications for language choice

The five-language SDK coverage means:

- **Python-first projects** can use the official Python SDK (`agent-client-protocol`) directly. No Node.js dependency required.
- **ACPX** (the OpenClaw headless CLI) is a TypeScript/Node.js tool, but it is an *optional convenience layer* on top of ACP, not a protocol requirement.
- The Vercel AI SDK ACP provider (`@anthropic-ai/acp-provider`) is TypeScript-only, but this only matters for web app frontends, not for backend/CLI orchestration.
- The stdio transport means even without an SDK, any language can implement the protocol by reading/writing JSON-RPC over subprocess pipes.

## Relevance to swain

This source confirms that ACP has first-class Python support. The Python SDK is official, maintained, and at parity with the TypeScript SDK. Swain does not need Node.js to use ACP. ACPX is a Node.js convenience layer, but the underlying protocol is language-agnostic and the Python SDK provides equivalent client/agent functionality.
