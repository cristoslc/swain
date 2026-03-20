# Synthesis: Claude Code Channels

## Key findings

- **Channels are MCP servers that push events into a running Claude Code session** — enabling two-way communication between external platforms and Claude. This is an architectural inversion: traditional tools sit idle until invoked, channels actively forward events. Events only flow while the session is open. (`claude-code-channels-docs`, `byteiota-channels-tutorial`)

- **Channels are Claude Code-only** — no other runtime (Claude Desktop, claude.ai web, API) supports channels as of launch. However, three distinct remote interaction modes now exist for Claude Code: Channels (messaging apps, hackable), Remote Control (claude.ai/mobile app, polished), and Web Sessions (cloud, no local access). (`claudefast-channels-guide`)

- **Research preview with strict constraints** — requires v2.1.80+, claude.ai login only (no API keys/Console), Bun runtime, and only Anthropic-allowlisted plugins during preview. Custom channels need `--dangerously-load-development-channels`. Team/Enterprise orgs disabled by default. (`claude-code-channels-docs`, `claude-code-channels-reference`)

- **Building custom channels requires only `@modelcontextprotocol/sdk`** — declare `capabilities.experimental['claude/channel']`, emit `notifications/claude/channel` events, connect over stdio. One-way (webhooks, alerts) or two-way (chat bridges with reply tools). Works with Bun, Node, or Deno. (`claude-code-channels-reference`)

- **Notification format** — events arrive as `<channel source="name" ...>body</channel>` tags. `content` becomes the body, `meta` keys become attributes (identifiers only — hyphens silently dropped). (`claude-code-channels-reference`)

- **Platform-specific tradeoffs** — Telegram: faster setup (5 min), no message history (messages lost if session down), auto-downloads photos, typing indicator. Discord: more setup (10 min), has message history via `fetch_messages` (can catch up after restart), supports guild channels for team collaboration, native threading. (`claudefast-channels-guide`)

- **Security model** — sender allowlist per channel (gate on sender identity, not room/chat), pairing-code bootstrap, explicit `--channels` opt-in per session, org-level `channelsEnabled` gate. Ungated channels are a prompt injection vector. Replies flow through platform servers — sensitive work should use fakechat localhost. (`claude-code-channels-docs`, `claude-code-channels-reference`, `claudefast-channels-guide`)

- **Competitive context: OpenClaw** — Channels is Anthropic's response to OpenClaw (210k GitHub stars), which offered persistent AI workers over iMessage/Slack/Telegram/WhatsApp/Discord. OpenClaw creator Peter Steinberger (originally "Clawd" until C&D) was hired by OpenAI. The AI agent ecosystem is converging on event-driven, persistent, autonomous architectures. (`byteiota-channels-tutorial`)

## Points of agreement

- All sources consistently describe channels as MCP servers spawned as subprocesses over stdio — the same architecture as regular MCP tools.
- All sources agree on the research preview allowlist restriction and the `--dangerously-load-development-channels` escape hatch.
- Security: gate on sender identity (not room), allowlist-based, silently drop unauthorized messages.
- Session must stay running; no persistent background mode built-in (tmux/screen as workaround).
- Community is requesting Slack, WhatsApp, and iMessage as next platforms.

## Points of disagreement

- **byteiota** reports WebSocket disconnects every 10 minutes for Remote Control and "unavailable/non-functional" GitHub connector — not corroborated by other sources. Likely early-day bugs.
- **byteiota** frames the OpenClaw comparison as competitive threat; **claudefast** takes a more neutral architectural comparison stance.
- Minor: **claudefast** describes Discord using WebSocket connection while official docs describe it via plugin polling — likely an implementation detail of the discord.js gateway.

## Gaps

- **No channels outside Claude Code** — despite the user's interest in "other runtimes," channels are exclusively a Claude Code CLI feature. No indication of when/if Claude Desktop, web, or API will get push-event support.
- **No persistent/background session patterns** — all sources mention tmux/screen as workarounds but none document a proper always-on daemon mode.
- **Rate limiting and message queuing** — no information on concurrent message handling or behavior when session is paused at a permission prompt.
- **File attachments protocol** — claudefast mentions Telegram photos auto-download and Discord's `download_attachment` tool, but the official reference doesn't document the attachment protocol.
- **Economic model** — byteiota raises the question of whether subscription plans will cover always-on usage at scale. No answer available.
- **Audit trails** — security teams want logs of what happened while the developer was away. Not addressed in any source.
- **Enterprise chat platforms** — Slack Enterprise Grid, Microsoft Teams not yet supported. Major gap for enterprise adoption.
