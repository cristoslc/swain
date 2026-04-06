# Synthesis: Chat Platforms for Bot-Driven Development

## Context

This trove evaluates chat platforms for a bot-driven dev workflow run by one person. The use case: one room per project, one thread per session. A bot posts updates nonstop. The operator reads and steers from a phone. This feeds an ADR for chat protocol selection under VISION-006 (Untethered Operator).

This revision reframes the central question. Earlier revisions compared self-hosted servers and asked which one to run on a VPS. This revision sees that **for v1, a hosted platform removes the VPS entirely**. The provisioning command (`/swain-stage`) just registers a bot and connects bridges. The chat adapter code speaks to an API. It does not care where the server lives. Self-hosting becomes an option, not a requirement.

## Hosted vs. Self-Hosted: The New Default

### Why hosted is the v1 default.

Earlier analysis found a three-way tension: threading UX vs. operational simplicity vs. vendor independence. Hosted platforms resolve the "operational simplicity" axis completely — zero servers to run, zero backups to manage, zero upgrades to perform. The bot code is the only thing to write and maintain.

For a solo developer trying swain for the first time, the path to value should be: install swain, run `/swain-stage`, start a session, see output on your phone. If the first step is "provision a VPS, install Docker, configure DNS, deploy a chat server," most operators will stop before they start. [zulip-cloud-hosted, slack-hosted-bot-platform, telegram-forum-topics-bot-api, discord-hosted-bot-transport]

### The chat adapter abstraction.

The bot code talks to an API. Whether that API is `https://yourorg.zulipchat.com` (Zulip Cloud) or `https://zulip.yourdomain.com` (self-hosted Zulip), the code is identical. The adapter layer abstracts the transport. This means:

- Hosted is the default for new adopters.
- Self-hosted is an option for operators who want data sovereignty or customization.
- Migration between hosted and self-hosted is a config change, not a rewrite.

This holds best for Zulip, where Cloud and self-hosted share the same codebase and API. For Slack, Discord, and Telegram, there is no self-hosted version — leaving means switching platforms entirely. [zulip-cloud-hosted, zulip-self-hosting]

### Zulip Cloud is the recommended starting point.

Zulip Cloud stands out because it is the only hosted platform where the bot code is identical to self-hosted and migration is bidirectional:

- **Same API.** The `zulip` Python SDK works with both Cloud and self-hosted. Change the `site` URL, everything else stays the same.
- **Same features.** No "open core" catch. Every feature on Cloud is available on self-hosted.
- **Bidirectional migration.** Export from Cloud, import to self-hosted (or vice versa). Message history, streams, topics, and files transfer.
- **Best threading.** Mandatory stream + topic model gives session-per-topic for free. No extra bot code to manage thread IDs.
- **Free tier.** 10,000-message search limit. Adequate for getting started. $8/month for unlimited.

No other hosted platform offers this combination. Slack, Discord, and Telegram are all one-way commitments with no self-hosted fallback. [zulip-cloud-hosted, zulip-bot-api, zulip-self-hosting]

## Key Findings

### Hosted platform comparison.

| Platform | Python SDK | Threading | Rate Limit | Free Tier | Security | Self-Hosted Path | Provisioning |
|---|---|---|---|---|---|---|---|
| **Zulip Cloud** | `zulip` (official, mature) | Mandatory topics (best) | Same as self-hosted | 10K msg search | Good (open-source co.) | Seamless (same software) | Org signup manual; rest via API. |
| **Slack** | Bolt for Python (excellent) | `thread_ts` (good) | 1 msg/sec/channel | 90-day history, 10 apps | SOC 2, ISO 27001 | None (no self-hosted Slack) | App creation manual; rest via API. |
| **Discord** | discord.py (excellent) | Forum channels (good) | 50 req/sec global | Unlimited, free | Weak (community platform) | None | Bot app creation manual; rest via API. |
| **Telegram** | python-telegram-bot (excellent) | Forum topics (good) | 20 msg/min/group | Unlimited, free | Adequate (cloud-stored) | None | BotFather manual; group setup manual. |
| **Teams** | teams.py (alpha) | Reply chains (adequate) | 1 msg/2sec/thread | Requires M365 ($6/mo) | Enterprise-grade | None | Azure AD app registration (complex). |

[zulip-cloud-hosted, slack-hosted-bot-platform, discord-hosted-bot-detailed, telegram-bot-sdk-detailed, teams-hosted-bot-platform]

### Python SDK quality and maturity.

The SDKs fall into three tiers:

