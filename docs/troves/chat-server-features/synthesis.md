# Synthesis: Self-Hostable Chat Servers for Bot-Driven Development

## Context

This trove looks at self-hostable chat servers for a bot-driven dev workflow run by one person. The use case: one room per project, one thread per session. A bot posts updates nonstop. The operator reads and steers from a phone. This feeds an ADR for chat protocol selection under VISION-006 (Untethered Operator).

This revision adds two new lenses: (1) whether Campfire's lack of threads can be worked around with prefixed room names, and (2) operational simplicity as a primary selection criterion. A solo operator cannot debug a five-service stack at 2 AM. The server must stay up without intervention, upgrade in seconds, and back up with a file copy.

## Key Findings

### Operational simplicity reshuffles the ranking.

When "single binary, trivial upgrade, file-copy backup" is a primary criterion, the field reorders:

| Server | Deployment | Upgrade | Backup | Rollback |
|---|---|---|---|---|
| **Conduwuit** | Single binary or single Docker container. No external services. | Replace binary, restart. Seconds of downtime. | File copy of one directory. | Swap binary back. |
| **Campfire** | Single Docker container, SQLite, no external services. | Pull new image, restart. | SQLite file copy. | Pull old image tag. |
| **Mattermost** | One binary + PostgreSQL. Docker Compose typical. | 12-step manual (binary) or image swap (Docker). Auto-migrations. | File copy + `pg_dump`. | Restore from backup. No documented rollback steps. |
| **Zulip** | Five services (app, PostgreSQL, Redis, RabbitMQ, Memcached). | Scripted upgrade, minutes of downtime. | Scripted tarball (PostgreSQL dump inside). | Minor: symlink swap. Major: restore from backup. |

[conduwuit-deployment-operations, zulip-upgrade-operations, mattermost-upgrade-operations, campfire-37signals]

Conduwuit and Campfire are the only true single-process deployments. Mattermost needs PostgreSQL. Zulip needs five services. For a solo operator who values not being paged, fewer moving parts means fewer failure modes.

### Threading still decides the feature winner.

The platforms fall into three tiers:

1. **Zulip** — every message must have a stream and a topic. A bot sets `topic: "session-2026-04-06-001"` and gets an organized thread for free. Threading is built in, not bolted on. [zulip-self-hosting, zulip-bot-api]
2. **Matrix and Mattermost** — both support threads, but threads are opt-in. In Matrix, the bot must track root event IDs and set `m.thread` relations (MSC3440). In Mattermost, the bot tracks parent post IDs. More code for the same result. [matrix-threading-msc3440, mattermost-vs-rocketchat-comparison]
3. **Campfire** — no threads at all. The prefix-as-room workaround is not viable (see below). [campfire-37signals, campfire-room-prefix-threading-analysis]

### The Campfire prefix-as-thread workaround is not viable.

The idea: use prefixed room names (`swain/SPEC-142-session-abc`) as pseudo-threads. Three blocking problems:

1. **No room creation API.** The bot API cannot create rooms. Only human admins can do it (and v1.4.0 restricts creation to admins). A source fork adding room CRUD is possible but adds ongoing merge burden. [campfire-bot-kit-api]
2. **No room hierarchy.** Rooms are a flat list in the sidebar. Prefixed names sort alphabetically but do not group visually. There are no folders, categories, or collapsible sections. [campfire-room-prefix-threading-analysis]
3. **PWA-only mobile.** Campfire has no native app. Room switching in a PWA is heavier than clicking a topic or thread in a native app. With 10+ thread rooms, the flat sidebar becomes cluttered. [campfire-37signals, campfire-room-prefix-threading-analysis]

No one in the Campfire community has proposed or documented this pattern. GitHub Discussions show webhook questions, not threading workarounds. [campfire-bot-kit-api, campfire-room-prefix-threading-analysis]

Compared to Zulip's stream+topic (zero bot effort, native topic sidebar) and Matrix's MSC3440 (moderate bot effort, thread panel in Element X), prefixed rooms are qualitatively worse on every axis.

### Bot APIs range from rich to bare.

Zulip and Mattermost have the best bot APIs. Both offer full CRUD on channels and messages, official SDKs, and webhook support. Matrix has a strong client-server API that serves all clients, not just bots. Campfire only has webhooks: bots cannot create rooms, read history, or manage membership. [zulip-bot-api, mattermost-vs-rocketchat-comparison, campfire-bot-kit-api]

### Backup stories vary from trivial to involved.

- **Conduwuit:** Stop server, `cp -r` the data directory. One command. [conduwuit-deployment-operations]
- **Campfire:** Stop container, copy the SQLite file. One command. [campfire-37signals]
- **Mattermost:** File copy for the app + `pg_dump` for the database. Two coordinated steps. [mattermost-upgrade-operations]
- **Zulip:** Run the backup script, which produces a tarball containing a PostgreSQL dump, uploaded files, and config. One command that wraps multiple steps. [zulip-upgrade-operations]

