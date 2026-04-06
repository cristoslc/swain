# Synthesis: Chat Platforms for Bot-Driven Development

## Context

This trove evaluates chat platforms for a bot-driven dev workflow run by one person. The use case: one room per project, one thread per session. A bot posts updates nonstop. The operator reads and steers from a phone. This feeds an ADR for chat protocol selection under VISION-006 (Untethered Operator).

This revision reframes the central question. Earlier revisions compared self-hosted servers and asked which one to run on a VPS. This revision sees that **for v1, a hosted platform removes the VPS entirely**. The provisioning command (`/swain-stage`) just registers a bot and connects bridges. The chat adapter code speaks to an API. It does not care where the server lives. Self-hosting becomes an option, not a requirement.

## Hosted vs. Self-Hosted: The New Default

### Why hosted is the v1 default.

Earlier analysis found a three-way tension: threading UX vs. operational simplicity vs. vendor independence. Hosted platforms resolve the "operational simplicity" axis completely — zero servers to run, zero backups to manage, zero upgrades to perform. The bot code is the only thing to write and maintain.

For a solo developer trying swain for the first time, the path to value should be short: install swain, run `/swain-stage`, start a session, see output on your phone. If step one is "provision a VPS, install Docker, configure DNS, deploy a chat server," most operators will stop before they start. [zulip-cloud-hosted, slack-hosted-bot-platform, telegram-forum-topics-bot-api, discord-hosted-bot-transport]

### The chat adapter abstraction.

The bot code talks to an API. Whether that API is `https://yourorg.zulipchat.com` (Zulip Cloud) or `https://zulip.yourdomain.com` (self-hosted Zulip), the code is identical. The adapter layer abstracts the transport. This means:

- Hosted is the default for new adopters.
- Self-hosted is an option for operators who want data sovereignty or customization.
- Migration between hosted and self-hosted is a config change, not a rewrite.

This holds best for Zulip, where Cloud and self-hosted share the same codebase and API. Slack, Discord, Telegram, and WhatsApp have no self-hosted version. Leaving means switching platforms entirely. [zulip-cloud-hosted, zulip-self-hosting]

### Zulip Cloud is the recommended starting point.

Zulip Cloud stands out because it is the only hosted platform where the bot code is identical to self-hosted and migration is bidirectional:

- **Same API.** The `zulip` Python SDK works with both Cloud and self-hosted. Change the `site` URL, everything else stays the same.
- **Same features.** No "open core" catch. Every feature on Cloud is available on self-hosted.
- **Bidirectional migration.** Export from Cloud, import to self-hosted (or vice versa). Message history, streams, topics, and files transfer.
- **Best threading.** Mandatory stream + topic model gives session-per-topic for free. No extra bot code to manage thread IDs.
- **Free tier.** 10,000-message search limit. Adequate for getting started. $8/month for unlimited.

No other hosted platform offers this combination. Slack, Discord, Telegram, and WhatsApp are all one-way commitments. [zulip-cloud-hosted, zulip-bot-api, zulip-self-hosting]

## Key Findings

### Hosted platform comparison.

| Platform | Python SDK | Threading | Rate Limit | Free Tier | Security | Self-Hosted Path | Provisioning |
|---|---|---|---|---|---|---|---|
| **Zulip Cloud** | `zulip` (official, mature) | Mandatory topics (best) | Same as self-hosted | 10K msg search | Good (open-source co.) | Seamless (same software) | Org signup manual; rest via API. |
| **Slack** | Bolt for Python (excellent) | `thread_ts` (good) | 1 msg/sec/channel | 90-day history, 10 apps | SOC 2, ISO 27001 | None (no self-hosted Slack) | App creation manual; rest via API. |
| **Discord** | discord.py (excellent) | Forum channels (good) | 50 req/sec global | Unlimited, free | Weak (community platform) | None | Bot app creation manual; rest via API. |
| **Telegram** | python-telegram-bot (excellent) | Forum topics (good) | 20 msg/min/group | Unlimited, free | Adequate (cloud-stored) | None | BotFather manual; group setup manual. |
| **WhatsApp** | PyWa (community, adequate) | Reply-to only (poor) | 80 MPS; volume tiers | No free tier (per-msg fees) | Weak (Meta sees content) | None | Meta Business Verification (complex). |
| **Teams** | teams.py (alpha) | Reply chains (adequate) | 1 msg/2sec/thread | Requires M365 ($6/mo) | Enterprise-grade | None | Azure AD app registration (complex). |