1. **Excellent and production-ready.** Bolt for Python (Slack), discord.py, python-telegram-bot. All are async-native, actively maintained, well-documented, and handle rate limiting automatically. Any of these would be a solid foundation for the swain chat adapter.
2. **Good and stable.** The `zulip` Python SDK. Official, functional, covers all API endpoints. Less community ecosystem than Slack/Discord, but reliable.
3. **Immature.** teams.py (Microsoft). Alpha-stage, breaking changes expected, threading support undocumented. Not ready for production use.

[slack-hosted-bot-platform, discord-hosted-bot-detailed, telegram-bot-sdk-detailed, zulip-bot-api, teams-hosted-bot-platform]

### Rate limits for continuous bot posting.

The bot posts every tool call, text output, status change, and error. This is high-frequency output. Rate limits determine whether the bot can stream output or must batch.

| Platform | Effective Limit | Batching Required? | SDK Auto-Handling? |
|---|---|---|---|
| **Discord** | 50 req/sec global; ~5-10 msg/sec/channel practical | No | Yes (discord.py) |
| **Slack** | 1 msg/sec/channel (60/min) | Light batching | Yes (Bolt SDK) |
| **Zulip Cloud** | Not explicitly documented; same as self-hosted | Light batching likely | Partial (SDK retries on 429) |
| **Teams** | 1 msg/2sec/thread (30/min) | Yes | Unknown (alpha SDK) |
| **Telegram** | 20 msg/min/group | Yes (significant) | Yes (AIORateLimiter) |

Discord is the most generous. Telegram is the most restrictive. For swain's use case, Discord and Slack allow near-real-time streaming. Telegram needs batching every ~3 seconds. Teams sits in the middle but its alpha SDK makes it impractical.

[discord-hosted-bot-detailed, slack-hosted-bot-platform, telegram-bot-sdk-detailed, teams-hosted-bot-platform, telegram-forum-topics-bot-api]

### Free tier viability for a single operator with N bots.

| Platform | Free? | Practical Limit | When to Pay |
|---|---|---|---|
| **Telegram** | Completely free. No limits on messages, bots, or groups. | File upload (50 MB). Rate limits (20/min/group). | Never. |
| **Discord** | Completely free for bot use. | File upload (25 MB). | Never for bot features. |
| **Zulip Cloud** | Free tier: 10K message search limit. | ~100 days at moderate use. | $8/month for unlimited history. |
| **Slack** | Free: 90-day history, 10 apps, data deleted after 1 year. | History loss and app limit are real constraints. | $7.25/month (Pro) for sustained use. |
| **Teams** | Free Teams cannot deploy bots. | Requires M365 ($6/month minimum). | Immediately. |

Telegram and Discord are free forever. Zulip Cloud is free to start and cheap to scale. Slack's free tier works to evaluate but not for production. Teams requires payment from day one.

[zulip-cloud-hosted, slack-hosted-bot-platform, discord-hosted-bot-detailed, telegram-bot-sdk-detailed, teams-hosted-bot-platform]

### Security: who can see your agent session data?

| Platform | Data Stored By | Encryption | Compliance | Risk Level |
|---|---|---|---|---|
| **Self-hosted (any)** | You | You control | You decide | Lowest (you own the data). |
| **Zulip Cloud** | Zulip Inc. | TLS + at-rest | Open-source company, good reputation | Low. |
| **Slack** | Slack (Salesforce/AWS) | TLS + at-rest | SOC 2, ISO 27001, FedRAMP | Low. |
| **Teams** | Microsoft | TLS + at-rest | SOC 2, ISO 27001, FedRAMP, HIPAA | Lowest among hosted (enterprise-grade). |
| **Telegram** | Telegram Inc. | TLS + at-rest (Telegram holds keys) | No formal compliance certs | Medium. No E2E for groups. |
| **Discord** | Discord Inc. | TLS + at-rest | No formal compliance certs | Highest. Data harvesting, community platform design. |

For dev session data (code output, architecture decisions, build logs), all hosted platforms are adequate. For proprietary or sensitive work, self-hosted or Zulip Cloud (with later migration to self-hosted) is the safer choice. Discord is the weakest — its community-platform design and data practices are not built for private work.

[zulip-cloud-hosted, slack-hosted-bot-platform, discord-hosted-bot-detailed, telegram-bot-sdk-detailed, teams-hosted-bot-platform]

### Provisioning automability.

Every hosted platform requires at least one manual step (account/app creation). After that, the degree of API-driven automation varies:

- **Zulip Cloud:** Manual org signup. Then streams, bots, and topics are all API-creatable. Bot API keys returned on creation. `/swain-stage` can automate everything after signup.
- **Slack:** Manual app creation in Slack App Directory. Then channels, bot invitations, and messaging are API-driven. OAuth token from app install.
- **Discord:** Manual bot application in Developer Portal. Then servers, channels, forum posts, and permissions are API-driven.
- **Telegram:** Manual BotFather chat to create bot. Group creation and forum mode enablement require operator action (Bot API cannot create groups). Topics are API-creatable after group exists.
- **Teams:** Manual Azure AD app registration with permission configuration and admin consent. Most complex setup of any platform.