For a solo operator, file-copy backups are far easier to automate, verify, and restore. Conduwuit and Campfire win here.

### Resource requirements span two orders of magnitude.

- **Conduwuit:** 20-100 MB RAM. Runs on a Raspberry Pi. [conduit-matrix-homeserver, conduwuit-deployment-operations]
- **Campfire:** ~2 GB RAM, 1 CPU. Light for a Rails app. [campfire-37signals]
- **Mattermost:** 2-4 GB RAM. [mattermost-vs-rocketchat-comparison, mattermost-upgrade-operations]
- **Zulip:** 2 GB RAM minimum. Five services share that budget. [zulip-self-hosting, zulip-upgrade-operations]
- **Synapse:** 350 MB for one user, grows fast with federation. [matrix-synapse-self-hosting-2025]

### Mobile apps vary in quality.

- **Matrix:** Element X is fast and polished. Many other clients exist. [matrix-synapse-self-hosting-2025]
- **Zulip:** Native iOS and Android apps. Push alerts free for up to 10 self-hosted users. [zulip-self-hosting]
- **Mattermost:** Native mobile apps. Solid. [mattermost-vs-rocketchat-comparison]
- **Campfire:** PWA only. No native apps. [campfire-37signals]

### E2E encryption does not matter here.

Only Matrix has mature E2E encryption. But bots must handle key swaps and device checks. When you own the server, E2E adds cost with no benefit. [matrix-synapse-self-hosting-2025]

## Points of Agreement

All sources agree on these points:

- Self-hosted chat is easier in 2026 than ever.
- Threading quality is the top factor when choosing a platform for structured bot output.
- Zulip has the best threading model for organized, searchable conversations.
- Matrix has the richest protocol but the most complexity (unless using conduwuit).
- Campfire trades features for simplicity but cannot compensate for missing threads.
- Fewer moving parts means fewer failure modes for a solo operator.

## Points of Disagreement

- **Matrix vs. Zulip for bots.** Matrix fans say the federated protocol and large client pool outweigh the threading gap. Zulip fans say first-class threading removes a whole class of bot problems.
- **Mattermost licensing.** Some see the open-core model as fine. Others call the 10,000-message search cap on the free tier a dealbreaker.
- **Conduwuit governance.** Fork drama (Conduit -> conduwuit -> Continuwuity) raises questions about long-term maintenance.
- **Zulip operational weight.** Zulip's five services are individually mature and well-understood. Some argue the scripted installer makes it "set and forget." Others argue any multi-service system has more failure modes than a single binary.

## Gaps

- **Zulip push on self-hosted.** Free tier caps push alerts at 10 users. Fine for one operator but worth noting.
- **Matrix bot thread code.** No source shows a side-by-side code comparison of thread handling in Matrix vs. Zulip. The design gap is clear but the code effort is not measured.
- **Campfire bot API growth.** Campfire is open source (MIT). The bot API may grow, but there is no public roadmap and community discussion is sparse.
- **Conduwuit long-term governance.** The fork lineage is messy. Worth monitoring.
- **Zulip Docker operational profile.** Docker deployment is documented as harder than the native installer, but detailed Docker-specific upgrade and rollback procedures are sparse.

## Recommendation Signal

For this use case (one operator, room per project, thread per session, bot posts nonstop, operator steers from mobile, minimal ops burden):

**Zulip remains the best feature fit.** Its mandatory topic threading maps straight to the session-per-thread need with zero extra bot code. The bot API covers all needed actions. Mobile apps work well. All features are free when self-hosted. The downside is operational weight: five services, PostgreSQL backup, and a heavier upgrade path. For a solo operator who values uptime over tinkering, this is a real cost.

**Conduwuit (Matrix) is the best operational fit.** Single binary, 20-100 MB RAM, file-copy backup, seconds-long upgrades. Threading works but requires more bot code (MSC3440 relation tracking). The protocol is richer and the client ecosystem (Element X) is excellent. If the bot can absorb the thread-management complexity, conduwuit offers the simplest operations by far.

**The tradeoff is threading UX vs. operational simplicity.** Zulip has the better threading model. Conduwuit has the better ops model. A decision here depends on whether the operator weights "never think about the server" above "never think about bot thread code."

**Mattermost is a solid third pick** if Slack-like UX matters. The open-core license and PostgreSQL dependency are downsides.

**Campfire is ruled out.** No threads, no room creation API, no room hierarchy, PWA-only mobile. The prefix-as-thread workaround does not salvage it. Even with a source fork, the UX remains poor compared to native threading in Zulip or Matrix.