[zulip-cloud-hosted, slack-hosted-bot-platform, discord-hosted-bot-detailed, telegram-bot-sdk-detailed, teams-hosted-bot-platform, whatsapp-business-api-platform, whatsapp-pywa-python-sdk]

### Python SDK quality and maturity.

The SDKs fall into four tiers:

1. **Excellent and production-ready.** Bolt for Python (Slack), discord.py, python-telegram-bot. All are async-native, actively maintained, well-documented, and handle rate limiting automatically. Any of these would be a solid foundation for the swain chat adapter.
2. **Good and stable.** The `zulip` Python SDK. Official, functional, covers all API endpoints. Less community ecosystem than Slack/Discord, but reliable.
3. **Adequate but constrained.** PyWa (WhatsApp). Async, typed, webhook-ready, actively maintained. But community-run (524 stars vs. 28K+ for python-telegram-bot), no built-in rate limiter, and the platform's complexity (template approvals, 24h service windows) bleeds through.
4. **Immature.** teams.py (Microsoft). Alpha-stage, breaking changes expected, threading support undocumented. Not ready for production use.

[slack-hosted-bot-platform, discord-hosted-bot-detailed, telegram-bot-sdk-detailed, zulip-bot-api, teams-hosted-bot-platform, whatsapp-pywa-python-sdk]

### Rate limits for continuous bot posting.

The bot posts every tool call, text output, status change, and error. This is high-frequency output. Rate limits determine whether the bot can stream output or must batch.

| Platform | Effective Limit | Batching Required? | SDK Auto-Handling? |
|---|---|---|---|
| **Discord** | 50 req/sec global; ~5-10 msg/sec/channel practical | No | Yes (discord.py) |
| **WhatsApp** | 80 MPS default (Cloud API throughput) | No (throughput is generous) | No (manual) |
| **Slack** | 1 msg/sec/channel (60/min) | Light batching | Yes (Bolt SDK) |
| **Zulip Cloud** | Not explicitly documented; same as self-hosted | Light batching likely | Partial (SDK retries on 429) |
| **Teams** | 1 msg/2sec/thread (30/min) | Yes | Unknown (alpha SDK) |
| **Telegram** | 20 msg/min/group | Yes (significant) | Yes (AIORateLimiter) |

WhatsApp's raw throughput (80 MPS) is the highest, but the number is misleading. The real constraint is cost: messages outside the 24-hour service window need paid templates. Within the window, throughput is generous. The binding constraint is economic, not technical.

[discord-hosted-bot-detailed, slack-hosted-bot-platform, telegram-bot-sdk-detailed, teams-hosted-bot-platform, telegram-forum-topics-bot-api, whatsapp-business-api-platform]

### Free tier viability for a single operator with N bots.

| Platform | Free? | Practical Limit | When to Pay |
|---|---|---|---|
| **Telegram** | Completely free. No limits on messages, bots, or groups. | File upload (50 MB). Rate limits (20/min/group). | Never. |
| **Discord** | Completely free for bot use. | File upload (25 MB). | Never for bot features. |
| **Zulip Cloud** | Free tier: 10K message search limit. | ~100 days at moderate use. | $8/month for unlimited history. |
| **Slack** | Free: 90-day history, 10 apps, data deleted after 1 year. | History loss and app limit are real constraints. | $7.25/month (Pro) for sustained use. |
| **WhatsApp** | No free tier. Service replies free within 24h window. Template messages cost per delivery. | Bot-initiated alerts cost money. No free tier for templates. | Immediately for proactive messages. Free only for reactive replies. |
| **Teams** | Free Teams cannot deploy bots. | Requires M365 ($6/month minimum). | Immediately. |

WhatsApp's pricing model is the most complex. When the operator sends a command, bot replies are free for 24 hours (the service window). But proactive alerts — session starts, errors, status updates when the operator has not messaged — need pre-approved templates and cost per delivery. During active sessions, most messages are free. For background monitoring or async alerts, costs add up.

[zulip-cloud-hosted, slack-hosted-bot-platform, discord-hosted-bot-detailed, telegram-bot-sdk-detailed, teams-hosted-bot-platform, whatsapp-business-api-platform]

