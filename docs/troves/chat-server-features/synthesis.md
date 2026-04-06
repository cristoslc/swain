# Synthesis: Self-Hostable Chat Servers for Bot-Driven Development

## Context

This trove looks at self-hostable chat servers for a bot-driven dev workflow run by one person. The use case: one room per project, one thread per session. A bot posts updates nonstop. The operator reads and steers from a phone. This feeds an ADR for chat protocol selection under VISION-006 (Untethered Operator).

This revision adds a third lens: **full chat platforms vs. lightweight alternatives**. The earlier revisions compared Zulip, Matrix/conduwuit, Mattermost, and Campfire — all "real" chat platforms with varying ops weight. This revision asks whether we need a full platform at all. The interaction model is one human + N bots in rooms. Could a push notification service, a hosted platform's bot API, IRC, or a custom build serve the need with less burden?

## Key Findings

### The field splits into three tiers, not two.

Earlier analysis compared "feature-rich but heavy" (Zulip, Mattermost) against "operationally simple" (conduwuit, Campfire). The lightweight alternatives reveal a third tier: **zero-ops hosted transport** — platforms where someone else runs the infrastructure entirely.

| Tier | Examples | Ops Burden | Threading | Mobile |
|---|---|---|---|---|
| **Full platform (self-hosted)** | Zulip, Mattermost | High (5 services) to medium (2 services) | Excellent (Zulip) to good (Mattermost) | Native apps |
| **Lightweight self-hosted** | Conduwuit, Tinode, IRC+The Lounge | Low (single binary + optional DB) | Good (conduwuit/Matrix) to none (IRC) | Native (Element X) to PWA/web |
| **Zero-ops hosted** | Telegram, Discord | None | Good (forum topics/channels) | Excellent native apps |

[zulip-self-hosting, conduwuit-deployment-operations, telegram-forum-topics-bot-api, discord-hosted-bot-transport, irc-thelounge-lightweight-chat, tinode-lightweight-chat-server]

### Operational simplicity reshuffles the ranking.

When "single binary, trivial upgrade, file-copy backup" is a primary criterion, the field reorders:

| Server | Deployment | Upgrade | Backup | Rollback |
|---|---|---|---|---|
| **Telegram/Discord** | Nothing to deploy. | Nothing to upgrade. | N/A (vendor holds data). | N/A. |
| **Conduwuit** | Single binary or single Docker container. No external services. | Replace binary, restart. Seconds of downtime. | File copy of one directory. | Swap binary back. |
| **IRC (Ergo) + The Lounge** | Two lightweight processes. No database. | Replace binaries. | File copy. | Swap binaries back. |
| **Campfire** | Single Docker container, SQLite, no external services. | Pull new image, restart. | SQLite file copy. | Pull old image tag. |
| **Tinode** | One binary + external database (PostgreSQL/MySQL/MongoDB). | Replace binary, run migrations. | File copy + DB dump. | Restore from backup. |
| **Mattermost** | One binary + PostgreSQL. Docker Compose typical. | 12-step manual (binary) or image swap (Docker). Auto-migrations. | File copy + `pg_dump`. | Restore from backup. |
| **Zulip** | Five services (app, PostgreSQL, Redis, RabbitMQ, Memcached). | Scripted upgrade, minutes of downtime. | Scripted tarball (PostgreSQL dump inside). | Minor: symlink swap. Major: restore from backup. |

[conduwuit-deployment-operations, zulip-upgrade-operations, mattermost-upgrade-operations, campfire-37signals, telegram-forum-topics-bot-api, discord-hosted-bot-transport, irc-thelounge-lightweight-chat, tinode-lightweight-chat-server]

### Threading still decides the feature winner.

The platforms fall into four tiers:

1. **Zulip** — every message must have a stream and a topic. A bot sets `topic: "session-2026-04-06-001"` and gets an organized thread for free. Threading is built in, not bolted on. [zulip-self-hosting, zulip-bot-api]
2. **Matrix, Mattermost, Telegram, Discord** — all support threads, but threads are opt-in. In Matrix, the bot tracks root event IDs and sets `m.thread` relations. In Telegram, the bot uses `message_thread_id` to post to forum topics. In Discord, the bot creates forum posts. More code for the same result, but the UX is good. [matrix-threading-msc3440, mattermost-vs-rocketchat-comparison, telegram-forum-topics-bot-api, discord-hosted-bot-transport]
3. **Tinode** — no native threading. Groups support flat message streams only. Session separation requires one-group-per-session or application-layer tagging. [tinode-lightweight-chat-server]
4. **Campfire, IRC** — no threads at all. IRC channels and Campfire rooms are flat streams. The prefix-as-thread workaround is not viable for either. [campfire-37signals, campfire-room-prefix-threading-analysis, irc-thelounge-lightweight-chat]

