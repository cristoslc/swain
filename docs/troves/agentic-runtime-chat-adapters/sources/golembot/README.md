# GolemBot Source Reference

**Source**: <https://github.com/0xranx/golembot> (v0.46.0, MIT)
**Captured**: 2026-04-24

## What was included

21 files (~6.9K lines) — the core adapter/gateway/engine architecture, not the full project.

### Core abstractions

| File | Purpose |
|------|---------|
| `channel.ts` | `ChannelAdapter` interface, `ChannelMessage` / `ReadReceipt` types — the contract every chat platform must implement. |
| `engine.ts` | `AgentEngine` interface, `StreamEvent` / `CompletionEvent` / `InvokeOpts` types — the contract every coding-agent backend must implement. |
| `gateway.ts` | Message router and orchestrator. Bridges adapters to engines. Handles mention detection, message splitting, streaming, multi-bot coordination, and proactive messaging. |
| `index.ts` | Public API surface — re-exports types and creates the `Assistant` façade. |
| `cli.ts` | CLI entry point — `gateway`, `doctor`, `onboard` commands. |

### Engine implementations

| File | Purpose |
|------|---------|
| `engines/claude-code.ts` | Claude Code CLI adapter. |
| `engines/codex.ts` | OpenAI Codex CLI adapter. |
| `engines/cursor.ts` | Cursor agent adapter. |
| `engines/opencode.ts` | OpenCode CLI adapter. |
| `engines/shared.ts` | Shared engine utilities (spawn helpers, NDJSON parsing). |
| `engines/provider-env.ts` | Per-engine environment variable setup for custom LLM providers. |

### Channel implementations (representative)

Only Slack and Telegram are included — they are the most mature adapters and show the pattern clearly. The full project also supports Discord, Feishu, DingTalk, WeCom, and WeChat.

| File | Purpose |
|------|---------|
| `channels/slack.ts` | Slack `ChannelAdapter` implementation. |
| `channels/slack-format.ts` | Slack markdown formatting helpers. |
| `channels/telegram.ts` | Telegram `ChannelAdapter` implementation. |
| `channels/telegram-format.ts` | Telegram markdown formatting helpers. |

### Support modules

| File | Purpose |
|------|---------|
| `session.ts` | Conversation session management (history, reset, conversation key). |
| `commands.ts` | Slash-command parsing and execution (`/help`, `/reset`, etc.). |
| `workspace.ts` | Workspace config loading (`golem.yaml`), skill scanning, provider presets. |

### Metadata

| File | Purpose |
|------|---------|
| `package.json` | Dependencies and project metadata. |
| `LICENSE` | MIT license. |
| `tsconfig.json` | TypeScript configuration. |

## What was excluded

- Tests (`src/__tests__/`)
- Other channel adapters (Discord, Feishu, DingTalk, WeCom, WeChat)
- Dashboard, fleet, server, scheduler, proactive, inbox, and history-fetcher modules
- Documentation site (`docs/`)
- Examples, skills, templates, Docker files
- Build artifacts (`dist/`), lockfiles, CI config