### Security: who can see your agent session data?

| Platform | Data Stored By | Encryption | Compliance | Risk Level |
|---|---|---|---|---|
| **Self-hosted (any)** | You | You control | You decide | Lowest (you own the data). |
| **Zulip Cloud** | Zulip Inc. | TLS + at-rest | Open-source company, good reputation | Low. |
| **Slack** | Slack (Salesforce/AWS) | TLS + at-rest | SOC 2, ISO 27001, FedRAMP | Low. |
| **Teams** | Microsoft | TLS + at-rest | SOC 2, ISO 27001, FedRAMP, HIPAA | Lowest among hosted (enterprise-grade). |
| **Telegram** | Telegram Inc. | TLS + at-rest (Telegram holds keys) | No formal compliance certs | Medium. No E2E for groups. |
| **WhatsApp** | Meta | TLS + at-rest (no E2E for Business API) | No formal compliance certs | High. Meta processes message content on Cloud API servers. Meta's privacy policy permits use for ads targeting. |
| **Discord** | Discord Inc. | TLS + at-rest | No formal compliance certs | Highest. Data harvesting, community platform design. |

WhatsApp's security story is counterintuitive. Personal WhatsApp has E2E encryption, but Business API messages are **not** E2E encrypted. Meta processes them on Cloud API servers. Its privacy policy permits using business messaging data for ad targeting. For dev session data with code output and architecture decisions, this matters. WhatsApp and Discord share the bottom tier for security.

[zulip-cloud-hosted, slack-hosted-bot-platform, discord-hosted-bot-detailed, telegram-bot-sdk-detailed, teams-hosted-bot-platform, whatsapp-business-api-platform]

### Provisioning automability.

Every hosted platform requires at least one manual step (account/app creation). After that, the degree of API-driven automation varies:

- **Zulip Cloud:** Manual org signup. Then streams, bots, and topics are all API-creatable. Bot API keys returned on creation. `/swain-stage` can automate everything after signup.
- **Slack:** Manual app creation in Slack App Directory. Then channels, bot invitations, and messaging are API-driven. OAuth token from app install.
- **Discord:** Manual bot application in Developer Portal. Then servers, channels, forum posts, and permissions are API-driven.
- **Telegram:** Manual BotFather chat to create bot. Group creation and forum mode enablement require operator action (Bot API cannot create groups). Topics are API-creatable after group exists.
- **WhatsApp:** Manual Meta Business Verification (business documents, up to 24h). Manual phone number setup. Manual WABA creation and display name approval. After setup, messaging and webhook config are API-driven. The most manual steps of any platform. `/swain-stage` cannot automate onboarding.
- **Teams:** Manual Azure AD app registration with permission configuration and admin consent. Most complex setup of any platform.

WhatsApp and Teams tie for the worst provisioning story. WhatsApp requires a verified business entity, a dedicated phone number, and Meta display name approval — all before a single message can be sent. [zulip-cloud-hosted, slack-hosted-bot-platform, discord-hosted-bot-detailed, telegram-bot-sdk-detailed, teams-hosted-bot-platform, whatsapp-business-api-platform]

### Threading still decides the feature winner.

Threading rankings are unchanged by adding WhatsApp. WhatsApp lands at the bottom alongside platforms that lack threading entirely:

1. **Zulip (Cloud or self-hosted)** — mandatory stream + topic. Best-in-class. Zero extra bot code for session separation.
2. **Slack** — `thread_ts` threading. Good. One parent message per session, replies in thread. Mature and well-understood.
3. **Discord** — forum channels. Good. Forum posts as sessions, tags for status. Auto-archiving adds friction.
4. **Matrix (conduwuit)** — `m.thread` relations via MSC3440. Good but more complex bot code.
5. **Telegram** — forum topics. Good. `message_thread_id` for topic posting. Topic CRUD via Bot API.
6. **Teams** — reply chains. Adequate. Less prominent than dedicated threading models.
7. **Mattermost** — threads. Good but requires self-hosting with PostgreSQL.
8. **WhatsApp** — reply-to-message only. Poor. No thread containers, no topics, no forums. Each group is a flat message stream. Session isolation requires creating separate groups (impractical) or message prefixes (not real threading).
9. **Tinode, Campfire, IRC** — no threading. Not viable for session-per-thread.