Zulip Cloud and Slack have the best provisioning story. Telegram's limitation (cannot create groups via Bot API) adds a manual step. Teams is the most complex.

[zulip-cloud-hosted, slack-hosted-bot-platform, discord-hosted-bot-detailed, telegram-bot-sdk-detailed, teams-hosted-bot-platform]

### Threading still decides the feature winner.

Threading rankings are unchanged by adding hosted platform depth:

1. **Zulip (Cloud or self-hosted)** — mandatory stream + topic. Best-in-class. Zero extra bot code for session separation.
2. **Slack** — `thread_ts` threading. Good. One parent message per session, replies in thread. Mature and well-understood.
3. **Discord** — forum channels. Good. Forum posts as sessions, tags for status. Auto-archiving adds friction.
4. **Matrix (conduwuit)** — `m.thread` relations via MSC3440. Good but more complex bot code.
5. **Telegram** — forum topics. Good. `message_thread_id` for topic posting. Topic CRUD via Bot API.
6. **Teams** — reply chains. Adequate. Less prominent than dedicated threading models.
7. **Mattermost** — threads. Good but requires self-hosting with PostgreSQL.
8. **Tinode, Campfire, IRC** — no threading. Not viable for session-per-thread.

[zulip-bot-api, slack-hosted-bot-platform, discord-hosted-bot-detailed, telegram-forum-topics-bot-api, matrix-threading-msc3440, teams-hosted-bot-platform]

### Self-hosted options remain valid for operators who need them.

The self-hosted analysis from earlier revisions still holds. For operators who need data sovereignty or want to avoid vendor lock-in:

- **Conduwuit (Matrix)** is the lightest self-hosted option. Single binary, 20-100 MB RAM, file-copy backup. Threading via MSC3440. Element X for mobile.
- **Zulip self-hosted** has the best threading but requires five services. The highest ops burden.
- **Mattermost** is a middle ground. One binary + PostgreSQL. Good threading, familiar Slack-like UX.

The key insight: **self-hosting is now a tier-2 option, not a prerequisite.** Start hosted, migrate to self-hosted when (and if) you need it.

[conduwuit-deployment-operations, zulip-self-hosting, zulip-upgrade-operations, mattermost-vs-rocketchat-comparison, mattermost-upgrade-operations]

### Migration paths vary dramatically.

| From | To Self-Hosted | Effort |
|---|---|---|
| **Zulip Cloud** | Zulip self-hosted | Config change. Data export/import. Bot code unchanged. |
| **Slack** | Any self-hosted | Platform switch. New adapter. Data export (JSON) requires ETL. |
| **Discord** | Any self-hosted | Platform switch. New adapter. Data export limited (ToS restrictions). |
| **Telegram** | Any self-hosted | Platform switch. New adapter. Desktop export available but import is custom. |
| **Teams** | Any self-hosted | Platform switch. New adapter. Export via eDiscovery/Graph API. |

Zulip Cloud is the only hosted platform where migration to self-hosted is a non-event. Every other platform requires a full platform switch.

[zulip-cloud-hosted, slack-hosted-bot-platform, discord-hosted-bot-detailed, telegram-bot-sdk-detailed, teams-hosted-bot-platform]

### Operational simplicity ranking (updated with hosted platforms at top).

| Platform | Deployment | Upgrade | Backup | Cost |
|---|---|---|---|---|
| **Telegram** | Nothing. | Nothing. | N/A. | Free. |
| **Discord** | Nothing. | Nothing. | N/A. | Free. |
| **Zulip Cloud** | Nothing. | Nothing. | N/A. | Free / $8/mo. |
| **Slack** | Nothing. | Nothing. | N/A. | Free / $7.25/mo. |
| **Teams** | Nothing (but complex app setup). | Nothing. | N/A. | $6/mo (M365). |
| **Conduwuit** | Single binary. | Replace binary. | File copy. | VPS cost (~$5/mo). |
| **Campfire** | Single Docker container. | Pull image. | SQLite file copy. | $299 one-time. |
| **Mattermost** | Binary + PostgreSQL. | 12-step or image swap. | File copy + pg_dump. | Free / VPS cost. |
| **Zulip self-hosted** | 5 services. | Scripted upgrade. | Scripted tarball. | Free / VPS cost. |

[conduwuit-deployment-operations, zulip-upgrade-operations, mattermost-upgrade-operations, campfire-37signals, zulip-cloud-hosted, slack-hosted-bot-platform]

### Push notification services (ntfy, Gotify) are not chat surfaces.