### Telegram is the strongest zero-ops option.

Telegram with forum topics maps cleanly to swain's needs:

- **Supergroup = project room.** One group per project.
- **Forum topic = session thread.** Bot creates topics via `createForumTopic`. Posts to them via `message_thread_id`.
- **Bot API is rich.** Full CRUD on topics, inline keyboards for structured commands, markdown formatting, file attachments.
- **Native mobile apps.** Already on most developers' phones. Push notifications built in.
- **Zero cost, zero infrastructure.** No server, no Docker, no backups.
- **Rate limit: 20 messages per minute to the same group.** Requires batching for rapid-fire bot output. One summary message per minute instead of per-event is workable.

The trade-off is vendor dependency. Telegram is a proprietary service. If it changes API terms, rate limits, or goes down, there is no self-hosted fallback. [telegram-forum-topics-bot-api]

### Discord is a viable alternative to Telegram but heavier.

Discord forum channels provide slightly better threading organization than Telegram topics. The bot API is richer (slash commands, buttons, select menus). Rate limits are more generous (50 req/s). But Discord is heavier, pushes Nitro upsells, and has gaming-community associations that may feel odd for a dev tool. Thread auto-archiving adds friction. [discord-hosted-bot-transport]

### Push notification services (ntfy, Gotify) are not chat surfaces.

ntfy and Gotify are one-way notification systems. They can deliver alerts to a phone and support action buttons for simple responses. But they lack: conversation UI, message threading, persistent history, and free-form reply. A bot could use ntfy to alert the operator "session needs input" and the operator could tap a button to approve, but the operator cannot type steering commands. ntfy is a complement to a chat system, not a replacement for one. [ntfy-push-notification-service]

### IRC is ultra-lightweight but threadless.

IRC (via Ergo) + The Lounge is the lightest self-hosted chat stack with a real web UI. Combined RAM under 250 MB. Bot development in IRC is trivial and mature. But IRC has zero threading support. One channel per session creates sprawl. For a flat conversation model, IRC is perfect. For structured session management, it is inadequate. [irc-thelounge-lightweight-chat]

### Tinode is lighter than Mattermost but heavier than conduwuit.

Tinode is a Go-based chat server with native mobile apps (iOS, Android), a web client, and a bot plugin system. It needs an external database (PostgreSQL, MySQL, or MongoDB). It is lighter than Mattermost or Rocket.Chat but has no native threading. The mobile apps exist but are less polished than Telegram or Element X. [tinode-lightweight-chat-server]

### Matterbridge is glue, not a platform.

Matterbridge bridges messages between 30+ platforms. It is useful if swain supports multiple chat backends and needs to relay messages between them. It preserves threading when both endpoints support it. But it is not a standalone solution — you still need at least one actual chat platform. Its main value is enabling a hybrid approach: bot posts to Matrix, operator reads on Telegram via bridge. [matterbridge-chat-bridge]

### Building a custom chat server is the wrong trade-off.

A minimal WebSocket chat server with rooms, threads, and a mobile-friendly UI is 4000-8000 lines of code and 1-3 weeks of initial development. But the ongoing maintenance cost (security patches, mobile UX polish, edge cases in reconnection and message ordering) makes it a poor choice. Every swain adopter would inherit this maintenance. Existing platforms provide more features with less code and less ongoing burden. [custom-websocket-chat-assessment]

### The Campfire prefix-as-thread workaround is not viable.

Three blocking problems remain from earlier analysis: no room creation API, no room hierarchy, and PWA-only mobile. No one in the Campfire community has proposed or documented this pattern. [campfire-bot-kit-api, campfire-room-prefix-threading-analysis]

### Bot APIs range from rich to bare.

