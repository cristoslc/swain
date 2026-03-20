# Synthesis: Claude Code Channels

## Key findings

- **Channels are MCP servers that push events into a running Claude Code session** — enabling two-way communication between external platforms (Telegram, Discord, custom systems) and Claude. Events only flow while the session is open. (`claude-code-channels-docs`)
- **Research preview status** — requires Claude Code v2.1.80+, claude.ai login only (no API keys), and during preview only Anthropic-allowlisted plugins are accepted via `--channels`. Custom channels require `--dangerously-load-development-channels`. (`claude-code-channels-docs`, `claude-code-channels-reference`)
- **Plugin-based architecture** — channels are installed as plugins (`/plugin install <name>@claude-plugins-official`), configured with platform tokens, and activated per-session with `--channels plugin:<name>@claude-plugins-official`. (`claude-code-channels-docs`)
- **Building custom channels requires only `@modelcontextprotocol/sdk`** — declare `capabilities.experimental['claude/channel']` in the Server constructor, emit `notifications/claude/channel` events, connect over stdio. Works with Bun, Node, or Deno. (`claude-code-channels-reference`)
- **One-way vs two-way** — one-way channels forward events (webhooks, CI alerts). Two-way channels add a reply tool via standard MCP tool registration (`capabilities.tools`), letting Claude send messages back through the same channel. (`claude-code-channels-reference`)
- **Notification format** — events arrive as `<channel source="name" ...>body</channel>` tags in Claude's context. `content` becomes the body, `meta` keys become tag attributes (identifiers only — hyphens silently dropped). (`claude-code-channels-reference`)
- **Security model** — sender allowlist per channel, pairing-code bootstrap for Telegram/Discord, explicit `--channels` opt-in per session, and org-level `channelsEnabled` gate for Team/Enterprise. Ungated channels are explicitly called out as a prompt injection vector — gate on sender identity, not room/chat ID. (`claude-code-channels-docs`, `claude-code-channels-reference`)

## Points of agreement

- Both sources consistently describe channels as MCP servers spawned as subprocesses communicating over stdio.
- Both emphasize the research preview allowlist restriction and the `--dangerously-load-development-channels` escape hatch.
- Security gating on sender identity (not room) is consistent across the user guide and the reference.

## Points of disagreement

No conflicts found between the two sources — the reference is a natural extension of the user guide.

## Gaps

- **No guidance on persistent/background session patterns** — both docs mention running Claude in a "background process or persistent terminal" for always-on channels, but neither elaborates on how.
- **Rate limiting and message queuing** — no information on what happens if many messages arrive simultaneously or if the session is paused at a permission prompt.
- **File attachments and rich content** — the reference mentions fakechat supports file attachments but doesn't document the attachment protocol. The Telegram/Discord plugin source would be needed for that.
- **Error handling in channels** — no guidance on what happens when `mcp.notification()` fails, or how to handle disconnections/reconnections.
- **Plugin marketplace submission process** — mentioned but not detailed; the plugins docs would fill this gap.
