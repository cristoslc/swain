# Synthesis: Claude Code Channels

## Key findings

- **Channels are MCP servers that push events into a running Claude Code session** — enabling two-way communication between external platforms (Telegram, Discord, custom systems) and Claude. Events only flow while the session is open.
- **Research preview status** — requires Claude Code v2.1.80+, claude.ai login only (no API keys), and during preview only Anthropic-allowlisted plugins are accepted via `--channels`.
- **Plugin-based architecture** — channels are installed as plugins (`/plugin install <name>@claude-plugins-official`), configured with platform tokens, and activated per-session with `--channels plugin:<name>@claude-plugins-official`.
- **Security model** — sender allowlist per channel, pairing-code bootstrap for Telegram/Discord, explicit `--channels` opt-in per session, and org-level `channelsEnabled` gate for Team/Enterprise.
- **Bun runtime required** — all pre-built channel plugins are Bun scripts.

## Points of agreement

(Single source — no cross-source comparison available.)

## Points of disagreement

(Single source — no conflicts to report.)

## Gaps

- **No detail on the MCP channel protocol itself** — the docs page references a channels-reference page for building custom channels, but that page was not collected. Extending the trove with the [channels-reference](https://code.claude.com/docs/en/channels-reference) would fill this gap.
- **No guidance on persistent/background session patterns** — the docs mention running Claude in a "background process or persistent terminal" for always-on channels, but don't elaborate on how.
- **No webhook or CI integration examples** — the intro mentions forwarding CI results and monitoring events, but only Telegram, Discord, and fakechat are documented.
- **Rate limiting and message queuing** — no information on what happens if many messages arrive simultaneously or if the session is paused at a permission prompt.