| Platform | Bot API Quality | Key Capability |
|---|---|---|
| **Discord** | Excellent | Slash commands, buttons, embeds, forum CRUD |
| **Zulip** | Excellent | Full CRUD on streams/topics, official SDKs |
| **Telegram** | Very good | Forum topic CRUD, inline keyboards, webhooks |
| **Mattermost** | Very good | Full CRUD on channels/posts, official SDKs |
| **Matrix** | Good | Client-server API covers everything, but thread handling is complex |
| **IRC** | Good (simple) | PRIVMSG, join, part. No REST API — persistent connection required |
| **Tinode** | Good | gRPC + WebSocket, plugin system, scriptable CLI |
| **Campfire** | Poor | Webhooks only. No room CRUD, no history, no membership management |

[zulip-bot-api, telegram-forum-topics-bot-api, discord-hosted-bot-transport, mattermost-vs-rocketchat-comparison, campfire-bot-kit-api, irc-thelounge-lightweight-chat, tinode-lightweight-chat-server]

### Resource requirements span three orders of magnitude.

| Platform | RAM | External Services | Docker Containers |
|---|---|---|---|
| **Telegram/Discord** | 0 (hosted) | 0 | 0 |
| **Ergo (IRC server)** | ~20 MB | 0 | 1 (optional) |
| **Conduwuit** | 20-100 MB | 0 | 1 |
| **The Lounge (IRC client)** | ~100-200 MB | IRC server | 1 |
| **Campfire** | ~2 GB | 0 | 1 |
| **Tinode** | ~200-500 MB | Database (PostgreSQL/MySQL) | 2 |
| **Mattermost** | 2-4 GB | PostgreSQL | 2 |
| **Synapse (Matrix)** | 350 MB+ (grows with federation) | PostgreSQL | 2+ |
| **Zulip** | 2 GB+ | PostgreSQL, Redis, RabbitMQ, Memcached | 5 |

[conduit-matrix-homeserver, conduwuit-deployment-operations, zulip-self-hosting, mattermost-vs-rocketchat-comparison, irc-thelounge-lightweight-chat, tinode-lightweight-chat-server, telegram-forum-topics-bot-api]

### Mobile apps vary in quality.

- **Telegram and Discord:** Best-in-class native apps. Already on most phones.
- **Matrix (Element X):** Fast, polished native app. Many other clients exist.
- **Zulip:** Native iOS and Android apps. Push alerts free for up to 10 self-hosted users.
- **Mattermost:** Native mobile apps. Solid.
- **Tinode:** Native iOS and Android apps. Functional but less polished.
- **Campfire:** PWA only. No native apps.
- **IRC (The Lounge):** Responsive web app. Works in mobile browser. Not a native app.

## Full Platform vs. Lightweight: The Core Trade-Off

The research reveals a spectrum, not a binary choice. The decision depends on which cost the operator is willing to pay.

### Hosted transport (Telegram, Discord): Zero ops, vendor risk.

**Best for:** A solo operator who wants to start using swain immediately with no infrastructure setup. The bot code is the only thing to write and maintain.

**Cost:** Vendor dependency. Messages live on someone else's server. API terms can change. If the platform goes down, you wait. No self-hosted fallback.

**Threading:** Good enough. Telegram forum topics and Discord forum channels both provide session separation. Not as clean as Zulip's mandatory topics, but adequate.

### Lightweight self-hosted (conduwuit, IRC): Minimal ops, some gaps.

**Best for:** An operator who wants data sovereignty and a self-hosted stack, but does not want to manage PostgreSQL, Redis, or multi-service deployments.

**Cost:** Some ops burden (trivial for conduwuit — file-copy backup, binary swap upgrades). Conduwuit has good threading via Matrix protocol. IRC has none. The gap is in the middle: there is no single-binary self-hosted server with both great threading AND great mobile apps.

**Threading:** Conduwuit (Matrix) has it via MSC3440. IRC does not. Tinode does not. The lightweight self-hosted tier has a threading gap outside of Matrix.

### Full platform (Zulip, Mattermost): Best features, highest ops.

**Best for:** An operator who wants the best threading UX (Zulip) or Slack-like familiarity (Mattermost) and is willing to manage a multi-service deployment.

**Cost:** Significant ops burden. Zulip needs five services. Mattermost needs PostgreSQL. Upgrades are multi-step. Backups require database dumps.

**Threading:** Zulip is the gold standard. Mattermost threads are good.

### The hybrid option: Hosted transport + matterbridge + self-hosted archive.