WhatsApp's reply-to-message feature is visual quoting, not navigable threading. It does not support the session-per-thread pattern that swain requires. [zulip-bot-api, slack-hosted-bot-platform, discord-hosted-bot-detailed, telegram-forum-topics-bot-api, matrix-threading-msc3440, teams-hosted-bot-platform, whatsapp-business-api-platform]

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
| **WhatsApp** | Any self-hosted | Platform switch. New adapter. No data export capability. Message history is not portable. |
| **Teams** | Any self-hosted | Platform switch. New adapter. Export via eDiscovery/Graph API. |

WhatsApp has the worst migration story. There is no self-hosted version, no data export API, and no history portability. Leaving means starting fresh.

[zulip-cloud-hosted, slack-hosted-bot-platform, discord-hosted-bot-detailed, telegram-bot-sdk-detailed, teams-hosted-bot-platform, whatsapp-business-api-platform]

### Operational simplicity ranking (updated with hosted platforms at top).

| Platform | Deployment | Upgrade | Backup | Cost |
|---|---|---|---|---|
| **Telegram** | Nothing. | Nothing. | N/A. | Free. |
| **Discord** | Nothing. | Nothing. | N/A. | Free. |
| **Zulip Cloud** | Nothing. | Nothing. | N/A. | Free / $8/mo. |
| **Slack** | Nothing. | Nothing. | N/A. | Free / $7.25/mo. |
| **WhatsApp** | Nothing (but complex account setup). | Nothing. | N/A. | Per-message (variable). |
| **Teams** | Nothing (but complex app setup). | Nothing. | N/A. | $6/mo (M365). |
| **Conduwuit** | Single binary. | Replace binary. | File copy. | VPS cost (~$5/mo). |
| **Campfire** | Single Docker container. | Pull image. | SQLite file copy. | $299 one-time. |
| **Mattermost** | Binary + PostgreSQL. | 12-step or image swap. | File copy + pg_dump. | Free / VPS cost. |
| **Zulip self-hosted** | 5 services. | Scripted upgrade. | Scripted tarball. | Free / VPS cost. |

WhatsApp has zero ops burden after setup, but the setup is the most bureaucratic of any platform. Per-message pricing adds ongoing cost uncertainty.

[conduwuit-deployment-operations, zulip-upgrade-operations, mattermost-upgrade-operations, campfire-37signals, zulip-cloud-hosted, slack-hosted-bot-platform, whatsapp-business-api-platform]

### Push notification services (ntfy, Gotify) are not chat surfaces.

Unchanged from earlier analysis. ntfy is a one-way notification system. It complements a chat system but cannot replace one. [ntfy-push-notification-service]

### Building a custom chat server is still the wrong trade-off.

Unchanged from earlier analysis. Existing platforms provide more features with less code and less ongoing burden. [custom-websocket-chat-assessment]

### Matterbridge enables hybrid approaches.

Matterbridge bridges messages between 30+ platforms. If swain supports multiple chat backends, Matterbridge can relay between them. The main hybrid scenario: bot posts to Zulip (self-hosted, for data sovereignty), Matterbridge bridges to Telegram (for mobile convenience). Thread fidelity across bridges is best-effort. Matterbridge does support WhatsApp bridging, but the threading limitation persists — bridged messages arrive as flat text in WhatsApp. [matterbridge-chat-bridge]

## Points of Agreement

All sources agree on these points:

- Hosted platforms eliminate ops burden entirely for the chat layer.
- Threading quality is the top factor when choosing a platform for structured bot output.
- Zulip has the best threading model regardless of deployment method.
- Python SDKs for Slack, Discord, and Telegram are mature and production-ready.
- Microsoft Teams is over-engineered for a solo developer use case.
- WhatsApp lacks the threading model needed for session-per-thread workflows.
- Push notification services are not chat replacements.
- Building a custom chat server is not worth the maintenance cost.

## Points of Disagreement

