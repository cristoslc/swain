---
source-id: "claude-code-remote-control-docs"
title: "Continue local sessions from any device with Remote Control — Claude Code Docs"
type: web
url: "https://code.claude.com/docs/en/remote-control"
fetched: 2026-03-20T00:00:00Z
hash: "cca8bd6b25725c7883685d894dc8902fbde01f924aa9b7926cefaa8325d3a88a"
---

# Continue local sessions from any device with Remote Control

Continue a local Claude Code session from your phone, tablet, or any browser using Remote Control. Works with claude.ai/code and the Claude mobile app.

> Remote Control is available on all plans. On Team and Enterprise, it is off by default until an admin enables the Remote Control toggle in Claude Code admin settings.

Remote Control connects claude.ai/code or the Claude app for iOS and Android to a Claude Code session running on your machine. Start a task at your desk, then pick it up from your phone on the couch or a browser on another computer.

When you start a Remote Control session on your machine, Claude keeps running locally the entire time, so nothing moves to the cloud. With Remote Control you can:

- **Use your full local environment remotely**: your filesystem, MCP servers, tools, and project configuration all stay available
- **Work from both surfaces at once**: the conversation stays in sync across all connected devices, so you can send messages from your terminal, browser, and phone interchangeably
- **Survive interruptions**: if your laptop sleeps or your network drops, the session reconnects automatically when your machine comes back online

Unlike Claude Code on the web, which runs on cloud infrastructure, Remote Control sessions run directly on your machine and interact with your local filesystem. The web and mobile interfaces are just a window into that local session.

Requires Claude Code v2.1.51 or later.

## Requirements

- **Subscription**: available on Pro, Max, Team, and Enterprise plans. On Team and Enterprise, an admin must first enable the Remote Control toggle in Claude Code admin settings. API keys are not supported.
- **Authentication**: run `claude` and use `/login` to sign in through claude.ai.
- **Workspace trust**: run `claude` in your project directory at least once to accept the workspace trust dialog.

## Start a Remote Control session

Three modes:

### Server mode

```bash
claude remote-control
```

The process stays running in your terminal in server mode, waiting for remote connections. Displays a session URL and QR code (press spacebar).

Available flags:

| Flag | Description |
|------|-------------|
| `--name "My Project"` | Custom session title visible in session list at claude.ai/code |
| `--spawn <mode>` | How concurrent sessions are created. `same-dir` (default) or `worktree` (git worktree per session). Press `w` at runtime to toggle. |
| `--capacity <N>` | Maximum concurrent sessions. Default is 32. |
| `--verbose` | Show detailed connection and session logs |
| `--sandbox` / `--no-sandbox` | Enable or disable sandboxing for filesystem and network isolation |

### Interactive session

```bash
claude --remote-control
# or with a name:
claude --remote-control "My Project"
```

Full interactive session in terminal that's also available remotely. Unlike server mode, you can type messages locally.

### From an existing session

```
/remote-control
# or /rc
```

Carries over current conversation history.

## Connect from another device

- **Open the session URL** in any browser (displayed in terminal)
- **Scan the QR code** (press spacebar to toggle) to open in Claude mobile app
- **Browse the session list** in claude.ai/code or Claude app — Remote Control sessions show a computer icon with green status dot

The conversation stays in sync across all connected devices.

## Enable Remote Control for all sessions

Run `/config` inside Claude Code and set "Enable Remote Control for all sessions" to `true`.

With this setting on, each interactive Claude Code process registers one remote session. Multiple instances get separate sessions. For concurrent sessions from a single process, use server mode with `--spawn`.

## Connection and security

- Local session makes **outbound HTTPS requests only** — never opens inbound ports
- Registers with Anthropic API and polls for work
- All traffic through Anthropic API over TLS (same transport security as any Claude Code session)
- Multiple short-lived credentials, each scoped to a single purpose and expiring independently

## Remote Control vs Claude Code on the web

Both use the claude.ai/code interface. Key difference is where the session runs:
- **Remote Control**: executes on your machine, local MCP servers/tools/config stay available
- **Claude Code on the web**: executes in Anthropic-managed cloud infrastructure

Use Remote Control for continuing local work from another device. Use web for tasks without local setup or parallel execution.

## Limitations

- **One remote session per interactive process** (use server mode with `--spawn` for multiple)
- **Terminal must stay open**: closing terminal ends the session
- **Extended network outage**: ~10 minute timeout, then session exits
