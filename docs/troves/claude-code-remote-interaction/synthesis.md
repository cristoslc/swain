# Synthesis: Claude Code Remote Interaction Patterns

Claude Code now offers three distinct modes for interacting with sessions beyond the local terminal: **Channels** (event-driven push via messaging apps/webhooks), **Remote Control** (sync local session to web/mobile), and **Headless/Agent SDK** (programmatic non-interactive execution). This synthesis covers all three.

## Key findings

### Three interaction modes with different tradeoffs

| Mode | Interface | Session runs on | Best for | Hackability |
|------|-----------|----------------|----------|-------------|
| **Channels** | Telegram, Discord, custom webhooks | Local machine | Async messages, event-driven automation, team channels | High (plugin architecture) |
| **Remote Control** | claude.ai/code, iOS/Android app | Local machine | Continuing sessions from phone/tablet, multi-device sync | Low (fixed interface) |
| **Headless / Agent SDK** | CLI (`-p`), Python, TypeScript | Local machine or CI/CD | Scripts, pipelines, structured output, unattended automation | Full (programmatic API) |

All three keep the session running locally with full filesystem, MCP, and tool access. Only **Claude Code on the web** (a separate feature) runs on Anthropic cloud. (`claude-code-remote-control-docs`, `claudefast-channels-guide`)

### Channels: event-driven push architecture

- MCP servers that push events into sessions (architectural inversion — channels forward events, not tools called by Claude) (`byteiota-channels-tutorial`)
- One-way (webhooks, CI alerts) or two-way (chat bridges with reply tools) (`claude-code-channels-reference`)
- Notification format: `<channel source="name" key="val">body</channel>` tags (`claude-code-channels-reference`)
- Telegram vs Discord tradeoffs: Telegram has faster setup but no message history; Discord has `fetch_messages` for catchup, guild channels for team collab, native threading (`claudefast-channels-guide`)
- Research preview: only Anthropic-allowlisted plugins via `--channels`; custom channels need `--dangerously-load-development-channels` (`claude-code-channels-docs`)

### Remote Control: session synchronization

- Outbound HTTPS only, no inbound ports. Registers with Anthropic API and polls for work. Short-lived, scoped credentials. (`claude-code-remote-control-docs`)
- Server mode (`claude remote-control`) supports `--spawn worktree` for concurrent sessions and `--capacity N` (default 32) (`claude-code-remote-control-docs`)
- Auto-reconnects when laptop wakes from sleep; ~10 min network timeout before session exits (`claude-code-remote-control-docs`, `claudefast-remote-control-guide`)
- Available on all plans (Pro, Max, Team, Enterprise with admin toggle) (`claude-code-remote-control-docs`)

### Headless / Agent SDK: programmatic automation

- `-p` flag for non-interactive execution with structured JSON output and optional schema conformance (`claude-code-headless-docs`)
- Session continuation via `--continue` and `--resume <session_id>` (`claude-code-headless-docs`)
- Tool auto-approval via `--allowedTools` for unattended operation (`claude-code-headless-docs`)
- Token-level streaming via `stream-json` format with retry events (`claude-code-headless-docs`)
- Full Python and TypeScript SDK packages available beyond CLI (`claude-code-headless-docs`)

### Security model (cross-cutting)

- **Channels**: sender allowlist per channel, pairing-code bootstrap, `--channels` opt-in per session, org `channelsEnabled` gate. Ungated channels are prompt injection vectors. Gate on sender identity, not room/chat. (`claude-code-channels-docs`, `claude-code-channels-reference`)
- **Remote Control**: outbound-only HTTPS, TLS, short-lived scoped credentials. No open ports. (`claude-code-remote-control-docs`)
- **Headless**: permission model via `--allowedTools` flag. `--dangerously-skip-permissions` for full unattended mode. (`claude-code-headless-docs`)
- **Contrast with OpenClaw**: OpenClaw had CVE-2026-25253 RCE affecting 50K+ instances via WebSocket. Claude Code's outbound-only model avoids this class of vulnerability. (`claudefast-remote-control-guide`)

### Competitive landscape

- OpenClaw (210k GitHub stars) offers persistent AI worker over 15+ platforms (iMessage, Slack, WhatsApp, etc.) for general-purpose tasks. Creator hired by OpenAI. (`byteiota-channels-tutorial`, `claudefast-remote-control-guide`)
- Claude Code's approach is narrower (coding-focused) but more secure (outbound-only, no self-hosting). Channels + Remote Control together cover messaging and web/mobile interfaces. (`claudefast-remote-control-guide`)
- MCP foundation (Linux Foundation, 5K+ servers) gives Claude Code an extensibility advantage. (`byteiota-channels-tutorial`)

## Points of agreement

- All sources agree: local execution is the core value proposition. Files, MCP servers, and tools never leave the machine.
- All modes require claude.ai authentication (not API keys) for remote/channel features. Headless works with API keys too.
- Session must stay running — no persistent daemon mode yet. tmux/screen as workaround.
- Community wants more platforms: Slack, WhatsApp, iMessage.

## Points of disagreement

- **claudefast** reports `--dangerously-skip-permissions` doesn't work with Remote Control yet; official docs don't mention this limitation.
- Minor: polling (Telegram) vs WebSocket (Discord) for channel connections — community sources differ on framing this as a design choice vs implementation detail.

## Gaps

- **No persistent daemon mode** — all modes require an open terminal/process. No systemd/launchd integration documented.
- **No cross-runtime support** — all features are Claude Code CLI only. No channels/remote-control for Claude Desktop, web API, or other SDKs.
- **Audit trails** — no logging of what happened during unattended sessions. Enterprise security concern.
- **Rate limiting / concurrent messages** — undocumented behavior when multiple channel events arrive simultaneously.
- **Cost model for always-on usage** — unclear if subscription covers persistent channel/remote sessions at scale.
- **File attachments protocol** — Telegram auto-downloads, Discord uses `download_attachment` tool, but the protocol isn't formally documented in the reference.
- **Slack / Teams / WhatsApp channels** — most requested by community, not yet available.