Matterbridge enables a hybrid model. The bot posts to a self-hosted platform (conduwuit for data sovereignty). Matterbridge bridges to Telegram for mobile convenience. The operator reads and replies on Telegram. Messages are archived on the self-hosted server. This gives zero mobile ops burden with data sovereignty as a secondary property.

**Cost:** Two systems to understand. Bridge fidelity is best-effort on threading. More moving parts than either pure approach.

## Points of Agreement

All sources agree on these points:

- Self-hosted chat is easier in 2026 than ever.
- Threading quality is the top factor when choosing a platform for structured bot output.
- Zulip has the best threading model for organized, searchable conversations.
- Fewer moving parts means fewer failure modes for a solo operator.
- Push notification services (ntfy, Gotify) are not chat replacements.
- Building a custom chat server is not worth the maintenance cost when existing options exist.
- Hosted platforms (Telegram, Discord) eliminate ops burden at the cost of vendor dependency.

## Points of Disagreement

- **Self-hosted vs. hosted transport.** Privacy advocates say messages must live on your server. Pragmatists say Telegram's reliability and UX outweigh data sovereignty concerns for a development tool (not a personal messenger).
- **Matrix vs. Zulip for bots.** Matrix fans say the federated protocol and client ecosystem outweigh the threading gap. Zulip fans say first-class threading removes a whole class of bot problems.
- **Mattermost licensing.** Some see the open-core model as fine. Others call the 10,000-message search cap on the free tier a dealbreaker.
- **Conduwuit governance.** Fork drama (Conduit -> conduwuit -> Continuwuity) raises questions about long-term maintenance.
- **Discord for dev tools.** Some see Discord as a natural fit (many dev communities already use it). Others find the gaming associations and Nitro upsells off-putting.
- **Telegram rate limits.** 20 msg/min/group is tight for rapid bot output. Some see batching as trivial. Others see it as a UX compromise.

## Gaps

- **Telegram bot thread code.** No source shows working code for a bot managing forum topics. The API is documented but real-world patterns (error handling, topic lifecycle) are untested.
- **Matterbridge thread fidelity.** How well do Zulip topics bridge to Telegram forum topics? No source tests this cross-platform thread mapping.
- **Conduwuit long-term governance.** The fork lineage is messy. Worth monitoring.
- **Signal as transport.** Signal has no official bot API. Unofficial bridges exist but are fragile. Not evaluated.
- **Revolt/Stoat.** Formerly known as Revolt, rebranded to Stoat in 2025. A Discord-like self-hosted platform in Rust. Has channels but threading support and bot API maturity are unclear. Not deeply evaluated.
- **Chatwoot.** Designed for customer support, not developer workflows. Requires Docker + PostgreSQL. Not a lightweight option. Not deeply evaluated.

## Recommendation Signal

For this use case (one operator, room per project, thread per session, bot posts nonstop, operator steers from mobile, minimal ops burden):

**Telegram is the easiest path to value.** Zero infrastructure. Rich bot API with forum topic support. The operator installs nothing new — Telegram is already on their phone. The rate limit (20 msg/min/group) is manageable with batched updates. The vendor risk is real but acceptable for a development tool. If swain wants the fastest time-to-value for adopters, Telegram is the answer.

**Conduwuit (Matrix) is the best self-hosted option.** Single binary, 20-100 MB RAM, file-copy backup. Threading works via MSC3440. Element X is a polished mobile client. The bot code is more complex than Telegram (thread relation tracking), but the protocol is open and the data is yours. For operators who want self-hosting without the weight of Zulip, conduwuit is the pick.

**Zulip remains the best feature fit if ops burden is acceptable.** Mandatory topic threading maps straight to sessions with zero extra bot code. But five services and PostgreSQL backups are a real cost for a solo operator.

**The pragmatic answer may be a tiered approach.** Swain could support multiple chat backends:

1. **Tier 1 (zero ops):** Telegram. The default for new adopters. No infrastructure needed.
2. **Tier 2 (minimal ops):** Conduwuit/Matrix. For operators who want self-hosting. Single binary, low maintenance.
3. **Tier 3 (full features):** Zulip. For operators who want the best threading UX and are willing to manage the stack.

Matterbridge could bridge between tiers, allowing an operator to start with Telegram and migrate to self-hosted later without losing conversation history.

**The tradeoff is no longer just threading vs. ops.** It is now a three-way tension: **threading UX vs. operational simplicity vs. vendor independence.** No single option wins on all three. The tiered approach lets each adopter pick their own balance point.