- **Hosted vs. self-hosted default.** Privacy advocates insist on self-hosting. Pragmatists say hosted is the right default for a dev tool, with self-hosting as an escape hatch.
- **Telegram rate limits.** 20 msg/min/group is tight. Some see batching as trivial and transparent (AIORateLimiter handles it). Others see it as a UX compromise that delays output visibility.
- **Discord security.** Some developers already use Discord for all project communication and see no issue. Others consider it inappropriate for anything beyond open-source work.
- **Slack pricing.** $7.25/month is cheap. But the free tier's 90-day history and 10-app limit make evaluation awkward — you outgrow free fast but must pay before knowing if you will stick.
- **Zulip Cloud free tier.** 10K messages is either "plenty to evaluate" or "gone in two weeks" depending on bot output volume.
- **Matrix vs. Zulip threading.** Matrix fans prefer the federated protocol and client ecosystem. Zulip fans prefer first-class mandatory threading.
- **WhatsApp's 24-hour service window.** Optimists say most swain messages would be reactive (operator sends command, bot replies) and therefore free. Pessimists note that proactive alerts and background monitoring require paid templates — making cost hard to predict.

## Gaps

- **Zulip Cloud bot billing.** Docs do not confirm whether bots count as billable users. Need to check with Zulip sales.
- **Zulip Cloud rate limits.** Not separately documented. Assumed to match self-hosted but not confirmed for high-volume bot use.
- **Slack Socket Mode at scale.** Socket Mode avoids needing a public endpoint, but behavior under sustained high-throughput bot output is undocumented.
- **Discord ToS for automated posting.** Discord's Terms of Service restrict automated bulk messaging. Bot output to a private server may be fine, but the line is fuzzy.
- **Telegram group creation automation.** The Bot API cannot create groups. MTProto API can but needs a user account. The provisioning story has a manual gap.
- **Matterbridge thread fidelity.** How well do Zulip topics bridge to Telegram forum topics or Slack threads? No source tests this cross-platform thread mapping.
- **WhatsApp template approval latency.** New templates need Meta review (up to 24h). If swain needs new notification types, this creates a bottleneck not present on other platforms.
- **WhatsApp BSUID migration impact.** The Business-Scoped User ID transition (March 31, 2026) requires PyWa v4.0.0 (still beta). The migration's impact on existing bot deployments is unclear.
- **Signal as transport.** No official bot API. Not evaluated.

## Recommendation

For this use case (one operator, room per project, thread per session, bot posts nonstop, operator steers from mobile, minimal ops burden):

**Zulip Cloud is the recommended starting point for v1.** It uniquely combines:

1. **Zero ops.** Hosted platform, nothing to deploy.
2. **Best threading.** Mandatory stream + topic maps directly to session-per-topic.
3. **Seamless migration.** Same API as self-hosted. Bot code unchanged. Data export/import supported.
4. **Good free tier.** 10K messages to evaluate. $8/month for unlimited.
5. **Mature Python SDK.** Official `zulip` package covers all API endpoints.

The migration path is the deciding factor. Every other hosted platform is a one-way bet. Only Zulip Cloud lets you move to self-hosted later with a config change, not a rewrite.

**Tiered backend support:**

1. **Tier 1 (recommended default): Zulip Cloud.** Best threading, seamless self-hosted migration, good SDK. The adapter code works for both Cloud and self-hosted.
2. **Tier 2 (alternative hosted): Slack or Telegram.** Slack for operators in Slack-native orgs. Telegram for operators who want completely free with good-enough threading. Both have excellent Python SDKs.
3. **Tier 3 (self-hosted): Conduwuit or Zulip self-hosted.** For operators who need data sovereignty. Conduwuit is lighter. Zulip self-hosted has better threading.
4. **Not recommended: WhatsApp (no threading, per-message costs, complex provisioning, weak security), Discord (security concerns), Teams (complexity and cost), Campfire (no threading), IRC (no threading).**

WhatsApp lands in the "not recommended" tier. The lack of threading is the decisive factor — swain's session-per-thread pattern has no viable path on WhatsApp. Per-message pricing, Meta Business Verification, no self-hosted fallback, and weak security all reinforce the exclusion. WhatsApp is a strong consumer messaging app, but its design does not fit structured bot-driven dev workflows.

**The adapter abstraction makes this viable.** The bot code talks to a platform adapter. The adapter talks to the platform API. Adding a new backend means writing a new adapter, not rewriting the bot. Start with the Zulip adapter (covers both Cloud and self-hosted). Add Slack and Telegram adapters later if demand arises.
