---
source-id: claudeck-browser-ui
type: web
url: "https://github.com/hamedafarag/claudeck"
title: "Claudeck — Browser-Based UI for Claude Code"
fetched: 2026-04-06T00:00:00Z
author: Hamed Farag
---

# Claudeck

## Overview

Claudeck is a browser-based UI for Claude Code built as a WebSocket bridge between the browser and the Claude Code SDK. Started as a weekend project on March 1, 2026, and grew into a two-week sprint. Installable as a PWA.

- **GitHub:** https://github.com/hamedafarag/claudeck
- **Stars:** 28
- **License:** Not specified
- **Language:** JavaScript
- **Created:** March 2026

## Runtimes supported

- Claude Code only.

## Key features

- Chat interface for Claude Code.
- Workflow management.
- MCP server management.
- Cost tracking.
- Autonomous agent orchestration.
- PWA installable.

## Limitations (self-reported by author)

- No authentication (anyone on local network can access).
- No multi-CLI support (CloudCLI supports 4 runtimes).
- No desktop app (Opcode and CodePilot are better for native macOS/Windows).
- No live file editing (CloudCLI offers this).

## Architecture

- WebSocket bridge between browser and Claude Code SDK.
- Local web interface.

## Maturity assessment

Small, early-stage project (28 stars). The author is transparent about its limitations compared to CloudCLI and other alternatives. Demonstrates a minimal viable approach to browser-based Claude Code interaction.

## Relevance to build-vs-buy

Useful as an architectural reference (WebSocket bridge to SDK) but not mature or runtime-agnostic enough for production use. The author's honest comparison with alternatives is informative for evaluating the landscape.