Unchanged from earlier analysis. ntfy is a one-way notification system. It complements a chat system but cannot replace one. [ntfy-push-notification-service]

### Building a custom chat server is still the wrong trade-off.

Unchanged from earlier analysis. Existing platforms provide more features with less code and less ongoing burden. [custom-websocket-chat-assessment]

### Matterbridge enables hybrid approaches.

Matterbridge bridges messages between 30+ platforms. If swain supports multiple chat backends, Matterbridge can relay between them. The main hybrid scenario: bot posts to Zulip (self-hosted, for data sovereignty), Matterbridge bridges to Telegram (for mobile convenience). Thread fidelity across bridges is best-effort. [matterbridge-chat-bridge]

## Points of Agreement

All sources agree on these points:

- Hosted platforms eliminate ops burden entirely for the chat layer.
- Threading quality is the top factor when choosing a platform for structured bot output.
- Zulip has the best threading model regardless of deployment method.
- Python SDKs for Slack, Discord, and Telegram are mature and production-ready.
- Microsoft Teams is over-engineered for a solo developer use case.
- Push notification services are not chat replacements.
- Building a custom chat server is not worth the maintenance cost.

## Points of Disagreement

- **Hosted vs. self-hosted default.** Privacy advocates insist on self-hosting. Pragmatists say hosted is the right default for a dev tool, with self-hosting as an escape hatch.
- **Telegram rate limits.** 20 msg/min/group is tight. Some see batching as trivial and transparent (AIORateLimiter handles it). Others see it as a UX compromise that delays output visibility.
- **Discord security.** Some developers already use Discord for all project communication and see no issue. Others consider it inappropriate for anything beyond open-source work.
- **Slack pricing.** $7.25/month is cheap. But the free tier's 90-day history and 10-app limit make evaluation awkward — you outgrow free fast but must pay before you know if you will stick with it.
- **Zulip Cloud free tier.** 10K messages is either "plenty to evaluate" or "gone in two weeks" depending on bot output volume.
- **Matrix vs. Zulip threading.** Matrix fans prefer the federated protocol and client ecosystem. Zulip fans prefer first-class mandatory threading.

## Gaps

- **Zulip Cloud bot billing.** Docs do not confirm whether bots count as billable users. Need to check with Zulip sales.
- **Zulip Cloud rate limits.** Not separately documented. Assumed to match self-hosted but not confirmed for high-volume bot use.
- **Slack Socket Mode at scale.** Socket Mode avoids needing a public endpoint, but behavior under sustained high-throughput bot output is undocumented.
- **Discord ToS for automated posting.** Discord's Terms of Service restrict automated bulk messaging. Bot output to a private server may be fine, but the line is fuzzy.
- **Telegram group creation automation.** The Bot API cannot create groups. MTProto API can but needs a user account. The provisioning story has a manual gap.
- **Matterbridge thread fidelity.** How well do Zulip topics bridge to Telegram forum topics or Slack threads? No source tests this cross-platform thread mapping.
- **Signal as transport.** No official bot API. Not evaluated.

## Recommendation

For this use case (one operator, room per project, thread per session, bot posts nonstop, operator steers from mobile, minimal ops burden):

**Zulip Cloud is the recommended starting point for v1.** It uniquely combines:

1. **Zero ops.** Hosted platform, nothing to deploy.
2. **Best threading.** Mandatory stream + topic maps directly to session-per-topic.
3. **Seamless migration.** Same API as self-hosted. Bot code unchanged. Data export/import supported.
4. **Good free tier.** 10K messages to evaluate. $8/month for unlimited.
5. **Mature Python SDK.** Official `zulip` package covers all API endpoints.

The migration path is the deciding factor. Every other hosted platform is a one-way bet. Zulip Cloud is the only one where moving to self-hosted later is a config change, not a rewrite.

**Tiered backend support:**

1. **Tier 1 (recommended default): Zulip Cloud.** Best threading, seamless self-hosted migration, good SDK. The adapter code works for both Cloud and self-hosted.
2. **Tier 2 (alternative hosted): Slack or Telegram.** Slack for operators in Slack-native orgs. Telegram for operators who want completely free with good-enough threading. Both have excellent Python SDKs.
3. **Tier 3 (self-hosted): Conduwuit or Zulip self-hosted.** For operators who need data sovereignty. Conduwuit is lighter. Zulip self-hosted has better threading.
4. **Not recommended: Discord (security concerns), Teams (complexity and cost), Campfire (no threading), IRC (no threading).**

**The adapter abstraction makes this viable.** The bot code talks to a platform adapter. The adapter talks to the platform API. Adding a new backend means writing a new adapter, not rewriting the bot. Start with the Zulip adapter (covers both Cloud and self-hosted). Add Slack and Telegram adapters later if demand arises.
